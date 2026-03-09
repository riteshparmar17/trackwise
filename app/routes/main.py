from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def dashboard():
    return render_template('dashboard.html',
        total_km=0,
        total_drives=0,
        incomplete=0,
        total_spent=0.00,
        recent_drives=[],
        recent_expenses=[]
    )