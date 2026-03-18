from flask import Blueprint, render_template
from app.models.drive_log import get_all_drives

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def dashboard():
    drives = get_all_drives()
    total_km   = sum(d['distance_km'] for d in drives if d.get('distance_km'))
    incomplete = [d for d in drives if not d.get('end_km')]
    return render_template('dashboard.html',
        total_km     = round(total_km, 1),
        total_drives = len(drives),
        incomplete   = len(incomplete),
        total_spent  = 0.00,
        recent_drives   = drives[:5],
        recent_expenses = []
    )