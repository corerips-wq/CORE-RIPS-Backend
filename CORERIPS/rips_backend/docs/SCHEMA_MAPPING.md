# Esquema de Base de Datos RIPS - Supabase

Este documento describe el esquema actual de las tablas RIPS en la base de datos Supabase.

**NOTA IMPORTANTE:** Este documento refleja los nombres REALES de las tablas y columnas en la base de datos actual.

---

## Tabla: rips_adjustments

**Descripción:** Almacena los ajustes realizados a las facturas RIPS (notas débito/crédito).

**Código RIPS:** AD - Adjustments/Notes

### Columnas

| Nombre de Columna        | Tipo          | Descripción                           |
| ------------------------ | ------------- | ------------------------------------- |
| **id**                   | SERIAL        | Identificador único (Primary Key)     |
| **consecutive_file**     | VARCHAR(20)   | Consecutivo del archivo               |
| **invoice_number**       | VARCHAR(50)   | Número de la factura (NOT NULL)       |
| **provider_code**        | VARCHAR(12)   | Código del prestador (NOT NULL)       |
| **note_type**            | VARCHAR(2)    | Tipo de nota (débito/crédito)         |
| **note_number**          | VARCHAR(50)   | Número de la nota                     |
| **note_issue_date**      | DATE          | Fecha de expedición de la nota        |
| **concept_code**         | VARCHAR(2)    | Código del concepto del ajuste        |
| **concept_description**  | VARCHAR(255)  | Descripción del concepto del ajuste   |
| **adjustment_value**     | DECIMAL(15,2) | Valor monetario del ajuste            |
| **file_id**              | INTEGER       | FK a tabla files                      |
| **created_at**           | TIMESTAMPTZ   | Fecha de creación del registro        |

---

## Tabla: rips_consultations

**Descripción:** Almacena las consultas médicas realizadas en el sistema RIPS.

**Código RIPS:** AC - Consultations

### Columnas

| Nombre de Columna           | Tipo          | Descripción                          |
| --------------------------- | ------------- | ------------------------------------ |
| **id**                      | SERIAL        | Identificador único (Primary Key)    |
| **consecutive_file**        | VARCHAR(20)   | Consecutivo del archivo              |
| **invoice_number**          | VARCHAR(50)   | Número de la factura                 |
| **provider_code**           | VARCHAR(12)   | Código del prestador (NOT NULL)      |
| **identification_type**     | VARCHAR(2)    | Tipo de identificación del paciente  |
| **identification_number**   | VARCHAR(20)   | Número de identificación del paciente|
| **consultation_date**       | DATE          | Fecha de la consulta médica          |
| **authorization_number**    | VARCHAR(20)   | Número de autorización del servicio  |
| **consultation_code**       | VARCHAR(10)   | Código del tipo de consulta (CUPS)   |
| **consultation_purpose**    | VARCHAR(2)    | Finalidad de la consulta             |
| **external_cause**          | VARCHAR(2)    | Causa externa de la consulta         |
| **primary_diagnosis**       | VARCHAR(7)    | Diagnóstico principal (CIE-10)       |
| **related_diagnosis_1**     | VARCHAR(7)    | Primer diagnóstico relacionado       |
| **related_diagnosis_2**     | VARCHAR(7)    | Segundo diagnóstico relacionado      |
| **related_diagnosis_3**     | VARCHAR(7)    | Tercer diagnóstico relacionado       |
| **primary_diagnosis_type**  | VARCHAR(2)    | Tipo del diagnóstico principal       |
| **consultation_value**      | DECIMAL(15,2) | Valor monetario de la consulta       |
| **copayment_value**         | DECIMAL(15,2) | Valor de la cuota moderadora         |
| **net_payment_value**       | DECIMAL(15,2) | Valor neto a pagar                   |
| **file_id**                 | INTEGER       | FK a tabla files                     |
| **created_at**              | TIMESTAMPTZ   | Fecha de creación del registro       |

---

## Tabla: rips_billing

**Descripción:** Almacena la información de facturación del sistema RIPS.

**Código RIPS:** AF - Billing

### Columnas

| Nombre de Columna               | Tipo          | Descripción                                 |
| ------------------------------- | ------------- | ------------------------------------------- |
| **id**                          | SERIAL        | Identificador único (Primary Key)           |
| **consecutive_file**            | VARCHAR(20)   | Consecutivo del archivo                     |
| **invoice_number**              | VARCHAR(50)   | Número de la factura (NOT NULL)             |
| **provider_code**               | VARCHAR(12)   | Código del prestador (NOT NULL)             |
| **invoice_issue_date**          | DATE          | Fecha de expedición de la factura           |
| **period_start_date**           | DATE          | Fecha de inicio del período de facturación  |
| **period_end_date**             | DATE          | Fecha de fin del período de facturación     |
| **administrator_entity_code**   | VARCHAR(6)    | Código de la entidad administradora         |
| **administrator_entity_name**   | VARCHAR(100)  | Nombre de la entidad administradora         |
| **contract_number**             | VARCHAR(50)   | Número del contrato                         |
| **benefits_plan**               | VARCHAR(50)   | Plan de beneficios                          |
| **policy_number**               | VARCHAR(50)   | Número de póliza                            |
| **copayment**                   | DECIMAL(15,2) | Valor del copago                            |
| **commission_value**            | DECIMAL(15,2) | Valor de la comisión                        |
| **discounts_value**             | DECIMAL(15,2) | Valor de los descuentos                     |
| **net_invoice_value**           | DECIMAL(15,2) | Valor neto de la factura                    |
| **file_id**                     | INTEGER       | FK a tabla files                            |
| **created_at**                  | TIMESTAMPTZ   | Fecha de creación del registro              |

---

## Tabla: rips_hospitalizations

**Descripción:** Almacena la información de hospitalizaciones del sistema RIPS.

**Código RIPS:** AH - Hospitalizations

### Columnas

| Nombre de Columna               | Tipo          | Descripción                                   |
| ------------------------------- | ------------- | --------------------------------------------- |
| **id**                          | SERIAL        | Identificador único (Primary Key)             |
| **consecutive_file**            | VARCHAR(20)   | Consecutivo del archivo                       |
| **invoice_number**              | VARCHAR(50)   | Número de la factura                          |
| **provider_code**               | VARCHAR(12)   | Código del prestador (NOT NULL)               |
| **identification_type**         | VARCHAR(2)    | Tipo de identificación del paciente           |
| **identification_number**       | VARCHAR(20)   | Número de identificación del paciente         |
| **admission_route**             | VARCHAR(2)    | Vía de ingreso del paciente                   |
| **admission_date**              | DATE          | Fecha de ingreso a hospitalización            |
| **admission_time**              | TIME          | Hora de ingreso a hospitalización             |
| **authorization_number**        | VARCHAR(20)   | Número de autorización del servicio           |
| **external_cause**              | VARCHAR(2)    | Causa externa de la hospitalización           |
| **admission_diagnosis**         | VARCHAR(7)    | Diagnóstico al momento del ingreso            |
| **discharge_diagnosis**         | VARCHAR(7)    | Diagnóstico al momento del egreso             |
| **related_diagnosis_1**         | VARCHAR(7)    | Primer diagnóstico relacionado                |
| **related_diagnosis_2**         | VARCHAR(7)    | Segundo diagnóstico relacionado               |
| **related_diagnosis_3**         | VARCHAR(7)    | Tercer diagnóstico relacionado                |
| **related_diagnosis_4**         | VARCHAR(7)    | Cuarto diagnóstico relacionado                |
| **primary_diagnosis_type**      | VARCHAR(2)    | Tipo del diagnóstico principal                |
| **stay_days**                   | INTEGER       | Días de estancia en hospitalización           |
| **discharge_type**              | VARCHAR(2)    | Tipo de egreso de la hospitalización          |
| **user_destination_condition**  | VARCHAR(2)    | Condición de destino del usuario              |
| **obstetric_death_cause**       | VARCHAR(2)    | Causa de muerte obstétrica (si aplica)        |
| **discharge_date**              | DATE          | Fecha de egreso de hospitalización            |
| **discharge_time**              | TIME          | Hora de egreso de hospitalización             |
| **service_value**               | DECIMAL(15,2) | Valor del servicio de hospitalización         |
| **copayment_value**             | DECIMAL(15,2) | Valor de la cuota moderadora                  |
| **net_value**                   | DECIMAL(15,2) | Valor neto                                    |
| **file_id**                     | INTEGER       | FK a tabla files                              |
| **created_at**                  | TIMESTAMPTZ   | Fecha de creación del registro                |

---

## Tabla: rips_medications

**Descripción:** Almacena la información de medicamentos suministrados en el sistema RIPS.

**Código RIPS:** AM - Medications

### Columnas

| Nombre de Columna             | Tipo          | Descripción                                   |
| ----------------------------- | ------------- | --------------------------------------------- |
| **id**                        | SERIAL        | Identificador único (Primary Key)             |
| **consecutive_file**          | VARCHAR(20)   | Consecutivo del archivo                       |
| **invoice_number**            | VARCHAR(50)   | Número de la factura                          |
| **provider_code**             | VARCHAR(12)   | Código del prestador (NOT NULL)               |
| **identification_type**       | VARCHAR(2)    | Tipo de identificación del paciente           |
| **identification_number**     | VARCHAR(20)   | Número de identificación del paciente         |
| **consultation_date**         | DATE          | Fecha de la consulta                          |
| **authorization_number**      | VARCHAR(20)   | Número de autorización del medicamento        |
| **medication_code**           | VARCHAR(20)   | Código del medicamento                        |
| **medication_type**           | VARCHAR(2)    | Tipo de medicamento                           |
| **generic_name**              | VARCHAR(255)  | Nombre genérico del medicamento               |
| **pharmaceutical_form**       | VARCHAR(2)    | Forma farmacéutica del medicamento            |
| **medication_concentration**  | VARCHAR(255)  | Concentración del medicamento                 |
| **unit_measure**              | VARCHAR(2)    | Unidad de medida                              |
| **unit_number**               | VARCHAR(10)   | Número de unidades                            |
| **unit_value**                | DECIMAL(15,2) | Valor unitario del medicamento                |
| **total_value**               | DECIMAL(15,2) | Valor total                                   |
| **file_id**                   | INTEGER       | FK a tabla files                              |
| **created_at**                | TIMESTAMPTZ   | Fecha de creación del registro                |

---

## Tabla: rips_other_services

**Descripción:** Almacena la información de otros servicios prestados en el sistema RIPS.

**Código RIPS:** AT - Other Services

### Columnas

| Nombre de Columna           | Tipo          | Descripción                                   |
| --------------------------- | ------------- | --------------------------------------------- |
| **id**                      | SERIAL        | Identificador único (Primary Key)             |
| **consecutive_file**        | VARCHAR(20)   | Consecutivo del archivo                       |
| **invoice_number**          | VARCHAR(50)   | Número de la factura                          |
| **provider_code**           | VARCHAR(12)   | Código del prestador (NOT NULL)               |
| **identification_type**     | VARCHAR(2)    | Tipo de identificación del paciente           |
| **identification_number**   | VARCHAR(20)   | Número de identificación del paciente         |
| **service_date**            | DATE          | Fecha del servicio prestado                   |
| **authorization_number**    | VARCHAR(20)   | Número de autorización del servicio           |
| **service_code**            | VARCHAR(7)    | Código del servicio (CUPS)                    |
| **service_name**            | VARCHAR(255)  | Nombre del servicio                           |
| **quantity**                | DECIMAL(10,2) | Cantidad de servicios prestados               |
| **unit_value**              | DECIMAL(15,2) | Valor unitario del servicio                   |
| **total_value**             | DECIMAL(15,2) | Valor total                                   |
| **file_id**                 | INTEGER       | FK a tabla files                              |
| **created_at**              | TIMESTAMPTZ   | Fecha de creación del registro                |

---

## Tabla: rips_procedures

**Descripción:** Almacena la información de procedimientos realizados en el sistema RIPS.

**Código RIPS:** AP - Procedures

### Columnas

| Nombre de Columna                   | Tipo          | Descripción                                   |
| ----------------------------------- | ------------- | --------------------------------------------- |
| **id**                              | SERIAL        | Identificador único (Primary Key)             |
| **consecutive_file**                | VARCHAR(20)   | Consecutivo del archivo                       |
| **invoice_number**                  | VARCHAR(50)   | Número de la factura                          |
| **provider_code**                   | VARCHAR(12)   | Código del prestador (NOT NULL)               |
| **identification_type**             | VARCHAR(2)    | Tipo de identificación del paciente           |
| **identification_number**           | VARCHAR(20)   | Número de identificación del paciente         |
| **procedure_date**                  | DATE          | Fecha del procedimiento                       |
| **authorization_number**            | VARCHAR(20)   | Número de autorización del procedimiento      |
| **procedure_code**                  | VARCHAR(7)    | Código del procedimiento (CUPS)               |
| **performance_scope**               | VARCHAR(2)    | Ámbito de realización del procedimiento       |
| **procedure_purpose**               | VARCHAR(2)    | Finalidad del procedimiento                   |
| **attending_personnel**             | VARCHAR(2)    | Personal que atendió el procedimiento         |
| **primary_diagnosis**               | VARCHAR(7)    | Diagnóstico principal (CIE-10)                |
| **related_diagnosis**               | VARCHAR(7)    | Diagnóstico relacionado                       |
| **complication**                    | VARCHAR(2)    | Complicaciones durante el procedimiento       |
| **surgical_act_performance_form**   | VARCHAR(2)    | Forma de realización del acto quirúrgico      |
| **procedure_value**                 | DECIMAL(15,2) | Valor del procedimiento                       |
| **file_id**                         | INTEGER       | FK a tabla files                              |
| **created_at**                      | TIMESTAMPTZ   | Fecha de creación del registro                |

---

## Tabla: rips_newborns

**Descripción:** Almacena la información de recién nacidos en el sistema RIPS.

**Código RIPS:** AN - Newborns

### Columnas

| Nombre de Columna                   | Tipo          | Descripción                                   |
| ----------------------------------- | ------------- | --------------------------------------------- |
| **id**                              | SERIAL        | Identificador único (Primary Key)             |
| **consecutive_file**                | VARCHAR(20)   | Consecutivo del archivo                       |
| **invoice_number**                  | VARCHAR(50)   | Número de la factura                          |
| **provider_code**                   | VARCHAR(12)   | Código del prestador (NOT NULL)               |
| **mother_identification_type**      | VARCHAR(2)    | Tipo de identificación de la madre            |
| **mother_identification_number**    | VARCHAR(20)   | Número de identificación de la madre          |
| **birth_date**                      | DATE          | Fecha de nacimiento del recién nacido         |
| **birth_time**                      | TIME          | Hora de nacimiento del recién nacido          |
| **gestational_age**                 | INTEGER       | Edad gestacional en semanas                   |
| **prenatal_control**                | VARCHAR(1)    | Control prenatal realizado                    |
| **sex**                             | VARCHAR(1)    | Sexo del recién nacido                        |
| **birth_weight**                    | DECIMAL(5,2)  | Peso al nacimiento en gramos                  |
| **primary_diagnosis**               | VARCHAR(7)    | Diagnóstico principal (CIE-10)                |
| **related_diagnosis_1**             | VARCHAR(7)    | Primer diagnóstico relacionado                |
| **related_diagnosis_2**             | VARCHAR(7)    | Segundo diagnóstico relacionado               |
| **related_diagnosis_3**             | VARCHAR(7)    | Tercer diagnóstico relacionado                |
| **basic_death_cause**               | VARCHAR(7)    | Causa básica de muerte (si aplica)            |
| **death_date**                      | DATE          | Fecha de muerte (si aplica)                   |
| **death_time**                      | TIME          | Hora de muerte (si aplica)                    |
| **file_id**                         | INTEGER       | FK a tabla files                              |
| **created_at**                      | TIMESTAMPTZ   | Fecha de creación del registro                |

---

## Tabla: rips_users

**Descripción:** Almacena la información de usuarios/pacientes en el sistema RIPS.

**Código RIPS:** US - Users

### Columnas

| Nombre de Columna               | Tipo         | Descripción                                        |
| ------------------------------- | ------------ | -------------------------------------------------- |
| **id**                          | SERIAL       | Identificador único (Primary Key)                  |
| **document_type**               | VARCHAR(2)   | Tipo de documento de identificación (NOT NULL)     |
| **document_number**             | VARCHAR(20)  | Número del documento de identificación (NOT NULL)  |
| **administrator_entity_code**   | VARCHAR(6)   | Código de la entidad administradora                |
| **user_type**                   | VARCHAR(2)   | Tipo de usuario/afiliación                         |
| **first_surname**               | VARCHAR(60)  | Primer apellido                                    |
| **second_surname**              | VARCHAR(60)  | Segundo apellido                                   |
| **first_name**                  | VARCHAR(60)  | Primer nombre                                      |
| **second_name**                 | VARCHAR(60)  | Segundo nombre                                     |
| **age_measure**                 | VARCHAR(2)   | Edad medida al momento del servicio                |
| **age**                         | VARCHAR(3)   | Edad del usuario                                   |
| **age_unit**                    | VARCHAR(2)   | Unidad de medida de la edad (años, meses, días)    |
| **department_code**             | VARCHAR(2)   | Código del departamento de residencia              |
| **municipality_code**           | VARCHAR(3)   | Código del municipio de residencia                 |
| **residential_zone**            | VARCHAR(1)   | Zona residencial (urbana/rural)                    |
| **file_id**                     | INTEGER      | FK a tabla files                                   |
| **created_at**                  | TIMESTAMPTZ  | Fecha de creación del registro                     |

---

## Tabla: rips_emergencies

**Descripción:** Almacena la información de atenciones de urgencias en el sistema RIPS.

**Código RIPS:** AU - Emergencies

### Columnas

| Nombre de Columna              | Tipo          | Descripción                                   |
| ------------------------------ | ------------- | --------------------------------------------- |
| **id**                         | SERIAL        | Identificador único (Primary Key)             |
| **consecutive_file**           | VARCHAR(20)   | Consecutivo del archivo                       |
| **invoice_number**             | VARCHAR(50)   | Número de la factura                          |
| **provider_code**              | VARCHAR(12)   | Código del prestador (NOT NULL)               |
| **identification_type**        | VARCHAR(2)    | Tipo de identificación del paciente           |
| **identification_number**      | VARCHAR(20)   | Número de identificación del paciente         |
| **admission_date**             | DATE          | Fecha de ingreso a urgencias                  |
| **admission_time**             | TIME          | Hora de ingreso a urgencias                   |
| **authorization_number**       | VARCHAR(20)   | Número de autorización del servicio           |
| **external_cause**             | VARCHAR(2)    | Causa externa de la urgencia                  |
| **admission_diagnosis**        | VARCHAR(7)    | Diagnóstico al momento del ingreso            |
| **discharge_diagnosis**        | VARCHAR(7)    | Diagnóstico al momento del egreso             |
| **related_diagnosis_1**        | VARCHAR(7)    | Primer diagnóstico relacionado                |
| **related_diagnosis_2**        | VARCHAR(7)    | Segundo diagnóstico relacionado               |
| **related_diagnosis_3**        | VARCHAR(7)    | Tercer diagnóstico relacionado                |
| **related_diagnosis_4**        | VARCHAR(7)    | Cuarto diagnóstico relacionado                |
| **primary_diagnosis_type**     | VARCHAR(2)    | Tipo del diagnóstico principal                |
| **service_value**              | DECIMAL(15,2) | Valor del servicio de urgencias               |
| **copayment_value**            | DECIMAL(15,2) | Valor de la cuota moderadora                  |
| **net_value**                  | DECIMAL(15,2) | Valor neto                                    |
| **file_id**                    | INTEGER       | FK a tabla files                              |
| **created_at**                 | TIMESTAMPTZ   | Fecha de creación del registro                |

---

## Tabla: rips_control

**Descripción:** Almacena información de control y resumen de archivos RIPS.

**Código RIPS:** CT - Control

### Columnas

| Nombre de Columna               | Tipo         | Descripción                                   |
| ------------------------------- | ------------ | --------------------------------------------- |
| **id**                          | SERIAL       | Identificador único (Primary Key)             |
| **record_type**                 | VARCHAR(1)   | Tipo de registro (NOT NULL)                   |
| **provider_code**               | VARCHAR(12)  | Código del prestador (NOT NULL)               |
| **generation_date**             | DATE         | Fecha de generación del archivo (NOT NULL)    |
| **rips_file**                   | VARCHAR(20)  | Nombre del archivo RIPS                       |
| **total_records**               | INTEGER      | Total de registros en el archivo              |
| **administrator_entity_code**   | VARCHAR(6)   | Código de la entidad administradora           |
| **administrator_entity_name**   | VARCHAR(100) | Nombre de la entidad administradora           |
| **contract_number**             | VARCHAR(50)  | Número del contrato                           |
| **benefits_plan**               | VARCHAR(50)  | Plan de beneficios                            |
| **technical_annex_version**     | VARCHAR(20)  | Versión del anexo técnico                     |
| **file_id**                     | INTEGER      | FK a tabla files                              |
| **created_at**                  | TIMESTAMPTZ  | Fecha de creación del registro                |

---

## Ejemplo de Uso en Código

### Python con Supabase

```python
from supabase import create_client

# Inicializar cliente
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Consultar datos de consultas
consultas = supabase.table('rips_consultations').select(
    'invoice_number',
    'consultation_date',
    'primary_diagnosis'
).execute()

# Consultar procedimientos
procedimientos = supabase.table('rips_procedures').select(
    'procedure_code',
    'procedure_date',
    'procedure_value'
).execute()

# Consultar usuarios/pacientes
usuarios = supabase.table('rips_users').select(
    'document_number',
    'first_name',
    'first_surname'
).eq('document_type', 'CC').execute()

# Consultar facturación
facturas = supabase.table('rips_billing').select(
    'invoice_number',
    'invoice_issue_date',
    'net_invoice_value'
).execute()

# Consultar hospitalizaciones
hospitalizaciones = supabase.table('rips_hospitalizations').select(
    'admission_date',
    'discharge_date',
    'stay_days'
).execute()

# Consultar urgencias
urgencias = supabase.table('rips_emergencies').select(
    'admission_date',
    'admission_time',
    'discharge_diagnosis'
).execute()

# Consultar recién nacidos
recien_nacidos = supabase.table('rips_newborns').select(
    'birth_date',
    'birth_weight',
    'sex'
).execute()

# Consultar medicamentos
medicamentos = supabase.table('rips_medications').select(
    'medication_code',
    'generic_name',
    'total_value'
).execute()

# Consultar otros servicios
otros_servicios = supabase.table('rips_other_services').select(
    'service_code',
    'service_name',
    'quantity'
).execute()

# Consultar ajustes
ajustes = supabase.table('rips_adjustments').select(
    'invoice_number',
    'note_type',
    'adjustment_value'
).execute()
```

---

## Índices Creados

Para optimizar el rendimiento, se han creado los siguientes índices:

### rips_consultations
- `idx_rips_consultations_file_id` → file_id
- `idx_rips_consultations_provider_code` → provider_code
- `idx_rips_consultations_date` → consultation_date

### rips_procedures
- `idx_rips_procedures_file_id` → file_id
- `idx_rips_procedures_provider_code` → provider_code
- `idx_rips_procedures_date` → procedure_date

### rips_users
- `idx_rips_users_file_id` → file_id
- `idx_rips_users_document` → (document_type, document_number)

### rips_medications
- `idx_rips_medications_file_id` → file_id
- `idx_rips_medications_provider_code` → provider_code

### rips_other_services
- `idx_rips_other_services_file_id` → file_id
- `idx_rips_other_services_provider_code` → provider_code

### rips_emergencies
- `idx_rips_emergencies_file_id` → file_id
- `idx_rips_emergencies_provider_code` → provider_code

### rips_hospitalizations
- `idx_rips_hospitalizations_file_id` → file_id
- `idx_rips_hospitalizations_provider_code` → provider_code

### rips_newborns
- `idx_rips_newborns_file_id` → file_id
- `idx_rips_newborns_provider_code` → provider_code

### rips_billing
- `idx_rips_billing_file_id` → file_id
- `idx_rips_billing_invoice_number` → invoice_number

### rips_adjustments
- `idx_rips_adjustments_file_id` → file_id
- `idx_rips_adjustments_invoice_number` → invoice_number

### rips_control
- `idx_rips_control_file_id` → file_id
- `idx_rips_control_provider_code` → provider_code

---

## Referencias

- Script de creación: `create_tables_supabase.sql`
- Plan de migración: `MIGRATION_PLAN.md`
- Análisis de diferencias: `SCHEMA_DIFFERENCES.md`
- Documentación oficial RIPS: Resolución 3374 de 2000 y actualizaciones

---

## Notas

- Todas las tablas RIPS incluyen `file_id` como Foreign Key a la tabla `files`
- Todas las tablas incluyen `created_at` con timestamp automático
- Los códigos de diagnóstico siguen el estándar CIE-10
- Los códigos de procedimientos siguen el estándar CUPS
- Fecha de última actualización: Octubre 2025
