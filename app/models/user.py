from datetime import datetime, timezone
from bson import ObjectId
from flask_login import UserMixin
from . import get_db
import bcrypt

class User(UserMixin):
    def __init__(self, doc: dict):
        self.id         = str(doc['_id'])
        self.email      = doc['email']
        self.name       = doc['name']
        self.password   = doc['password']
        self.created_at = doc.get('created_at')

    def get_id(self) -> str:
        return self.id

def col():
    return get_db().users

def create_user(name: str, email: str, password: str) -> str:
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    doc = {
        'name':       name.strip(),
        'email':      email.lower().strip(),
        'password':   hashed,
        'created_at': datetime.now(timezone.utc),
    }
    return str(col().insert_one(doc).inserted_id)

def get_user_by_email(email: str) -> User | None:
    doc = col().find_one({'email': email.lower().strip()})
    return User(doc) if doc else None

def get_user_by_id(user_id: str) -> User | None:
    doc = col().find_one({'_id': ObjectId(user_id)})
    return User(doc) if doc else None

def email_exists(email: str) -> bool:
    return col().find_one({'email': email.lower().strip()}) is not None

def check_password(user: User, password: str) -> bool:
    return bcrypt.checkpw(password.encode(), user.password)

def update_password(user_id: str, new_password: str) -> None:
    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
    col().update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'password': hashed,
                  'updated_at': datetime.now(timezone.utc)}}
    )

def ensure_indexes() -> None:
    col().create_index('email', unique=True)