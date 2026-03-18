from flask import Blueprint, render_template
from app.models.drive_log import get_all_drives
from app.models.expense import get_all_expenses

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def dashboard():
    drives   = get_all_drives()
    expenses = get_all_expenses()
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