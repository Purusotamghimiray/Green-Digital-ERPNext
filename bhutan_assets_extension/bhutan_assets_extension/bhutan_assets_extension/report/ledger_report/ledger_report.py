import frappe
from frappe.utils import flt, getdate, today

DOC_TYPE_MAP = {
    "Journal Entry": "SA",
    "Payment Entry": "AB",
    "Sales Invoice": "DR",
    "Purchase Invoice": "KR",
    "Asset": "AA",
    "Period Closing Voucher": "CL"
}

def execute(filters=None):
    if not filters:
        filters = {}
    columns = get_columns()
    data, _ = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"fieldname": "cleared_status", "label": "Cleared/open items symbol", "fieldtype": "Data", "width": 130},
        {"fieldname": "assignment", "label": "Assignment", "fieldtype": "Data", "width": 140},
        {"fieldname": "document_number", "label": "Document Number", "fieldtype": "Dynamic Link", "options": "voucher_type", "width": 140},
        {"fieldname": "business_area", "label": "Business Area", "fieldtype": "Data", "width": 110},
        {"fieldname": "document_type", "label": "Document Type", "fieldtype": "Data", "width": 110},
        {"fieldname": "posting_date", "label": "Posting Date", "fieldtype": "Date", "width": 110},
        {"fieldname": "document_date", "label": "Document Date", "fieldtype": "Date", "width": 110},
        {"fieldname": "posting_key", "label": "Posting Key", "fieldtype": "Data", "width": 95},
        {"fieldname": "profit_center", "label": "Profit Center", "fieldtype": "Data", "width": 120},
        {"fieldname": "amount_loc_curr_2", "label": "Amount in loc.curr.2", "fieldtype": "Float", "precision": 2, "width": 150},
        {"fieldname": "local_currency_2", "label": "Local currency 2", "fieldtype": "Data", "width": 115},
        {"fieldname": "amount_local_curr", "label": "Amount in local currency", "fieldtype": "Float", "precision": 2, "width": 160},
        {"fieldname": "local_currency", "label": "Local Currency", "fieldtype": "Data", "width": 110},
        {"fieldname": "tax_code", "label": "Tax code", "fieldtype": "Data", "width": 90},
        {"fieldname": "clearing_document", "label": "Clearing Document", "fieldtype": "Data", "width": 140},
        {"fieldname": "text", "label": "Text", "fieldtype": "Data", "width": 240}
    ]

def get_usd_rate(posting_date, override_rate=0):
    if flt(override_rate) > 0:
        return flt(override_rate)
    rate = frappe.db.sql("""
        SELECT exchange_rate
        FROM `tabCurrency Exchange`
        WHERE from_currency = 'USD'
          AND to_currency = 'BTN'
          AND date <= %(posting_date)s
        ORDER BY date DESC
        LIMIT 1
    """, {"posting_date": posting_date})
    return flt(rate[0][0]) if rate else 1.0

def get_data(filters):
    company = filters.get("company")
    account = filters.get("account")
    from_date = filters.get("from_date") or today()
    to_date = filters.get("to_date") or today()
    cost_center = filters.get("cost_center")
    override_rate = flt(filters.get("usd_exchange_rate"))

    if not account:
        return [], {}

    acc_info = frappe.db.get_value(
        "Account", account, ["account_number", "account_name", "name"], as_dict=True
    ) or {}

    conditions = [
        "gle.company = %(company)s",
        "gle.account = %(account)s",
        "gle.is_cancelled = 0",
        "gle.posting_date BETWEEN %(from_date)s AND %(to_date)s"
    ]
    if cost_center:
        conditions.append("gle.cost_center = %(cost_center)s")

    has_business_area = frappe.db.has_column("GL Entry", "business_area")
    ba_select = "COALESCE(gle.business_area, '') AS business_area" if has_business_area else "'' AS business_area"

    entries = frappe.db.sql(f"""
        SELECT
            gle.name,
            gle.posting_date,
            gle.voucher_type,
            gle.voucher_no,
            gle.against_voucher,
            gle.against_voucher_type,
            gle.cost_center,
            gle.debit,
            gle.credit,
            gle.debit_in_account_currency,
            gle.credit_in_account_currency,
            gle.account_currency,
            gle.remarks,
            {ba_select}
        FROM `tabGL Entry` gle
        WHERE {' AND '.join(conditions)}
        ORDER BY gle.posting_date ASC, gle.creation ASC
    """, {
        "company": company,
        "account": account,
        "from_date": from_date,
        "to_date": to_date,
        "cost_center": cost_center
    }, as_dict=True)

    rows = []
    rate_cache = {}

    for gle in entries:
        debit = flt(gle.debit)
        credit = flt(gle.credit)
        btn_amount = debit - credit

        # Posting Key: 40 for Debit, 50 for Credit
        posting_key = "40" if debit > 0 else "50"

        # Document Date (check linked Invoice bill_date or Journal Entry posting_date)
        doc_date = gle.posting_date
        if gle.voucher_type in ("Purchase Invoice", "Sales Invoice"):
            inv_date = frappe.db.get_value(gle.voucher_type, gle.voucher_no, "bill_date" if gle.voucher_type == "Purchase Invoice" else "posting_date")
            if inv_date:
                doc_date = inv_date

        # Profit Center short code (strip company suffix like ' - GDL')
        profit_center = (gle.cost_center or "").split(" - ")[0]

        # Dual Currency Calculation (USD)
        if gle.account_currency == "USD" and not override_rate:
            usd_amount = flt(gle.debit_in_account_currency) - flt(gle.credit_in_account_currency)
        else:
            pdate_str = str(gle.posting_date)
            if pdate_str not in rate_cache:
                rate_cache[pdate_str] = get_usd_rate(gle.posting_date, override_rate)
            rate = rate_cache[pdate_str]
            usd_amount = (btn_amount / rate) if rate else 0.0

        # Clearing Document & Status
        clearing_doc = ""
        if gle.against_voucher and gle.against_voucher != gle.voucher_no:
            clearing_doc = gle.against_voucher
        else:
            linked_clear = frappe.db.get_value(
                "Payment Entry Reference",
                {"reference_name": gle.voucher_no, "docstatus": 1},
                "parent"
            )
            if linked_clear:
                clearing_doc = linked_clear

        cleared_status = "Cleared" if clearing_doc else ""

        # Assignment (Voucher No + Year)
        yr = str(getdate(gle.posting_date).year)
        assignment = f"{gle.voucher_no}{yr}"

        rows.append({
            "cleared_status": cleared_status,
            "assignment": assignment,
            "document_number": gle.voucher_no,
            "voucher_type": gle.voucher_type,
            "business_area": gle.business_area,
            "document_type": DOC_TYPE_MAP.get(gle.voucher_type, "SA"),
            "posting_date": gle.posting_date,
            "document_date": doc_date,
            "posting_key": posting_key,
            "profit_center": profit_center,
            "amount_loc_curr_2": round(usd_amount, 2),
            "local_currency_2": "USD",
            "amount_local_curr": round(btn_amount, 2),
            "local_currency": "BTN",
            "tax_code": "V0",
            "clearing_document": clearing_doc,
            "text": (gle.remarks or "").strip()
        })

    return rows, acc_info