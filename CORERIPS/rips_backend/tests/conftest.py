"""
Configuración de fixtures para tests
Provee fixtures compartidos para todos los tests del proyecto
"""
import pytest
import tempfile
import os
import json
import sys
from unittest.mock import Mock, MagicMock, patch, DEFAULT
from fastapi.testclient import TestClient
from pathlib import Path

# Agregar el directorio raíz al path para poder importar los módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

# Establecer variable de entorno para indicar modo test
os.environ['TESTING'] = 'true'

# Mockear create_client de supabase antes de cualquier importación
mock_supabase_client = MagicMock()
mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
mock_supabase_client.table.return_value.insert.return_value.execute.return_value.data = [{"id": 1}]
mock_supabase_client.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{"id": 1}]

def mock_create_client(*args, **kwargs):
    """Mock de create_client que retorna nuestro cliente mockeado"""
    return mock_supabase_client

# Patchear el módulo supabase antes de importar
import supabase
supabase.create_client = mock_create_client

# Ahora importar los módulos de la aplicación
from main import app
from db.database import get_db


# ============================================================================
# FIXTURES DE CLIENTE Y CONFIGURACIÓN
# ============================================================================

@pytest.fixture(scope="session")
def test_client():
    """Cliente de prueba de FastAPI para toda la sesión"""
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
def client():
    """Cliente de prueba de FastAPI por función (se reinicia en cada test)"""
    with TestClient(app) as test_client:
        yield test_client


# ============================================================================
# FIXTURES DE ARCHIVOS DE PRUEBA
# ============================================================================

@pytest.fixture
def valid_rips_ac_content():
    """Contenido válido de archivo RIPS tipo AC (Consultas)"""
    return """123456789012|1|CC|12345678|01|1990-03-15|M|170|11001|08001001|2024-03-15|123456|890101|10|A001|Z000|||
123456789012|1|TI|87654321|02|2005-08-20|F|169|11001|05001001|2024-03-15|123457|890102|10|B002|J180|||"""


@pytest.fixture
def invalid_rips_ac_content():
    """Contenido inválido de archivo RIPS tipo AC"""
    return """INVALID|DATA|FORMAT|WRONG
|||||||||||||||||"""


@pytest.fixture
def valid_rips_json():
    """Contenido válido de archivo JSON RIPS"""
    return {
        "numFactura": "FAC001",
        "tipoRegistro": "1",
        "fechaGeneracion": "2024-03-15",
        "tipoFactura": "01",
        "cuv": "1234567890ABC",
        "versionAnexoTecnico": "1.0",
        "usuarios": [
            {
                "tipoDocumentoIdentificacion": "CC",
                "numDocumentoIdentificacion": "12345678",
                "fechaNacimiento": "1990-03-15",
                "codSexo": "M",
                "tipoUsuario": "01",
                "codPaisResidencia": "170",
                "codMunicipioResidencia": "11001",
                "servicios": {
                    "consultas": [
                        {
                            "codPrestador": "123456789012",
                            "fechaInicioAtencion": "2024-03-15",
                            "numAutorizacion": "AUT123",
                            "codConsulta": "890101",
                            "finalidadTecnologiaSalud": "10",
                            "codDiagnosticoPrincipal": "Z000"
                        }
                    ],
                    "procedimientos": [],
                    "medicamentos": []
                }
            }
        ]
    }


@pytest.fixture
def temp_rips_file(valid_rips_ac_content):
    """Crear archivo temporal RIPS válido"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='_AC.txt', delete=False, encoding='utf-8') as f:
        f.write(valid_rips_ac_content)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def temp_invalid_rips_file(invalid_rips_ac_content):
    """Crear archivo temporal RIPS inválido"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='_AC.txt', delete=False, encoding='utf-8') as f:
        f.write(invalid_rips_ac_content)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def temp_json_rips_file(valid_rips_json):
    """Crear archivo temporal JSON RIPS"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(valid_rips_json, f)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


# ============================================================================
# FIXTURES DE AUTENTICACIÓN
# ============================================================================

@pytest.fixture
def mock_auth_token():
    """Token de autenticación simulado"""
    return "test_token_12345abcdef"


@pytest.fixture
def auth_headers(mock_auth_token):
    """Headers de autenticación para requests"""
    return {"Authorization": f"Bearer {mock_auth_token}"}


@pytest.fixture
def admin_credentials():
    """Credenciales de usuario administrador"""
    return {
        "username": "admin",
        "password": "admin123"
    }


@pytest.fixture
def validator_credentials():
    """Credenciales de usuario validador"""
    return {
        "username": "validator1",
        "password": "validator123"
    }


@pytest.fixture
def test_user(mock_db):
    """
    Fixture de usuario de prueba (simula usuario en DB)
    Compatible con tests antiguos de test_api.py
    Retorna validator1 que tiene credenciales válidas en el sistema
    """
    from unittest.mock import MagicMock
    
    # Crear objeto usuario mock
    user = MagicMock()
    user.id = 1
    user.username = "validator1"
    user.email = "validator@rips.com"
    user.role = "validator"
    user.is_active = "true"
    
    # Configurar mock_db para retornar este usuario
    mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "id": 1,
            "username": "validator1",
            "email": "validator@rips.com",
            "role": "validator",
            "is_active": "true"
        }
    ]
    
    return user


@pytest.fixture
def admin_user(mock_db):
    """
    Fixture de usuario administrador (simula usuario en DB)
    Compatible con tests antiguos de test_api.py
    """
    from unittest.mock import MagicMock
    
    # Crear objeto usuario admin mock
    user = MagicMock()
    user.id = 2
    user.username = "admin"
    user.email = "admin@example.com"
    user.role = "admin"
    user.is_active = "true"
    
    # Configurar mock_db para retornar este usuario
    mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "id": 2,
            "username": "admin",
            "email": "admin@example.com",
            "role": "admin",
            "is_active": "true"
        }
    ]
    
    return user


# ============================================================================
# FIXTURES DE DATOS DE PRUEBA
# ============================================================================

@pytest.fixture
def sample_upload_file():
    """Archivo de prueba para upload"""
    content = b"Test file content for RIPS validation"
    return ("test_rips_AC.txt", content, "text/plain")


@pytest.fixture
def sample_file_data():
    """Datos de archivo de prueba"""
    return {
        "filename": "test_AC_20240315.txt",
        "original_filename": "test_AC_20240315.txt",
        "file_path": "/tmp/test_AC_20240315.txt",
        "file_size": 1024,
        "status": "uploaded",
        "user_id": 1
    }


@pytest.fixture
def sample_validation_request():
    """Request de validación de prueba"""
    return {
        "file_id": 1,
        "validation_types": ["deterministic"]
    }


# ============================================================================
# FIXTURES DE LIMPIEZA
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_uploads():
    """Limpiar archivos de upload después de cada test"""
    yield
    
    # Limpiar directorio uploads después del test
    uploads_dir = Path("uploads")
    if uploads_dir.exists():
        for file in uploads_dir.glob("test_*"):
            try:
                file.unlink()
            except Exception:
                pass


# ============================================================================
# FIXTURES DE MOCK DATABASE
# ============================================================================

@pytest.fixture
def mock_db():
    """Mock de cliente de base de datos Supabase"""
    from unittest.mock import MagicMock
    
    mock = MagicMock()
    
    # Configurar comportamiento por defecto
    mock.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
    mock.table.return_value.insert.return_value.execute.return_value.data = [{"id": 1}]
    mock.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{"id": 1}]
    
    return mock


@pytest.fixture
def override_get_db(mock_db):
    """Override de dependencia get_db para tests"""
    # Configurar respuestas por defecto para usuarios comunes
    mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "id": 1,
            "username": "admin",
            "email": "admin@rips.com",
            "role": "admin",
            "is_active": "true"
        }
    ]
    
    def _override_get_db():
        return mock_db
    
    app.dependency_overrides[get_db] = _override_get_db
    yield mock_db
    app.dependency_overrides.clear()


# ============================================================================
# FIXTURES DE MODELOS
# ============================================================================

@pytest.fixture
def sample_error_response():
    """ErrorResponse de ejemplo"""
    from models.schemas import ErrorResponse
    return ErrorResponse(
        line=1,
        field="codPrestador",
        error="Código prestador debe ser 12 dígitos numéricos"
    )


@pytest.fixture
def sample_validation_results():
    """Resultados de validación de ejemplo"""
    return {
        "file_id": 1,
        "filename": "test_AC.txt",
        "total_lines": 10,
        "total_errors": 2,
        "total_warnings": 1,
        "validations": []
    }
