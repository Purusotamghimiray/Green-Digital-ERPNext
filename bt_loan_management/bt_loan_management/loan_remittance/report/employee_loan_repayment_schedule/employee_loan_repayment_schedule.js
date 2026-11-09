frappe.query_reports["Employee Loan Repayment Schedule"] = {
    "filters": [
        {
            "fieldname": "bank_name",
            "label": __("Bank Name"),
            "fieldtype": "Link",
            "options": "Remittance Bank"
        },
        {
            "fieldname": "loan_type",
            "label": __("Loan Type"),
            "fieldtype": "Link",
            "options": "External Loan Type"
        },
        {
            "fieldname": "employee",
            "label": __("Employee"),
            "fieldtype": "Link",
            "options": "Employee"
        }
    ]
};
