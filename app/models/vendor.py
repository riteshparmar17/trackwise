from datetime import datetime, timezone
from bson import ObjectId
from . import get_db

def col():
    return get_db().vendors

def get_vendors(user_id: str) -> list:
    docs = list(col().find(
        {'user_id': user_id}, {'name': 1}
    ).sort('name', 1))
    return [d['name'] for d in docs]

def add_vendor(user_id: str, name: str) -> None:
    name = name.strip()
    if not name:
        return
    col().update_one(
        {'user_id': user_id, 'name_lower': name.lower()},
        {'$setOnInsert': {
            'user_id':    user_id,
            'name':       name,
            'name_lower': name.lower(),
            'created_at': datetime.now(timezone.utc)
        }},
        upsert=True
    )

def delete_vendor(user_id: str, vendor_id: str) -> None:
    col().delete_one({'_id': ObjectId(vendor_id), 'user_id': user_id})

def get_vendors_with_ids(user_id: str) -> list:
    docs = list(col().find({'user_id': user_id}).sort('name', 1))
    for d in docs:
        d['_id'] = str(d['_id'])
    return docs

def ensure_indexes() -> None:
    col().create_index(
        [('user_id', 1), ('name_lower', 1)], unique=True
    )