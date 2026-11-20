import frappe
from frappe.utils import flt

def execute(filters=None):
    if not filters:
        filters = {}
        
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"fieldname": "asset_head", "label": "Asset Head", "fieldtype": "Link", "options": "Asset Category", "width": 200},
        {"fieldname": "gross_opening", "label": "Gross Block - Opening", "fieldtype": "Currency", "width": 140},
        {"fieldname": "gross_addition", "label": "Acquisition", "fieldtype": "Currency", "width": 130},
        {"fieldname": "gross_disposal", "label": "Disposal/Adjustment", "fieldtype": "Currency", "width": 140},
        {"fieldname": "gross_closing", "label": "Gross Block", "fieldtype": "Currency", "width": 140},
        {"fieldname": "dep_opening", "label": "Accum Dep - Opening", "fieldtype": "Currency", "width": 140},
        {"fieldname": "dep_addition", "label": "Depreciation", "fieldtype": "Currency", "width": 130},
        {"fieldname": "dep_disposal", "label": "Disposal/Adjustment", "fieldtype": "Currency", "width": 140},
        {"fieldname": "dep_closing", "label": "Accum Dep", "fieldtype": "Currency", "width": 140},
        {"fieldname": "book_value", "label": "Book Value", "fieldtype": "Currency", "width": 140}
    ]

def get_data(filters):
    company = filters.get("company")
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    finance_book = filters.get("finance_book") or "Standard Reporting"

    raw_data = frappe.db.sql("""
        SELECT 
            a.asset_category AS asset_head,
            SUM(CASE WHEN a.purchase_date < %(from_date)s THEN a.net_purchase_amount ELSE 0 END) AS gross_opening,
            SUM(CASE WHEN a.purchase_date >= %(from_date)s AND a.purchase_date <= %(to_date)s THEN a.net_purchase_amount ELSE 0 END) AS gross_addition,
            SUM(CASE WHEN a.status IN ('Sold', 'Scrapped') AND a.disposal_date >= %(from_date)s AND a.disposal_date <= %(to_date)s THEN a.net_purchase_amount ELSE 0 END) AS gross_disposal,
            SUM(CASE WHEN a.purchase_date < %(from_date)s THEN COALESCE(a.opening_accumulated_depreciation, 0) ELSE 0 END) AS base_opening_dep
        FROM `tabAsset` a
        WHERE a.docstatus = 1 AND a.company = %(company)s
        GROUP BY a.asset_category
    """, {"from_date": from_date, "to_date": to_date, "company": company}, as_dict=True)

    rows = []
    totals = {
        "asset_head": "Total", "gross_opening": 0.0, "gross_addition": 0.0, "gross_disposal": 0.0,
        "gross_closing": 0.0, "dep_opening": 0.0, "dep_addition": 0.0, "dep_disposal": 0.0,
        "dep_closing": 0.0, "book_value": 0.0
    }

    for row in raw_data:
        dep_open_res = frappe.db.sql("""
            SELECT COALESCE(SUM(ds.depreciation_amount), 0)
            FROM `tabDepreciation Schedule` ds
            INNER JOIN `tabAsset Depreciation Schedule` ads ON ds.parent = ads.name
            INNER JOIN `tabAsset` a ON ads.asset = a.name
            WHERE a.asset_category = %(head)s
              AND a.company = %(company)s
              AND a.docstatus = 1
              AND ads.finance_book = %(fb)s
              AND ads.docstatus = 1
              AND ds.journal_entry IS NOT NULL
              AND ds.journal_entry != ''
              AND ds.schedule_date < %(from_date)s
        """, {"head": row.asset_head, "company": company, "fb": finance_book, "from_date": from_date})

        dep_add_res = frappe.db.sql("""
            SELECT COALESCE(SUM(ds.depreciation_amount), 0)
            FROM `tabDepreciation Schedule` ds
            INNER JOIN `tabAsset Depreciation Schedule` ads ON ds.parent = ads.name
            INNER JOIN `tabAsset` a ON ads.asset = a.name
            WHERE a.asset_category = %(head)s
              AND a.company = %(company)s
              AND a.docstatus = 1
              AND ads.finance_book = %(fb)s
              AND ads.docstatus = 1
              AND ds.journal_entry IS NOT NULL
              AND ds.journal_entry != ''
              AND ds.schedule_date >= %(from_date)s
              AND ds.schedule_date <= %(to_date)s
        """, {"head": row.asset_head, "company": company, "fb": finance_book, "from_date": from_date, "to_date": to_date})

        row["gross_opening"] = flt(row.gross_opening)
        row["gross_addition"] = flt(row.gross_addition)
        row["gross_disposal"] = flt(row.gross_disposal)
        row["gross_closing"] = row["gross_opening"] + row["gross_addition"] - row["gross_disposal"]

        row["dep_opening"] = flt(row.base_opening_dep) + (flt(dep_open_res[0][0]) if dep_open_res else 0.0)
        row["dep_addition"] = flt(dep_add_res[0][0]) if dep_add_res else 0.0
        row["dep_disposal"] = (row["dep_opening"] + row["dep_addition"]) if row["gross_disposal"] > 0 else 0.0
        row["dep_closing"] = row["dep_opening"] + row["dep_addition"] - row["dep_disposal"]
        row["book_value"] = row["gross_closing"] - row["dep_closing"]

        for k in totals:
            if k != "asset_head":
                totals[k] += row[k]

        rows.append(row)

    rows.append(totals)
    return rows