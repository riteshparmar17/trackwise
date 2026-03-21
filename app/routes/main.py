from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.drive_log import get_all_drives
from app.models.expense import get_all_expenses

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def dashboard():
    drives      = get_all_drives(user_id=current_user.id)
    expenses    = get_all_expenses(user_id=current_user.id)
    total_km    = sum(d['distance_km'] for d in drives if d.get('distance_km'))
    incomplete  = [d for d in drives if not d.get('end_km')]
    total_spent = sum(e['total_amount'] for e in expenses)
    return render_template('dashboard.html',
        total_km        = round(total_km, 1),
        total_drives    = len(drives),
        incomplete      = len(incomplete),
        total_spent     = round(total_spent, 2),
        recent_drives   = drives[:5],
        recent_expenses = expenses[:5]
    )