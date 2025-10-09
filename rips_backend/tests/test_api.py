import pytest
from fastapi.testclient import TestClient
import tempfile
import os

def test_health_check(client):
    """Probar endpoint de health check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root_endpoint(client):
    """Probar endpoint raíz"""
    response = client.get("/")
    assert response.status_code == 200
    assert "RIPS Validator API" in response.json()["message"]

def test_register_user(client):
    """Probar registro de usuario"""
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "newpassword",
        "role": "validator"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert data["role"] == "validator"

def test_register_duplicate_user(client, test_user):
    """Probar registro de usuario duplicado"""
    user_data = {
        "username": "testuser",  # Usuario ya existe
        "email": "different@example.com",
        "password": "password",
        "role": "validator"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400
    assert "ya está registrado" in response.json()["detail"]

def test_login_valid_user(client, test_user):
    """Probar login con usuario válido"""
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_user(client):
    """Probar login con usuario inválido"""
    login_data = {
        "username": "nonexistent",
        "password": "wrongpassword"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 401
    assert "Credenciales incorrectas" in response.json()["detail"]

def test_get_current_user(client, test_user):
    """Probar obtener usuario actual"""
    # Primero hacer login
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    
    login_response = client.post("/api/v1/auth/login", json=login_data)
    token = login_response.json()["access_token"]
    
    # Usar token para obtener información del usuario
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"

def test_upload_file_unauthorized(client):
    """Probar subida de archivo sin autorización"""
    with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
        temp_file.write(b"test content")
        temp_file.seek(0)
        
        files = {"file": ("test.txt", temp_file, "text/plain")}
        response = client.post("/api/v1/upload", files=files)
        
        assert response.status_code == 401

def test_upload_file_authorized(client, test_user):
    """Probar subida de archivo con autorización"""
    # Hacer login
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    
    login_response = client.post("/api/v1/auth/login", json=login_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Crear archivo temporal
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
        temp_file.write(b"123456789012|1|CC|12345678|1|15/03/1990|M|1|1|1|15/03/2024|1|1|1|1|Z000|Z001")
        temp_file_path = temp_file.name
    
    try:
        with open(temp_file_path, "rb") as file:
            files = {"file": ("test_rips.txt", file, "text/plain")}
            response = client.post("/api/v1/upload", files=files, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "file_id" in data
        assert data["filename"] == "test_rips.txt"
        assert "exitosamente" in data["message"]
        
    finally:
        # Limpiar archivo temporal
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

def test_upload_invalid_file_type(client, test_user):
    """Probar subida de archivo con tipo inválido"""
    # Hacer login
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    
    login_response = client.post("/api/v1/auth/login", json=login_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Crear archivo con extensión inválida
    with tempfile.NamedTemporaryFile(suffix=".pdf") as temp_file:
        temp_file.write(b"test content")
        temp_file.seek(0)
        
        files = {"file": ("test.pdf", temp_file, "application/pdf")}
        response = client.post("/api/v1/upload", files=files, headers=headers)
        
        assert response.status_code == 400
        assert "Tipo de archivo no válido" in response.json()["detail"]

def test_get_user_files(client, test_user):
    """Probar obtener archivos del usuario"""
    # Hacer login
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    
    login_response = client.post("/api/v1/auth/login", json=login_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/files", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_admin_endpoints_unauthorized(client, test_user):
    """Probar endpoints de admin sin permisos"""
    # Hacer login con usuario normal
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    
    login_response = client.post("/api/v1/auth/login", json=login_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Intentar acceder a endpoint de admin
    response = client.get("/api/v1/admin/users", headers=headers)
    assert response.status_code == 403
    assert "Not enough permissions" in response.json()["detail"]

def test_admin_endpoints_authorized(client, admin_user):
    """Probar endpoints de admin con permisos"""
    # Hacer login con usuario admin
    login_data = {
        "username": "admin",
        "password": "adminpassword"
    }
    
    login_response = client.post("/api/v1/auth/login", json=login_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Acceder a endpoint de admin
    response = client.get("/api/v1/admin/users", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
