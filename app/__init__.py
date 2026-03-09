from flask import Flask
from .config import Config
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    @app.route('/')
    def health():
        return '<h2>TrackWise is running! ✅</h2>'    
        
    return app