import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page_status(client):
    """Verifies if the response is successful"""
    resp = client.get('/')
    assert resp.status_code == 200

def test_home_page_content(client):
    """Verifying if html is working"""
    resp = client.get('/')
    html_cont = resp.data.decode('utf-8')
    
    # Validating the dashboard
    assert "System Monitor" in html_cont