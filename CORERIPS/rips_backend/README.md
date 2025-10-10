# RIPS Validator API

Sistema de validación de archivos RIPS (Registros Individuales de Prestación de Servicios de Salud) desarrollado con FastAPI.

## Características

- ✅ **Validaciones Determinísticas**: Reglas de negocio basadas en normatividad RIPS
- 🤖 **Validaciones IA**: Módulo preparado para validaciones con inteligencia artificial
- 🔐 **Autenticación JWT**: Sistema de autenticación con roles (admin, validator, auditor)
- 📊 **Base de Datos**: PostgreSQL con SQLAlchemy y migraciones Alembic
- 🧪 **Testing**: Pruebas unitarias con pytest
- 📁 **Gestión de Archivos**: Subida y gestión de archivos RIPS

## Estructura del Proyecto

```
rips_backend/
├── api/                    # Controladores (endpoints)
├── services/              # Lógica de negocio
├── validators/            # Reglas de validación
├── models/               # Modelos Pydantic y SQLAlchemy
├── db/                   # Conexión y configuración de BD
├── tests/                # Pruebas unitarias
├── alembic/              # Migraciones de base de datos
├── uploads/              # Archivos subidos (se crea automáticamente)
├── main.py               # Punto de entrada de la aplicación
└── requirements.txt      # Dependencias
```

## Instalación

1. **Clonar el repositorio y navegar al directorio**
   ```bash
   cd rips_backend
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Editar .env con tus configuraciones
   ```

5. **Configurar PostgreSQL**
   - Crear base de datos: `rips_db`
   - Actualizar `DATABASE_URL` en `.env`

6. **Ejecutar migraciones**
   ```bash
   alembic upgrade head
   ```

## Uso

### Iniciar el servidor
```bash
python main.py
```

La API estará disponible en: `http://localhost:8000`

### Documentación interactiva
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Endpoints principales

#### Autenticación
- `POST /api/v1/auth/register` - Registrar usuario
- `POST /api/v1/auth/login` - Iniciar sesión
- `GET /api/v1/auth/me` - Información del usuario actual

#### Gestión de archivos
- `POST /api/v1/upload` - Subir archivo RIPS
- `GET /api/v1/files` - Listar archivos del usuario
- `DELETE /api/v1/files/{id}` - Eliminar archivo

#### Validación
- `POST /api/v1/validate` - Validar archivo RIPS
- `GET /api/v1/results/{id}` - Obtener resultados de validación

#### Administración (solo admin)
- `GET /api/v1/admin/users` - Listar todos los usuarios
- `GET /api/v1/admin/files` - Listar todos los archivos

## Validaciones Implementadas

**Total de reglas implementadas: 41** (basadas en análisis de archivos Excel normativos)

### Validaciones Determinísticas (33 reglas)
- ✅ **Estructura de archivos**: Validación de campos obligatorios y cardinalidad
- ✅ **Códigos de prestador**: 12 dígitos numéricos obligatorios
- ✅ **Tipos de documento**: CC, TI, RC, CE, PA, NUIP, MS (catálogo DIAN/MinSalud)
- ✅ **Fechas**: Formato YYYY-MM-DD, validación de lógica temporal
- ✅ **Códigos CUPS**: Validación contra catálogo oficial MinSalud
- ✅ **Códigos CIE-10/CIE-11**: Validación de existencia y vigencia
- ✅ **Campos numéricos**: Validación de tipo y longitud
- ✅ **Catálogos oficiales**: DANE, DIAN, MinSalud, SISPRO
- ✅ **Reglas de negocio**: Campos condicionales y dependencias

### Validaciones de Inteligencia Artificial (8 reglas)
- 🤖 **Coherencia clínica**: 
  - Diagnóstico incompatible con sexo (ej: embarazo en hombres)
  - Diagnóstico incompatible con edad (ej: enfermedades pediátricas en adultos)
- 🤖 **Detección de patrones atípicos**:
  - Procedimientos duplicados en períodos cortos
  - Volúmenes anómalos de servicios por prestador
- 🤖 **Detección de fraude**:
  - Servicios costosos sin soporte clínico
  - Patrones de facturación sospechosos
  - Análisis de variabilidad en procedimientos

### Archivos RIPS Soportados
- **CT**: Control (información del lote)
- **US**: Usuarios (datos demográficos)
- **AC**: Consultas médicas
- **AP**: Procedimientos
- **AM**: Medicamentos
- **AF**: Facturación
- **AD**: Ajustes/Notas (crédito/débito)

## Testing

Ejecutar todas las pruebas:
```bash
pytest
```

Ejecutar con cobertura:
```bash
pytest --cov=. --cov-report=html
```

Ejecutar pruebas específicas:
```bash
pytest tests/test_deterministic_validator.py
pytest tests/test_api.py
```

## Documentación Adicional

- 📋 **[Reglas de Validación](docs/VALIDATION_RULES.md)**: Documentación completa de todas las reglas implementadas
- 🗄️ **[Configuración Supabase](docs/SUPABASE_SETUP.md)**: Guía para configurar la base de datos
- 📊 **Análisis de reglas**: Basado en 5 archivos Excel normativos oficiales

## Normatividad Implementada

- **Resolución 2275 de 2023**: Anexo Técnico estructura RIPS/FEV
- **Resolución 1884 de 2024**: Modificaciones y reglas transitorias  
- **Catálogos oficiales**: CUPS, CIE-10/CIE-11, DANE
- **Lineamientos MinSalud**: Generación, validación y envío RIPS-FEV

## Roles de Usuario

- **admin**: Acceso completo al sistema
- **validator**: Puede subir y validar archivos
- **auditor**: Solo lectura de resultados

## Desarrollo

### Agregar nuevas validaciones
1. Editar `validators/deterministic.py`
2. Agregar pruebas en `tests/test_deterministic_validator.py`
3. Ejecutar pruebas: `pytest`

### Crear nueva migración
```bash
alembic revision --autogenerate -m "Descripción del cambio"
alembic upgrade head
```

### Variables de entorno requeridas
```
DATABASE_URL=postgresql://username:password@localhost:5432/rips_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Contribuir

1. Fork del proyecto
2. Crear rama feature (`git checkout -b feature/nueva-validacion`)
3. Commit cambios (`git commit -am 'Agregar nueva validación'`)
4. Push a la rama (`git push origin feature/nueva-validacion`)
5. Crear Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT.
