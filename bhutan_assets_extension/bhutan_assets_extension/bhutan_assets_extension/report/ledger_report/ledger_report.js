frappe.query_reports["Ledger Report"] = {
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
            "fieldname": "account",
            "label": __("GL Account"),
            "fieldtype": "Link",
            "options": "Account",
            "get_query": function() {
                let company = frappe.query_report.get_filter_value('company');
                return { filters: { "company": company, "is_group": 0 } };
            },
            "reqd": 1
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.month_start(),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        {
            "fieldname": "cost_center",
            "label": __("Profit Center"),
            "fieldtype": "Link",
            "options": "Cost Center"
        },
        {
            "fieldname": "usd_exchange_rate",
            "label": __("USD Rate Override (Optional)"),
            "fieldtype": "Float",
            "description": __("Leave 0 to use native USD amounts or historical Exchange Rates on Posting Date")
        }
    ],
    "onload": function(report) {
        report.page.add_inner_button(__("Download Exact Ledger Excel"), function() {
            let filters = report.get_values();
            if (!filters.company || !filters.account) {
                frappe.msgprint(__("Please select Company and GL Account first."));
                return;
            }
            let params = new URLSearchParams({
                company: filters.company,
                account: filters.account,
                from_date: filters.from_date || "",
                to_date: filters.to_date || "",
                cost_center: filters.cost_center || "",
                usd_exchange_rate: filters.usd_exchange_rate || 0
            });
            window.open(`/api/method/bhutan_assets_extension.api.download_ledger_report?${params.toString()}`);
        });
    }
};