# Configuración de Supabase para RIPS Validator

Esta guía te ayudará a configurar Supabase como base de datos para el sistema RIPS Validator.

## 1. Crear Proyecto en Supabase

1. Ve a [supabase.com](https://supabase.com) y crea una cuenta
2. Crea un nuevo proyecto
3. Espera a que el proyecto se inicialice (puede tomar unos minutos)

## 2. Obtener Credenciales

Una vez creado el proyecto, ve a **Settings > Database** y encontrarás:

### Connection String
```
postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
```

### API Settings (Settings > API)
- **Project URL**: `https://[YOUR-PROJECT-REF].supabase.co`
- **Anon Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
- **Service Role Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

## 3. Configurar Variables de Entorno

Edita el archivo `.env` con tus credenciales:

```env
# Configuración de Supabase
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# JWT Configuration
SECRET_KEY=tu-clave-secreta-muy-segura-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development
```

## 4. Inicializar Base de Datos

Ejecuta el script de inicialización:

```bash
python scripts/init_db.py
```

Este script:
- ✅ Prueba la conexión a Supabase
- ✅ Crea las tablas necesarias
- ✅ Crea usuarios de prueba

## 5. Verificar Conexión

Puedes verificar que todo funciona correctamente:

```bash
python -c "from db.database import test_connection; print('✅ OK' if test_connection() else '❌ Error')"
```

## 6. Ejecutar Migraciones (Opcional)

Si necesitas usar Alembic para migraciones:

```bash
# Inicializar Alembic (solo la primera vez)
alembic init alembic

# Crear migración
alembic revision --autogenerate -m "Initial migration"

# Aplicar migración
alembic upgrade head
```

## 7. Configuración de Seguridad en Supabase

### Row Level Security (RLS)

Para mayor seguridad, puedes habilitar RLS en Supabase:

1. Ve a **Authentication > Policies**
2. Habilita RLS para las tablas `users`, `files`, `validations`
3. Crea políticas según tus necesidades

### Ejemplo de política para tabla `files`:
```sql
-- Solo el propietario puede ver sus archivos
CREATE POLICY "Users can view own files" ON files
FOR SELECT USING (auth.uid()::text = user_id::text);

-- Solo el propietario puede insertar archivos
CREATE POLICY "Users can insert own files" ON files
FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);
```

## 8. Monitoreo

Puedes monitorear tu base de datos desde el dashboard de Supabase:

- **Database > Tables**: Ver tablas y datos
- **Database > Logs**: Ver logs de consultas
- **Settings > Usage**: Ver uso de recursos

## 9. Backup y Restauración

Supabase maneja automáticamente los backups, pero puedes:

1. **Backup manual**: Settings > Database > Database backups
2. **Exportar datos**: Usar `pg_dump` con la connection string
3. **Restaurar**: Usar `pg_restore` o el dashboard de Supabase

## 10. Troubleshooting

### Error de conexión
- ✅ Verifica que la DATABASE_URL sea correcta
- ✅ Confirma que el proyecto de Supabase esté activo
- ✅ Revisa que no haya restricciones de firewall

### Error de autenticación
- ✅ Verifica la contraseña en la connection string
- ✅ Confirma que el usuario `postgres` tenga permisos

### Tablas no se crean
- ✅ Ejecuta `python scripts/init_db.py`
- ✅ Verifica los logs en Supabase Dashboard
- ✅ Revisa que SQLAlchemy tenga permisos de escritura

## Comandos Útiles

```bash
# Probar conexión
python -c "from db.database import test_connection; test_connection()"

# Inicializar BD
python scripts/init_db.py

# Ejecutar servidor
python start.py

# Ejecutar pruebas
python scripts/run_tests.py
```

## Recursos Adicionales

- [Documentación de Supabase](https://supabase.com/docs)
- [Supabase Python Client](https://github.com/supabase/supabase-py)
- [SQLAlchemy con PostgreSQL](https://docs.sqlalchemy.org/en/14/dialects/postgresql.html)
