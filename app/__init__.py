from flask import Flask
from .config import Config
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
    from .routes.main import main_bp
    from .routes.drives import drives_bp
    from .routes.expenses import expenses_bp
    from .routes.reports  import reports_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(drives_bp, url_prefix='/drives')
    app.register_blueprint(expenses_bp, url_prefix='/expenses')
    app.register_blueprint(reports_bp,  url_prefix='/reports')        

    return app