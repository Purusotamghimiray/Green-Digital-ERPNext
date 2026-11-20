from frappe import _

def get_data():
    return {
        "fieldname": "ref_docname",
        "non_standard_fieldnames": {
            "Additional Salary": "ref_docname"
        },
        # This tells Frappe to also filter where ref_doctype = "Employee Loan Schedule"
        "dynamic_links": {
            "ref_docname": ["Employee Loan Schedule", "ref_doctype"]
        },
        "transactions": [
            {
                "label": _("Payroll Integration"),
                "items": ["Additional Salary"]
            }
        ]
    }