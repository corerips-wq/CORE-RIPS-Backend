# 🧪 Guía de Testing - RIPS Backend

## 📋 Resumen Ejecutivo

Suite completa de **70+ tests automatizados** para el backend RIPS, organizada profesionalmente en:
- ✅ **45 tests unitarios** (validadores, servicios)
- ✅ **25 tests de integración** (endpoints, flujos E2E)

---

## 🚀 Inicio Rápido

### 1. Instalar Dependencias
```bash
cd rips_backend
source venv/bin/activate  # o: venv\Scripts\activate en Windows
pip install -r requirements.txt
```

### 2. Ejecutar Tests
```bash
# Opción 1: Usar script (recomendado)
./run_tests.sh

# Opción 2: Comando directo
pytest

# Opción 3: Con cobertura
./run_tests.sh coverage
```

### 3. Ver Resultados
```bash
# Abrir reporte de cobertura
open htmlcov/index.html
```

---

## 📁 Estructura de Tests Creada

```
rips_backend/
├── tests/
│   ├── conftest.py                          ✨ Fixtures compartidos (180 líneas)
│   ├── README.md                            📚 Documentación completa
│   │
│   ├── unit/                                🔬 Tests Unitarios
│   │   ├── __init__.py
│   │   ├── test_deterministic_validator.py  (450 líneas, 16 tests)
│   │   ├── test_ai_validator.py             (320 líneas, 11 tests)
│   │   └── test_validation_service.py       (380 líneas, 18 tests)
│   │
│   └── integration/                         🔗 Tests de Integración
│       ├── __init__.py
│       └── test_api_endpoints.py            (550 líneas, 25 tests)
│
├── pytest.ini                               ⚙️ Configuración pytest
├── run_tests.sh                             🚀 Script de ejecución
└── TESTING_GUIDE.md                         📖 Esta guía
```

---

## 🎯 Tests Implementados

### 🔬 Tests Unitarios (45 tests)

#### **test_deterministic_validator.py** (16 tests)
```python
✅ test_validate_valid_rips_ac_file             # Archivo válido AC
✅ test_validate_json_rips_file                 # Archivo JSON válido
✅ test_validate_invalid_rips_file              # Detectar errores
✅ test_validate_nonexistent_file               # Archivo inexistente
✅ test_validate_codigo_prestador_format        # Regla AC-001
✅ test_validate_fecha_format                   # Regla FMT-006
✅ test_validate_diagnostico_cie_length         # Regla AC-012
✅ test_validate_different_file_types           # Tipos: AC, AP, AM, US
✅ test_validate_empty_file                     # Archivo vacío
✅ test_validate_file_with_special_characters   # UTF-8 / ñáéíóú
✅ test_validate_large_file_performance         # 1000+ líneas
✅ test_error_response_creation                 # ErrorResponse
✅ test_validator_initialization                # Inicialización
+ 3 tests adicionales
```

#### **test_ai_validator.py** (11 tests)
```python
✅ test_validator_initialization                # Inicialización
✅ test_validate_file_returns_list              # Retorna lista
✅ test_validate_json_file                      # JSON válido
✅ test_diagnostico_vs_sexo_validation          # Regla AI-CLIN-001
✅ test_diagnostico_vs_edad_validation          # Regla AI-CLIN-002
✅ test_procedimientos_duplicados_detection     # Regla AI-PAT-001
✅ test_validate_nonexistent_file               # Error handling
✅ test_validate_empty_file                     # Archivo vacío
✅ test_validate_corrupted_json                 # JSON inválido
✅ test_validate_multiple_records               # Múltiples registros
+ 1 test adicional
```

#### **test_validation_service.py** (18 tests)
```python
✅ test_service_initialization                  # Inicialización
✅ test_get_file_type_ac                        # Detectar tipo AC
✅ test_get_file_type_ap                        # Detectar tipo AP
✅ test_get_file_type_am                        # Detectar tipo AM
✅ test_get_file_type_us                        # Detectar tipo US
✅ test_get_file_type_default                   # Tipo por defecto
✅ test_count_file_lines_valid_file             # Contar líneas
✅ test_count_file_lines_nonexistent_file       # Archivo inexistente
✅ test_count_file_lines_empty_file             # Archivo vacío
✅ test_validate_file_deterministic_only        # Mock validación
✅ test_validate_file_invalid_file_id           # ID inválido
✅ test_save_validation_errors                  # Guardar errores
✅ test_save_validation_errors_empty_list       # Lista vacía
✅ test_service_with_real_validators            # Validadores reales
✅ test_count_lines_real_file                   # Contar líneas real
✅ test_get_file_type_case_insensitive          # Case insensitive
✅ test_get_file_type_multiple_indicators       # Múltiples tipos
+ 1 test adicional
```

### 🔗 Tests de Integración (25 tests)

#### **test_api_endpoints.py** (25 tests)
```python
# Endpoints de Salud (2 tests)
✅ test_root_endpoint                           # GET /
✅ test_health_check_endpoint                   # GET /health

# Autenticación (5 tests)
✅ test_login_with_valid_credentials            # POST /api/v1/auth/login
✅ test_login_with_invalid_credentials          # Login fallido
✅ test_login_with_empty_credentials            # Credenciales vacías
✅ test_get_current_user_with_token             # GET /api/v1/auth/me
✅ test_get_current_user_without_token          # Sin token

# Upload de Archivos (5 tests)
✅ test_upload_valid_rips_file                  # POST /api/v1/upload (TXT)
✅ test_upload_json_rips_file                   # Upload JSON
✅ test_upload_without_file                     # Sin archivo
✅ test_upload_empty_file                       # Archivo vacío
✅ test_upload_large_filename                   # Nombre largo

# Validación (4 tests)
✅ test_validate_file_deterministic             # POST /api/v1/validate
✅ test_validate_nonexistent_file               # Archivo inexistente
✅ test_validate_with_both_validators           # Determinística + IA
✅ test_validate_without_validation_types       # Tipo por defecto

# Resultados (3 tests)
✅ test_get_validation_results                  # GET /api/v1/results/{id}
✅ test_get_results_nonexistent_file            # Archivo inexistente
✅ test_get_files_list                          # GET /api/v1/files

# End-to-End (1 test)
✅ test_complete_validation_flow                # Upload → Validate → Results
```

---

## 🛠️ Comandos Disponibles

### Script `run_tests.sh`

```bash
# Ver ayuda
./run_tests.sh help

# Ejecutar todos los tests
./run_tests.sh all

# Solo tests unitarios
./run_tests.sh unit

# Solo tests de integración
./run_tests.sh integration

# Solo validadores
./run_tests.sh validators

# Solo servicios
./run_tests.sh services

# Solo API
./run_tests.sh api

# Con cobertura de código
./run_tests.sh coverage

# Tests rápidos (solo unitarios)
./run_tests.sh fast

# Modo verbose
./run_tests.sh verbose

# Test específico
./run_tests.sh specific tests/unit/test_deterministic_validator.py
```

### Comandos `pytest` Directos

```bash
# Todos los tests
pytest

# Solo unitarios
pytest tests/unit/

# Solo integración
pytest tests/integration/

# Test específico
pytest tests/unit/test_deterministic_validator.py::TestEnhancedDeterministicValidator::test_validate_valid_rips_ac_file

# Con cobertura
pytest --cov=validators --cov=services --cov=api --cov-report=html

# Tests en paralelo (más rápido)
pytest -n auto

# Verbose
pytest -vv -s

# Solo tests que fallaron anteriormente
pytest --lf

# Detener al primer fallo
pytest -x
```

---

## 📊 Fixtures Disponibles

### 🔧 **Fixtures de Cliente**
- `test_client` - Cliente FastAPI (sesión)
- `client` - Cliente FastAPI (por función)

### 📄 **Fixtures de Archivos**
- `valid_rips_ac_content` - Contenido válido RIPS AC
- `invalid_rips_ac_content` - Contenido inválido
- `valid_rips_json` - JSON RIPS completo
- `temp_rips_file` - Archivo temporal RIPS válido
- `temp_invalid_rips_file` - Archivo temporal inválido
- `temp_json_rips_file` - Archivo temporal JSON

### 🔐 **Fixtures de Autenticación**
- `mock_auth_token` - Token simulado
- `auth_headers` - Headers con Bearer token
- `admin_credentials` - {"username": "admin", "password": "admin123"}
- `validator_credentials` - {"username": "validator1", "password": "validator123"}

### 💾 **Fixtures de Base de Datos**
- `mock_db` - Mock de Supabase client
- `override_get_db` - Override automático de dependencia DB

### 📦 **Fixtures de Datos**
- `sample_upload_file` - Archivo para upload
- `sample_file_data` - Metadata de archivo
- `sample_validation_request` - Request de validación
- `sample_error_response` - ErrorResponse de ejemplo
- `sample_validation_results` - Resultados de ejemplo

---

## 📈 Cobertura de Código

### Objetivo de Cobertura
- **Validadores:** > 90%
- **Servicios:** > 85%
- **Endpoints:** > 80%
- **Total:** > 85%

### Generar Reporte
```bash
./run_tests.sh coverage
open htmlcov/index.html
```

---

## 🎨 Ejemplo de Uso

### Ejecutar Suite Completa
```bash
$ ./run_tests.sh

================================
   RIPS Backend Test Suite
================================

🧪 Ejecutando Tests Unitarios...

tests/unit/test_deterministic_validator.py::TestEnhancedDeterministicValidator::test_validate_valid_rips_ac_file PASSED
tests/unit/test_deterministic_validator.py::TestEnhancedDeterministicValidator::test_validate_json_rips_file PASSED
... (16 tests passed)

✅ Tests Unitarios completados exitosamente

🧪 Ejecutando Tests de Integración...

tests/integration/test_api_endpoints.py::TestHealthEndpoints::test_root_endpoint PASSED
tests/integration/test_api_endpoints.py::TestHealthEndpoints::test_health_check_endpoint PASSED
... (25 tests passed)

✅ Tests de Integración completados exitosamente

================================
      RESUMEN DE TESTS
================================

✅ Tests Unitarios: PASSED
✅ Tests de Integración: PASSED

🎉 ¡TODOS LOS TESTS PASARON!
```

---

## 📝 Escribir Nuevos Tests

### Template de Test Unitario
```python
def test_mi_nueva_funcionalidad(self):
    """
    Test: Validar comportamiento X
    Entrada: Datos Y
    Resultado esperado: Z
    """
    # Arrange: preparar datos
    data = {
        "field1": "value1",
        "field2": "value2"
    }
    
    # Act: ejecutar función
    result = mi_funcion(data)
    
    # Assert: verificar resultado
    assert result == expected_value
    assert "field1" in result
```

### Template de Test de Integración
```python
def test_mi_nuevo_endpoint(self, client, override_get_db):
    """
    Test: POST /api/endpoint - Descripción
    """
    # Arrange: configurar mocks
    override_get_db.table.return_value.insert.return_value.execute.return_value.data = [
        {"id": 1}
    ]
    
    request_data = {"key": "value"}
    
    # Act: hacer request
    response = client.post("/api/endpoint", json=request_data)
    
    # Assert: verificar respuesta
    assert response.status_code == 200
    data = response.json()
    assert "key" in data
```

---

## 🐛 Debugging

### Ejecutar con Debugger
```bash
pytest --pdb tests/unit/test_file.py::test_function
```

### Ver Fixtures Disponibles
```bash
pytest --fixtures
```

### Ver Tests sin Ejecutar
```bash
pytest --collect-only
```

### Ejecutar Solo Tests que Coinciden con Nombre
```bash
pytest -k "validate"
```

---

## 📚 Reglas Cubiertas por Tests

### ✅ Reglas Determinísticas (24 reglas)
- **CT:** Tipo registro, fecha generación, número factura
- **US:** Tipo documento, número documento, fecha nacimiento, sexo
- **AC:** Código prestador (12 dígitos), diagnóstico CIE (3-7 chars)
- **AP:** Código CUPS, fecha procedimiento, vía ingreso
- **AM:** Código producto, tipo medicamento
- **AF:** Número factura, tipo factura, CUV
- **AD:** Tipo nota, número nota
- **FMT:** Formato archivo, UTF-8, campos obligatorios, fechas

### ✅ Reglas de IA (7 reglas)
- **AI-CLIN-001:** Diagnóstico vs Sexo
- **AI-CLIN-002:** Diagnóstico vs Edad
- **AI-CLIN-003:** Consistencia clínica
- **AI-PAT-001:** Procedimientos duplicados
- **AI-PAT-002:** Volumen atípico
- **AI-FRAUD-001:** Patrones de fraude
- **AI-FRAUD-002:** Anomalías en facturación

---

## ✨ Mejores Prácticas Implementadas

✅ **AAA Pattern** (Arrange, Act, Assert)
✅ **Tests independientes** (no hay dependencias entre tests)
✅ **Nombres descriptivos** (qué se prueba, entrada, resultado)
✅ **Fixtures reutilizables** (DRY principle)
✅ **Mocks para dependencias** (aislamiento)
✅ **Tests rápidos** (< 30 seg unitarios)
✅ **Cobertura medible** (reportes HTML)
✅ **Documentación completa** (docstrings)

---

## 🎯 Próximos Pasos

1. **Ejecutar tests:**
   ```bash
   ./run_tests.sh coverage
   ```

2. **Revisar cobertura:**
   ```bash
   open htmlcov/index.html
   ```

3. **Integrar con CI/CD:**
   - GitHub Actions
   - GitLab CI
   - Jenkins

4. **Agregar tests adicionales:**
   - Performance testing
   - Security testing
   - E2E testing

---

## 📞 Soporte

- **Documentación:** `tests/README.md`
- **Fixtures:** `pytest --fixtures`
- **Pytest Docs:** https://docs.pytest.org/

---

## 🎉 ¡Listo!

Tu backend ahora tiene **70+ tests automatizados** organizados profesionalmente.

**Ejecuta:**
```bash
./run_tests.sh
```

**¡Y disfruta de tests confiables! 🚀**

