from pymongo import MongoClient
from flask import current_app, g

def get_db():
    if 'db' not in g:
        timeout = current_app.config.get('MONGO_SERVER_SELECTION_TIMEOUT_MS', 30000)
        client = MongoClient(
            current_app.config['MONGO_URI'],
            serverSelectionTimeoutMS=timeout
        )
        g.db = client[current_app.config['MONGO_DBNAME']]
    return g.db