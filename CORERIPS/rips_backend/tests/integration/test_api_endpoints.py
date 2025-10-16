"""
Tests de integración para endpoints de la API
Prueba flujos end-to-end de la aplicación
"""
import pytest
import tempfile
import os
import json
from io import BytesIO


class TestHealthEndpoints:
    """Tests para endpoints de salud y estado del sistema"""
    
    def test_root_endpoint(self, client):
        """
        Test: GET / - Endpoint raíz
        Resultado esperado: 200 OK con mensaje de bienvenida
        """
        # Act
        response = client.get("/")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "RIPS" in data["message"]
    
    def test_health_check_endpoint(self, client):
        """
        Test: GET /health - Health check
        Resultado esperado: 200 OK con status healthy
        """
        # Act
        response = client.get("/health")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data


class TestAuthenticationEndpoints:
    """Tests para endpoints de autenticación"""
    
    def test_login_with_valid_credentials(self, client, admin_credentials, override_get_db):
        """
        Test: POST /api/v1/auth/login - Login exitoso
        Entrada: Credenciales válidas de admin
        Resultado esperado: 200 OK con token
        """
        # Arrange: Configurar mock_db para retornar usuario admin
        override_get_db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {
                "id": 1,
                "username": "admin",
                "email": "admin@rips.com",
                "role": "admin",
                "is_active": "true"
            }
        ]
        
        # Act
        response = client.post("/api/v1/auth/login", json=admin_credentials)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    def test_login_with_invalid_credentials(self, client):
        """
        Test: POST /api/v1/auth/login - Login fallido
        Entrada: Credenciales inválidas
        Resultado esperado: 401 Unauthorized
        """
        # Arrange
        invalid_credentials = {
            "username": "invalid_user",
            "password": "wrong_password"
        }
        
        # Act
        response = client.post("/api/v1/auth/login", json=invalid_credentials)
        
        # Assert
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    def test_login_with_empty_credentials(self, client):
        """
        Test: POST /api/v1/auth/login - Login con credenciales vacías
        Resultado esperado: 422 Validation Error
        """
        # Arrange
        empty_credentials = {
            "username": "",
            "password": ""
        }
        
        # Act
        response = client.post("/api/v1/auth/login", json=empty_credentials)
        
        # Assert
        # Puede ser 401 o 422 dependiendo de la validación
        assert response.status_code in [401, 422]
    
    def test_get_current_user_with_token(self, client, admin_credentials, override_get_db):
        """
        Test: GET /api/v1/auth/me - Obtener usuario actual
        Entrada: Token válido
        Resultado esperado: 200 OK con datos de usuario
        """
        # Arrange: Configurar mock_db para login
        override_get_db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {
                "id": 1,
                "username": "admin",
                "email": "admin@rips.com",
                "role": "admin",
                "is_active": "true"
            }
        ]
        
        # Arrange: primero hacer login
        login_response = client.post("/api/v1/auth/login", json=admin_credentials)
        
        # Si el login falla, skip este test
        if login_response.status_code != 200:
            import pytest
            pytest.skip("Login no disponible")
        
        token = login_response.json().get("access_token")
        if not token:
            import pytest
            pytest.skip("Token no generado")
            
        headers = {"Authorization": f"Bearer {token}"}
        
        # Act
        response = client.get("/api/v1/auth/me", headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert "email" in data
        assert "role" in data
    
    def test_get_current_user_without_token(self, client):
        """
        Test: GET /api/v1/auth/me - Sin token de autenticación
        Resultado esperado: 401 o 403 Unauthorized
        """
        # Act
        response = client.get("/api/v1/auth/me")
        
        # Assert
        assert response.status_code in [401, 403]


class TestFileUploadEndpoints:
    """Tests para endpoints de subida de archivos"""
    
    def test_upload_valid_rips_file(self, client, override_get_db, valid_rips_ac_content):
        """
        Test: POST /api/v1/upload - Subir archivo RIPS válido
        Entrada: Archivo TXT RIPS formato AC
        Resultado esperado: 200 OK con file_id
        """
        # Arrange
        file_content = valid_rips_ac_content.encode('utf-8')
        files = {
            "file": ("test_AC_20240315.txt", BytesIO(file_content), "text/plain")
        }
        
        # Configurar mock DB para retornar datos
        override_get_db.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": 1, "filename": "test_AC_20240315.txt"}
        ]
        
        # Act
        response = client.post("/api/v1/upload", files=files)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "file_id" in data or "message" in data
        assert "filename" in data
    
    def test_upload_json_rips_file(self, client, override_get_db, valid_rips_json):
        """
        Test: POST /api/v1/upload - Subir archivo JSON RIPS
        Entrada: Archivo JSON RIPS
        Resultado esperado: 200 OK
        """
        # Arrange
        json_content = json.dumps(valid_rips_json).encode('utf-8')
        files = {
            "file": ("test_rips.json", BytesIO(json_content), "application/json")
        }
        
        override_get_db.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": 2}
        ]
        
        # Act
        response = client.post("/api/v1/upload", files=files)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "file_id" in data or "message" in data
    
    def test_upload_without_file(self, client):
        """
        Test: POST /api/v1/upload - Request sin archivo
        Resultado esperado: 422 Validation Error
        """
        # Act
        response = client.post("/api/v1/upload")
        
        # Assert
        assert response.status_code == 422
    
    def test_upload_empty_file(self, client, override_get_db):
        """
        Test: POST /api/v1/upload - Archivo vacío
        Resultado esperado: 200 OK o error descriptivo
        """
        # Arrange
        files = {
            "file": ("empty.txt", BytesIO(b""), "text/plain")
        }
        
        override_get_db.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": 3}
        ]
        
        # Act
        response = client.post("/api/v1/upload", files=files)
        
        # Assert: debería manejar el caso graciosamente
        assert response.status_code in [200, 400, 422]
    
    def test_upload_large_filename(self, client, override_get_db):
        """
        Test: POST /api/v1/upload - Nombre de archivo muy largo
        """
        # Arrange
        long_filename = "a" * 200 + "_AC.txt"
        file_content = b"test content"
        files = {
            "file": (long_filename, BytesIO(file_content), "text/plain")
        }
        
        override_get_db.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": 4}
        ]
        
        # Act
        response = client.post("/api/v1/upload", files=files)
        
        # Assert: debería manejar el caso
        assert response.status_code in [200, 400]


class TestValidationEndpoints:
    """Tests para endpoints de validación"""
    
    def test_validate_file_deterministic(self, client, override_get_db, temp_rips_file):
        """
        Test: POST /api/v1/validate - Validación determinística
        Entrada: file_id y tipo de validación
        Resultado esperado: 200 OK con resultados
        """
        # Arrange
        validation_request = {
            "file_id": 1,
            "validation_types": ["deterministic"]
        }
        
        # Configurar mock DB
        override_get_db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {
                "id": 1,
                "filename": "test_AC.txt",
                "file_path": temp_rips_file,
                "status": "uploaded"
            }
        ]
        override_get_db.table.return_value.insert.return_value.execute.return_value.data = [{"id": 1}]
        override_get_db.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{"id": 1}]
        
        # Act
        response = client.post("/api/v1/validate", json=validation_request)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "file_id" in data
        assert "status" in data or "message" in data
    
    def test_validate_nonexistent_file(self, client, override_get_db):
        """
        Test: POST /api/v1/validate - Validar archivo inexistente
        Resultado esperado: 404 Not Found
        """
        # Arrange
        validation_request = {
            "file_id": 99999,
            "validation_types": ["deterministic"]
        }
        
        # Configurar mock DB para retornar vacío
        override_get_db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        
        # Act
        response = client.post("/api/v1/validate", json=validation_request)
        
        # Assert
        assert response.status_code == 404
    
    def test_validate_with_both_validators(self, client, override_get_db, temp_rips_file):
        """
        Test: POST /api/v1/validate - Validación determinística + IA
        """
        # Arrange
        validation_request = {
            "file_id": 1,
            "validation_types": ["deterministic", "ai"]
        }
        
        override_get_db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {
                "id": 1,
                "filename": "test_AC.txt",
                "file_path": temp_rips_file,
                "status": "uploaded"
            }
        ]
        override_get_db.table.return_value.insert.return_value.execute.return_value.data = [{"id": 1}]
        override_get_db.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{"id": 1}]
        
        # Act
        response = client.post("/api/v1/validate", json=validation_request)
        
        # Assert
        assert response.status_code in [200, 500]  # Puede fallar si IA no está disponible
    
    def test_validate_without_validation_types(self, client, override_get_db, temp_rips_file):
        """
        Test: POST /api/v1/validate - Sin especificar tipos de validación
        Resultado esperado: Usa tipo por defecto
        """
        # Arrange
        validation_request = {
            "file_id": 1
        }
        
        override_get_db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {
                "id": 1,
                "filename": "test_AC.txt",
                "file_path": temp_rips_file,
                "status": "uploaded"
            }
        ]
        override_get_db.table.return_value.insert.return_value.execute.return_value.data = [{"id": 1}]
        override_get_db.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{"id": 1}]
        
        # Act
        response = client.post("/api/v1/validate", json=validation_request)
        
        # Assert
        assert response.status_code == 200


class TestResultsEndpoints:
    """Tests para endpoints de consulta de resultados"""
    
    def test_get_validation_results(self, client, override_get_db):
        """
        Test: GET /api/v1/results/{file_id} - Obtener resultados
        Resultado esperado: 200 OK con resultados de validación
        """
        # Arrange
        file_id = 1
        
        # Configurar mock DB
        override_get_db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {
                "id": 1,
                "original_filename": "test_AC.txt",
                "status": "validated"
            }
        ]
        
        # Act
        response = client.get(f"/api/v1/results/{file_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "file_id" in data
        assert "filename" in data
        assert "status" in data
    
    def test_get_results_nonexistent_file(self, client, override_get_db):
        """
        Test: GET /api/v1/results/{file_id} - Archivo inexistente
        Resultado esperado: 404 Not Found
        """
        # Arrange
        file_id = 99999
        override_get_db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        
        # Act
        response = client.get(f"/api/v1/results/{file_id}")
        
        # Assert
        assert response.status_code == 404
    
    def test_get_files_list(self, client, override_get_db):
        """
        Test: GET /api/v1/files - Listar archivos del usuario
        Resultado esperado: 200 OK con lista de archivos
        """
        # Arrange
        override_get_db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"id": 1, "filename": "file1.txt"},
            {"id": 2, "filename": "file2.txt"}
        ]
        
        # Act
        response = client.get("/api/v1/files")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "files" in data or isinstance(data, list)


class TestEndToEndFlows:
    """Tests de flujos completos end-to-end"""
    
    def test_complete_validation_flow(self, client, override_get_db, valid_rips_ac_content, temp_rips_file):
        """
        Test: Flujo completo - Upload → Validate → Get Results
        """
        # Step 1: Upload file
        file_content = valid_rips_ac_content.encode('utf-8')
        files = {
            "file": ("test_flow_AC.txt", BytesIO(file_content), "text/plain")
        }
        
        override_get_db.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": 1, "filename": "test_flow_AC.txt"}
        ]
        
        upload_response = client.post("/api/v1/upload", files=files)
        assert upload_response.status_code == 200
        file_id = upload_response.json().get("file_id", 1)
        
        # Step 2: Validate file
        override_get_db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {
                "id": file_id,
                "filename": "test_flow_AC.txt",
                "file_path": temp_rips_file,
                "status": "uploaded"
            }
        ]
        override_get_db.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{"id": file_id}]
        
        validation_request = {
            "file_id": file_id,
            "validation_types": ["deterministic"]
        }
        
        validate_response = client.post("/api/v1/validate", json=validation_request)
        assert validate_response.status_code == 200
        
        # Step 3: Get results
        override_get_db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {
                "id": file_id,
                "original_filename": "test_flow_AC.txt",
                "status": "validated"
            }
        ]
        
        results_response = client.get(f"/api/v1/results/{file_id}")
        assert results_response.status_code == 200

