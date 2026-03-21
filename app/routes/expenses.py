import os
from datetime import datetime
from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, current_app)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models.expense import (
    create_expense, get_all_expenses, get_expense_by_id,
    update_expense, delete_expense, EXPENSE_TYPES
)

expenses_bp = Blueprint('expenses', __name__)

def save_receipt(file) -> str | None:
    if not file or file.filename == '':
        return None
    allowed = current_app.config['ALLOWED_EXTENSIONS']
    ext = file.filename.rsplit('.', 1)[-1].lower()
    if ext not in allowed:
        return None
    ts       = datetime.now().strftime('%Y%m%d_%H%M%S_')
    filename = ts + secure_filename(file.filename)
    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
    return filename

@expenses_bp.route('/')
@login_required
def list_expenses():
    start = request.args.get('start_date', '')
    end   = request.args.get('end_date', '')
    etype = request.args.get('expense_type', '')
    expenses  = get_all_expenses(user_id=current_user.id,
                                  start_date=start or None,
                                  end_date=end or None,
                                  expense_type=etype or None)
    total     = sum(e['total_amount'] for e in expenses)
    total_hst = sum(e['hst'] for e in expenses)
    return render_template('expenses/list.html',
        expenses=expenses, total=round(total, 2),
        total_hst=round(total_hst, 2),
        expense_types=EXPENSE_TYPES,
        start_date=start, end_date=end, selected_type=etype)

@expenses_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        for field in ['expense_date', 'expense_type', 'vendor', 'amount']:
            if not request.form.get(field):
                flash(f'{field.replace("_"," ").title()} is required.', 'danger')
                return render_template('expenses/add.html',
                    expense_types=EXPENSE_TYPES, form=request.form)
        receipt = save_receipt(request.files.get('receipt'))
        create_expense(request.form, current_user.id, receipt)
        flash('Expense saved! ✅', 'success')
        return redirect(url_for('expenses.list_expenses'))
    return render_template('expenses/add.html',
        expense_types=EXPENSE_TYPES, form={})

@expenses_bp.route('/edit/<expense_id>', methods=['GET', 'POST'])
@login_required
def edit_expense(expense_id):
    expense = get_expense_by_id(expense_id, current_user.id)
    if not expense:
        flash('Expense not found.', 'danger')
        return redirect(url_for('expenses.list_expenses'))
    if request.method == 'POST':
        for field in ['expense_date', 'expense_type', 'vendor', 'amount']:
            if not request.form.get(field):
                flash(f'{field.replace("_"," ").title()} is required.', 'danger')
                return render_template('expenses/edit.html',
                    expense=expense, expense_types=EXPENSE_TYPES)
        update_expense(expense_id, request.form)
        flash('Expense updated! ✅', 'success')
        return redirect(url_for('expenses.list_expenses'))
    return render_template('expenses/edit.html',
        expense=expense, expense_types=EXPENSE_TYPES)

@expenses_bp.route('/delete/<expense_id>', methods=['POST'])
@login_required
def delete_expense_entry(expense_id):
    delete_expense(expense_id, current_user.id)
    flash('Expense deleted.', 'info')
    return redirect(url_for('expenses.list_expenses'))