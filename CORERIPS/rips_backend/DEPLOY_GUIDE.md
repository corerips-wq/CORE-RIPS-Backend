# 🚀 GUÍA DE DEPLOY: GitHub + Google Cloud

## 📋 TABLA DE CONTENIDOS
1. [Pre-requisitos](#pre-requisitos)
2. [Parte 1: Subir a GitHub](#parte-1-subir-a-github)
3. [Parte 2: Deploy en Google Cloud](#parte-2-deploy-en-google-cloud)
4. [Verificación Post-Deploy](#verificación-post-deploy)
5. [Troubleshooting](#troubleshooting)

---

## PRE-REQUISITOS

### ✅ Verificar antes de empezar:

```bash
# 1. Git instalado
git --version

# 2. Acceso a GitHub
git remote -v
# Debe mostrar: origin https://github.com/tu-usuario/tu-repo.git

# 3. Google Cloud SDK instalado
gcloud --version

# 4. Autenticado en Google Cloud
gcloud auth list

# 5. Variables de entorno configuradas
cat .env
# Debe tener: SUPABASE_URL, SUPABASE_KEY
```

### 📦 Instalar Google Cloud SDK (si no lo tienes):

```bash
# macOS
brew install --cask google-cloud-sdk

# Después de instalar:
gcloud init
gcloud auth login
```

---

## PARTE 1: SUBIR A GITHUB

### Paso 1: Ver qué archivos se van a subir

```bash
cd /Users/ub-col-tec-t2q/Documents/ProjectsYP/Yully/CORERIPS/rips_backend

# Ver estado actual
git status

# Ver diferencias
git diff api/supabase_routes.py
```

### Paso 2: Agregar archivos al staging

```bash
# Archivos CRÍTICOS (obligatorios)
git add api/supabase_routes.py
git add validators/field_mappings.py
git add services/rips_data_service.py

# Documentación (recomendado)
git add docs/API_ENDPOINTS.md
git add docs/SCHEMA_MAPPING.md
git add docs/RIPS_DATA_INTEGRATION.md
git add docs/MIGRATION_PLAN.md
git add docs/SCHEMA_DIFFERENCES.md

# Scripts (opcional)
git add scripts/test_field_mapping.py
git add scripts/test_upload_integration.py

# Guías de deploy
git add DEPLOY_CHECKLIST.md
git add DEPLOY_GUIDE.md
git add DEPLOY_GITHUB_GCLOUD.sh
```

### Paso 3: Hacer commit

```bash
git commit -m "feat: Implementar procesamiento automático de datos RIPS

- Agregar mapeo automático español → inglés
- Implementar servicio de inserción de datos
- Actualizar endpoint /upload
- Agregar documentación completa
- Los datos se insertan automáticamente en Supabase"
```

### Paso 4: Push a GitHub

```bash
git push origin main
```

**Resultado esperado:**
```
Enumerating objects: 25, done.
Counting objects: 100% (25/25), done.
Delta compression using up to 8 threads
Compressing objects: 100% (15/15), done.
Writing objects: 100% (18/18), 45.32 KiB | 7.55 MiB/s, done.
Total 18 (delta 8), reused 0 (delta 0)
To https://github.com/tu-usuario/tu-repo.git
   abc1234..def5678  main -> main
```

✅ **CÓDIGO SUBIDO A GITHUB**

---

## PARTE 2: DEPLOY EN GOOGLE CLOUD

### Opción A: Deploy Automático (Script)

```bash
# Dar permisos al script
chmod +x DEPLOY_GITHUB_GCLOUD.sh

# Ejecutar
./DEPLOY_GITHUB_GCLOUD.sh
```

### Opción B: Deploy Manual (Paso a Paso)

#### Paso 1: Configurar proyecto de Google Cloud

```bash
# Listar proyectos disponibles
gcloud projects list

# Seleccionar proyecto
gcloud config set project TU-PROJECT-ID

# Verificar configuración
gcloud config list
```

#### Paso 2: Habilitar APIs necesarias

```bash
# Habilitar Cloud Run API
gcloud services enable run.googleapis.com

# Habilitar Cloud Build API
gcloud services enable cloudbuild.googleapis.com

# Habilitar Container Registry API
gcloud services enable containerregistry.googleapis.com
```

#### Paso 3: Verificar Dockerfile

```bash
# Ver Dockerfile actual
cat Dockerfile

# Debería existir en: /CORERIPS/rips_backend/Dockerfile
```

Si no existe, créalo:

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Crear directorio para uploads
RUN mkdir -p uploads

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Paso 4: Construir y subir imagen

```bash
# Obtener PROJECT_ID
PROJECT_ID=$(gcloud config get-value project)
echo "PROJECT_ID: $PROJECT_ID"

# Construir imagen con Cloud Build
gcloud builds submit --tag gcr.io/$PROJECT_ID/rips-backend

# Esto tomará 2-5 minutos
```

**Salida esperada:**
```
Creating temporary tarball archive of 45 file(s) totalling 2.5 MiB before compression.
Uploading tarball of [.] to [gs://...]
...
DONE
--------------------------------------------------------------------------------
ID                                    CREATE_TIME                DURATION  STATUS
abc123-def4-5678-9012-3456789abcdef  2025-10-23T10:30:00+00:00  2M45S     SUCCESS

IMAGES
gcr.io/tu-project-id/rips-backend
```

#### Paso 5: Deploy a Cloud Run

```bash
# Deploy con configuración de variables de entorno
gcloud run deploy rips-backend \
  --image gcr.io/$PROJECT_ID/rips-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --timeout 300 \
  --max-instances 10
```

**IMPORTANTE:** El comando te pedirá configurar variables de entorno.

**Mejor manera: Usar archivo .env.yaml**

Crea `env.yaml`:
```yaml
SUPABASE_URL: "https://tu-proyecto.supabase.co"
SUPABASE_KEY: "tu-supabase-anon-key"
SECRET_KEY: "tu-secret-key-segura"
ALGORITHM: "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: "30"
```

Luego deploy:
```bash
gcloud run deploy rips-backend \
  --image gcr.io/$PROJECT_ID/rips-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --env-vars-file env.yaml \
  --memory 512Mi \
  --timeout 300 \
  --max-instances 10
```

**Salida esperada:**
```
Deploying container to Cloud Run service [rips-backend] in project [tu-project] region [us-central1]
✓ Deploying new service... Done.
  ✓ Creating Revision...
  ✓ Routing traffic...
  ✓ Setting IAM Policy...
Done.
Service [rips-backend] revision [rips-backend-00001-xyz] has been deployed and is serving 100 percent of traffic.
Service URL: https://rips-backend-abc123-uc.a.run.app
```

✅ **DEPLOY EN GOOGLE CLOUD COMPLETADO**

---

## VERIFICACIÓN POST-DEPLOY

### 1. Verificar que el servicio esté corriendo

```bash
# Obtener URL del servicio
SERVICE_URL=$(gcloud run services describe rips-backend \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)')

echo "Service URL: $SERVICE_URL"

# Health check
curl $SERVICE_URL/health

# Debería retornar:
# {"status":"healthy","service":"rips-validator"}
```

### 2. Verificar documentación

```bash
# Abrir en navegador
open $SERVICE_URL/docs
# O visita: https://tu-servicio.run.app/docs
```

### 3. Probar endpoint de upload

```bash
# Subir archivo de prueba
curl -X POST "$SERVICE_URL/api/v1/upload" \
  -F "file=@/Users/ub-col-tec-t2q/Documents/ProjectsYP/Yully/TEST/archivo_completo_prueba.json"

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

### 4. Verificar logs

```bash
# Ver logs en tiempo real
gcloud run services logs read rips-backend \
  --region us-central1 \
  --limit 50

# O con tail
gcloud run services logs tail rips-backend --region us-central1
```

### 5. Verificar datos en Supabase

Ir a Supabase Dashboard → SQL Editor:

```sql
-- Ver últimos archivos procesados
SELECT * FROM files ORDER BY created_at DESC LIMIT 5;

-- Ver últimas consultas insertadas
SELECT * FROM rips_consultations ORDER BY created_at DESC LIMIT 5;

-- Ver usuarios insertados
SELECT * FROM rips_users ORDER BY created_at DESC LIMIT 5;
```

---

## CONFIGURACIÓN ADICIONAL

### Configurar dominio personalizado

```bash
# Mapear dominio
gcloud run domain-mappings create \
  --service rips-backend \
  --domain api.tudominio.com \
  --region us-central1
```

### Escalar el servicio

```bash
# Actualizar configuración
gcloud run services update rips-backend \
  --region us-central1 \
  --memory 1Gi \
  --cpu 2 \
  --max-instances 20 \
  --concurrency 80
```

### Ver métricas

```bash
# Abrir en Cloud Console
gcloud run services describe rips-backend \
  --region us-central1 \
  --format 'value(status.url)'

# Ir a: Cloud Console → Cloud Run → rips-backend → Metrics
```

---

## TROUBLESHOOTING

### Error: "gcloud: command not found"

```bash
# Instalar Google Cloud SDK
brew install --cask google-cloud-sdk

# Inicializar
gcloud init
```

### Error: "Permission denied"

```bash
# Autenticarse
gcloud auth login

# Configurar proyecto
gcloud config set project TU-PROJECT-ID
```

### Error: "Image not found"

```bash
# Verificar que la imagen se construyó correctamente
gcloud container images list --repository=gcr.io/$PROJECT_ID

# Reconstruir
gcloud builds submit --tag gcr.io/$PROJECT_ID/rips-backend
```

### Error: "Service deployment failed"

```bash
# Ver logs de deploy
gcloud builds log $(gcloud builds list --limit=1 --format='value(id)')

# Ver logs del servicio
gcloud run services logs read rips-backend --region us-central1 --limit 100
```

### Error: "ModuleNotFoundError" en producción

```bash
# Verificar requirements.txt
cat requirements.txt

# Asegurarse de que todas las dependencias estén listadas
pip freeze > requirements.txt

# Hacer nuevo deploy
gcloud builds submit --tag gcr.io/$PROJECT_ID/rips-backend
gcloud run deploy rips-backend --image gcr.io/$PROJECT_ID/rips-backend ...
```

### Error: Datos no se insertan en Supabase

```bash
# Verificar variables de entorno
gcloud run services describe rips-backend \
  --region us-central1 \
  --format 'value(spec.template.spec.containers[0].env)'

# Actualizar variables
gcloud run services update rips-backend \
  --region us-central1 \
  --update-env-vars SUPABASE_URL=https://...,SUPABASE_KEY=...
```

---

## COMANDOS ÚTILES

### Ver estado del servicio

```bash
gcloud run services describe rips-backend --region us-central1
```

### Actualizar servicio con nueva imagen

```bash
# Reconstruir
gcloud builds submit --tag gcr.io/$PROJECT_ID/rips-backend

# Redesplegar (usa la imagen más reciente automáticamente)
gcloud run deploy rips-backend \
  --image gcr.io/$PROJECT_ID/rips-backend:latest \
  --region us-central1
```

### Eliminar servicio

```bash
gcloud run services delete rips-backend --region us-central1
```

### Ver costos

```bash
# Ver en Cloud Console
# https://console.cloud.google.com/billing
```

---

## RESUMEN DE COMANDOS RÁPIDOS

```bash
# ============== GITHUB ==============
cd /Users/ub-col-tec-t2q/Documents/ProjectsYP/Yully/CORERIPS/rips_backend
git add api/supabase_routes.py validators/field_mappings.py services/rips_data_service.py
git commit -m "feat: Procesamiento automático RIPS"
git push origin main

# ========== GOOGLE CLOUD ============
PROJECT_ID=$(gcloud config get-value project)
gcloud builds submit --tag gcr.io/$PROJECT_ID/rips-backend
gcloud run deploy rips-backend \
  --image gcr.io/$PROJECT_ID/rips-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi

# =========== VERIFICAR ==============
SERVICE_URL=$(gcloud run services describe rips-backend --platform managed --region us-central1 --format 'value(status.url)')
curl $SERVICE_URL/health
open $SERVICE_URL/docs
```

---

## ✅ CHECKLIST FINAL

- [ ] Código subido a GitHub
- [ ] Imagen construida en Google Cloud
- [ ] Servicio desplegado en Cloud Run
- [ ] Health check funciona
- [ ] Endpoint /upload funciona
- [ ] Datos se insertan en Supabase
- [ ] Variables de entorno configuradas
- [ ] URL del servicio guardada

---

**Última actualización:** Octubre 2025

