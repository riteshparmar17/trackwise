from flask import Blueprint, render_template, request, send_file
from flask_login import login_required, current_user
from app.models.drive_log import get_all_drives, get_monthly_summary
from app.models.expense import get_all_expenses, get_expense_by_type
from app.utils.export import export_to_excel, export_to_pdf

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/')
@login_required
def index():
    start = request.args.get('start_date', '')
    end   = request.args.get('end_date', '')
    drives   = get_all_drives(user_id=current_user.id,
                               start_date=start or None, end_date=end or None)
    expenses = get_all_expenses(user_id=current_user.id,
                                 start_date=start or None, end_date=end or None)
    total_km    = sum(d['distance_km'] for d in drives if d.get('distance_km'))
    total_spent = sum(e['total_amount'] for e in expenses)
    total_hst   = sum(e['hst'] for e in expenses)
    return render_template('reports/index.html',
        monthly_km  = get_monthly_summary(user_id=current_user.id),
        by_type     = get_expense_by_type(
                          user_id=current_user.id,
                          start_date=start or None,
                          end_date=end or None),
        total_km    = round(total_km, 1),
        total_spent = round(total_spent, 2),
        total_hst   = round(total_hst, 2),
        start_date  = start,
        end_date    = end
    )

@reports_bp.route('/export/excel')
@login_required
def export_excel():
    start = request.args.get('start_date')
    end   = request.args.get('end_date')
    output = export_to_excel(
        get_all_drives(user_id=current_user.id,
                       start_date=start, end_date=end),
        get_all_expenses(user_id=current_user.id,
                         start_date=start, end_date=end)
    )
    return send_file(output,
        download_name='trackwise-report.xlsx',
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@reports_bp.route('/export/pdf')
@login_required
def export_pdf():
    start = request.args.get('start_date')
    end   = request.args.get('end_date')
    buf   = export_to_pdf(
        drives    = get_all_drives(user_id=current_user.id,
                                   start_date=start, end_date=end),
        expenses  = get_all_expenses(user_id=current_user.id,
                                     start_date=start, end_date=end),
        user_name = current_user.name
    )
    return send_file(buf,
        download_name='trackwise-report.pdf',
        as_attachment=True,
        mimetype='application/pdf')