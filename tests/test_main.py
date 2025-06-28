import pytest
from fastapi.testclient import TestClient
import tempfile
import os
from pathlib import Path

# Import the app
import sys
sys.path.append(str(Path(__file__).parent.parent))

from app import app
from app.core.dependencies import get_url_service

@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)

@pytest.fixture
def temp_storage():
    """Create a temporary storage file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        f.write('{}')
        temp_file = f.name
    
    # Override the storage file
    url_service = get_url_service()
    original_storage = url_service.storage_file
    url_service.storage_file = temp_file
    url_service.urls = {}
    
    yield temp_file
    
    # Cleanup
    url_service.storage_file = original_storage
    os.unlink(temp_file)

def test_read_main(client):
    """Test the main page loads"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Universal URL Shortener" in response.text

def test_api_docs(client):
    """Test API documentation is accessible"""
    response = client.get("/docs")
    assert response.status_code == 200

def test_create_short_url(client, temp_storage):
    """Test creating a short URL"""
    response = client.post(
        "/shorten-form",
        data={
            "long_url": "https://www.example.com",
            "custom_alias": "",
            "description": "Test URL",
            "password": ""
        }
    )
    # Should redirect to result page
    assert response.status_code == 303

def test_api_shorten_url(client, temp_storage):
    """Test API endpoint for URL shortening"""
    response = client.post(
        "/api/shorten",
        json={
            "long_url": "https://www.example.com",
            "description": "API Test URL"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "short_url" in data
    assert "short_code" in data
    assert data["long_url"] == "https://www.example.com"

def test_invalid_url(client, temp_storage):
    """Test invalid URL handling"""
    response = client.post(
        "/api/shorten",
        json={
            "long_url": "not-a-valid-url"
        }
    )
    assert response.status_code == 400

def test_dashboard_loads(client):
    """Test dashboard page loads"""
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "Dashboard" in response.text

def test_analytics_loads(client):
    """Test analytics page loads"""
    response = client.get("/analytics")
    assert response.status_code == 200

def test_bulk_page_loads(client):
    """Test bulk shortening page loads"""
    response = client.get("/bulk")
    assert response.status_code == 200
