import datetime
from io import BytesIO

import frappe
from frappe import _
from frappe.utils import flt, get_first_day, get_last_day, getdate, today
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters, is_export=False)
    return columns, data


def get_columns():
    return [
        {"fieldname": "sl_no", "label": _("SL. No"), "fieldtype": "Int", "width": 60},
        {"fieldname": "employee_name", "label": _("Name of Employee"), "fieldtype": "Data", "width": 180},
        {"fieldname": "designation", "label": _("Designation"), "fieldtype": "Data", "width": 140},
        {"fieldname": "department", "label": _("Department"), "fieldtype": "Data", "width": 140},
        {"fieldname": "account_number", "label": _("Account Number"), "fieldtype": "Data", "width": 140},
        {"fieldname": "bank_name", "label": _("Bank Name"), "fieldtype": "Data", "width": 140},
        {"fieldname": "tpn_no", "label": _("TPN No."), "fieldtype": "Data", "width": 100},
        {"fieldname": "tfmr", "label": _("TFMR"), "fieldtype": "Currency", "width": 110},
        {"fieldname": "corporate_allowance", "label": _("Corporate Allowance"), "fieldtype": "Currency", "width": 110},
        {"fieldname": "project_allowance", "label": _("Project Allowance"), "fieldtype": "Currency", "width": 110},
        {"fieldname": "fixed_allowance", "label": _("Fixed Allowance"), "fieldtype": "Currency", "width": 110},
        {"fieldname": "communication_allowance", "label": _("Communication Allowance"), "fieldtype": "Currency", "width": 110},
        {"fieldname": "hardship_allowance", "label": _("Hardship Allowance (10%)"), "fieldtype": "Currency", "width": 110},
        {"fieldname": "shift_allowance", "label": _("Shift Allowance (10%)"), "fieldtype": "Currency", "width": 110},
        {"fieldname": "specialized_skills_allowance", "label": _("Specialized Skills Allowance"), "fieldtype": "Currency", "width": 110},
        {"fieldname": "talent_retention_allowance", "label": _("Talent retention Allowance"), "fieldtype": "Currency", "width": 110},
        {"fieldname": "officiating_allowance", "label": _("Officiating Allowance"), "fieldtype": "Currency", "width": 110},
        {"fieldname": "gross_salary", "label": _("Gross salary"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "gis", "label": _("Group Health Insurance (GIS)"), "fieldtype": "Currency", "width": 110},
        {"fieldname": "pf", "label": _("PF"), "fieldtype": "Currency", "width": 90},
        {"fieldname": "employee_welfare", "label": _("Employee Welfare Scheme"), "fieldtype": "Currency", "width": 110},
        {"fieldname": "salary_advance", "label": _("Salary Advance"), "fieldtype": "Currency", "width": 110},
        {"fieldname": "loan", "label": _("Loan"), "fieldtype": "Currency", "width": 90},
        {"fieldname": "pit", "label": _("PIT"), "fieldtype": "Currency", "width": 90},
        {"fieldname": "health_contribution", "label": _("H. Contri."), "fieldtype": "Currency", "width": 100},
        {"fieldname": "other_deductions", "label": _("Other Deductions"), "fieldtype": "Currency", "width": 100},
        {"fieldname": "total_deduction", "label": _("Total Deduction"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "net_salary", "label": _("Net Salary"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "taxable_amount", "label": _("Taxable Amount"), "fieldtype": "Currency", "width": 130},
    ]


def get_data(filters=None, is_export=False):
    filters = filters or {}
    conditions = ["slip.docstatus = 1"]
    values = {}

    if filters.get("company"):
        conditions.append("slip.company = %(company)s")
        values["company"] = filters["company"]

    if filters.get("month") and filters.get("year"):
        month = int(filters["month"])
        year = int(filters["year"])
        start_date = get_first_day(f"{year}-{month:02d}-01")
        end_date = get_last_day(start_date)
        conditions.append("slip.start_date >= %(start_date)s AND slip.start_date <= %(end_date)s")
        values.update({"start_date": start_date, "end_date": end_date})

    where_clause = " AND ".join(conditions)

    # 1. Fetch Salary Slips and joined Employee details in a single query
    slips = frappe.db.sql(f"""
        SELECT
            slip.name, slip.employee, slip.employee_name, slip.designation,
            slip.department, slip.total_working_days, slip.gross_pay,
            slip.total_deduction, slip.net_pay, slip.bank_account_no, slip.bank_name,
            emp.custom_tpn_no, emp.bank_name AS emp_bank_name
        FROM `tabSalary Slip` slip
        LEFT JOIN `tabEmployee` emp ON emp.name = slip.employee
        WHERE {where_clause}
        ORDER BY slip.name ASC
    """, values, as_dict=True)

    if not slips:
        return []

    # 2. Bulk fetch Salary Details
    slip_names = [s.name for s in slips]
    salary_details = frappe.get_all(
        "Salary Detail",
        filters={"parent": ("in", slip_names), "parenttype": "Salary Slip"},
        fields=["parent", "salary_component", "abbr", "amount", "parentfield"]
    )

    details_by_slip = {}
    for item in salary_details:
        details_by_slip.setdefault(item.parent, []).append(item)

    data = []
    diagnostic_info = []

    for idx, slip in enumerate(slips, start=1):
        raw_account_no = (slip.bank_account_no or "").strip()
        clean_account_no = raw_account_no
        bank_name = slip.bank_name or slip.emp_bank_name or ""

        if "(" in raw_account_no and ")" in raw_account_no:
            start_idx = raw_account_no.find("(")
            end_idx = raw_account_no.find(")")
            extracted_bank = raw_account_no[start_idx + 1:end_idx].strip()
            if not bank_name:
                bank_name = extracted_bank
            clean_account_no = raw_account_no[:start_idx].strip()

        row = {
            "sl_no": idx,
            "employee_name": slip.employee_name,
            "designation": slip.designation or "",
            "department": slip.department or "",
            "account_number": clean_account_no,
            "bank_name": bank_name,
            "tpn_no": slip.custom_tpn_no or "",
            "working_days": slip.total_working_days or 0,
            "gross_salary": flt(slip.gross_pay),
            "total_deduction": flt(slip.total_deduction),
            "net_salary": flt(slip.net_pay),
            "tfmr": 0.0, "corporate_allowance": 0.0, "project_allowance": 0.0,
            "fixed_allowance": 0.0, "communication_allowance": 0.0,
            "hardship_allowance": 0.0, "shift_allowance": 0.0,
            "specialized_skills_allowance": 0.0, "talent_retention_allowance": 0.0,
            "officiating_allowance": 0.0, "gis": 0.0, "pf": 0.0,
            "employee_welfare": 0.0, "salary_advance": 0.0, "loan": 0.0,
            "pit": 0.0, "health_contribution": 0.0, "other_deductions": 0.0
        }

        slip_raw_comps = []
        components = details_by_slip.get(slip.name, [])

        for c in components:
            comp = (c.salary_component or "").lower().strip()
            abbr = (c.abbr or "").lower().strip()
            amount = flt(c.amount)
            slip_raw_comps.append(f"{c.salary_component} ({amount})")

            # Earnings breakdown
            if any(k in comp for k in ["tfmr", "basic", "total fixed", "renum", "remun"]) or abbr in ["tfmr", "basic", "bs"]:
                row["tfmr"] += amount
            elif "corporate" in comp:
                row["corporate_allowance"] += amount
            elif "project" in comp:
                row["project_allowance"] += amount
            elif "communication" in comp:
                row["communication_allowance"] += amount
            elif "hardship" in comp:
                row["hardship_allowance"] += amount
            elif "shift" in comp:
                row["shift_allowance"] += amount
            elif "specialized" in comp or "skill" in comp:
                row["specialized_skills_allowance"] += amount
            elif "talent" in comp or "retention" in comp:
                row["talent_retention_allowance"] += amount
            elif "officiating" in comp:
                row["officiating_allowance"] += amount
            elif "fixed" in comp:
                row["fixed_allowance"] += amount
            # Deductions breakdown
            elif any(k in comp for k in ["loan", "bnb", "bob", "nppf"]):
                row["loan"] += amount
            elif "gis" in comp or "group health" in comp or "insurance" in comp:
                row["gis"] += amount
            elif "pf" in comp.split() or "provident" in comp:
                if "employer" not in comp:
                    row["pf"] += amount
            elif "welfare" in comp:
                row["employee_welfare"] += amount
            elif "advance" in comp:
                row["salary_advance"] += amount
            elif "pit" in comp.split() or "tax" in comp.split() or "tds" in comp.split():
                row["pit"] += amount
            elif "health" in comp or "contri" in comp or "hc" in comp.split():
                row["health_contribution"] += amount
            elif any(k in comp for k in ["btl", "house rent", "other recovery"]):
                row["other_deductions"] += amount
            else:
                if c.parentfield == "deductions":
                    row["other_deductions"] += amount

        if row["tfmr"] == 0.0 and slip_raw_comps:
            diagnostic_info.append(f"<b>{slip.employee_name}:</b> {', '.join(slip_raw_comps)}")

        # Bhutan PIT taxable base calculation
        row["taxable_amount"] = max(0.0, row["gross_salary"] - (row["pf"] + row["gis"]))
        data.append(row)

    if diagnostic_info and not is_export:
        msg = "TFMR was 0.00 for the following employees. Database contents:<br><br>" + "<br>".join(diagnostic_info)
        frappe.msgprint(msg, title="Debug: Missing TFMR Components", indicator="orange")

    return data


@frappe.whitelist()
def export_custom_excel(company=None, month=None, year=None):
    current_date = getdate(today())
    month = int(month) if month else current_date.month
    year = int(year) if year else current_date.year

    month_name = datetime.date(year, month, 1).strftime("%B")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Salary Sheet"
    ws.views.sheetView[0].showGridLines = True

    GREEN_HEADER_FILL = PatternFill(start_color="1E4D2B", end_color="1E4D2B", fill_type="solid")
    SUBHEADER_FILL = PatternFill(start_color="2E7D32", end_color="2E7D32", fill_type="solid")
    TOTAL_BG = PatternFill(start_color="E8F5E9", end_color="E8F5E9", fill_type="solid")

    TITLE_FONT = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
    WHITE_FONT = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    DATA_FONT = Font(name="Calibri", size=10, color="1F2937")
    TOTAL_FONT = Font(name="Calibri", size=10, bold=True, color="1E4D2B")

    BORDER_THIN = Border(
        left=Side(style="thin", color="C8E6C9"), right=Side(style="thin", color="C8E6C9"),
        top=Side(style="thin", color="C8E6C9"), bottom=Side(style="thin", color="C8E6C9")
    )
    BORDER_TOTAL = Border(
        left=Side(style="thin", color="1E4D2B"), right=Side(style="thin", color="1E4D2B"),
        top=Side(style="thin", color="1E4D2B"), bottom=Side(style="double", color="1E4D2B")
    )

    ws.merge_cells("A3:AC3")
    title_cell = ws["A3"]
    title_cell.value = f"SALARY SHEET  |  {month_name.upper()} {year}"
    title_cell.font = TITLE_FONT
    title_cell.fill = GREEN_HEADER_FILL
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    title_cell.border = Border(bottom=Side(style="medium", color="2E7D32"))
    ws.row_dimensions[3].height = 34

    headers_merged = [
        ("A5:A6", "SL.\nNo"), ("B5:B6", "Name of Employee"), ("C5:C6", "Designation"),
        ("D5:D6", "Department"), ("E5:E6", "Account Number"), ("F5:F6", "Bank Name"),
        ("G5:G6", "TPN No."), ("H5:R5", "Gross Salary"), ("S5:Z5", "Deduction"),
        ("AA5:AA6", "Total\nDeduction"), ("AB5:AB6", "Net Salary"), ("AC5:AC6", "Taxable Amount")
    ]

    for r_str, txt in headers_merged:
        ws.merge_cells(r_str)
        cell = ws[r_str.split(":")[0]]
        cell.value = txt
        cell.font = WHITE_FONT
        cell.fill = GREEN_HEADER_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    subheaders = {
        "H6": "TFMR", "I6": "Corporate Allowance", "J6": "Project Allowance", "K6": "Fixed Allowance",
        "L6": "Communication Allowance", "M6": "Hardship Allowance (10%)", "N6": "Shift Allowance (10%)",
        "O6": "Specialized Skills Allowance", "P6": "Talent retention Allowance", "Q6": "Officiating Allowance",
        "R6": "Gross\nsalary", "S6": "Group Health Insurance (GIS)", "T6": "PF", "U6": "Employee Welfare Scheme",
        "V6": "Salary Advance", "W6": "Loan", "X6": "PIT", "Y6": "H.\nContri.", "Z6": "Other Deductions"
    }

    for col_ref, txt in subheaders.items():
        cell = ws[col_ref]
        cell.value = txt
        cell.font = WHITE_FONT
        cell.fill = SUBHEADER_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for r in range(5, 7):
        for c in range(1, 30):
            ws.cell(row=r, column=c).border = BORDER_THIN

    data = get_data({"company": company, "month": month, "year": year}, is_export=True)

    col_mapping = [
        "sl_no", "employee_name", "designation", "department", "account_number", "bank_name", "tpn_no",
        "tfmr", "corporate_allowance", "project_allowance", "fixed_allowance", "communication_allowance",
        "hardship_allowance", "shift_allowance", "specialized_skills_allowance", "talent_retention_allowance",
        "officiating_allowance", "gross_salary",
        "gis", "pf", "employee_welfare", "salary_advance", "loan", "pit", "health_contribution", "other_deductions",
        "total_deduction", "net_salary", "taxable_amount"
    ]

    totals = {k: 0.0 for k in col_mapping[7:]}
    start_row = 7

    for r_idx, row in enumerate(data, start=start_row):
        for c_idx, key in enumerate(col_mapping, start=1):
            val = row.get(key, 0)
            cell = ws.cell(row=r_idx, column=c_idx, value=val)
            cell.font = DATA_FONT
            cell.border = BORDER_THIN

            if c_idx in [1, 7]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif c_idx <= 6:
                cell.alignment = Alignment(horizontal="left", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="right", vertical="center")
                cell.number_format = "#,##0.00"
                totals[key] += flt(val)

    tot_row_idx = start_row + len(data)
    ws.merge_cells(start_row=tot_row_idx, start_column=1, end_row=tot_row_idx, end_column=7)
    tot_label_cell = ws.cell(row=tot_row_idx, column=1, value="Total:")
    tot_label_cell.alignment = Alignment(horizontal="right", vertical="center")

    for c_idx, key in enumerate(col_mapping, start=1):
        cell = ws.cell(row=tot_row_idx, column=c_idx)
        cell.font = TOTAL_FONT
        cell.fill = TOTAL_BG
        cell.border = BORDER_TOTAL

        if c_idx > 7:
            cell.value = totals[key]
            cell.number_format = "#,##0.00"
            cell.alignment = Alignment(horizontal="right", vertical="center")

    widths = {
        "A": 6, "B": 24, "C": 18, "D": 24, "E": 20, "F": 22, "G": 12,
        "H": 14, "I": 14, "J": 14, "K": 14, "L": 15, "M": 15, "N": 15,
        "O": 16, "P": 15, "Q": 15, "R": 15,
        "S": 16, "T": 12, "U": 16, "V": 14, "W": 12, "X": 12, "Y": 12, "Z": 14,
        "AA": 16, "AB": 16, "AC": 16
    }
    for col_let, w in widths.items():
        ws.column_dimensions[col_let].width = w

    ws.row_dimensions[5].height = 24
    ws.row_dimensions[6].height = 40
    ws.row_dimensions[tot_row_idx].height = 25

    output = BytesIO()
    wb.save(output)

    frappe.response["filename"] = f"GDL_{month_name}_{year}_Salary_Sheet.xlsx"
    frappe.response["filecontent"] = output.getvalue()
    frappe.response["type"] = "binary"
