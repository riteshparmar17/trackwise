from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.drive_log import (
    create_drive, get_all_drives, get_drive_by_id, update_drive,
    delete_drive, PURPOSES
)

drives_bp = Blueprint('drives', __name__)

@drives_bp.route('/')
def list_drives():
    start  = request.args.get('start_date', '')
    end    = request.args.get('end_date', '')
    drives = get_all_drives(start or None, end or None)
    total_km = sum(d['distance_km'] for d in drives if d.get('distance_km'))
    return render_template('drives/list.html',
        drives=drives, total_km=round(total_km, 1),
        start_date=start, end_date=end)

@drives_bp.route('/add', methods=['GET', 'POST'])
def add_drive():
    if request.method == 'POST':
        if not request.form.get('log_date') or not request.form.get('start_km'):
            flash('Date and Start KM are required.', 'danger')
            return render_template('drives/add.html',
                purposes=PURPOSES, form=request.form)
        end_km   = request.form.get('end_km')
        start_km = float(request.form['start_km'])
        if end_km and float(end_km) <= start_km:
            flash('End KM must be greater than Start KM.', 'danger')
            return render_template('drives/add.html',
                purposes=PURPOSES, form=request.form)
        create_drive(request.form)
        flash('Drive log saved! ✅', 'success')
        return redirect(url_for('drives.list_drives'))
    return render_template('drives/add.html', purposes=PURPOSES, form={})

@drives_bp.route('/edit/<drive_id>', methods=['GET', 'POST'])
def edit_drive(drive_id):
    drive = get_drive_by_id(drive_id)
    if not drive:
        flash('Drive log not found.', 'danger')
        return redirect(url_for('drives.list_drives'))
    if request.method == 'POST':
        end_km = request.form.get('end_km')
        if end_km and float(end_km) <= drive['start_km']:
            flash('End KM must be greater than Start KM.', 'danger')
            return render_template('drives/edit.html',
                drive=drive, purposes=PURPOSES)
        update_drive(drive_id, request.form)
        flash('Drive log updated! ✅', 'success')
        return redirect(url_for('drives.list_drives'))
    return render_template('drives/edit.html', drive=drive, purposes=PURPOSES)

@drives_bp.route('/delete/<drive_id>', methods=['POST'])
def delete_drive_entry(drive_id):
    delete_drive(drive_id)
    flash('Drive log deleted.', 'info')
    return redirect(url_for('drives.list_drives'))