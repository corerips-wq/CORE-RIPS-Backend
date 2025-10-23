# 📚 Documentación de API Endpoints

## Base URL
```
http://localhost:8000/api/v1
```

---

## 🔐 AUTENTICACIÓN

### 1. **POST** `/auth/login`
**Descripción:** Iniciar sesión en el sistema

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access_token": "dGhpc19pc19hX3Rva2Vu...",
  "token_type": "bearer"
}
```

**Usuarios disponibles:**
- `admin` / `admin123` (Administrador)
- `validator1` / `validator123` (Validador)
- `auditor1` / `auditor123` (Auditor)

**Ejemplo curl:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

---

### 2. **GET** `/auth/me`
**Descripción:** Obtener información del usuario actual

**Headers:**
```
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@rips.com",
  "role": "admin",
  "is_active": "true"
}
```

**Ejemplo curl:**
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer dGhpc19pc19hX3Rva2Vu"
```

---

## 📂 GESTIÓN DE ARCHIVOS

### 3. **POST** `/upload` 🆕 ⭐
**Descripción:** Subir archivo RIPS JSON y procesar datos automáticamente

**Qué hace:**
1. ✅ Valida que sea archivo `.json`
2. ✅ Guarda el archivo en disco
3. ✅ Crea registro en tabla `files`
4. ✅ **PROCESA e INSERTA datos RIPS en Supabase**
5. ✅ Mapea campos de español → inglés
6. ✅ Inserta en todas las tablas RIPS correspondientes
7. ✅ Retorna estadísticas de inserción

**Request:**
```
Content-Type: multipart/form-data
file: archivo_rips.json
```

**Response (Éxito):**
```json
{
  "message": "Archivo procesado e insertado exitosamente",
  "file_id": 1,
  "filename": "archivo_completo_prueba.json",
  "status": "validated",
  "data_inserted": {
    "usuarios": 1,
    "consultas": 1,
    "procedimientos": 1,
    "medicamentos": 2,
    "otros_servicios": 0,
    "urgencias": 0,
    "hospitalizaciones": 0,
    "recien_nacidos": 0,
    "facturacion": 0,
    "ajustes": 0,
    "control": 0
  },
  "errores": []
}
```

**Response (Con errores):**
```json
{
  "message": "Archivo subido pero con errores al procesar datos",
  "file_id": 1,
  "filename": "archivo.json",
  "status": "error",
  "error": "Descripción del error..."
}
```

**Ejemplo curl:**
```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "file=@/path/to/archivo_completo_prueba.json"
```

**Ejemplo Python:**
```python
import requests

url = "http://localhost:8000/api/v1/upload"
files = {'file': open('archivo_completo_prueba.json', 'rb')}
response = requests.post(url, files=files)
print(response.json())
```

**Tablas donde se insertan los datos:**
- `rips_users` (Usuarios/Pacientes)
- `rips_consultations` (Consultas médicas)
- `rips_procedures` (Procedimientos)
- `rips_medications` (Medicamentos)
- `rips_other_services` (Otros servicios)
- `rips_emergencies` (Urgencias)
- `rips_hospitalizations` (Hospitalizaciones)
- `rips_newborns` (Recién nacidos)
- `rips_billing` (Facturación)
- `rips_adjustments` (Ajustes/Notas)
- `rips_control` (Control)

---

### 4. **GET** `/files`
**Descripción:** Listar todos los archivos subidos por el usuario

**Response:**
```json
{
  "files": [
    {
      "id": 1,
      "filename": "archivo_completo_prueba.json",
      "original_filename": "archivo_completo_prueba.json",
      "file_path": "uploads/archivo_completo_prueba.json",
      "file_size": 15234,
      "status": "validated",
      "user_id": 1,
      "created_at": "2025-10-23T10:30:00Z",
      "updated_at": "2025-10-23T10:30:15Z"
    }
  ]
}
```

**Estados posibles:**
- `uploaded` - Archivo subido
- `processing` - Procesando datos
- `validated` - Procesado exitosamente
- `error` - Error al procesar

**Ejemplo curl:**
```bash
curl -X GET "http://localhost:8000/api/v1/files"
```

---

## ✅ VALIDACIÓN

### 5. **POST** `/validate`
**Descripción:** Validar archivo RIPS con reglas determinísticas

**Request:**
```json
{
  "file_id": 1,
  "validation_types": ["deterministic"]
}
```

**Response:**
```json
{
  "message": "Validación completada",
  "file_id": 1,
  "status": "validated",
  "errors": 3,
  "warnings": 0,
  "total_validations": 3
}
```

**Tipos de validación disponibles:**
- `deterministic` - Validaciones determinísticas (formato, rangos, catálogos)
- `ai` - Validaciones con IA (coherencia clínica, detección de fraude)

**Ejemplo curl:**
```bash
curl -X POST "http://localhost:8000/api/v1/validate" \
  -H "Content-Type: application/json" \
  -d '{"file_id": 1, "validation_types": ["deterministic"]}'
```

---

### 6. **GET** `/results/{file_id}`
**Descripción:** Obtener resultados de validación de un archivo

**Response:**
```json
{
  "file_id": 1,
  "filename": "archivo_completo_prueba.json",
  "status": "validated",
  "validations": [
    {
      "id": 1,
      "file_id": 1,
      "line_number": 5,
      "field_name": "tipoDocumentoIdentificacion",
      "rule_name": "deterministic_validation",
      "error_message": "Valor inválido. Debe ser uno de: CC, TI, RC, CE",
      "status": "failed",
      "validator_type": "deterministic",
      "created_at": "2025-10-23T10:30:20Z"
    }
  ]
}
```

**Ejemplo curl:**
```bash
curl -X GET "http://localhost:8000/api/v1/results/1"
```

---

## 🏥 ENDPOINTS DE SISTEMA

### 7. **GET** `/` (Root)
**Descripción:** Información básica de la API

**Response:**
```json
{
  "message": "RIPS Validator API - Sistema de validación de archivos RIPS"
}
```

---

### 8. **GET** `/health`
**Descripción:** Health check del servicio

**Response:**
```json
{
  "status": "healthy",
  "service": "rips-validator"
}
```

**Ejemplo curl:**
```bash
curl -X GET "http://localhost:8000/health"
```

---

## 📊 FLUJO COMPLETO DE TRABAJO

### Opción 1: Subir y Procesar Automáticamente (Recomendado)

```bash
# 1. Subir archivo (procesa e inserta automáticamente)
curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "file=@archivo_rips.json"

# Respuesta:
# {
#   "file_id": 1,
#   "status": "validated",
#   "data_inserted": {
#     "usuarios": 1,
#     "consultas": 1,
#     ...
#   }
# }

# 2. Los datos YA están en Supabase!
# Puedes consultarlos directamente:
# SELECT * FROM rips_consultations WHERE file_id = 1;
```

### Opción 2: Subir, Validar y Revisar Resultados

```bash
# 1. Subir archivo
curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "file=@archivo_rips.json"

# 2. Validar (opcional - para reglas adicionales)
curl -X POST "http://localhost:8000/api/v1/validate" \
  -H "Content-Type: application/json" \
  -d '{"file_id": 1, "validation_types": ["deterministic"]}'

# 3. Ver resultados de validación
curl -X GET "http://localhost:8000/api/v1/results/1"

# 4. Listar archivos
curl -X GET "http://localhost:8000/api/v1/files"
```

---

## 🔍 DIFERENCIA CLAVE: `/upload` vs `/validate`

### `/upload` (NUEVO) 🆕
- ✅ Sube el archivo
- ✅ **INSERTA datos en Supabase automáticamente**
- ✅ Mapea campos español → inglés
- ✅ Retorna estadísticas de inserción
- 📊 **Resultado:** Datos guardados en BD

### `/validate`
- ✅ Ejecuta reglas de validación
- ✅ Detecta errores de formato/negocio
- ✅ Guarda errores en tabla `validations`
- ✅ NO inserta datos RIPS
- 📊 **Resultado:** Lista de errores encontrados

---

## 💡 EJEMPLOS PRÁCTICOS

### Ejemplo 1: Subir archivo de TEST

```bash
cd /Users/ub-col-tec-t2q/Documents/ProjectsYP/Yully

# Subir archivo
curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "file=@TEST/archivo_completo_prueba.json"

# Respuesta:
# {
#   "message": "Archivo procesado e insertado exitosamente",
#   "file_id": 1,
#   "data_inserted": {
#     "usuarios": 1,
#     "consultas": 1,
#     "procedimientos": 1,
#     "medicamentos": 2,
#     ...
#   }
# }
```

### Ejemplo 2: Ver datos insertados en Supabase

```sql
-- Ver usuarios insertados
SELECT * FROM rips_users WHERE file_id = 1;

-- Ver consultas
SELECT * FROM rips_consultations WHERE file_id = 1;

-- Resumen por paciente
SELECT 
    u.document_number,
    u.first_name || ' ' || u.first_surname as nombre_completo,
    COUNT(DISTINCT c.id) as total_consultas,
    COUNT(DISTINCT m.id) as total_medicamentos
FROM rips_users u
LEFT JOIN rips_consultations c ON c.identification_number = u.document_number
LEFT JOIN rips_medications m ON m.identification_number = u.document_number
WHERE u.file_id = 1
GROUP BY u.document_number, nombre_completo;
```

### Ejemplo 3: Usar desde Python

```python
import requests
import json

# URL de la API
base_url = "http://localhost:8000/api/v1"

# 1. Login
login_response = requests.post(
    f"{base_url}/auth/login",
    json={"username": "admin", "password": "admin123"}
)
token = login_response.json()["access_token"]

# 2. Subir archivo RIPS
with open("archivo_rips.json", "rb") as f:
    upload_response = requests.post(
        f"{base_url}/upload",
        files={"file": f}
    )

print("Archivo subido:")
print(json.dumps(upload_response.json(), indent=2))

file_id = upload_response.json()["file_id"]
print(f"\nDatos insertados en Supabase con file_id: {file_id}")

# 3. Listar archivos
files_response = requests.get(f"{base_url}/files")
print("\nArchivos:")
print(json.dumps(files_response.json(), indent=2))
```

---

## 🚀 INICIAR EL SERVIDOR

```bash
cd /Users/ub-col-tec-t2q/Documents/ProjectsYP/Yully/CORERIPS/rips_backend

# Opción 1: Uvicorn directamente
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Opción 2: Python
python3 main.py

# La API estará disponible en:
# http://localhost:8000

# Documentación interactiva:
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

---

## 📝 NOTAS IMPORTANTES

### Formato de Archivo Requerido
- ✅ Solo archivos `.json`
- ✅ Estructura RIPS válida
- ✅ Campos en español (camelCase)
- ❌ No se aceptan `.txt`, `.csv`, `.xml`

### Mapeo Automático
Los campos se mapean automáticamente:
- `tipoDocumentoIdentificacion` → `identification_type`
- `codDiagnosticoPrincipal` → `primary_diagnosis`
- `vrServicio` → `consultation_value`
- etc...

Ver documentación completa en: `docs/SCHEMA_MAPPING.md`

### Manejo de Errores

**Error 400:** Archivo inválido
```json
{
  "detail": "Solo se permiten archivos JSON. Por favor suba un archivo .json"
}
```

**Error 404:** Archivo no encontrado
```json
{
  "detail": "Archivo no encontrado"
}
```

**Error 500:** Error interno del servidor
```json
{
  "detail": "Error al subir archivo: ..."
}
```

---

## 📚 DOCUMENTACIÓN RELACIONADA

- `RIPS_DATA_INTEGRATION.md` - Integración completa de datos
- `SCHEMA_MAPPING.md` - Mapeo de campos
- `VALIDATION_RULES.md` - Reglas de validación

---

## ✅ RESUMEN

| Endpoint | Método | Qué Hace | Inserta Datos |
|----------|--------|----------|---------------|
| `/auth/login` | POST | Iniciar sesión | ❌ |
| `/auth/me` | GET | Info del usuario | ❌ |
| **`/upload`** | **POST** | **Subir y procesar RIPS** | **✅ SÍ** |
| `/files` | GET | Listar archivos | ❌ |
| `/validate` | POST | Validar con reglas | ❌ |
| `/results/{id}` | GET | Ver resultados validación | ❌ |

**El endpoint más importante es `/upload` porque:**
1. ✅ Sube el archivo
2. ✅ Mapea campos automáticamente  
3. ✅ **INSERTA los datos en Supabase**
4. ✅ Todo en un solo paso

---

**Última actualización:** Octubre 2025  
**Versión API:** 1.0.0

