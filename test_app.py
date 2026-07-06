import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page_status(client):
    """Verifica que la ruta principal responda exitosamente"""
    respuesta = client.get('/')
    assert respuesta.status_code == 200

def test_home_page_content(client):
    """Verifica que el HTML renderizado contenga los elementos clave de la app"""
    respuesta = client.get('/')
    html_contenido = respuesta.data.decode('utf-8')
    
    # Validamos que las palabras clave de tu dashboard de psutil existan en el HTML
    assert "System Monitor" in html_contenido