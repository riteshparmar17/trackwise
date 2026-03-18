import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY    = os.environ.get('SECRET_KEY', 'tracking-trackwise-app-dev-secret-key')
    MONGO_DBNAME = os.environ.get('MONGO_DBNAME', 'trackwise')
    MONGO_URI     = os.environ.get('MONGO_URI', 'mongodb://localhost/trackwise')
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_UPLOAD_MB', 5)) * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'webp'}

class TestConfig(Config):
    TESTING   = True
    MONGO_URI = 'mongodb://localhost/trackwise_test'