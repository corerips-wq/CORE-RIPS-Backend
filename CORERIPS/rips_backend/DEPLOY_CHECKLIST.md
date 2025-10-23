# 🚀 CHECKLIST PARA DEPLOY

## ✅ ARCHIVOS MODIFICADOS/CREADOS

### 🔴 CRÍTICOS (Necesarios para que funcione)

```bash
# Estos 3 archivos SON NECESARIOS:
api/supabase_routes.py              # Endpoint /upload actualizado
validators/field_mappings.py        # Mapeo español → inglés (NUEVO)
services/rips_data_service.py       # Servicio de procesamiento (NUEVO)
```

### 🟡 DOCUMENTACIÓN (Recomendados)

```bash
docs/API_ENDPOINTS.md               # Documentación de endpoints
docs/SCHEMA_MAPPING.md              # Mapeo de tablas
docs/RIPS_DATA_INTEGRATION.md       # Guía de integración
```

### 🟢 OPCIONALES

```bash
scripts/test_field_mapping.py       # Script de prueba
scripts/test_upload_integration.py  # Script de prueba completa
```

---

## 📝 COMANDOS PARA EJECUTAR

### Paso 1: Agregar archivos al repositorio

```bash
cd /Users/ub-col-tec-t2q/Documents/ProjectsYP/Yully/CORERIPS/rips_backend

# Agregar archivos críticos
git add api/supabase_routes.py
git add validators/field_mappings.py
git add services/rips_data_service.py

# Agregar documentación
git add docs/API_ENDPOINTS.md
git add docs/SCHEMA_MAPPING.md
git add docs/RIPS_DATA_INTEGRATION.md
git add docs/MIGRATION_PLAN.md
git add docs/SCHEMA_DIFFERENCES.md

# Agregar scripts de prueba (opcional)
git add scripts/test_field_mapping.py
git add scripts/test_upload_integration.py
```

### Paso 2: Hacer commit

```bash
git commit -m "feat: Implementar procesamiento e inserción automática de datos RIPS

- Agregar mapeo automático de campos español → inglés
- Implementar servicio de procesamiento de datos RIPS
- Actualizar endpoint /upload para insertar datos automáticamente
- Agregar documentación completa de API y mapeo de esquemas
- Agregar scripts de prueba de integración

Los datos RIPS ahora se insertan automáticamente en Supabase
cuando se sube un archivo JSON."
```

### Paso 3: Push al repositorio

```bash
git push origin main
```

---

## 🌐 DEPLOY AL SERVIDOR

### Opción A: Servidor con acceso SSH

```bash
# 1. Conectar al servidor
ssh usuario@tu-servidor.com

# 2. Ir al directorio del proyecto
cd /path/to/rips_backend

# 3. Pull de los cambios
git pull origin main

# 4. Reiniciar el servicio
sudo systemctl restart rips-api
# O si usas PM2:
pm2 restart rips-api
```

### Opción B: Plataforma Cloud (Heroku, Railway, etc)

```bash
# El deploy se hace automáticamente con el push
git push origin main
```

### Opción C: Docker

```bash
# 1. Construir imagen
docker build -t rips-backend .

# 2. Detener contenedor anterior
docker stop rips-backend-container

# 3. Iniciar nuevo contenedor
docker run -d --name rips-backend-container \
  -p 8000:8000 \
  --env-file .env \
  rips-backend
```

### Opción D: Google Cloud Run

```bash
# 1. Construir y subir imagen
gcloud builds submit --tag gcr.io/PROJECT_ID/rips-backend

# 2. Deploy
gcloud run deploy rips-backend \
  --image gcr.io/PROJECT_ID/rips-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## ✅ VERIFICACIÓN POST-DEPLOY

### 1. Verificar que el servidor esté corriendo

```bash
# Health check
curl https://tu-servidor.com/health

# Respuesta esperada:
# {"status": "healthy", "service": "rips-validator"}
```

### 2. Probar el endpoint de upload

```bash
# Subir archivo de prueba
curl -X POST "https://tu-servidor.com/api/v1/upload" \
  -F "file=@TEST/archivo_completo_prueba.json"

# Respuesta esperada:
# {
#   "message": "Archivo procesado e insertado exitosamente",
#   "file_id": 1,
#   "data_inserted": {
#     "usuarios": 1,
#     "consultas": 1,
#     ...
#   }
# }
```

### 3. Verificar datos en Supabase

```sql
-- Conectar a Supabase Dashboard → SQL Editor

-- Ver datos insertados
SELECT * FROM rips_consultations ORDER BY created_at DESC LIMIT 5;
SELECT * FROM rips_users ORDER BY created_at DESC LIMIT 5;

-- Verificar último file_id procesado
SELECT * FROM files ORDER BY created_at DESC LIMIT 1;
```

---

## 🔧 CONFIGURACIÓN REQUERIDA

### Variables de Entorno (.env)

Asegúrate de que estén configuradas en el servidor:

```bash
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-supabase-api-key
SECRET_KEY=tu-secret-key-para-jwt
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## ⚠️ COSAS IMPORTANTES

### 1. Dependencias Python

Si agregaste nuevas dependencias, actualiza `requirements.txt`:

```bash
# En el servidor después del deploy:
pip install -r requirements.txt
```

### 2. Base de Datos

✅ **NO necesitas** ejecutar migraciones porque:
- Las tablas ya existen en Supabase
- Solo estamos insertando datos, no modificando el esquema

### 3. Permisos de Archivos

Asegúrate de que el directorio `uploads/` tenga permisos de escritura:

```bash
mkdir -p uploads
chmod 755 uploads
```

---

## 🐛 TROUBLESHOOTING

### Error: "ModuleNotFoundError: No module named 'validators.field_mappings'"

**Solución:**
```bash
# Verificar que el archivo exista
ls validators/field_mappings.py

# Reinstalar dependencias
pip install -r requirements.txt
```

### Error: "Column 'codigo_prestador' does not exist"

**Causa:** El código antiguo no está usando el mapeo

**Solución:** Asegúrate de que `api/supabase_routes.py` esté actualizado con la versión nueva

### Error al subir archivo: "Error procesando datos RIPS"

**Solución:**
1. Ver logs del servidor: `tail -f /var/log/rips-backend.log`
2. Verificar que Supabase esté configurado correctamente
3. Verificar que el archivo JSON sea válido

---

## 📊 RESUMEN

### Antes del Deploy:
- [ ] Agregar archivos a git
- [ ] Hacer commit
- [ ] Push al repositorio

### Durante el Deploy:
- [ ] Pull en el servidor
- [ ] Reinstalar dependencias (si es necesario)
- [ ] Reiniciar servicio

### Después del Deploy:
- [ ] Verificar health check
- [ ] Probar endpoint /upload
- [ ] Verificar datos en Supabase

---

## 🎉 ¡LISTO!

Una vez completados todos los pasos, tu sistema estará:

✅ Subiendo archivos RIPS JSON
✅ Mapeando campos automáticamente
✅ Insertando datos en Supabase
✅ Retornando estadísticas de inserción

---

**Última actualización:** Octubre 2025

