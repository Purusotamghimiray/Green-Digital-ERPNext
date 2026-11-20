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

        # 1. Validation: Throw an error instead of silently failing
        if not self.salary_component or not amount or not emp:
            frappe.throw("Cannot create Additional Salary: Missing Salary Component, Amount, or Employee ID.")

        # 2. Duplicate Check: Ensure an Additional Salary wasn't already created
        existing_salary = frappe.db.exists(
            "Additional Salary", 
            {
                "ref_doctype": self.doctype, 
                "ref_docname": self.name, 
                "docstatus": ["!=", 2] # Look for anything not cancelled
            }
        )
        if existing_salary:
            return

        company = frappe.db.get_value("Employee", emp, "company") or frappe.db.get_default("company")

        add_sal = frappe.new_doc("Additional Salary")
        add_sal.employee = emp
        add_sal.salary_component = self.salary_component
        add_sal.amount = amount
        add_sal.company = company
        add_sal.overwrite_salary_structure_amount = 0
        
        # 3. Recurring Setup: Replaces the one-time payroll_date
        add_sal.is_recurring = 1
        add_sal.from_date = self.start_date
        add_sal.to_date = self.end_date
        
        # Relational Linking
        add_sal.ref_doctype = self.doctype
        add_sal.ref_docname = self.name
        
        # 4. Safe Insertion: Bypass permissions safely and insert before submitting
        add_sal.flags.ignore_permissions = True
        add_sal.insert()
        add_sal.submit()

    def cancel_additional_salary(self):
        linked_salaries = frappe.get_all(
            "Additional Salary",
            filters={"ref_doctype": self.doctype, "ref_docname": self.name, "docstatus": 1},
            pluck="name"
        )
        for sal_name in linked_salaries:
            sal_doc = frappe.get_doc("Additional Salary", sal_name)
            # Safely bypass permissions to ensure HR can cancel the linked record
            sal_doc.flags.ignore_permissions = True 
            sal_doc.cancel()