import frappe
from frappe.utils import format_date
from io import BytesIO
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Sl", "fieldname": "sl", "fieldtype": "Int", "width": 50},
        {"label": "Emp ID", "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 110},
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 160},
        {"label": "Bank Name", "fieldname": "bank_name", "fieldtype": "Link", "options": "Remittance Bank", "width": 110},
        {"label": "Loan Type", "fieldname": "loan_type", "fieldtype": "Link", "options": "External Loan Type", "width": 180},
        {"label": "Loan Acc No.", "fieldname": "loan_acc_no", "fieldtype": "Data", "width": 140},
        {"label": "Assignment Number", "fieldname": "assignment_number", "fieldtype": "Data", "width": 150},
        {"label": "Loan Amount", "fieldname": "loan_amount", "fieldtype": "Currency", "width": 130},
        {"label": "Monthly Salary deduction", "fieldname": "monthly_deduction", "fieldtype": "Currency", "width": 160},
        {"label": "Start Date", "fieldname": "start_date", "fieldtype": "Date", "width": 110},
        {"label": "End Date", "fieldname": "end_date", "fieldtype": "Date", "width": 110},
        {"label": "BFSC code For DHI", "fieldname": "bfsc_code", "fieldtype": "Data", "width": 140}
    ]

def get_data(filters):
    conditions = {"docstatus": ["<", 2]}
    if filters:
        if filters.get("bank_name"):
            conditions["bank_name"] = filters.get("bank_name")
        if filters.get("employee"):
            conditions["employee"] = filters.get("employee")
        if filters.get("loan_type"):
            conditions["loan_type"] = filters.get("loan_type")

    schedules = frappe.get_all(
        "Employee Loan Schedule",
        fields=[
            "name",
            "employee",
            "employee_name",
            "bank_name",
            "loan_type",
            "loan_acc_no",
            "assignment_number",
            "loan_amount",
            "monthly_deduction",
            "start_date",
            "end_date",
            "bfsc_code"
        ],
        filters=conditions,
        order_by="creation asc"
    )

    data = []
    for idx, row in enumerate(schedules, start=1):
        row["sl"] = idx
        data.append(row)

    return data

@frappe.whitelist()
def download_gdl_excel(filters=None):
    if isinstance(filters, str):
        filters = frappe.parse_json(filters)

    data = get_data(filters)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Loan Repayment Schedule"

    thin_border = Border(
        left=Side(style='thin', color='B0B0B0'),
        right=Side(style='thin', color='B0B0B0'),
        top=Side(style='thin', color='B0B0B0'),
        bottom=Side(style='thin', color='B0B0B0')
    )

    # Styles
    title_font = Font(name="Calibri", size=13, bold=True, color="1F4E79")
    title_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="2F5597", end_color="2F5597", fill_type="solid")
    
    data_font = Font(name="Calibri", size=10)
    total_font = Font(name="Calibri", size=10, bold=True)
    total_fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")

    headers = [
        "Sl", "Emp ID", "Employee Name", "Bank Name", "Loan Type",
        "Loan Acc No.", "Assignment Number", "Loan Amount",
        "Monthly Salary deduction", "Start Date", "End Date", "BFSC code For DHI"
    ]

    # --- ROW 1: Title Header merged across all 12 columns ---
    ws.append(["Employee loan Repayment schedule "] + [""] * 11)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=12)
    ws.row_dimensions[1].height = 28

    for col in range(1, 13):
        cell = ws.cell(row=1, column=col)
        cell.fill = title_fill
        cell.border = thin_border
        if col == 1:
            cell.font = title_font
            cell.alignment = Alignment(horizontal="center", vertical="center")

    # --- ROW 2: Column Headers ---
    ws.append(headers)
    ws.row_dimensions[2].height = 24

    for col in range(1, 13):
        cell = ws.cell(row=2, column=col)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border

    # --- Data Rows (Row 3 onwards) ---
    row_num = 3
    for r in data:
        row_vals = [
            r.get("sl"),
            r.get("employee") or "",
            r.get("employee_name") or "",
            r.get("bank_name") or "",
            r.get("loan_type") or "",
            r.get("loan_acc_no") or "",
            r.get("assignment_number") or "",
            r.get("loan_amount") or 0.0,
            r.get("monthly_deduction") or 0.0,
            format_date(r.get("start_date")) if r.get("start_date") else "",
            format_date(r.get("end_date")) if r.get("end_date") else "",
            r.get("bfsc_code") or ""
        ]
        ws.append(row_vals)
        ws.row_dimensions[row_num].height = 20

        for col_idx in range(1, 13):
            cell = ws.cell(row=row_num, column=col_idx)
            cell.font = data_font
            cell.border = thin_border
            if col_idx in [1, 2, 4, 6, 7, 10, 11, 12]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif col_idx in [8, 9]:
                cell.alignment = Alignment(horizontal="right", vertical="center")
                cell.number_format = '#,##0.00'
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")
        row_num += 1

    # --- Total Row ---
    if data:
        total_row = ["Total", "", "", "", "", "", "", f"=SUM(H3:H{row_num-1})", f"=SUM(I3:I{row_num-1})", "", "", ""]
        ws.append(total_row)
        ws.row_dimensions[row_num].height = 22
        ws.merge_cells(start_row=row_num, start_column=1, end_row=row_num, end_column=7)

        for col_idx in range(1, 13):
            cell = ws.cell(row=row_num, column=col_idx)
            cell.font = total_font
            cell.fill = total_fill
            cell.border = thin_border
            if col_idx in [8, 9]:
                cell.alignment = Alignment(horizontal="right", vertical="center")
                cell.number_format = '#,##0.00'
            else:
                cell.alignment = Alignment(horizontal="right", vertical="center")

    # Column widths
    col_widths = [6, 16, 26, 14, 28, 18, 18, 16, 26, 14, 14, 22]
    for i, w in enumerate(col_widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    frappe.response['filename'] = 'GDL_Loan_Report.xlsx'
    frappe.response['filecontent'] = output.getvalue()
    frappe.response['type'] = 'binary'
