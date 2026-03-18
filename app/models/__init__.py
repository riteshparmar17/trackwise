from pymongo import MongoClient
from flask import current_app, g

def get_db():
    """Return MongoDB database for this request context."""
    if 'db' not in g:
        client = MongoClient(current_app.config['MONGO_URI'])
        g.db = client[current_app.config['MONGO_DBNAME']]
    return g.db