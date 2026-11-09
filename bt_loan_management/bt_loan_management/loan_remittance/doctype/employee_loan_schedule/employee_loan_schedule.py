import frappe
from frappe.model.document import Document

class EmployeeLoanSchedule(Document):
    def on_submit(self):
        self.db_set("status", "Active")
        self.create_additional_salary()

    def on_cancel(self):
        self.db_set("status", "Cancelled")
        self.cancel_additional_salary()

    def create_additional_salary(self):
        amount = getattr(self, "monthly_deduction", None) or getattr(self, "monthly_salary_deduction", None)
        emp = getattr(self, "employee", None) or getattr(self, "emp_id", None)

        if not self.salary_component or not amount or not emp:
            return

        company = frappe.db.get_value("Employee", emp, "company") or frappe.db.get_default("company")

        add_sal = frappe.new_doc("Additional Salary")
        add_sal.employee = emp
        add_sal.salary_component = self.salary_component
        add_sal.amount = amount
        add_sal.payroll_date = self.start_date
        add_sal.company = company
        add_sal.overwrite_salary_structure_amount = 0
        add_sal.ref_doctype = self.doctype
        add_sal.ref_docname = self.name
        add_sal.submit()

    def cancel_additional_salary(self):
        linked_salaries = frappe.get_all(
            "Additional Salary",
            filters={"ref_doctype": self.doctype, "ref_docname": self.name, "docstatus": 1},
            pluck="name"
        )
        for sal_name in linked_salaries:
            sal_doc = frappe.get_doc("Additional Salary", sal_name)
            sal_doc.cancel()
