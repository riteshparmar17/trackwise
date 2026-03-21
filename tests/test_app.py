import pytest
from unittest.mock import patch
from app import create_app
from app.config import TestConfig

@pytest.fixture
def client():
    with patch('app.models.user.ensure_indexes'):
        app = create_app(TestConfig)
    with app.test_client() as c:
        yield c

def test_dashboard_redirects_to_login(client):
    res = client.get('/')
    assert res.status_code == 302
    assert '/login' in res.headers['Location']

def test_login_page_loads(client):
    res = client.get('/login')
    assert res.status_code == 200
    assert b'Login' in res.data

def test_register_page_loads(client):
    res = client.get('/register')
    assert res.status_code == 200
    assert b'Create' in res.data

def test_add_drive_redirects_to_login(client):
    res = client.get('/drives/add')
    assert res.status_code == 302
    assert '/login' in res.headers['Location']

def test_add_expense_redirects_to_login(client):
    res = client.get('/expenses/add')
    assert res.status_code == 302
    assert '/login' in res.headers['Location']