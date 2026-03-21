from flask import Flask, render_template
from flask_login import LoginManager
from flask_mail import Mail
from .config import Config
import os

login_manager = LoginManager()
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Init Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    # Init Flask-Mail
    mail.init_app(app)

    # User loader
    from .models.user import get_user_by_id, ensure_indexes

    @login_manager.user_loader
    def load_user(user_id):
        return get_user_by_id(user_id)

    # Register blueprints
    from .routes.auth     import auth_bp
    from .routes.main     import main_bp
    from .routes.drives   import drives_bp
    from .routes.expenses import expenses_bp
    from .routes.reports  import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(drives_bp,   url_prefix='/drives')
    app.register_blueprint(expenses_bp, url_prefix='/expenses')
    app.register_blueprint(reports_bp,  url_prefix='/reports')

    # Error pages
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    with app.app_context():
        ensure_indexes()

    return app