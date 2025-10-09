import re
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from models.schemas import ErrorResponse

class EnhancedDeterministicValidator:
    """Validador determinístico mejorado basado en reglas específicas de los archivos Excel"""
    
    def __init__(self):
        # Catálogos basados en las reglas extraídas
        self.valid_document_types = ["CC", "TI", "RC", "CE", "PA", "NUIP", "MS"]
        self.valid_sexes = ["M", "F"]
        self.valid_regimes = ["C", "S", "E", "P"]
        self.valid_note_types = ["NC", "ND"]  # Notas crédito/débito
        self.valid_control_types = ["1"]  # Solo tipo 1 para control
        
        # Mapeo de archivos RIPS y sus campos obligatorios
        self.file_structures = {
            "CT": {  # Control
                "fields": ["TIPO_REGISTRO", "FECHA_GENERACION", "VERSION_ANEXO_TECNICO"],
                "field_rules": {
                    "TIPO_REGISTRO": {"type": "numeric", "min_len": 1, "max_len": 1, "mandatory": True, "values": ["1"]},
                    "FECHA_GENERACION": {"type": "date", "min_len": 10, "max_len": 10, "mandatory": True, "format": "YYYY-MM-DD"},
                    "VERSION_ANEXO_TECNICO": {"type": "string", "min_len": 1, "max_len": 20, "mandatory": True}
                }
            },
            "US": {  # Usuarios
                "fields": ["TIPO_DOCUMENTO_USUARIO", "NUMERO_DOCUMENTO_USUARIO", "FECHA_NACIMIENTO", "SEXO"],
                "field_rules": {
                    "TIPO_DOCUMENTO_USUARIO": {"type": "code", "min_len": 1, "max_len": 2, "mandatory": True, "values": self.valid_document_types},
                    "NUMERO_DOCUMENTO_USUARIO": {"type": "string", "min_len": 1, "max_len": 20, "mandatory": True},
                    "FECHA_NACIMIENTO": {"type": "date", "min_len": 10, "max_len": 10, "mandatory": True, "format": "YYYY-MM-DD"},
                    "SEXO": {"type": "code", "min_len": 1, "max_len": 1, "mandatory": True, "values": self.valid_sexes}
                }
            },
            "AC": {  # Consultas
                "fields": ["CODIGO_PRESTADOR", "TIPO_DOCUMENTO_USUARIO", "NUMERO_DOCUMENTO_USUARIO", 
                          "FECHA_CONSULTA", "DIAGNOSTICO_PRINCIPAL_CIE"],
                "field_rules": {
                    "CODIGO_PRESTADOR": {"type": "numeric", "min_len": 12, "max_len": 12, "mandatory": True},
                    "TIPO_DOCUMENTO_USUARIO": {"type": "code", "min_len": 1, "max_len": 2, "mandatory": True, "values": self.valid_document_types},
                    "NUMERO_DOCUMENTO_USUARIO": {"type": "string", "min_len": 1, "max_len": 20, "mandatory": True},
                    "FECHA_CONSULTA": {"type": "date", "min_len": 10, "max_len": 10, "mandatory": True, "format": "YYYY-MM-DD"},
                    "DIAGNOSTICO_PRINCIPAL_CIE": {"type": "code", "min_len": 3, "max_len": 7, "mandatory": True}
                }
            },
            "AP": {  # Procedimientos
                "fields": ["CODIGO_PRESTADOR", "CODIGO_CUPS", "FECHA_PROCEDIMIENTO"],
                "field_rules": {
                    "CODIGO_PRESTADOR": {"type": "numeric", "min_len": 12, "max_len": 12, "mandatory": True},
                    "CODIGO_CUPS": {"type": "string", "min_len": 3, "max_len": 7, "mandatory": True},
                    "FECHA_PROCEDIMIENTO": {"type": "date", "min_len": 10, "max_len": 10, "mandatory": True, "format": "YYYY-MM-DD"}
                }
            },
            "AM": {  # Medicamentos
                "fields": ["CODIGO_PRESTADOR", "CODIGO_PRODUCTO"],
                "field_rules": {
                    "CODIGO_PRESTADOR": {"type": "numeric", "min_len": 12, "max_len": 12, "mandatory": True},
                    "CODIGO_PRODUCTO": {"type": "string", "min_len": 3, "max_len": 20, "mandatory": True}
                }
            },
            "AF": {  # Facturación
                "fields": ["CODIGO_PRESTADOR", "CUV"],
                "field_rules": {
                    "CODIGO_PRESTADOR": {"type": "numeric", "min_len": 12, "max_len": 12, "mandatory": True},
                    "CUV": {"type": "string", "min_len": 10, "max_len": 64, "mandatory": False}  # Condicional
                }
            },
            "AD": {  # Ajustes/Notas
                "fields": ["TIPO_NOTA"],
                "field_rules": {
                    "TIPO_NOTA": {"type": "code", "min_len": 1, "max_len": 2, "mandatory": True, "values": self.valid_note_types}
                }
            }
        }
    
    def validate_file(self, file_path: str, file_type: str = "AC") -> List[ErrorResponse]:
        """Validar archivo RIPS completo con reglas específicas"""
        errors = []
        
        if file_type not in self.file_structures:
            errors.append(ErrorResponse(
                line=0,
                field="file_type",
                error=f"Tipo de archivo no soportado: {file_type}"
            ))
            return errors
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line_number, line in enumerate(file, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    fields = line.split('|')
                    line_errors = self._validate_line_enhanced(fields, line_number, file_type)
                    errors.extend(line_errors)
                    
        except Exception as e:
            errors.append(ErrorResponse(
                line=0,
                field="file",
                error=f"Error al leer archivo: {str(e)}"
            ))
        
        return errors
    
    def _validate_line_enhanced(self, fields: List[str], line_number: int, file_type: str) -> List[ErrorResponse]:
        """Validar línea con reglas específicas del tipo de archivo"""
        errors = []
        file_structure = self.file_structures[file_type]
        field_rules = file_structure["field_rules"]
        
        # Validar número de campos (básico)
        expected_min_fields = len(field_rules)
        if len(fields) < expected_min_fields:
            errors.append(ErrorResponse(
                line=line_number,
                field="estructura",
                error=f"Número insuficiente de campos. Mínimo esperado: {expected_min_fields}, Encontrado: {len(fields)}"
            ))
            return errors
        
        # Validar cada campo según sus reglas
        field_names = list(field_rules.keys())
        for i, field_name in enumerate(field_names):
            if i >= len(fields):
                break
                
            field_value = fields[i]
            rule = field_rules[field_name]
            
            field_errors = self._validate_field_by_rule(field_value, field_name, rule, line_number)
            errors.extend(field_errors)
        
        return errors
    
    def _validate_field_by_rule(self, value: str, field_name: str, rule: Dict, line_number: int) -> List[ErrorResponse]:
        """Validar un campo específico según su regla"""
        errors = []
        
        # Validar campo obligatorio
        if rule.get("mandatory", False) and not value:
            errors.append(ErrorResponse(
                line=line_number,
                field=field_name,
                error=f"Campo obligatorio vacío"
            ))
            return errors
        
        if not value and not rule.get("mandatory", False):
            return errors  # Campo opcional vacío es válido
        
        # Validar longitud
        min_len = rule.get("min_len", 0)
        max_len = rule.get("max_len", float('inf'))
        
        if len(value) < min_len:
            errors.append(ErrorResponse(
                line=line_number,
                field=field_name,
                error=f"Longitud insuficiente. Mínimo: {min_len}, Actual: {len(value)}"
            ))
        
        if len(value) > max_len:
            errors.append(ErrorResponse(
                line=line_number,
                field=field_name,
                error=f"Longitud excesiva. Máximo: {max_len}, Actual: {len(value)}"
            ))
        
        # Validar tipo de dato
        data_type = rule.get("type", "string")
        type_errors = self._validate_data_type(value, data_type, field_name, line_number, rule)
        errors.extend(type_errors)
        
        # Validar valores permitidos
        allowed_values = rule.get("values", [])
        if allowed_values and value not in allowed_values:
            errors.append(ErrorResponse(
                line=line_number,
                field=field_name,
                error=f"Valor no permitido. Valores válidos: {', '.join(allowed_values)}"
            ))
        
        return errors
    
    def _validate_data_type(self, value: str, data_type: str, field_name: str, line_number: int, rule: Dict) -> List[ErrorResponse]:
        """Validar tipo de dato específico"""
        errors = []
        
        if data_type == "numeric":
            if not value.isdigit():
                errors.append(ErrorResponse(
                    line=line_number,
                    field=field_name,
                    error="Debe ser numérico"
                ))
        
        elif data_type == "date":
            date_format = rule.get("format", "YYYY-MM-DD")
            if not self._validate_date_format(value, date_format):
                errors.append(ErrorResponse(
                    line=line_number,
                    field=field_name,
                    error=f"Formato de fecha inválido. Esperado: {date_format}"
                ))
            else:
                # Validar lógica de fecha
                date_errors = self._validate_date_logic(value, field_name, line_number)
                errors.extend(date_errors)
        
        elif data_type == "code":
            # Los códigos deben ser alfanuméricos
            if not re.match(r'^[A-Za-z0-9]+$', value):
                errors.append(ErrorResponse(
                    line=line_number,
                    field=field_name,
                    error="Código debe ser alfanumérico"
                ))
        
        elif data_type == "string":
            # Validar caracteres especiales si es necesario
            if not re.match(r'^[A-Za-z0-9\s\-_.,]+$', value):
                errors.append(ErrorResponse(
                    line=line_number,
                    field=field_name,
                    error="Contiene caracteres no permitidos"
                ))
        
        return errors
    
    def _validate_date_format(self, date_str: str, format_type: str) -> bool:
        """Validar formato de fecha"""
        try:
            if format_type == "YYYY-MM-DD":
                datetime.strptime(date_str, '%Y-%m-%d')
            elif format_type == "DD/MM/YYYY":
                datetime.strptime(date_str, '%d/%m/%Y')
            else:
                return False
            return True
        except ValueError:
            return False
    
    def _validate_date_logic(self, date_str: str, field_name: str, line_number: int) -> List[ErrorResponse]:
        """Validar lógica de fechas (no futuras, coherencia, etc.)"""
        errors = []
        
        try:
            if '-' in date_str:
                parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            else:
                parsed_date = datetime.strptime(date_str, '%d/%m/%Y').date()
            
            today = date.today()
            
            # Fecha no puede ser futura (excepto para algunos casos específicos)
            if parsed_date > today and field_name not in ["FECHA_VENCIMIENTO", "FECHA_PROGRAMADA"]:
                errors.append(ErrorResponse(
                    line=line_number,
                    field=field_name,
                    error="La fecha no puede ser futura"
                ))
            
            # Validar fechas de nacimiento
            if field_name == "FECHA_NACIMIENTO":
                # No puede ser mayor a 150 años
                min_birth_date = date(today.year - 150, today.month, today.day)
                if parsed_date < min_birth_date:
                    errors.append(ErrorResponse(
                        line=line_number,
                        field=field_name,
                        error="Fecha de nacimiento muy antigua (>150 años)"
                    ))
        
        except ValueError:
            # Error de formato ya se maneja en _validate_date_format
            pass
        
        return errors
    
    def validate_cross_field_rules(self, fields: List[str], file_type: str, line_number: int) -> List[ErrorResponse]:
        """Validar reglas que involucran múltiples campos"""
        errors = []
        
        if file_type == "US" and len(fields) >= 4:
            # Validar coherencia edad-sexo para usuarios
            try:
                birth_date_str = fields[2]  # FECHA_NACIMIENTO
                sex = fields[3]  # SEXO
                
                if birth_date_str and sex:
                    birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
                    age = (date.today() - birth_date).days // 365
                    
                    # Ejemplo: validaciones específicas por edad y sexo
                    if age < 0:
                        errors.append(ErrorResponse(
                            line=line_number,
                            field="FECHA_NACIMIENTO",
                            error="Fecha de nacimiento resulta en edad negativa"
                        ))
            
            except (ValueError, IndexError):
                pass  # Errores de formato ya se manejan individualmente
        
        return errors
    
    def get_validation_summary(self, errors: List[ErrorResponse]) -> Dict[str, Any]:
        """Generar resumen de validación"""
        if not errors:
            return {
                "status": "success",
                "total_errors": 0,
                "error_types": {},
                "severity_distribution": {"bloqueante": 0, "advertencia": 0}
            }
        
        error_types = {}
        severity_dist = {"bloqueante": 0, "advertencia": 0}
        
        for error in errors:
            field = error.field
            error_types[field] = error_types.get(field, 0) + 1
            
            # Clasificar severidad basada en el tipo de error
            if any(keyword in error.error.lower() for keyword in ["obligatorio", "formato", "tipo"]):
                severity_dist["bloqueante"] += 1
            else:
                severity_dist["advertencia"] += 1
        
        return {
            "status": "error",
            "total_errors": len(errors),
            "error_types": error_types,
            "severity_distribution": severity_dist,
            "most_common_errors": sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:5]
        }
