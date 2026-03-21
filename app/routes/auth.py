from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash)
from flask_login import login_user, logout_user, login_required
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from app.models.user import (
    create_user, get_user_by_email,
    email_exists, check_password, update_password
)

auth_bp = Blueprint('auth', __name__)

def _ts():
    from flask import current_app
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

# ── Register ──────────────────────────────────────────────────────────────────
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm', '')
        if not all([name, email, password, confirm]):
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html', form=request.form)
        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html', form=request.form)
        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
            return render_template('auth/register.html', form=request.form)
        if email_exists(email):
            flash('An account with that email already exists.', 'danger')
            return render_template('auth/register.html', form=request.form)
        create_user(name, email, password)
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form={})

# ── Login ─────────────────────────────────────────────────────────────────────
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user     = get_user_by_email(email)
        if not user or not check_password(user, password):
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html', form=request.form)
        login_user(user, remember=request.form.get('remember') == 'on')
        next_page = request.args.get('next')
        return redirect(next_page or url_for('main.dashboard'))
    return render_template('auth/login.html', form={})

# ── Logout ────────────────────────────────────────────────────────────────────
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

# ── Forgot Password ───────────────────────────────────────────────────────────
@auth_bp.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        user  = get_user_by_email(email)
        if user:
            _send_reset_email(user)
        flash('If that email exists, a reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot.html')

# ── Reset Password ────────────────────────────────────────────────────────────
@auth_bp.route('/reset/<token>', methods=['GET', 'POST'])
def reset(token):
    try:
        email = _ts().loads(token, salt='pw-reset', max_age=3600)
    except (SignatureExpired, BadSignature):
        flash('Reset link is invalid or expired (1hr limit).', 'danger')
        return redirect(url_for('auth.forgot'))
    user = get_user_by_email(email)
    if not user:
        flash('Account not found.', 'danger')
        return redirect(url_for('auth.forgot'))
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm', '')
        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
            return render_template('auth/reset.html', token=token)
        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/reset.html', token=token)
        update_password(user.id, password)
        flash('Password updated! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset.html', token=token)

def _send_reset_email(user):
    from flask import current_app
    from app import mail
    token = _ts().dumps(user.email, salt='pw-reset')
    link  = url_for('auth.reset', token=token, _external=True)
    msg   = Message('TrackWise — Reset Your Password',
                    recipients=[user.email])
    msg.body = (
        f"Hi {user.name},\n\n"
        f"Click the link below to reset your password.\n"
        f"This link expires in 1 hour.\n\n"
        f"{link}\n\n"
        f"If you did not request this, ignore this email.\n\n"
        f"— TrackWise"
    )
    mail.send(msg)