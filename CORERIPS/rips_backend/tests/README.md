# 🧪 Tests Automatizados - RIPS Backend

Suite completa de tests automatizados para el sistema de validación de archivos RIPS.

## 📁 Estructura de Tests

```
tests/
├── conftest.py                              # Fixtures compartidos
├── unit/                                     # Tests unitarios
│   ├── test_deterministic_validator.py      # Validador determinístico
│   ├── test_ai_validator.py                 # Validador de IA
│   └── test_validation_service.py           # Servicio de validación
├── integration/                              # Tests de integración
│   └── test_api_endpoints.py                # Endpoints de la API
├── test_api.py                              # Tests legacy de API
└── test_deterministic_validator.py          # Tests legacy
```

## 🚀 Comandos para Ejecutar Tests

### Ejecutar TODOS los tests
```bash
pytest
```

### Ejecutar solo tests unitarios
```bash
pytest tests/unit/
```

### Ejecutar solo tests de integración
```bash
pytest tests/integration/
```

### Ejecutar tests específicos por archivo
```bash
pytest tests/unit/test_deterministic_validator.py
pytest tests/unit/test_ai_validator.py
pytest tests/unit/test_validation_service.py
pytest tests/integration/test_api_endpoints.py
```

### Ejecutar un test específico
```bash
pytest tests/unit/test_deterministic_validator.py::TestEnhancedDeterministicValidator::test_validate_valid_rips_ac_file
```

### Ejecutar tests con cobertura
```bash
pytest --cov=validators --cov=services --cov=api --cov-report=html
```

### Ejecutar tests con salida detallada
```bash
pytest -vv
```

### Ejecutar tests y ver print statements
```bash
pytest -s
```

### Ejecutar tests en paralelo (más rápido)
```bash
pytest -n auto
```

## 📊 Cobertura de Tests

### Ver reporte de cobertura
Después de ejecutar los tests con cobertura, abre:
```bash
open htmlcov/index.html
```

## 🎯 Tests por Categoría

### ✅ Tests Unitarios

#### **test_deterministic_validator.py** (16 tests)
- ✓ Validación de archivos RIPS válidos (AC, JSON)
- ✓ Validación de archivos inválidos
- ✓ Validación de reglas específicas (AC-001, AC-012, FMT-006)
- ✓ Manejo de archivos inexistentes
- ✓ Validación de diferentes tipos RIPS (AC, AP, AM, US, etc.)
- ✓ Casos edge: archivos vacíos, caracteres especiales
- ✓ Performance con archivos grandes

#### **test_ai_validator.py** (11 tests)
- ✓ Inicialización del validador de IA
- ✓ Validación de archivos JSON
- ✓ Reglas clínicas (AI-CLIN-001, AI-CLIN-002)
- ✓ Detección de patrones (AI-PAT-001)
- ✓ Manejo de errores (archivos inexistentes, vacíos, JSON corrupto)
- ✓ Validación de múltiples registros

#### **test_validation_service.py** (18 tests)
- ✓ Inicialización del servicio
- ✓ Detección de tipos de archivo (_get_file_type)
- ✓ Conteo de líneas (_count_file_lines)
- ✓ Validación con mocks de base de datos
- ✓ Guardado de errores de validación
- ✓ Casos edge: múltiples indicadores de tipo, líneas vacías

### 🔗 Tests de Integración

#### **test_api_endpoints.py** (25 tests)
- ✓ Endpoints de salud (/, /health)
- ✓ Autenticación (login, logout, me)
- ✓ Upload de archivos (válidos, inválidos, vacíos)
- ✓ Validación de archivos (determinística, IA, ambas)
- ✓ Consulta de resultados
- ✓ Flujo end-to-end completo

## 🏗️ Fixtures Disponibles

### Fixtures de Cliente
- `test_client` - Cliente FastAPI para toda la sesión
- `client` - Cliente FastAPI por función

### Fixtures de Archivos
- `valid_rips_ac_content` - Contenido válido RIPS AC
- `invalid_rips_ac_content` - Contenido inválido
- `valid_rips_json` - JSON RIPS válido
- `temp_rips_file` - Archivo temporal RIPS
- `temp_invalid_rips_file` - Archivo temporal inválido
- `temp_json_rips_file` - Archivo temporal JSON

### Fixtures de Autenticación
- `mock_auth_token` - Token de prueba
- `auth_headers` - Headers con autenticación
- `admin_credentials` - Credenciales de admin
- `validator_credentials` - Credenciales de validador

### Fixtures de Base de Datos
- `mock_db` - Mock de Supabase client
- `override_get_db` - Override de dependencia DB

### Fixtures de Datos
- `sample_upload_file` - Archivo de prueba
- `sample_file_data` - Datos de archivo
- `sample_validation_request` - Request de validación
- `sample_error_response` - ErrorResponse de ejemplo
- `sample_validation_results` - Resultados de ejemplo

## 📝 Escribir Nuevos Tests

### Template para test unitario
```python
def test_mi_funcionalidad(self, fixture_necesaria):
    """
    Test: Descripción clara de qué se prueba
    Entrada: Datos de entrada
    Resultado esperado: Qué debe pasar
    """
    # Arrange: preparar datos
    data = preparar_datos()
    
    # Act: ejecutar funcionalidad
    result = funcion_a_probar(data)
    
    # Assert: verificar resultado
    assert result == valor_esperado
```

### Template para test de integración
```python
def test_endpoint_api(self, client, override_get_db):
    """
    Test: POST /api/endpoint - Descripción
    """
    # Arrange: configurar request y mocks
    request_data = {"key": "value"}
    override_get_db.table.return_value...
    
    # Act: hacer request
    response = client.post("/api/endpoint", json=request_data)
    
    # Assert: verificar respuesta
    assert response.status_code == 200
    assert "key" in response.json()
```

## 🔧 Configuración

### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --cov=.
    --cov-report=html
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

## 📈 Métricas de Calidad

### Cobertura Objetivo
- **Validadores:** > 90%
- **Servicios:** > 85%
- **Endpoints:** > 80%
- **Total:** > 85%

### Tiempos de Ejecución
- Tests unitarios: < 30 segundos
- Tests integración: < 2 minutos
- Suite completa: < 3 minutos

## 🐛 Debugging

### Ejecutar test con debugger
```bash
pytest --pdb tests/unit/test_file.py::test_function
```

### Ver valores de fixtures
```bash
pytest --fixtures
```

### Ver qué tests se ejecutarían (sin ejecutar)
```bash
pytest --collect-only
```

## 📚 Recursos

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Coverage.py](https://coverage.readthedocs.io/)

## ✨ Mejores Prácticas

1. **Tests independientes:** Cada test debe poder ejecutarse solo
2. **AAA Pattern:** Arrange, Act, Assert
3. **Nombres descriptivos:** `test_validate_invalid_format_returns_error`
4. **Un concepto por test:** No probar múltiples cosas en un test
5. **Usar fixtures:** Reutilizar código de setup
6. **Mock dependencies:** Aislar unidad bajo prueba
7. **Tests rápidos:** Optimizar para ejecución rápida

## 🎯 Roadmap

- [ ] Tests de carga/stress
- [ ] Tests de seguridad
- [ ] Tests e2e con Selenium
- [ ] Integración con CI/CD
- [ ] Tests de regresión visual
- [ ] Mutación testing

