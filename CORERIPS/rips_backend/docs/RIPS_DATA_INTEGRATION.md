# Integración Completa de Datos RIPS

## 📋 Resumen

Se ha implementado la funcionalidad completa para:
1. ✅ **Subir archivos JSON RIPS**
2. ✅ **Mapear campos** de español (JSON) a inglés (Base de Datos)
3. ✅ **Insertar datos** automáticamente en Supabase
4. ✅ **Verificar** que los datos se guardan correctamente

---

## 🎯 ¿Qué problema resuelve?

**ANTES:** 
- Los archivos JSON vienen con campos en español (`tipoDocumentoIdentificacion`, `codDiagnosticoPrincipal`)
- La base de datos tiene columnas en inglés (`identification_type`, `primary_diagnosis`)
- ❌ No había forma de insertar los datos automáticamente

**AHORA:**
- ✅ El sistema mapea automáticamente español → inglés
- ✅ Los datos se insertan en las tablas correctas
- ✅ Todo funciona con un solo endpoint `/upload`

---

## 📂 Archivos Creados

### 1. `validators/field_mappings.py`
**Qué hace:** Mapeo completo de campos JSON (español) → Base de Datos (inglés)

**Incluye:**
- Mapeos para 11 tipos de archivos RIPS (US, AC, AP, AM, AT, AU, AH, AN, AF, AD, CT)
- Funciones de utilidad para conversión automática
- ~400 líneas de código

**Ejemplo de uso:**
```python
from validators.field_mappings import map_json_to_db, get_table_name

# Datos del JSON en español
consulta_json = {
    "codPrestador": "080010395301",
    "tipoDocumentoIdentificacion": "CC",
    "codDiagnosticoPrincipal": "A09"
}

# Convertir a formato de BD (inglés)
consulta_db = map_json_to_db(consulta_json, "AC")
# Resultado: {
#     "provider_code": "080010395301",
#     "identification_type": "CC",
#     "primary_diagnosis": "A09"
# }

# Obtener nombre de tabla
table_name = get_table_name("AC")  # "rips_consultations"
```

---

### 2. `services/rips_data_service.py`
**Qué hace:** Servicio completo para procesar e insertar datos RIPS en Supabase

**Funcionalidades:**
- ✅ Lee archivos JSON RIPS
- ✅ Mapea campos automáticamente
- ✅ Inserta datos en las tablas correctas
- ✅ Maneja errores y estadísticas
- ✅ Soporta todos los tipos de RIPS

**Ejemplo de uso:**
```python
from services.rips_data_service import RIPSDataService
from db.supabase_client import get_supabase_client

supabase = get_supabase_client()
service = RIPSDataService(supabase)

# Procesar archivo
stats = service.process_rips_file("archivo.json", file_id=1)

# Resultado:
# {
#     "usuarios": 1,
#     "consultas": 1,
#     "procedimientos": 1,
#     "medicamentos": 2,
#     "errores": []
# }
```

---

### 3. `api/supabase_routes.py` (ACTUALIZADO)
**Qué hace:** Endpoint `/upload` mejorado que ahora procesa e inserta datos automáticamente

**ANTES:**
```python
POST /upload
→ Guarda archivo en disco
→ Crea registro en tabla 'files'
→ ❌ NO inserta datos RIPS
```

**AHORA:**
```python
POST /upload
→ Guarda archivo en disco
→ Crea registro en tabla 'files'
→ ✅ Mapea campos español → inglés
→ ✅ Inserta datos en tablas RIPS
→ ✅ Retorna estadísticas de inserción
```

**Respuesta del endpoint:**
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

---

### 4. Scripts de Prueba

#### `scripts/test_field_mapping.py`
Prueba el mapeo de campos usando archivos reales de TEST

```bash
cd /Users/ub-col-tec-t2q/Documents/ProjectsYP/Yully/CORERIPS/rips_backend
python3 scripts/test_field_mapping.py
```

#### `scripts/test_upload_integration.py`
Prueba completa de integración (requiere Supabase configurado)

```bash
python3 scripts/test_upload_integration.py
```

---

## 🚀 Cómo Usar

### Opción 1: Usar el API Endpoint (Recomendado)

```bash
# 1. Iniciar servidor
cd CORERIPS/rips_backend
uvicorn main:app --reload

# 2. Subir archivo RIPS
curl -X POST "http://localhost:8000/upload" \
  -F "file=@/path/to/archivo_rips.json"
```

**Respuesta:**
```json
{
  "message": "Archivo procesado e insertado exitosamente",
  "file_id": 1,
  "data_inserted": {
    "usuarios": 1,
    "consultas": 1,
    ...
  }
}
```

### Opción 2: Usar Programáticamente

```python
from services.rips_data_service import RIPSDataService
from db.supabase_client import get_supabase_client

# Conectar a Supabase
supabase = get_supabase_client()

# Crear servicio
service = RIPSDataService(supabase)

# Procesar archivo
stats = service.process_rips_file(
    file_path="/path/to/archivo.json",
    file_id=1
)

print(f"Usuarios insertados: {stats['usuarios']}")
print(f"Consultas insertadas: {stats['consultas']}")
```

---

## 📊 Tablas Soportadas

El sistema inserta datos en las siguientes tablas de Supabase:

| Código | Tabla                   | Descripción                |
|--------|-------------------------|----------------------------|
| US     | rips_users              | Usuarios/Pacientes         |
| AC     | rips_consultations      | Consultas médicas          |
| AP     | rips_procedures         | Procedimientos             |
| AM     | rips_medications        | Medicamentos               |
| AT     | rips_other_services     | Otros servicios            |
| AU     | rips_emergencies        | Urgencias                  |
| AH     | rips_hospitalizations   | Hospitalizaciones          |
| AN     | rips_newborns           | Recién nacidos             |
| AF     | rips_billing            | Facturación                |
| AD     | rips_adjustments        | Ajustes/Notas              |
| CT     | rips_control            | Control                    |

---

## 🔍 Verificar Datos en Supabase

### Ver datos insertados:

```sql
-- Ver archivos procesados
SELECT * FROM files WHERE status = 'validated';

-- Ver usuarios insertados
SELECT * FROM rips_users WHERE file_id = 1;

-- Ver consultas insertadas
SELECT * FROM rips_consultations WHERE file_id = 1;

-- Resumen por paciente
SELECT 
    u.document_number,
    u.first_name,
    u.first_surname,
    COUNT(DISTINCT c.id) as total_consultas,
    COUNT(DISTINCT p.id) as total_procedimientos
FROM rips_users u
LEFT JOIN rips_consultations c ON c.identification_number = u.document_number
LEFT JOIN rips_procedures p ON p.identification_number = u.document_number
WHERE u.file_id = 1
GROUP BY u.document_number, u.first_name, u.first_surname;
```

---

## ✅ Validación del Mapeo

Se probó con el archivo real `/TEST/archivo_completo_prueba.json` y se verificó:

✅ **Campos mapeados correctamente:**
- `tipoDocumentoIdentificacion` → `identification_type`
- `numDocumentoIdentificacion` → `identification_number`
- `codDiagnosticoPrincipal` → `primary_diagnosis`
- `vrServicio` → `consultation_value`
- Y más de 100 campos adicionales...

✅ **Inserción exitosa:**
- Usuarios: ✅
- Consultas: ✅
- Procedimientos: ✅
- Medicamentos: ✅

---

## 🔐 Configuración Requerida

### Variables de Entorno (`.env`):

```bash
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-api-key
```

### Base de Datos:

Asegúrate de que las tablas RIPS estén creadas en Supabase ejecutando:

```bash
# Ejecutar en Supabase SQL Editor
cat create_tables_supabase.sql | pbcopy
# Pegar y ejecutar en Supabase Dashboard → SQL Editor
```

---

## 📖 Documentación Relacionada

- `SCHEMA_MAPPING.md` - Mapeo completo de tablas y columnas
- `MIGRATION_PLAN.md` - Plan de migración (si fuera necesario)
- `SCHEMA_DIFFERENCES.md` - Análisis de diferencias
- `SUPABASE_SETUP.md` - Configuración de Supabase

---

## 🐛 Solución de Problemas

### Error: "Column 'codigo_prestador' does not exist"

**Causa:** El código está intentando usar nombres en español que no existen en la BD

**Solución:** Asegúrate de que estás usando el mapeo:
```python
from validators.field_mappings import map_json_to_db
data_mapped = map_json_to_db(data_json, "AC")
```

### Error: "Table 'rips_consultations' does not exist"

**Causa:** Las tablas RIPS no están creadas en Supabase

**Solución:** Ejecuta `create_tables_supabase.sql` en Supabase Dashboard

### Datos no se insertan

**Solución:**
1. Verifica logs: `logger.info` mostrará qué está pasando
2. Revisa que el archivo sea JSON válido
3. Verifica conexión a Supabase: `.env` configurado correctamente

---

## 🎉 Resultado Final

### ✅ Ahora puedes:

1. **Subir archivos RIPS JSON** → Endpoint `/upload`
2. **Ver datos insertados** → Tablas en Supabase
3. **Consultar información** → SQL o API
4. **Validar campos** → Mapeo automático

### ✅ Los campos se mapean automáticamente:

| JSON (Español)                | Base de Datos (Inglés)    |
|-------------------------------|---------------------------|
| `tipoDocumentoIdentificacion` | `identification_type`     |
| `numDocumentoIdentificacion`  | `identification_number`   |
| `codDiagnosticoPrincipal`     | `primary_diagnosis`       |
| `vrServicio`                  | `consultation_value`      |
| `fechaInicioAtencion`         | `consultation_date`       |

### ✅ ¡Todo funciona! 🚀

---

## 📞 Soporte

Si tienes problemas o preguntas:
1. Revisa los logs del servidor
2. Ejecuta los scripts de prueba
3. Consulta la documentación en `/docs`

---

**Última actualización:** Octubre 2025  
**Estado:** ✅ Implementado y probado

