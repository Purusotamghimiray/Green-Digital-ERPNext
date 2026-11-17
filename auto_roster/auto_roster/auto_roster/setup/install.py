import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def after_install():
    frappe.flags.in_install = True
    ensure_module_exists()
    configure_hr_settings()
    build_shift_blocks()
    build_doctypes()
    inject_employee_field()
    frappe.db.commit()

def ensure_module_exists():
    if not frappe.db.exists("Module Def", "Auto Roster"):
        frappe.get_doc({
            "doctype": "Module Def",
            "module_name": "Auto Roster",
            "app_name": "auto_roster"
        }).insert(ignore_permissions=True)

def configure_hr_settings():
    # Automatically enable multiple shifts in HR Settings if the field exists
    if frappe.db.exists("DocType", "HR Settings"):
        hr_settings = frappe.get_single("HR Settings")
        if hasattr(hr_settings, "allow_multiple_shifts") and not hr_settings.allow_multiple_shifts:
            hr_settings.allow_multiple_shifts = 1
            hr_settings.save(ignore_permissions=True)

def build_shift_blocks():
    shifts = [
        {"name": "Day Shift 12H", "start": "06:00:00", "end": "18:00:00", "overnight": 0},
        {"name": "Night Shift 12H", "start": "18:00:00", "end": "06:00:00", "overnight": 1}
    ]
    for s in shifts:
        if not frappe.db.exists("Shift Type", s["name"]):
            frappe.get_doc({
                "doctype": "Shift Type",
                "name": s["name"],
                "start_time": s["start"],
                "end_time": s["end"],
                "enable_auto_attendance": 1,
                "is_overnight_shift": s["overnight"],
                "begin_check_in_before_shift_start_time": 60,
                "allow_check_out_after_shift_end_time": 60
            }).insert(ignore_permissions=True)

def build_doctypes():
    day_options = "\n".join(str(i) for i in range(1, 32))

    if not frappe.db.exists("DocType", "Roster Cycle Shift"):
        frappe.get_doc({
            "doctype": "DocType",
            "name": "Roster Cycle Shift",
            "module": "Auto Roster",
            "custom": 1,
            "istable": 1,
            "fields": [
                {
                    "fieldname": "day_number",
                    "label": "Cycle Day",
                    "fieldtype": "Select",
                    "options": day_options,
                    "reqd": 1,
                    "default": "1",
                    "in_list_view": 1
                },
                {
                    "fieldname": "shift_type",
                    "label": "Shift Type",
                    "fieldtype": "Link",
                    "options": "Shift Type",
                    "in_list_view": 1
                }
            ]
        }).insert(ignore_permissions=True)
    else:
        dt = frappe.get_doc("DocType", "Roster Cycle Shift")
        for f in dt.fields:
            if f.fieldname == "day_number":
                f.fieldtype = "Select"
                f.options = day_options
                f.default = "1"
        dt.save(ignore_permissions=True)

    if not frappe.db.exists("DocType", "Rolling Roster Config"):
        frappe.get_doc({
            "doctype": "DocType",
            "name": "Rolling Roster Config",
            "module": "Auto Roster",
            "custom": 1,
            "is_submittable": 1,
            "fields": [
                {"fieldname": "employee", "label": "Employee", "fieldtype": "Link", "options": "Employee", "reqd": 1},
                {"fieldname": "cycle_start_date", "label": "Start Date", "fieldtype": "Date", "reqd": 1},
                {"fieldname": "cycle_length", "label": "Cycle Length (Days)", "fieldtype": "Int", "reqd": 1, "non_negative": 1},
                {"fieldname": "cycle_shifts", "label": "Shifts", "fieldtype": "Table", "options": "Roster Cycle Shift"}
            ],
            "permissions": [
                {
                    "role": "System Manager",
                    "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1
                },
                {
                    "role": "HR Manager",
                    "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1
                }
            ]
        }).insert(ignore_permissions=True)

def inject_employee_field():
    create_custom_fields({
        "Employee": [
            {
                "fieldname": "custom_rolling_roster",
                "label": "Active Roster Config",
                "fieldtype": "Link",
                "options": "Rolling Roster Config",
                "insert_after": "default_shift"
            }
        ]
    })