from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, jsonify)
from flask_login import login_required, current_user
from app.models.vendor import (
    get_vendors, get_vendors_with_ids, add_vendor, delete_vendor
)

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings')
@login_required
def index():
    vendors = get_vendors_with_ids(current_user.id)
    return render_template('settings.html', vendors=vendors)

@settings_bp.route('/settings/vendors/add', methods=['POST'])
@login_required
def add_vendor_manual():
    name = request.form.get('name', '').strip()
    if name:
        add_vendor(current_user.id, name)
        flash(f'"{name}" added to your vendor list.', 'success')
    return redirect(url_for('settings.index'))

@settings_bp.route('/settings/vendors/delete/<vendor_id>', methods=['POST'])
@login_required
def delete_vendor_entry(vendor_id):
    delete_vendor(current_user.id, vendor_id)
    flash('Vendor removed.', 'info')
    return redirect(url_for('settings.index'))

@settings_bp.route('/api/vendors')
@login_required
def api_vendors():
    return jsonify(get_vendors(current_user.id))