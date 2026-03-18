import pytest
from unittest.mock import patch
from app import create_app
from app.config import TestConfig

@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.test_client() as c:
        yield c

def test_dashboard_loads(client):
    # Mock both model calls so no real DB needed
    with patch('app.routes.main.get_all_drives', return_value=[]), \
         patch('app.routes.main.get_all_expenses', return_value=[]):
        res = client.get('/')
    assert res.status_code == 200

def test_add_drive_get(client):
    res = client.get('/drives/add')
    assert res.status_code == 200
    assert b'Start KM' in res.data

def test_add_expense_get(client):
    res = client.get('/expenses/add')
    assert res.status_code == 200
    assert b'Vendor' in res.data

def test_drive_missing_fields(client):
    res = client.post('/drives/add', data={})
    assert res.status_code == 200