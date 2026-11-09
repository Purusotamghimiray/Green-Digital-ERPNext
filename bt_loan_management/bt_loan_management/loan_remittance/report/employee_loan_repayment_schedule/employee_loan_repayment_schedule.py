import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Sl"), "fieldname": "sl", "fieldtype": "Int", "width": 50},
        {"label": _("Emp ID"), "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 100},
        {"label": _("Employee Name"), "fieldname": "employee_name", "fieldtype": "Data", "width": 160},
        {"label": _("Bank Name"), "fieldname": "bank_name", "fieldtype": "Data", "width": 110},
        {"label": _("Loan Type"), "fieldname": "loan_type", "fieldtype": "Data", "width": 180},
        {"label": _("Loan Acc No."), "fieldname": "loan_acc_no", "fieldtype": "Data", "width": 140},
        {"label": _("Assignment Number"), "fieldname": "assignment_number", "fieldtype": "Data", "width": 150},
        {"label": _("Loan Amount"), "fieldname": "loan_amount", "fieldtype": "Currency", "width": 130},
        {"label": _("Monthly Salary deduction"), "fieldname": "monthly_deduction", "fieldtype": "Currency", "width": 160},
        {"label": _("Start Date"), "fieldname": "start_date", "fieldtype": "Date", "width": 110},
        {"label": _("End Date"), "fieldname": "end_date", "fieldtype": "Date", "width": 110},
        {"label": _("BFSC code For DHI"), "fieldname": "bfsc_code", "fieldtype": "Data", "width": 140}
    ]

def get_data(filters=None):
    conditions = {"docstatus": 1} # Only submitted/active records
    if filters:
        if filters.get("bank_name"):
            conditions["bank_name"] = filters.get("bank_name")
        if filters.get("employee"):
            conditions["employee"] = filters.get("employee")
        if filters.get("loan_type"):
            conditions["loan_type"] = filters.get("loan_type")

    records = frappe.get_all(
        "Employee Loan Schedule",
        fields=[
            "employee", "employee_name", "bank_name", "loan_type",
            "loan_acc_no", "assignment_number", "loan_amount",
            "monthly_deduction", "start_date", "end_date", "bfsc_code"
        ],
        filters=conditions,
        order_by="creation asc"
    )

    for idx, row in enumerate(records, start=1):
        row["sl"] = idx

    return records
