import frappe
from frappe.utils import flt, add_months, today

def execute(filters=None):
    if not filters:
        filters = {}
        
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"fieldname": "asset_code", "label": "Asset Code / ID", "fieldtype": "Link", "options": "Asset", "width": 130},
        {"fieldname": "asset_name", "label": "Asset Name", "fieldtype": "Data", "width": 160},
        {"fieldname": "asset_category_shortform", "label": "Asset Category (ShortForm)", "fieldtype": "Data", "width": 140},
        {"fieldname": "asset_category", "label": "Asset Category", "fieldtype": "Link", "options": "Asset Category", "width": 160},
        {"fieldname": "asset_head", "label": "Asset Head", "fieldtype": "Data", "width": 160},
        {"fieldname": "location", "label": "Location", "fieldtype": "Link", "options": "Location", "width": 140},
        {"fieldname": "cost_center", "label": "Cost Center", "fieldtype": "Link", "options": "Cost Center", "width": 120},
        {"fieldname": "custodian", "label": "Custodian / Assigned To", "fieldtype": "Data", "width": 150},
        {"fieldname": "purchase_date", "label": "Acquisition Date", "fieldtype": "Date", "width": 120},
        {"fieldname": "useful_life", "label": "Useful Life (Years)", "fieldtype": "Float", "width": 120},
        {"fieldname": "end_of_life_date", "label": "End of Life Date", "fieldtype": "Date", "width": 120},
        {"fieldname": "net_purchase_amount", "label": "Acquisition Cost", "fieldtype": "Currency", "width": 140},
        {"fieldname": "additional_value", "label": "Additional value during the Year", "fieldtype": "Currency", "width": 160},
        {"fieldname": "termination", "label": "Termination", "fieldtype": "Currency", "width": 130},
        {"fieldname": "dep_for_year", "label": "Depreciation for the Year", "fieldtype": "Currency", "width": 160},
        {"fieldname": "dep_for_termination", "label": "Depreciation for Termination", "fieldtype": "Currency", "width": 160},
        {"fieldname": "accumulated_depreciation", "label": "Accumulated Depreciation till date", "fieldtype": "Currency", "width": 180},
        {"fieldname": "net_value", "label": "Net Value (NBV)", "fieldtype": "Currency", "width": 140}
    ]

def get_data(filters):
    company = filters.get("company")
    report_date = filters.get("report_date") or today()
    finance_book = "Tax Reporting"
    year_start = str(report_date)[:4] + "-01-01"

    # Safely check for custom fields without crashing if absent
    shortform_select = "'' AS asset_category_shortform"
    if frappe.db.has_column("Asset Category", "custom_shortform"):
        shortform_select = "ac.custom_shortform AS asset_category_shortform"
    elif frappe.db.has_column("Asset Category", "shortform"):
        shortform_select = "ac.shortform AS asset_category_shortform"
    elif frappe.db.has_column("Asset", "custom_asset_category_shortform"):
        shortform_select = "a.custom_asset_category_shortform AS asset_category_shortform"

    head_select = "'' AS asset_head"
    if frappe.db.has_column("Asset Category", "custom_asset_head"):
        head_select = "ac.custom_asset_head AS asset_head"
    elif frappe.db.has_column("Asset Category", "asset_head"):
        head_select = "ac.asset_head AS asset_head"
    elif frappe.db.has_column("Asset", "custom_asset_head"):
        head_select = "a.custom_asset_head AS asset_head"

    assets = frappe.db.sql(f"""
        SELECT 
            a.name AS asset_code,
            a.asset_name,
            {shortform_select},
            a.asset_category,
            {head_select},
            a.location,
            a.cost_center,
            a.custodian,
            a.purchase_date,
            a.disposal_date,
            a.status,
            a.net_purchase_amount,
            COALESCE(a.opening_accumulated_depreciation, 0) AS opening_dep
        FROM `tabAsset` a
        LEFT JOIN `tabAsset Category` ac ON a.asset_category = ac.name
        WHERE a.docstatus = 1
          AND a.company = %(company)s
          AND a.purchase_date <= %(report_date)s
    """, {"company": company, "report_date": report_date}, as_dict=True)

    rows = []
    for asset in assets:
        fb_data = frappe.db.sql("""
            SELECT 
                total_number_of_depreciations, 
                frequency_of_depreciation
            FROM `tabAsset Finance Book`
            WHERE parent = %(asset_code)s
              AND finance_book = %(finance_book)s
            LIMIT 1
        """, {"asset_code": asset.asset_code, "finance_book": finance_book}, as_dict=True)

        opening_dep = flt(asset.opening_dep)
        if fb_data and fb_data[0].total_number_of_depreciations:
            months = flt(fb_data[0].total_number_of_depreciations) * flt(fb_data[0].frequency_of_depreciation)
            asset["useful_life"] = months / 12.0
            asset["end_of_life_date"] = add_months(asset.purchase_date, int(months))
        else:
            asset["useful_life"] = 0.0
            asset["end_of_life_date"] = None

        purchase_cost = flt(asset.net_purchase_amount)
        is_current_year = str(asset.purchase_date) >= year_start
        asset["additional_value"] = purchase_cost if is_current_year else 0.0

        is_terminated = asset.status in ("Sold", "Scrapped") and asset.disposal_date and str(asset.disposal_date) <= str(report_date)
        asset["termination"] = purchase_cost if is_terminated else 0.0

        dep_year = frappe.db.sql("""
            SELECT COALESCE(SUM(ds.depreciation_amount), 0)
            FROM `tabDepreciation Schedule` ds
            INNER JOIN `tabAsset Depreciation Schedule` ads ON ds.parent = ads.name
            WHERE ads.asset = %(asset_code)s
              AND ads.finance_book = %(finance_book)s
              AND ads.docstatus = 1
              AND ds.journal_entry IS NOT NULL
              AND ds.journal_entry != ''
              AND ds.schedule_date >= %(year_start)s
              AND ds.schedule_date <= %(report_date)s
        """, {"asset_code": asset.asset_code, "finance_book": finance_book, "year_start": year_start, "report_date": report_date})
        asset["dep_for_year"] = flt(dep_year[0][0]) if dep_year else 0.0

        dep_total = frappe.db.sql("""
            SELECT COALESCE(SUM(ds.depreciation_amount), 0)
            FROM `tabDepreciation Schedule` ds
            INNER JOIN `tabAsset Depreciation Schedule` ads ON ds.parent = ads.name
            WHERE ads.asset = %(asset_code)s
              AND ads.finance_book = %(finance_book)s
              AND ads.docstatus = 1
              AND ds.journal_entry IS NOT NULL
              AND ds.journal_entry != ''
              AND ds.schedule_date <= %(report_date)s
        """, {"asset_code": asset.asset_code, "finance_book": finance_book, "report_date": report_date})
        posted_dep = flt(dep_total[0][0]) if dep_total else 0.0
        total_dep = opening_dep + posted_dep

        asset["dep_for_termination"] = total_dep if is_terminated else 0.0
        asset["accumulated_depreciation"] = 0.0 if is_terminated else total_dep
        asset["net_value"] = (purchase_cost - asset["termination"]) - asset["accumulated_depreciation"]

        rows.append(asset)
        
    return rows