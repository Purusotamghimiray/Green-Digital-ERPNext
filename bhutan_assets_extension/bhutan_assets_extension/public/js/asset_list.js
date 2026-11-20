frappe.listview_settings['Asset'] = {
    onload: function(listview) {
        listview.page.add_inner_button(__("Export Consolidated Excel"), function() {
            
            frappe.prompt([
                {
                    fieldname: "company",
                    label: __("Company"),
                    fieldtype: "Link",
                    options: "Company",
                    default: frappe.defaults.get_user_default("Company"),
                    reqd: 1
                },
                {
                    fieldname: "report_date",
                    label: __("Report Date"),
                    fieldtype: "Date",
                    default: frappe.datetime.get_today(),
                    reqd: 1
                }
            ], function(values) {
                // Trigger the download once the user submits the prompt
                const queryParams = new URLSearchParams({
                    company: values.company,
                    report_date: values.report_date
                });

                const download_url = frappe.urllib.get_full_url(
                    "/api/method/bhutan_assets_extension.api.download_consolidated_reports?" +
                    queryParams.toString()
                );
                
                // Open download link
                window.open(download_url, '_blank');

            }, __("Consolidated Report Parameters"), __("Download"));
        });
    }
};