import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Verifica que la ruta principal cargue correctamente"""
    respuesta = client.get('/')
    assert respuesta.status_code == 200