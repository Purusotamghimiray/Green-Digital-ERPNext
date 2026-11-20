import frappe
from frappe.utils import today
import io
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

@frappe.whitelist()
def download_consolidated_reports(company, report_date=None, from_date=None):
    if not report_date: report_date = today()
    if not from_date: from_date = str(report_date)[:4] + "-01-01"

    # Fetch data from all three asset reports
    from bhutan_assets_extension.bhutan_assets_extension.report.asset_report_as_per_standard.asset_report_as_per_standard import get_data as get_std_data
    from bhutan_assets_extension.bhutan_assets_extension.report.asset_report_as_per_tax.asset_report_as_per_tax import get_data as get_tax_data
    from bhutan_assets_extension.bhutan_assets_extension.report.asset_schedule.asset_schedule import get_data as get_sch_data
    
    filters = {"company": company, "report_date": report_date, "from_date": from_date, "to_date": report_date}
    std_data = get_std_data(filters)
    tax_data = get_tax_data(filters)
    sch_data = get_sch_data(filters)

    # Initialize Workbook and Styling
    wb = openpyxl.Workbook()
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="364152", end_color="364152", fill_type="solid")
    alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    thin_border = Border(
        left=Side(style='thin'), right=Side(style='thin'), 
        top=Side(style='thin'), bottom=Side(style='thin')
    )

    def write_sheet(ws, headers, data, key_map):
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = alignment
            cell.border = thin_border
            ws.column_dimensions[get_column_letter(col_num)].width = 18

        for row_num, row_data in enumerate(data, 2):
            for col_num, key in enumerate(key_map, 1):
                val = row_data.get(key, "")
                if key in ["purchase_date", "end_of_life_date"] and val:
                    val = str(val) 
                ws.cell(row=row_num, column=col_num, value=val)

    # ---------------------------------------------------------
    # SHEET 1: Asset Report as per Standard (18 Columns)
    # ---------------------------------------------------------
    ws_std = wb.active
    ws_std.title = "Asset Report as per Standard"
    std_headers = [
        "Asset Code", "Asset Name", "Asset Category (ShortForm)", "Asset Category", 
        "Asset Head", "Location", "Cost Center", "Custodian / Assigned To", 
        "Acquisition Date", "Useful Life (Years)", "End of Life Date", 
        "Acquisition Cost", "Additional value during the Year", "Termination", 
        "Depreciation for the Year", "Depreciation for Termination", 
        "Accumulated Depreciation till date", "Net Value (NBV)"
    ]
    std_keys = [
        "asset_code", "asset_name", "asset_category_shortform", "asset_category", 
        "asset_head", "location", "cost_center", "custodian", 
        "purchase_date", "useful_life", "end_of_life_date", 
        "net_purchase_amount", "additional_value", "termination", 
        "dep_for_year", "dep_for_termination", 
        "accumulated_depreciation", "net_value"
    ]
    write_sheet(ws_std, std_headers, std_data, std_keys)

    # ---------------------------------------------------------
    # SHEET 2: Asset Report as per Tax (18 Columns)
    # ---------------------------------------------------------
    ws_tax = wb.create_sheet("Asset Report as per Tax")
    tax_headers = [
        "Asset Code / ID", "Asset Name", "Asset Category (ShortForm)", "Asset Category", 
        "Asset Head", "Location", "Cost Center", "Custodian / Assigned To", 
        "Acquisition Date", "Useful Life (Years)", "End of Life Date", 
        "Acquisition Cost", "Additional value during the Year", "Termination", 
        "Depreciation for the Year", "Depreciation for Termination", 
        "Accumulated Depreciation till date", "Net Value (NBV)"
    ]
    write_sheet(ws_tax, tax_headers, tax_data, std_keys)

    # ---------------------------------------------------------
    # SHEET 3: Asset Schedule
    # ---------------------------------------------------------
    ws_sch = wb.create_sheet("Asset Schedule")
    sch_headers = [
        "Asset Head", "Gross Block - Opening", "Acquisition", "Disposal/Adjustment", 
        "Gross Block", "Accum Dep - Opening", "Depreciation", "Disposal/Adjustment", 
        "Accum Dep", "Book Value"
    ]
    sch_keys = [
        "asset_head", "gross_opening", "gross_addition", "gross_disposal", "gross_closing",
        "dep_opening", "dep_addition", "dep_disposal", "dep_closing", "book_value"
    ]
    write_sheet(ws_sch, sch_headers, sch_data, sch_keys)

    # ---------------------------------------------------------
    # Return File to Browser
    # ---------------------------------------------------------
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    frappe.response['filename'] = f"Consolidated_Asset_Reports_{today()}.xlsx"
    frappe.response['filecontent'] = output.getvalue()
    frappe.response['type'] = 'download'


@frappe.whitelist()
def download_ledger_report(company, account, from_date=None, to_date=None, cost_center=None, usd_exchange_rate=0):
    from bhutan_assets_extension.bhutan_assets_extension.report.ledger_report.ledger_report import get_data

    filters = {
        "company": company,
        "account": account,
        "from_date": from_date or today(),
        "to_date": to_date or today(),
        "cost_center": cost_center or None,
        "usd_exchange_rate": float(usd_exchange_rate or 0)
    }
    rows, acc_info = get_data(filters)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Ledger Report"

    # Exact styles matching Reporting Format (1).xlsx
    header_fill = PatternFill(start_color="C0C0C0", end_color="C0C0C0", fill_type="solid")
    total_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
    green_font = Font(color="00B050")
    default_font = Font(color="000000")
    thin_border = Border(
        left=Side(style='thin', color="D9D9D9"), right=Side(style='thin', color="D9D9D9"),
        top=Side(style='thin', color="D9D9D9"), bottom=Side(style='thin', color="D9D9D9")
    )

    # Row 1: GL Account Header
    acc_num = acc_info.get("account_number") or account
    acc_name = acc_info.get("account_name") or ""
    ws.cell(row=1, column=1, value="GL Account")
    ws.cell(row=1, column=2, value=int(acc_num) if str(acc_num).isdigit() else acc_num)
    ws.cell(row=1, column=3, value=acc_name)

    # Row 2: 16 Exact Column Headers
    headers = [
        "Cleared/open items symbol", "Assignment", "Document Number", "Business Area",
        "Document Type", "Posting Date", "Document Date", "Posting Key",
        "Profit Center", "Amount in loc.curr.2", "Local currency 2",
        "Amount in local currency", "Local Currency", "Tax code",
        "Clearing Document", "Text"
    ]
    col_widths = [18, 18, 18, 14, 14, 14, 14, 12, 14, 20, 16, 22, 15, 11, 18, 38]

    for c_idx, h_text in enumerate(headers, 1):
        cell = ws.cell(row=2, column=c_idx, value=h_text)
        cell.fill = header_fill
        cell.border = thin_border
        cell.font = green_font if c_idx in (10, 11, 12, 13) else default_font
        ws.column_dimensions[get_column_letter(c_idx)].width = col_widths[c_idx - 1]

    # Rows 3+: Ledger Entries
    keys = [
        "cleared_status", "assignment", "document_number", "business_area",
        "document_type", "posting_date", "document_date", "posting_key",
        "profit_center", "amount_loc_curr_2", "local_currency_2",
        "amount_local_curr", "local_currency", "tax_code",
        "clearing_document", "text"
    ]

    start_row = 3
    for idx, r_data in enumerate(rows):
        r_num = start_row + idx
        for c_idx, key in enumerate(keys, 1):
            val = r_data.get(key, "")
            cell = ws.cell(row=r_num, column=c_idx, value=val)
            if c_idx in (6, 7) and val:
                cell.number_format = "mm-dd-yy"
            elif c_idx in (10, 12):
                cell.number_format = "#,##0.00"
            if c_idx in (10, 11, 12, 13):
                cell.font = green_font

    # Final Row: Yellow Summary Row with Dynamic Excel Formulas
    end_data_row = max(start_row, start_row + len(rows) - 1)
    total_row = start_row + len(rows)

    for c_idx in range(1, 17):
        cell = ws.cell(row=total_row, column=c_idx)
        cell.fill = total_fill
        if c_idx == 10:
            cell.value = f"=SUM(J{start_row}:J{end_data_row})" if rows else 0
            cell.number_format = "#,##0.00"
            cell.font = green_font
        elif c_idx == 11:
            cell.value = "USD"
            cell.font = green_font
        elif c_idx == 12:
            cell.value = f"=SUM(L{start_row}:L{end_data_row})" if rows else 0
            cell.number_format = "#,##0.00"
            cell.font = green_font
        elif c_idx == 13:
            cell.value = "BTN"
            cell.font = green_font
        elif c_idx in (6, 7):
            cell.value = None
            cell.number_format = "mm-dd-yy"
        else:
            cell.value = ""

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    frappe.response['filename'] = f"Ledger_Report_{acc_num}_{today()}.xlsx"
    frappe.response['filecontent'] = output.getvalue()
    frappe.response['type'] = 'download'