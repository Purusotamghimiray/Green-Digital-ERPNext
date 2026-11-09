frappe.query_reports["GDL Loan Report"] = {
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
    ],
    onload: function(report) {
        // Clear any lingering primary action buttons from previously viewed reports
        report.page.clear_primary_action();

        // Make "Export GDL Excel" the primary action button for this report
        report.page.set_primary_action(__("Export GDL Excel"), function() {
            let filters = JSON.stringify(report.get_values());
            let download_url = `/api/method/bt_loan_management.loan_remittance.report.gdl_loan_report.gdl_loan_report.download_gdl_excel?filters=${encodeURIComponent(filters)}`;
            window.open(download_url);
        });
    }
};