# Guía de Despliegue a Google Cloud Run

Esta guía te ayudará a desplegar el backend de RIPS Validator en Google Cloud Run.

## Prerrequisitos

1. **Cuenta de Google Cloud Platform (GCP)**
   - Crear una cuenta en https://cloud.google.com/
   - Crear un proyecto nuevo o usar uno existente
   - Habilitar facturación

2. **Google Cloud CLI instalado**
   ```bash
   # Instalar gcloud CLI (macOS)
   brew install --cask google-cloud-sdk
   
   # O descargar desde:
   # https://cloud.google.com/sdk/docs/install
   ```

3. **Docker instalado**
   ```bash
   # Verificar instalación de Docker
   docker --version
   ```

## Pasos para el Despliegue

### 1. Autenticación y Configuración Inicial

```bash
# Autenticarse en Google Cloud
gcloud auth login

# Configurar el proyecto (reemplazar PROJECT_ID con tu ID de proyecto)
gcloud config set project PROJECT_ID

# Habilitar los servicios necesarios
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 2. Configurar Variables de Entorno

Antes de desplegar, necesitas configurar las variables de entorno en Cloud Run:

```bash
# Variables requeridas (ajustar con tus valores reales)
SUPABASE_URL="https://tu-proyecto.supabase.co"
SUPABASE_KEY="tu-supabase-key"
DATABASE_URL="tu-database-url-de-supabase"
SECRET_KEY="tu-secret-key-para-jwt"
ENVIRONMENT="production"
```

### 3. Construir y Desplegar

**Opción A: Despliegue Directo desde el Código Fuente**

```bash
# Ir al directorio del backend
cd /Users/ub-col-tec-t2q/Documents/ProjectsYP/Yully/CORERIPS/rips_backend

# Desplegar a Cloud Run (reemplazar PROJECT_ID y REGION)
gcloud run deploy rips-validator-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ENVIRONMENT=production,SECRET_KEY=tu-secret-key \
  --set-env-vars SUPABASE_URL=tu-supabase-url \
  --set-env-vars SUPABASE_KEY=tu-supabase-key \
  --set-env-vars DATABASE_URL=tu-database-url \
  --max-instances 10 \
  --memory 512Mi \
  --timeout 300
```

**Opción B: Construir Imagen Docker Primero**

```bash
# 1. Construir la imagen Docker localmente
docker build -t rips-validator-api .

# 2. Probar localmente (opcional)
docker run -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e SUPABASE_URL=tu-supabase-url \
  -e SUPABASE_KEY=tu-supabase-key \
  -e DATABASE_URL=tu-database-url \
  -e SECRET_KEY=tu-secret-key \
  rips-validator-api

# 3. Configurar Docker para usar Google Container Registry
gcloud auth configure-docker

# 4. Etiquetar la imagen
docker tag rips-validator-api gcr.io/PROJECT_ID/rips-validator-api

# 5. Subir la imagen a GCR
docker push gcr.io/PROJECT_ID/rips-validator-api

# 6. Desplegar desde la imagen
gcloud run deploy rips-validator-api \
  --image gcr.io/PROJECT_ID/rips-validator-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ENVIRONMENT=production,SECRET_KEY=tu-secret-key \
  --set-env-vars SUPABASE_URL=tu-supabase-url \
  --set-env-vars SUPABASE_KEY=tu-supabase-key \
  --set-env-vars DATABASE_URL=tu-database-url \
  --max-instances 10 \
  --memory 512Mi \
  --timeout 300
```

### 4. Configurar Variables de Entorno (Método Alternativo)

Si prefieres no pasar las variables en el comando, puedes crear un archivo `.env.yaml`:

```yaml
ENVIRONMENT: "production"
SECRET_KEY: "tu-secret-key"
ALGORITHM: "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: "30"
SUPABASE_URL: "tu-supabase-url"
SUPABASE_KEY: "tu-supabase-key"
DATABASE_URL: "tu-database-url"
```

Luego desplegar con:
```bash
gcloud run deploy rips-validator-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --env-vars-file .env.yaml
```

### 5. Verificar el Despliegue

Una vez completado el despliegue, obtendrás una URL como:
```
https://rips-validator-api-xxxxxxxxxx-uc.a.run.app
```

Probar los endpoints:
```bash
# Health check
curl https://tu-url.run.app/health

# Endpoint principal
curl https://tu-url.run.app/
```

## Configuración de CORS

El código actual permite CORS desde cualquier origen (`allow_origins=["*"]`). Para producción, actualiza `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://tu-dominio-frontend.com",
        "https://www.tu-dominio-frontend.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Comandos Útiles

```bash
# Ver logs de la aplicación
gcloud run services logs read rips-validator-api --limit 50

# Ver logs en tiempo real
gcloud run services logs tail rips-validator-api

# Listar servicios desplegados
gcloud run services list

# Obtener detalles del servicio
gcloud run services describe rips-validator-api

# Actualizar variables de entorno sin redesplegar
gcloud run services update rips-validator-api \
  --update-env-vars NEW_VAR=new_value

# Eliminar el servicio
gcloud run services delete rips-validator-api
```

## Consideraciones de Seguridad

1. **Variables de Entorno**: Nunca incluyas las variables de entorno en el código o repositorio
2. **CORS**: Limita los orígenes permitidos en producción
3. **Autenticación**: Considera agregar autenticación si el servicio no es público
4. **Cloud Secret Manager**: Para información sensible, usa:
   ```bash
   gcloud run services update rips-validator-api \
     --update-secrets DATABASE_URL=database-url:latest
   ```

## Costos Estimados

Cloud Run cobra por:
- Tiempo de CPU usado
- Memoria consumida
- Solicitudes

Con el plan gratuito incluye:
- 2 millones de solicitudes/mes
- 360,000 GB-seconds/mes
- 180,000 vCPU-seconds/mes

## Monitoreo

Acceder al monitoreo en:
https://console.cloud.google.com/run

## Troubleshooting

### Error de conexión a Supabase
- Verificar que las variables `SUPABASE_URL` y `SUPABASE_KEY` sean correctas
- Verificar que Supabase permita conexiones desde Google Cloud

### Error de timeout
- Aumentar el timeout: `--timeout 600`

### Error de memoria
- Aumentar memoria: `--memory 1Gi`

### Ver logs detallados
```bash
gcloud run services logs read rips-validator-api --limit 100 --format json
```

## Siguiente Paso: CI/CD

Para automatizar despliegues, considera configurar Cloud Build con GitHub/GitLab:

1. Crear `cloudbuild.yaml`
2. Conectar repositorio a Cloud Build
3. Configurar triggers automáticos

## Soporte

- Documentación oficial: https://cloud.google.com/run/docs
- Pricing: https://cloud.google.com/run/pricing

