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

def create_expense(data: dict, receipt_filename: str | None = None) -> str:
    total  = round(float(data['amount']), 2)          # amount entered = total incl HST
    hst    = round(float(data.get('hst', 0) or 0), 2) # auto-calc or user-edited
    pretax = round(total - hst, 2)                    # pre-tax portion
    doc = {
        'expense_date': data['expense_date'],
        'expense_type': data['expense_type'],
        'vendor':       data['vendor'].strip(),
        'amount':       pretax,        # stored as pre-tax
        'hst':          hst,
        'total_amount': total,         # what was on the receipt
        'description':  data.get('description', '').strip(),
        'receipt_file': receipt_filename,
        'created_at':   datetime.now(timezone.utc),
        'updated_at':   datetime.now(timezone.utc),
    }
    return str(col().insert_one(doc).inserted_id)
def get_all_expenses(
    start_date: str | None = None,
    end_date: str | None = None,
    expense_type: str | None = None
) -> list:
    q: dict = {}
    if start_date:
        q['expense_date'] = {'$gte': start_date}
    if end_date:
        q.setdefault('expense_date', {})['$lte'] = end_date
    if expense_type:
        q['expense_type'] = expense_type
    docs = list(col().find(q).sort('expense_date', -1))
    for e in docs:
        e['_id'] = str(e['_id'])
    return docs

def delete_expense(expense_id: str) -> None:
    col().delete_one({'_id': ObjectId(expense_id)})


def get_expense_by_id(expense_id: str) -> dict | None:
    doc = col().find_one({'_id': ObjectId(expense_id)})
    if doc:
        doc['_id'] = str(doc['_id'])
    return doc

def update_expense(expense_id: str, data: dict) -> None:
    total  = round(float(data['amount']), 2)
    hst    = round(float(data.get('hst', 0) or 0), 2)
    pretax = round(total - hst, 2)
    updates = {
        'expense_date': data['expense_date'],
        'expense_type': data['expense_type'],
        'vendor':       data['vendor'].strip(),
        'amount':       pretax,
        'hst':          hst,
        'total_amount': total,
        'description':  data.get('description', '').strip(),
        'updated_at':   datetime.now(timezone.utc),
    }
    col().update_one({'_id': ObjectId(expense_id)}, {'$set': updates})

def get_expense_by_type(
    start_date: str | None = None,
    end_date: str | None = None
) -> list:
    q: dict = {}
    if start_date:
        q['expense_date'] = {'$gte': start_date}
    if end_date:
        q.setdefault('expense_date', {})['$lte'] = end_date
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