from datetime import datetime, timezone
from bson import ObjectId
from . import get_db

EXPENSE_TYPES = [
    'Gas', 'Groceries', 'Water', 'Electricity',
    'Internet', 'Phone', 'Vehicle Maintenance',
    'Office Supplies', 'Meal / Dining', 'Parking',
    'Software / Subscriptions', 'Other'
]

def col():
    return get_db().expenses

def create_expense(data: dict, user_id: str,
                   receipt_filename: str | None = None) -> str:
    total  = round(float(data['amount']), 2)
    hst    = round(float(data.get('hst', 0) or 0), 2)
    doc = {
        'user_id':      user_id,
        'expense_date': data['expense_date'],
        'expense_type': data['expense_type'],
        'vendor':       data['vendor'].strip(),
        'amount':       round(total - hst, 2),
        'hst':          hst,
        'total_amount': total,
        'description':  data.get('description', '').strip(),
        'receipt_file': receipt_filename,
        'created_at':   datetime.now(timezone.utc),
        'updated_at':   datetime.now(timezone.utc),
    }
    return str(col().insert_one(doc).inserted_id)

def get_all_expenses(
    user_id: str,
    start_date: str | None = None,
    end_date: str | None = None,
    expense_type: str | None = None
) -> list:
    q: dict = {'user_id': user_id}
    if start_date: q['expense_date'] = {'$gte': start_date}
    if end_date:   q.setdefault('expense_date', {})['$lte'] = end_date
    if expense_type: q['expense_type'] = expense_type
    docs = list(col().find(q).sort('expense_date', -1))
    for e in docs:
        e['_id'] = str(e['_id'])
    return docs

def get_expense_by_id(expense_id: str, user_id: str) -> dict | None:
    doc = col().find_one({'_id': ObjectId(expense_id), 'user_id': user_id})
    if doc:
        doc['_id'] = str(doc['_id'])
    return doc

def update_expense(expense_id: str, data: dict,
                   receipt_filename: str | None = None) -> None:
    total  = round(float(data['amount']), 2)
    hst    = round(float(data.get('hst', 0) or 0), 2)
    updates: dict = {
        'expense_date': data['expense_date'],
        'expense_type': data['expense_type'],
        'vendor':       data['vendor'].strip(),
        'amount':       round(total - hst, 2),
        'hst':          hst,
        'total_amount': total,
        'description':  data.get('description', '').strip(),
        'updated_at':   datetime.now(timezone.utc),
    }
    if receipt_filename is not None:
        updates['receipt_file'] = receipt_filename
    col().update_one(
        {'_id': ObjectId(expense_id)},
        {'$set': updates}
    )

def delete_expense(expense_id: str, user_id: str) -> None:
    col().delete_one({'_id': ObjectId(expense_id), 'user_id': user_id})

def get_expense_by_type(
    user_id: str,
    start_date: str | None = None,
    end_date: str | None = None
) -> list:
    q: dict = {'user_id': user_id}
    if start_date: q['expense_date'] = {'$gte': start_date}
    if end_date:   q.setdefault('expense_date', {})['$lte'] = end_date
    pipeline = [
        {'$match': q},
        {'$group': {
            '_id':       '$expense_type',
            'total':     {'$sum': '$total_amount'},
            'total_hst': {'$sum': '$hst'},
            'count':     {'$sum': 1}
        }},
        {'$sort': {'total': -1}}
    ]
    return list(get_db().expenses.aggregate(pipeline))