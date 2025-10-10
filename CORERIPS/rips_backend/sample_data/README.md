# Datos de Ejemplo RIPS

Este directorio contiene archivos de ejemplo para probar el sistema de validación RIPS.

## Archivos Disponibles

### AC_sample.txt
Archivo de consultas (AC) con datos válidos para pruebas exitosas.

**Estructura de campos:**
1. Código prestador (12 dígitos)
2. Razón social prestador
3. Tipo de documento
4. Número de documento
5. Primer apellido
6. Fecha de nacimiento (DD/MM/AAAA)
7. Sexo (M/F)
8. Código municipio
9. Zona residencial (U/R)
10. Incapacidad (S/N)
11. Fecha de consulta (DD/MM/AAAA)
12. Número de autorización
13. Código de consulta
14. Finalidad de consulta
15. Causa externa
16. Diagnóstico principal
17. Diagnóstico relacionado

### AC_invalid.txt
Archivo de consultas con errores intencionados para probar validaciones:

- **Línea 1**: Código prestador inválido (muy corto)
- **Línea 2**: Tipo de documento inválido (XX)
- **Línea 3**: Fecha en formato incorrecto y sexo inválido

## Uso

1. **Subir archivo válido:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/upload" \
        -H "Authorization: Bearer YOUR_TOKEN" \
        -F "file=@sample_data/AC_sample.txt"
   ```

2. **Subir archivo con errores:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/upload" \
        -H "Authorization: Bearer YOUR_TOKEN" \
        -F "file=@sample_data/AC_invalid.txt"
   ```

3. **Validar archivo:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/validate" \
        -H "Authorization: Bearer YOUR_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"file_id": 1, "validation_types": ["deterministic"]}'
   ```

## Resultados Esperados

### AC_sample.txt
- ✅ Sin errores de validación
- ✅ 3 líneas procesadas correctamente

### AC_invalid.txt
- ❌ Error en línea 1: Código de prestador inválido
- ❌ Error en línea 2: Tipo de documento inválido
- ❌ Error en línea 3: Fecha inválida y sexo inválido
