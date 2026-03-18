from datetime import datetime, timezone, date as date_type
from bson import ObjectId
from . import get_db

PURPOSES = ['Business', 'Personal', 'Medical', 'Volunteer', 'Other']

def col():
    return get_db().drive_logs

def create_drive(data: dict) -> str:
    doc = {
        'log_date':   data['log_date'],           # string 'YYYY-MM-DD'
        'start_km':   float(data['start_km']),
        'end_km':     float(data['end_km']) if data.get('end_km') else None,
        'purpose':    data.get('purpose', 'Business'),
        'notes':      data.get('notes', '').strip(),
        'created_at': datetime.now(timezone.utc),
        'updated_at': datetime.now(timezone.utc),
    }
    return str(col().insert_one(doc).inserted_id)

def get_all_drives(start_date: str | None = None, end_date: str | None = None) -> list:
    q: dict = {}
    if start_date:
        q['log_date'] = {'$gte': start_date}
    if end_date:
        q.setdefault('log_date', {})['$lte'] = end_date
    drives = list(col().find(q).sort('log_date', -1))
    for d in drives:
        d['_id'] = str(d['_id'])
        if d.get('end_km') is not None and d.get('start_km') is not None:
            d['distance_km'] = round(d['end_km'] - d['start_km'], 2)
        else:
            d['distance_km'] = None
    return drives

def get_drive_by_id(drive_id: str) -> dict | None:
    doc = col().find_one({'_id': ObjectId(drive_id)})
    if doc:
        doc['_id'] = str(doc['_id'])
        if doc.get('end_km') is not None:
            doc['distance_km'] = round(doc['end_km'] - doc['start_km'], 2)
        else:
            doc['distance_km'] = None
    return doc

def update_drive(drive_id: str, data: dict) -> None:
    updates: dict = {'updated_at': datetime.now(timezone.utc)}
    if data.get('end_km'):
        updates['end_km'] = float(data['end_km'])
    if data.get('purpose'):
        updates['purpose'] = data['purpose']
    if 'notes' in data:
        updates['notes'] = data['notes'].strip()
    col().update_one({'_id': ObjectId(drive_id)}, {'$set': updates})

def delete_drive(drive_id: str) -> None:
    col().delete_one({'_id': ObjectId(drive_id)})

def get_monthly_summary() -> list:
    pipeline = [
        {'$match': {'end_km': {'$ne': None}}},
        {'$addFields': {
            'year':  {'$substr': ['$log_date', 0, 4]},
            'month': {'$substr': ['$log_date', 5, 2]},
            'km':    {'$subtract': ['$end_km', '$start_km']}
        }},
        {'$group': {
            '_id': {'year': '$year', 'month': '$month'},
            'total_km': {'$sum': '$km'},
            'trips':    {'$sum': 1}
        }},
        {'$sort': {'_id.year': 1, '_id.month': 1}}
    ]
    return list(get_db().drive_logs.aggregate(pipeline))