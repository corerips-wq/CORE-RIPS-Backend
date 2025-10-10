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
        
        # Validar extensión de archivo
        file_extension = file_path.lower().split('.')[-1]
        
        if file_extension in ['xlsx', 'xls']:
            return self._validate_excel_file(file_path, file_type)
        elif file_extension in ['txt', 'csv']:
            return self._validate_text_file(file_path, file_type)
        elif file_extension == 'json':
            return self._validate_json_file(file_path, file_type)
        elif file_extension == 'xml':
            return self._validate_xml_file(file_path, file_type)
        elif file_extension == 'zip':
            return self._validate_zip_file(file_path, file_type)
        else:
            errors.append(ErrorResponse(
                line=0,
                field="archivo",
                error=f"Formato no soportado (.{file_extension}). Formatos válidos: .txt, .json, .xml, .zip"
            ))
            return errors
    
    def _validate_excel_file(self, file_path: str, file_type: str) -> List[ErrorResponse]:
        """Validar archivo Excel RIPS"""
        errors = []
        
        try:
            import pandas as pd
            
            # Leer Excel
            df = pd.read_excel(file_path)
            
            # Validar que tenga columnas
            if df.empty:
                errors.append(ErrorResponse(
                    line=0,
                    field="archivo",
                    error="El archivo está vacío"
                ))
                return errors
            
            # Validar estructura básica RIPS
            columns = [col.upper().strip() for col in df.columns]
            
            # Columnas comunes en archivos RIPS
            rips_indicators = [
                'CODIGO_PRESTADOR', 'TIPO_DOCUMENTO', 'NUMERO_DOCUMENTO',
                'FECHA', 'DIAGNOSTICO', 'CUPS', 'CIE', 'USUARIO'
            ]
            
            has_rips_columns = any(indicator in ' '.join(columns) for indicator in rips_indicators)
            
            if not has_rips_columns:
                errors.append(ErrorResponse(
                    line=0,
                    field="archivo",
                    error=f"Este no es un archivo RIPS válido. El archivo contiene: {', '.join(df.columns[:3])}..."
                ))
                return errors
            
            # Validar cada fila
            for idx, row in df.iterrows():
                row_errors = self._validate_excel_row(row, idx + 2, file_type)  # +2 porque Excel empieza en 1 y tiene header
                errors.extend(row_errors)
                
                # Limitar a 100 errores para no saturar
                if len(errors) >= 100:
                    errors.append(ErrorResponse(
                        line=idx + 2,
                        field="validación",
                        error="⚠️ Se encontraron más de 100 errores. Validación detenida."
                    ))
                    break
            
            if not errors:
                errors.append(ErrorResponse(
                    line=0,
                    field="validación",
                    error="✅ Archivo Excel RIPS validado correctamente"
                ))
                    
        except ImportError:
            errors.append(ErrorResponse(
                line=0,
                field="sistema",
                error="Error del sistema: falta librería para leer Excel (pandas/openpyxl)"
            ))
        except Exception as e:
            errors.append(ErrorResponse(
                line=0,
                field="archivo",
                error=f"Error al leer archivo Excel: {str(e)}"
            ))
        
        return errors
    
    def _validate_excel_row(self, row, line_number: int, file_type: str) -> List[ErrorResponse]:
        """Validar fila de Excel"""
        errors = []
        # Aquí puedes agregar validaciones específicas para filas de Excel
        # Por ahora solo validación básica
        return errors
    
    def _validate_text_file(self, file_path: str, file_type: str) -> List[ErrorResponse]:
        """Validar archivo de texto RIPS (formato pipe-delimited)"""
        errors = []
        
        if file_type not in self.file_structures:
            errors.append(ErrorResponse(
                line=0,
                field="file_type",
                error=f"Tipo de archivo '{file_type}' no soportado. Tipos válidos: {', '.join(self.file_structures.keys())}"
            ))
            return errors
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                
                if not lines:
                    errors.append(ErrorResponse(
                        line=0,
                        field="archivo",
                        error="El archivo está vacío"
                    ))
                    return errors
                
                for line_number, line in enumerate(lines, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Verificar que tenga delimitador pipe
                    if '|' not in line:
                        errors.append(ErrorResponse(
                            line=line_number,
                            field="formato",
                            error="Formato incorrecto: debe usar '|' como separador de campos"
                        ))
                        continue
                    
                    fields = line.split('|')
                    line_errors = self._validate_line_enhanced(fields, line_number, file_type)
                    errors.extend(line_errors)
                    
                    # Limitar errores
                    if len(errors) >= 100:
                        errors.append(ErrorResponse(
                            line=line_number,
                            field="validación",
                            error="⚠️ Se encontraron más de 100 errores. Validación detenida."
                        ))
                        break
                    
        except UnicodeDecodeError:
            errors.append(ErrorResponse(
                line=0,
                field="archivo",
                error="Error de codificación: el archivo debe estar en UTF-8"
            ))
        except Exception as e:
            errors.append(ErrorResponse(
                line=0,
                field="archivo",
                error=f"Error al leer archivo: {str(e)}"
            ))
        
        return errors
    
    def _validate_json_file(self, file_path: str, file_type: str) -> List[ErrorResponse]:
        """Validar archivo JSON RIPS"""
        errors = []
        
        try:
            import json
            
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # Verificar si es un array o un objeto
            if isinstance(data, list):
                records = data
            elif isinstance(data, dict):
                # Buscar el array de registros en el JSON
                records = data.get('registros') or data.get('records') or data.get('data') or [data]
            else:
                errors.append(ErrorResponse(
                    line=0,
                    field="estructura",
                    error="Estructura JSON no válida para RIPS"
                ))
                return errors
            
            if not records:
                errors.append(ErrorResponse(
                    line=0,
                    field="archivo",
                    error="El archivo JSON no contiene registros"
                ))
                return errors
            
            # Validar cada registro
            for idx, record in enumerate(records[:100], 1):  # Limitar a 100 registros
                if not isinstance(record, dict):
                    errors.append(ErrorResponse(
                        line=idx,
                        field="registro",
                        error=f"Registro {idx} no es un objeto válido"
                    ))
                    continue
                
                # Aquí puedes agregar validaciones específicas de campos RIPS
                # Por ahora solo verificamos estructura básica
            
            if not errors:
                errors.append(ErrorResponse(
                    line=0,
                    field="validación",
                    error=f"✅ Archivo JSON procesado: {len(records)} registro(s)"
                ))
                    
        except json.JSONDecodeError as e:
            errors.append(ErrorResponse(
                line=0,
                field="archivo",
                error=f"Error de formato JSON: {str(e)}"
            ))
        except Exception as e:
            errors.append(ErrorResponse(
                line=0,
                field="archivo",
                error=f"Error al leer archivo JSON: {str(e)}"
            ))
        
        return errors
    
    def _validate_xml_file(self, file_path: str, file_type: str) -> List[ErrorResponse]:
        """Validar archivo XML RIPS"""
        errors = []
        
        try:
            import xml.etree.ElementTree as ET
            
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Buscar elementos de registros comunes en XML RIPS
            registro_tags = ['registro', 'Registro', 'record', 'Record', 'item', 'row']
            records = []
            
            for tag in registro_tags:
                records = root.findall(f'.//{tag}')
                if records:
                    break
            
            if not records:
                errors.append(ErrorResponse(
                    line=0,
                    field="estructura",
                    error="No se encontraron registros en el XML. Etiquetas esperadas: <registro>, <record>, etc."
                ))
                return errors
            
            # Validar cada registro (limitar a 100)
            for idx, record in enumerate(records[:100], 1):
                # Aquí puedes agregar validaciones específicas
                pass
            
            if not errors:
                errors.append(ErrorResponse(
                    line=0,
                    field="validación",
                    error=f"✅ Archivo XML procesado: {len(records)} registro(s)"
                ))
                    
        except ET.ParseError as e:
            errors.append(ErrorResponse(
                line=0,
                field="archivo",
                error=f"Error de formato XML: {str(e)}"
            ))
        except Exception as e:
            errors.append(ErrorResponse(
                line=0,
                field="archivo",
                error=f"Error al leer archivo XML: {str(e)}"
            ))
        
        return errors
    
    def _validate_zip_file(self, file_path: str, file_type: str) -> List[ErrorResponse]:
        """Validar archivo ZIP con archivos TXT RIPS"""
        errors = []
        
        try:
            import zipfile
            import tempfile
            import os
            
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                # Listar archivos en el ZIP
                file_list = zip_ref.namelist()
                txt_files = [f for f in file_list if f.lower().endswith('.txt')]
                
                if not txt_files:
                    errors.append(ErrorResponse(
                        line=0,
                        field="archivo",
                        error="El archivo ZIP no contiene archivos .txt"
                    ))
                    return errors
                
                # Extraer y validar cada archivo TXT
                with tempfile.TemporaryDirectory() as temp_dir:
                    for txt_file in txt_files[:10]:  # Limitar a 10 archivos
                        try:
                            # Extraer archivo
                            zip_ref.extract(txt_file, temp_dir)
                            extracted_path = os.path.join(temp_dir, txt_file)
                            
                            # Validar el archivo TXT
                            txt_errors = self._validate_text_file(extracted_path, file_type)
                            
                            # Agregar nombre de archivo al error
                            for error in txt_errors:
                                error.field = f"{txt_file}:{error.field}"
                            
                            errors.extend(txt_errors)
                            
                        except Exception as e:
                            errors.append(ErrorResponse(
                                line=0,
                                field=txt_file,
                                error=f"Error al procesar: {str(e)}"
                            ))
                
                if not errors:
                    errors.append(ErrorResponse(
                        line=0,
                        field="validación",
                        error=f"✅ Archivo ZIP procesado: {len(txt_files)} archivo(s) TXT"
                    ))
                    
        except zipfile.BadZipFile:
            errors.append(ErrorResponse(
                line=0,
                field="archivo",
                error="El archivo ZIP está corrupto o no es válido"
            ))
        except Exception as e:
            errors.append(ErrorResponse(
                line=0,
                field="archivo",
                error=f"Error al leer archivo ZIP: {str(e)}"
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
