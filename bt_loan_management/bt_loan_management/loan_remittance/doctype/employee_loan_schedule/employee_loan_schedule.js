frappe.ui.form.on('Employee Loan Schedule', {
    loan_type: function(frm) {
        if (frm.doc.loan_type) {
            frappe.db.get_value('External Loan Type', frm.doc.loan_type, 'salary_component')
                .then(r => {
                    if (r.message && r.message.salary_component) {
                        frm.set_value('salary_component', r.message.salary_component);
                    }
                });
        }
    }
});
