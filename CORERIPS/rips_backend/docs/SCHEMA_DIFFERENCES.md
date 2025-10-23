# Diferencias entre SQL Actual y Mapeo Definido

## Resumen

Este documento compara los nombres de columnas en `create_tables_supabase.sql` (estado actual) con los nombres definidos en `SCHEMA_MAPPING.md` (estándar deseado).

## Diferencias Encontradas

### 📋 Tabla: rips_consultations

| Campo en SQL Actual | Campo en SCHEMA_MAPPING | ¿Coincide? | Acción Recomendada |
|---------------------|------------------------|------------|-------------------|
| `consecutive_file` | `file_sequence` | ❌ | Ajustar SQL o mantener actual |
| `identification_type` | `id_type` | ❌ | Ajustar SQL o mantener actual |
| `identification_number` | `id_number` | ❌ | Ajustar SQL o mantener actual |
| `primary_diagnosis` | `main_diagnosis` | ❌ | Ajustar SQL o mantener actual |
| `primary_diagnosis_type` | `main_diagnosis_type` | ❌ | Ajustar SQL o mantener actual |
| `net_payment_value` | `net_payable_value` | ❌ | Ajustar SQL o mantener actual |

### 📋 Tabla: rips_procedures

| Campo en SQL Actual | Campo en SCHEMA_MAPPING | ¿Coincide? | Acción Recomendada |
|---------------------|------------------------|------------|-------------------|
| `consecutive_file` | `file_sequence` | ❌ | Ajustar SQL o mantener actual |
| `identification_type` | `id_type` | ❌ | Ajustar SQL o mantener actual |
| `identification_number` | `id_number` | ❌ | Ajustar SQL o mantener actual |
| `performance_scope` | `scope_of_procedure` | ❌ | Ajustar SQL o mantener actual |
| `attending_personnel` | `attending_staff` | ❌ | Ajustar SQL o mantener actual |
| `primary_diagnosis` | `main_diagnosis` | ❌ | Ajustar SQL o mantener actual |
| `surgical_act_performance_form` | `surgical_method` | ❌ | Ajustar SQL o mantener actual |

### 📋 Tabla: rips_users

| Campo en SQL Actual | Campo en SCHEMA_MAPPING | ¿Coincide? | Acción Recomendada |
|---------------------|------------------------|------------|-------------------|
| `first_surname` | `first_lastname` | ❌ | Ajustar SQL o mantener actual |
| `second_surname` | `second_lastname` | ❌ | Ajustar SQL o mantener actual |
| `second_name` | `middle_name` | ❌ | Ajustar SQL o mantener actual |

### 📋 Tabla: rips_medications

| Campo en SQL Actual | Campo en SCHEMA_MAPPING | ¿Coincide? | Acción Recomendada |
|---------------------|------------------------|------------|-------------------|
| `consecutive_file` | `file_sequence` | ❌ | Ajustar SQL o mantener actual |
| `identification_type` | `id_type` | ❌ | Ajustar SQL o mantener actual |
| `identification_number` | `id_number` | ❌ | Ajustar SQL o mantener actual |
| `unit_measure` | `measurement_unit` | ❌ | Ajustar SQL o mantener actual |
| `unit_number` | `units_number` | ❌ | Ajustar SQL o mantener actual |

### 📋 Tabla: rips_other_services

| Campo en SQL Actual | Campo en SCHEMA_MAPPING | ¿Coincide? | Acción Recomendada |
|---------------------|------------------------|------------|-------------------|
| `consecutive_file` | `file_sequence` | ❌ | Ajustar SQL o mantener actual |
| `identification_type` | `id_type` | ❌ | Ajustar SQL o mantener actual |
| `identification_number` | `id_number` | ❌ | Ajustar SQL o mantener actual |

### 📋 Tabla: rips_emergencies (urgencias)

| Campo en SQL Actual | Campo en SCHEMA_MAPPING | ¿Coincide? | Acción Recomendada |
|---------------------|------------------------|------------|-------------------|
| Nombre de tabla: `rips_emergencies` | `rips_emergency` | ❌ | Singular vs Plural |
| `consecutive_file` | `file_sequence` | ❌ | Ajustar SQL o mantener actual |
| `identification_type` | `id_type` | ❌ | Ajustar SQL o mantener actual |
| `identification_number` | `id_number` | ❌ | Ajustar SQL o mantener actual |
| `primary_diagnosis_type` | `main_diagnosis_type` | ❌ | Ajustar SQL o mantener actual |
| `copayment_value` | `copay_value` | ❌ | Ajustar SQL o mantener actual |

### 📋 Tabla: rips_hospitalizations

| Campo en SQL Actual | Campo en SCHEMA_MAPPING | ¿Coincide? | Acción Recomendada |
|---------------------|------------------------|------------|-------------------|
| Nombre de tabla: `rips_hospitalizations` | `rips_hospitalization` | ❌ | Singular vs Plural |
| `consecutive_file` | `file_sequence` | ❌ | Ajustar SQL o mantener actual |
| `identification_type` | `id_type` | ❌ | Ajustar SQL o mantener actual |
| `identification_number` | `id_number` | ❌ | Ajustar SQL o mantener actual |
| `primary_diagnosis_type` | `main_diagnosis_type` | ❌ | Ajustar SQL o mantener actual |
| `stay_days` | `days_stayed` | ❌ | Ajustar SQL o mantener actual |
| `user_destination_condition` | `user_discharge_condition` | ❌ | Ajustar SQL o mantener actual |

### 📋 Tabla: rips_newborns

| Campo en SQL Actual | Campo en SCHEMA_MAPPING | ¿Coincide? | Acción Recomendada |
|---------------------|------------------------|------------|-------------------|
| Nombre de tabla: `rips_newborns` | `rips_newborn` | ❌ | Singular vs Plural |
| `consecutive_file` | `file_sequence` | ❌ | Ajustar SQL o mantener actual |
| `mother_identification_type` | `mother_id_type` | ❌ | Ajustar SQL o mantener actual |
| `mother_identification_number` | `mother_id_number` | ❌ | Ajustar SQL o mantener actual |
| `primary_diagnosis` | `main_diagnosis` | ❌ | Ajustar SQL o mantener actual |
| `basic_death_cause` | `underlying_cause_of_death` | ❌ | Ajustar SQL o mantener actual |

### 📋 Tabla: rips_billing

| Campo en SQL Actual | Campo en SCHEMA_MAPPING | ¿Coincide? | Acción Recomendada |
|---------------------|------------------------|------------|-------------------|
| `consecutive_file` | `file_sequence` | ❌ | Ajustar SQL o mantener actual |
| `administrator_entity_code` | `administrator_code` | ❌ | Ajustar SQL o mantener actual |
| `administrator_entity_name` | `administrator_name` | ❌ | Ajustar SQL o mantener actual |
| `benefits_plan` | `benefit_plan` | ❌ | Ajustar SQL o mantener actual |
| `copayment` | `copayment_value` | ❌ | Ajustar SQL o mantener actual |
| `discounts_value` | `discount_value` | ❌ | Ajustar SQL o mantener actual |

### 📋 Tabla: rips_adjustments

| Campo en SQL Actual | Campo en SCHEMA_MAPPING | ¿Coincide? | Comentario |
|---------------------|------------------------|------------|-----------|
| `consecutive_file` | `file_sequence` | ❌ | Ajustar SQL o mantener actual |
| ✅ Resto de campos coinciden | - | ✅ | - |

### 📋 Tabla: rips_control

| Campo en SQL Actual | Campo en SCHEMA_MAPPING | ¿Coincide? | Comentario |
|---------------------|------------------------|------------|-----------|
| `administrator_entity_code` | `administrator_code` | ❌ | Ajustar SQL o mantener actual |
| `administrator_entity_name` | `administrator_name` | ❌ | Ajustar SQL o mantener actual |
| `benefits_plan` | `benefit_plan` | ❌ | Ajustar SQL o mantener actual |
| Campo extra: `record_type` | No definido en mapeo | ⚠️ | Parece ser campo adicional del SQL |

## Patrones de Diferencias

### 1. **Singular vs Plural en Nombres de Tablas**
- SQL actual usa **PLURAL**: `rips_emergencies`, `rips_hospitalizations`, `rips_newborns`
- SCHEMA_MAPPING usa **SINGULAR**: `rips_emergency`, `rips_hospitalization`, `rips_newborn`

### 2. **Patrón "consecutive_file" vs "file_sequence"**
- SQL actual: `consecutive_file`
- SCHEMA_MAPPING: `file_sequence`

### 3. **Patrón "identification" vs "id"**
- SQL actual: `identification_type`, `identification_number`
- SCHEMA_MAPPING: `id_type`, `id_number`

### 4. **Patrón "primary" vs "main"**
- SQL actual: `primary_diagnosis`, `primary_diagnosis_type`
- SCHEMA_MAPPING: `main_diagnosis`, `main_diagnosis_type`

### 5. **Otros Patrones**
- `surname` vs `lastname`
- `unit_measure` vs `measurement_unit`
- `copayment` vs `copayment_value` (inconsistente)

## Recomendaciones

### Opción 1: ✅ **MANTENER SQL ACTUAL (Recomendado)**
**Razón:** El SQL actual ya está en inglés y es funcional. Los nombres son claros y descriptivos.

**Acción:** 
- Actualizar `SCHEMA_MAPPING.md` para reflejar los nombres reales del SQL
- Usar el SQL como fuente de verdad
- Documentar cualquier diferencia menor

**Ventajas:**
- No requiere cambios en la base de datos
- No requiere cambios en el código existente
- Menor riesgo de introducir errores

### Opción 2: ⚠️ **ACTUALIZAR SQL PARA COINCIDIR CON SCHEMA_MAPPING**
**Razón:** Mantener consistencia con el documento de mapeo original.

**Acción:**
- Actualizar `create_tables_supabase.sql`
- Crear script de migración `ALTER TABLE`
- Actualizar todo el código que use estos campos
- Probar exhaustivamente

**Desventajas:**
- Alto riesgo de romper código existente
- Requiere migración de base de datos
- Mucho trabajo de actualización

### Opción 3: 🎯 **HÍBRIDA (Recomendada para equipo)**
**Razón:** Mantener lo mejor de ambos mundos.

**Acción:**
- Mantener nombres actuales del SQL
- Actualizar solo los patrones más problemáticos:
  - `consecutive_file` → `file_sequence` (más claro)
  - `identification_*` → `id_*` (más corto)
- Dejar el resto como está

## Decisión Requerida

**¿Qué opción prefieres?**

1. [ ] Mantener SQL actual tal cual está
2. [ ] Actualizar SQL para coincidir 100% con SCHEMA_MAPPING
3. [ ] Híbrida: solo cambiar los patrones más importantes

Una vez decidas, puedo ayudarte a:
- Actualizar el documento SCHEMA_MAPPING.md
- Generar scripts de migración SQL si es necesario
- Buscar y actualizar referencias en el código Python

## Siguiente Paso

Por favor indica qué opción prefieres y procederé con los cambios necesarios.

