import frappe
from frappe.utils import getdate, add_days, date_diff
from hrms.hr.doctype.shift_assignment.shift_assignment import OverlappingShiftError

def plot_rosters():
    configs = frappe.get_all("Rolling Roster Config", filters={"docstatus": 1})
    today = getdate()
    
    for record in configs:
        config = frappe.get_doc("Rolling Roster Config", record.name)
        
        if not config.cycle_length or config.cycle_length <= 0:
            continue
            
        # Plot shifts 30 days ahead
        for i in range(30):
            target_date = add_days(today, i)
            days_elapsed = date_diff(target_date, config.cycle_start_date)
            if days_elapsed < 0: 
                continue
            
            cycle_day = (days_elapsed % config.cycle_length) + 1
            
            shifts_for_day = [
                r.shift_type for r in config.cycle_shifts 
                if r.day_number and int(r.day_number) == cycle_day and r.shift_type
            ]
            
            for shift in shifts_for_day:
                exists = frappe.db.exists("Shift Assignment", {
                    "employee": config.employee,
                    "start_date": target_date,
                    "shift_type": shift,
                    "docstatus": 1
                })
                
                if not exists:
                    try:
                        assignment = frappe.get_doc({
                            "doctype": "Shift Assignment",
                            "employee": config.employee,
                            "start_date": target_date,
                            "end_date": target_date,
                            "shift_type": shift,
                            "status": "Active"
                        })
                        assignment.insert(ignore_permissions=True)
                        assignment.submit()
                    except OverlappingShiftError:
                        # Skip dates that already have a conflicting active shift
                        frappe.clear_last_message()
                        continue
                
    frappe.db.commit()