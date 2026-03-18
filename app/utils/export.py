import io
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

def export_to_excel(drives: list, expenses: list) -> io.BytesIO:
    wb = openpyxl.Workbook()

    # Drive Logs sheet
    ws = wb.active
    ws.title = 'Drive Logs'
    _headers(ws, ['Date','Start KM','End KM','Distance (km)','Purpose','Notes'], '2563EB')
    for d in drives:
        ws.append([
            d.get('log_date',''),
            d.get('start_km',''),
            d.get('end_km', '—'),
            d.get('distance_km', 'Incomplete'),
            d.get('purpose',''),
            d.get('notes','')
        ])
    _auto_width(ws)

    # Expenses sheet
    ws2 = wb.create_sheet('Expenses')
    _headers(ws2, ['Date','Type','Vendor','Amount','HST','Total','Receipt'], '16A34A')
    for e in expenses:
        ws2.append([
            e.get('expense_date',''),
            e.get('expense_type',''),
            e.get('vendor',''),
            float(e.get('amount', 0)),
            float(e.get('hst', 0)),
            float(e.get('total_amount', 0)),
            'Yes' if e.get('receipt_file') else ''
        ])
    _auto_width(ws2)

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf

def _headers(ws, cols: list, color: str) -> None:
    fill = PatternFill('solid', fgColor=color)
    bold = Font(bold=True, color='FFFFFF')
    for i, h in enumerate(cols, 1):
        c = ws.cell(row=1, column=i, value=h)
        c.font, c.fill = bold, fill
        c.alignment = Alignment(horizontal='center')

def _auto_width(ws) -> None:
    for col in ws.columns:
        w = max(len(str(c.value or '')) for c in col)
        ws.column_dimensions[col[0].column_letter].width = min(w + 4, 40)