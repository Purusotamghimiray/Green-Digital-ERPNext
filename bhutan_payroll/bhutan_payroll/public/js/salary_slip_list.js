frappe.listview_settings['Salary Slip'] = {
    onload: function(listview) {
        listview.page.add_inner_button(__("Export Salary Sheet"), function() {
            
            // Generate year options for the prompt
            const cur_year = new Date().getFullYear();
            const year_options = Array.from({length: 8}, (_, i) => (cur_year - 2 + i).toString()).join("\n");
            const month_options = Array.from({length: 12}, (_, i) => (i + 1).toString()).join("\n");

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
                    fieldname: "month",
                    label: __("Month"),
                    fieldtype: "Select",
                    options: month_options,
                    default: (new Date().getMonth() + 1).toString(),
                    reqd: 1
                },
                {
                    fieldname: "year",
                    label: __("Year"),
                    fieldtype: "Select",
                    options: year_options,
                    default: cur_year.toString(),
                    reqd: 1
                }
            ], function(values) {
                // Trigger the download once the user submits the prompt
                const queryParams = new URLSearchParams({
                    company: values.company,
                    month: values.month,
                    year: values.year
                });

                const download_url = frappe.urllib.get_full_url(
                    "/api/method/bhutan_payroll.bhutan_payroll.report.bhutan_salary_report.bhutan_salary_report.export_custom_excel?" +
                    queryParams.toString()
                );
                
                window.location.href = download_url;

            }, __("Select Period for Salary Sheet"), __("Download"));
        });
    }
};