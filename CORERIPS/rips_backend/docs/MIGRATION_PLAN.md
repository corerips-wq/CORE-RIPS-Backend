# Plan de Migración: Nombres de Tablas y Columnas (Español → Inglés)

## Resumen

Este documento describe el plan para migrar los nombres de tablas y columnas de la base de datos Supabase de español a inglés.

## Estado Actual

### ✅ Ya Completado
- El archivo `create_tables_supabase.sql` YA tiene tablas RIPS con nombres en inglés:
  - `rips_consultations`
  - `rips_procedures`
  - `rips_users`
  - `rips_medications`
  - `rips_other_services`
  - `rips_emergencies`
  - `rips_hospitalizations`
  - `rips_newborns`
  - `rips_billing`
  - `rips_adjustments`
  - `rips_control`

### ⚠️ Por Verificar/Actualizar
Las **columnas dentro de estas tablas** necesitan revisarse para asegurar que coincidan con el mapeo definido en `SCHEMA_MAPPING.md`.

## Archivos a Actualizar

### 1. 📄 `create_tables_supabase.sql`
**Acción:** Revisar y actualizar los nombres de columnas en cada tabla RIPS.

**Ejemplo de lo que hay que cambiar:**
```sql
-- ANTES (si tuviera nombres en español)
CREATE TABLE rips_consultations (
    numero_factura VARCHAR(50),
    codigo_prestador VARCHAR(12),
    -- ...
);

-- DESPUÉS (nombres en inglés según SCHEMA_MAPPING.md)
CREATE TABLE rips_consultations (
    invoice_number VARCHAR(50),
    provider_code VARCHAR(12),
    -- ...
);
```

### 2. 🐍 **Scripts Python** (si existen consultas a tablas RIPS)

Archivos a revisar:
- `api/supabase_routes.py` - Rutas que consultan tablas RIPS
- `services/file_service.py` - Servicios que insertan/consultan datos RIPS
- `services/validation_service.py` - Validaciones que acceden a datos RIPS
- `scripts/init_supabase.py` - Scripts de inicialización
- Cualquier script en `scripts/` que use tablas RIPS

**Ejemplo de cambios:**
```python
# ANTES
result = supabase.table('rips_consultas').select('numero_factura').execute()

# DESPUÉS
result = supabase.table('rips_consultations').select('invoice_number').execute()
```

### 3. 📊 **Modelos (Opcional)**
- `models/models.py` - Actualizar comentarios/documentación si es necesario
- `models/schemas.py` - Crear nuevos schemas Pydantic si se van a usar

### 4. 🗄️ **Base de Datos en Supabase**

**IMPORTANTE:** Una vez actualizados los archivos:

#### Opción A: Base de Datos Nueva
1. Ejecutar el nuevo `create_tables_supabase.sql` en un proyecto nuevo

#### Opción B: Migrar Base de Datos Existente
Si ya tienes datos en producción, necesitarás crear un script de migración:

```sql
-- Ejemplo: Renombrar tabla
ALTER TABLE rips_ajustes RENAME TO rips_adjustments;

-- Ejemplo: Renombrar columnas
ALTER TABLE rips_adjustments 
    RENAME COLUMN numero_factura TO invoice_number;
ALTER TABLE rips_adjustments 
    RENAME COLUMN codigo_prestador TO provider_code;
-- ... etc
```

## Pasos Recomendados

### Fase 1: Preparación ✅
- [x] Crear documento `SCHEMA_MAPPING.md` con mapeo completo
- [x] Crear este plan de migración
- [ ] Hacer backup completo de la base de datos actual

### Fase 2: Actualización de Código 🔄
1. [ ] Actualizar `create_tables_supabase.sql` con nombres de columnas correctos
2. [ ] Buscar y actualizar todas las referencias en código Python
3. [ ] Actualizar schemas Pydantic si existen
4. [ ] Ejecutar tests para verificar que no haya errores

### Fase 3: Migración de Base de Datos 🗄️
1. [ ] Decidir estrategia: ¿BD nueva o migración?
2. [ ] Si migración: crear script `migrate_schema.sql`
3. [ ] Ejecutar migración en ambiente de desarrollo
4. [ ] Verificar que todo funcione correctamente
5. [ ] Ejecutar migración en producción

### Fase 4: Verificación ✔️
1. [ ] Probar todas las funcionalidades
2. [ ] Verificar que las consultas funcionen correctamente
3. [ ] Actualizar documentación de API si existe
4. [ ] Comunicar cambios al equipo

## Herramientas Útiles

### Buscar Referencias en el Código
```bash
# Buscar referencias a nombres de tablas en español
grep -r "rips_consultas" .
grep -r "rips_facturacion" .
grep -r "rips_hospitalizacion" .
# ... etc

# Buscar referencias a columnas en español
grep -r "numero_factura" .
grep -r "codigo_prestador" .
# ... etc
```

### Script de Generación de SQL de Migración
Si necesitas un script para generar automáticamente las sentencias ALTER TABLE, puedo ayudarte a crearlo.

## Notas Importantes

1. **Timing:** Realizar la migración en horario de bajo tráfico
2. **Backup:** SIEMPRE hacer backup antes de modificar la BD
3. **Testing:** Probar exhaustivamente en desarrollo antes de producción
4. **Rollback:** Tener plan de rollback en caso de problemas
5. **Comunicación:** Notificar al equipo sobre los cambios

## Referencias

- `SCHEMA_MAPPING.md` - Mapeo completo de nombres
- `create_tables_supabase.sql` - Script de creación de tablas
- Documentación de Supabase: https://supabase.com/docs

## Contacto

Para preguntas sobre la migración, consultar el archivo `SCHEMA_MAPPING.md` o contactar al equipo de desarrollo.

