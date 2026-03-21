import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY    = os.environ.get('SECRET_KEY', 'tracking-trackwise-app-dev-secret-key')
    MONGO_URI     = os.environ.get('MONGO_URI', 'mongodb://localhost/trackwise')
    MONGO_DBNAME  = os.environ.get('MONGO_DBNAME', 'trackwise')
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_UPLOAD_MB', 5)) * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'webp'}
    MONGO_SERVER_SELECTION_TIMEOUT_MS = 30000

    # Flask-Mail
    MAIL_SERVER         = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT           = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS        = True
    MAIL_USERNAME       = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD       = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')

class TestConfig(Config):
    TESTING      = True
    MONGO_URI    = 'mongodb://localhost/trackwise_test'
    MONGO_DBNAME = 'trackwise_test'
    MONGO_SERVER_SELECTION_TIMEOUT_MS = 1000
    MAIL_SUPPRESS_SEND = True