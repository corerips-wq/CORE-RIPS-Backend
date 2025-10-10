# Reglas de Validación RIPS

Este documento describe todas las reglas de validación implementadas en el sistema, basadas en los archivos Excel de normatividad RIPS.

## Resumen de Análisis

**Archivos analizados:** 5
- `RIPS_By_Norm_Catalogos_CUPS_CIE10_DANE.xlsx`
- `RIPS_By_Norm_Resolucion_1884_2024.xlsx`
- `RIPS_By_Norm_Lineamientos_FEV_RIPS.xlsx`
- `RIPS_By_Norm_Resolucion_2275_2023.xlsx`
- `RIPS_Validaciones_AI.xlsx`

**Total de reglas:** 41
- ✅ **Reglas determinísticas:** 33
- 🤖 **Reglas de IA:** 8

## Validaciones Determinísticas

### 1. Validaciones de Estructura

#### Archivo CT (Control)
- **CT-001**: `TIPO_REGISTRO` debe ser "1" (numérico, 1 carácter, obligatorio)
- **CT-002**: `FECHA_GENERACION` formato YYYY-MM-DD (fecha, 10 caracteres, obligatorio)
- **GEN-001**: `VERSION_ANEXO_TECNICO` indicar versión normativa (string, 1-20 caracteres, obligatorio)

#### Archivo US (Usuarios)
- **US-001**: `TIPO_DOCUMENTO_USUARIO` valores: CC,TI,RC,CE,PA,NUIP,MS (código, 1-2 caracteres, obligatorio)
- **US-002**: `NUMERO_DOCUMENTO_USUARIO` alfanumérico (string, 1-20 caracteres, obligatorio)
- **US-007**: `FECHA_NACIMIENTO` formato YYYY-MM-DD, <= fecha atención (fecha, 10 caracteres, obligatorio)
- **US-008**: `SEXO` valores: M,F (código, 1 carácter, obligatorio)

#### Archivo AC (Consultas)
- **AC-001**: `CODIGO_PRESTADOR` 12 dígitos numéricos (numérico, 12 caracteres, obligatorio)
- **AC-012**: `DIAGNOSTICO_PRINCIPAL_CIE` código CIE-10/CIE-11 (código, 3-7 caracteres, obligatorio)

#### Archivo AP (Procedimientos)
- **AP-001**: `CODIGO_CUPS` código CUPS vigente (string, 3-7 caracteres, obligatorio)
- **AP-002**: `FECHA_PROCEDIMIENTO` formato YYYY-MM-DD (fecha, 10 caracteres, obligatorio)

#### Archivo AM (Medicamentos)
- **AM-001**: `CODIGO_PRODUCTO` código POS/GTIN/IPS (string, 3-20 caracteres, obligatorio)

#### Archivo AF (Facturación)
- **AF-004**: `CUV` Código Único de Validación (string, 10-64 caracteres, condicional)

#### Archivo AD (Ajustes/Notas)
- **AD-001**: `TIPO_NOTA` valores: NC,ND (código, 1-2 caracteres, obligatorio)

### 2. Validaciones de Formato

#### Fechas
- Formato YYYY-MM-DD obligatorio
- No pueden ser futuras (excepto fechas programadas)
- Fechas de nacimiento no pueden ser > 150 años
- Coherencia entre fechas relacionadas

#### Códigos
- Códigos alfanuméricos sin caracteres especiales
- Longitudes específicas según campo
- Validación contra catálogos oficiales

#### Campos Numéricos
- Solo dígitos permitidos
- Longitudes específicas
- Rangos válidos según contexto

### 3. Validaciones de Negocio

#### Campos Obligatorios
- Validación de cardinalidad 1..1
- Campos condicionales según contexto
- Dependencias entre campos

#### Catálogos de Referencia
- CUPS (Clasificación Única de Procedimientos en Salud)
- CIE-10/CIE-11 (Clasificación Internacional de Enfermedades)
- DANE (códigos de municipios/departamentos)
- Catálogos DIAN/MinSalud

## Validaciones de Inteligencia Artificial

### 1. Coherencia Clínica

#### AI-CLIN-001: Diagnóstico incompatible con sexo
- **Descripción**: Detecta diagnósticos que no corresponden al sexo del paciente
- **Ejemplos**: 
  - Embarazo reportado en paciente masculino
  - Cáncer de próstata en mujer
- **Severidad**: Alta
- **Implementación**: Modelo IA basado en reglas clínicas y aprendizaje supervisado

#### AI-CLIN-002: Diagnóstico incompatible con edad
- **Descripción**: Detecta diagnósticos que no corresponden a la edad del paciente
- **Ejemplos**:
  - Enfermedades pediátricas reportadas en adultos mayores
  - Demencia senil en menores de edad
- **Severidad**: Alta
- **Implementación**: IA con cruces de edad, diagnóstico y prevalencia epidemiológica

#### AI-CLIN-003: Procedimiento incompatible con diagnóstico
- **Descripción**: Detecta procedimientos que no tienen relación clínica con el diagnóstico
- **Ejemplos**: Cirugía cardíaca para diagnóstico dermatológico
- **Severidad**: Media
- **Implementación**: Análisis de coherencia clínica mediante IA

### 2. Detección de Patrones Atípicos

#### AI-PAT-001: Procedimientos duplicados en períodos cortos
- **Descripción**: Detecta procedimientos repetidos anómalamente
- **Ejemplos**: Dos cesáreas facturadas al mismo usuario en la misma semana
- **Severidad**: Media
- **Implementación**: IA detecta patrones de facturación anómalos comparando históricos

#### AI-PAT-002: Volumen atípico de servicios
- **Descripción**: Detecta prestadores con volúmenes anómalos de servicios
- **Ejemplos**: Prestador factura 100 cirugías en un día
- **Severidad**: Alta
- **Implementación**: Análisis estadístico de volúmenes por prestador

### 3. Detección de Fraude

#### AI-FRAUD-001: Servicios costosos sin soporte clínico
- **Descripción**: Detecta servicios de alto costo sin justificación clínica
- **Ejemplos**: Hospitalización facturada sin diagnóstico que la justifique
- **Severidad**: Alta
- **Implementación**: IA analiza correlación costo-diagnóstico-procedimiento

#### AI-FRAUD-002: Patrones de facturación sospechosos
- **Descripción**: Detecta patrones de facturación que sugieren fraude
- **Ejemplos**: 
  - Siempre facturar el máximo permitido
  - Servicios fantasma
  - Baja variabilidad en procedimientos
- **Severidad**: Alta
- **Implementación**: Análisis de patrones mediante machine learning

## Distribución de Reglas por Archivo

| Archivo Excel | Determinísticas | IA | Total |
|---------------|-----------------|----| ------|
| RIPS_By_Norm_Catalogos_CUPS_CIE10_DANE.xlsx | 3 | 1 | 4 |
| RIPS_By_Norm_Resolucion_1884_2024.xlsx | 6 | 0 | 6 |
| RIPS_By_Norm_Lineamientos_FEV_RIPS.xlsx | 11 | 1 | 12 |
| RIPS_By_Norm_Resolucion_2275_2023.xlsx | 10 | 0 | 10 |
| RIPS_Validaciones_AI.xlsx | 3 | 6 | 9 |
| **TOTAL** | **33** | **8** | **41** |

## Severidad de Errores

### Bloqueantes
- Errores de estructura de archivo
- Campos obligatorios vacíos
- Formatos de fecha incorrectos
- Códigos inválidos en catálogos
- Incoherencias clínicas graves

### Advertencias
- Patrones atípicos de facturación
- Volúmenes anómalos de servicios
- Incoherencias clínicas menores
- Campos opcionales con formato incorrecto

## Referencias Normativas

- **Resolución 2275 de 2023**: Anexo Técnico (estructura RIPS/FEV)
- **Resolución 1884 de 2024**: Modificación Anexo Técnico 2 y reglas transitorias
- **Catálogos oficiales**: 
  - CUPS (MinSalud)
  - CIE-10/CIE-11 (MinSalud/SISPRO)
  - DANE (municipios/departamentos)
- **Lineamientos**: Generación/validación/envío RIPS-FEV (MinSalud)

## Implementación Técnica

### Validaciones Determinísticas
- Implementadas en `EnhancedDeterministicValidator`
- Validación campo por campo según reglas específicas
- Validación cruzada entre campos relacionados
- Generación de reportes detallados de errores

### Validaciones de IA
- Implementadas en `EnhancedAIValidator`
- Análisis de coherencia clínica
- Detección de patrones anómalos
- Clasificación de riesgo de fraude
- Aprendizaje continuo basado en históricos

### Integración
- Ambos validadores se ejecutan en paralelo
- Resultados consolidados en reporte único
- Clasificación automática de severidad
- API REST para integración con sistemas externos
