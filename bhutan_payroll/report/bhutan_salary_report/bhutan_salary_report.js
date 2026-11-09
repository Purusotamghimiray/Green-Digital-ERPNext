frappe.query_reports["Bhutan Salary Report"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company")
        },
        {
            "fieldname": "month",
            "label": __("Month"),
            "fieldtype": "Select",
            "options": Array.from({length: 12}, (_, i) => (i + 1).toString()).join("\n"),
            "default": (new Date().getMonth() + 1).toString()
        },
        {
            "fieldname": "year",
            "label": __("Year"),
            "fieldtype": "Select",
            "options": (() => {
                const cur = new Date().getFullYear();
                return Array.from({length: 8}, (_, i) => (cur - 2 + i).toString()).join("\n");
            })(),
            "default": new Date().getFullYear().toString()
        }
    ],
    onload: function(report) {
        const trigger_custom_export = function() {
            const filters = report.get_values();
            const curDate = new Date();
            const queryParams = new URLSearchParams({
                company: filters.company || "",
                month: filters.month || (curDate.getMonth() + 1).toString(),
                year: filters.year || curDate.getFullYear().toString()
            });

            const download_url = frappe.urllib.get_full_url(
                "/api/method/bhutan_payroll.bhutan_payroll.report.bhutan_salary_report.bhutan_salary_report.export_custom_excel?" +
                queryParams.toString()
            );
            window.location.href = download_url;
        };

        // Override standard Export handler
        report.export_report = function() {
            trigger_custom_export();
        };

        // Primary toolbar export button
        report.page.set_primary_action(__("Download GDL Salary Sheet"), function() {
            trigger_custom_export();
        });
    }
};