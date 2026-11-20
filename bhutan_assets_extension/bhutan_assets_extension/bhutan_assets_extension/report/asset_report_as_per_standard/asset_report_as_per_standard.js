frappe.query_reports["Asset Report as per Standard"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company"),
            "reqd": 1
        },
        {
            "fieldname": "report_date",
            "label": __("Report Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        }
    ],
    "onload": function(report) {
        // This adds a custom button to the top right of the report screen
        report.page.add_inner_button(__("Download Consolidated Excel"), function() {
            // Get the currently selected company and date
            let company = frappe.query_report.get_filter_value('company');
            let report_date = frappe.query_report.get_filter_value('report_date') || frappe.datetime.get_today();
            
            // Trigger the download from your custom API
            window.open(`/api/method/bhutan_assets_extension.api.download_consolidated_reports?company=${encodeURIComponent(company)}&report_date=${report_date}`);
        });
    }
};