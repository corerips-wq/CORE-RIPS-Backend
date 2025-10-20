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
        
        # Fechas importantes para transición CIE-10/CIE-11 (Resolución 1442/1657 de 2024)
        self.fecha_inicio_cie11 = date(2024, 8, 14)  # Inicio CIE-11
        self.fecha_fin_coexistencia = date(2027, 8, 14)  # Fin coexistencia CIE-10/CIE-11
        
        # Diagnósticos obstétricos (para validación con sexo)
        # Códigos CIE-10 del capítulo O (Embarazo, parto y puerperio)
        self.codigos_obstetricos = set()  # Se inicializará con catálogo
        self.codigos_cie10_validos = set()  # Catálogo CIE-10
        self.codigos_cie11_validos = set()  # Catálogo CIE-11
        self.codigos_cups_validos = {}  # {código: {vigencia_inicio, vigencia_fin, tipo_servicio, etc}}
        self.mapa_cie_cups = {}  # Mapeo de correspondencia CIE-CUPS
        
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
    
    # ========================================================================
    # REGLAS CIE11 - Resolución 1442/1657 de 2024
    # ========================================================================
    
    def validate_cie11_001_transicion_cie10_cie11(self, codigo_cie: str, fecha_servicio: date, line_number: int) -> List[ErrorResponse]:
        """
        CIE11_001: Validar que los códigos CIE correspondan a CIE-10 o CIE-11 según fecha del servicio.
        - Antes del 14/08/2024: Solo CIE-10
        - Después del 14/08/2024: CIE-10 o CIE-11
        """
        errors = []
        
        if fecha_servicio < self.fecha_inicio_cie11:
            # Antes del 14/08/2024: Solo CIE-10 permitido
            if not self._is_valid_cie10(codigo_cie):
                errors.append(ErrorResponse(
                    line=line_number,
                    field="codigo_cie",
                    error=f"[CIE11_001] Código CIE '{codigo_cie}' no válido. Antes del 14/08/2024 solo se permiten códigos CIE-10."
                ))
        else:
            # Después del 14/08/2024: CIE-10 o CIE-11 permitidos
            if not (self._is_valid_cie10(codigo_cie) or self._is_valid_cie11(codigo_cie)):
                errors.append(ErrorResponse(
                    line=line_number,
                    field="codigo_cie",
                    error=f"[CIE11_001] Código CIE '{codigo_cie}' no existe en catálogos CIE-10 ni CIE-11."
                ))
        
        return errors
    
    def validate_cie11_002_coexistencia(self, codigo_cie: str, fecha_servicio: date, line_number: int) -> List[ErrorResponse]:
        """
        CIE11_002: Permitir coexistencia de CIE-10 y CIE-11 hasta el 14/08/2027.
        Después de esa fecha, solo CIE-11 será válido.
        """
        errors = []
        
        if fecha_servicio > self.fecha_fin_coexistencia:
            # Después del 14/08/2027: Solo CIE-11
            if not self._is_valid_cie11(codigo_cie):
                errors.append(ErrorResponse(
                    line=line_number,
                    field="codigo_cie",
                    error=f"[CIE11_002] Después del 14/08/2027 solo se permiten códigos CIE-11. Código '{codigo_cie}' no es CIE-11 válido."
                ))
        
        return errors
    
    def validate_cie11_003_existencia_catalogo(self, codigo_cie: str, line_number: int) -> List[ErrorResponse]:
        """
        CIE11_003: Verificar que el código CIE exista en el catálogo oficial (CIE-10 o CIE-11).
        """
        errors = []
        
        if not (self._is_valid_cie10(codigo_cie) or self._is_valid_cie11(codigo_cie)):
            errors.append(ErrorResponse(
                line=line_number,
                field="codigo_cie",
                error=f"[CIE11_003] Código CIE '{codigo_cie}' no existe en catálogos oficiales CIE-10/CIE-11."
            ))
        
        return errors
    
    def validate_cie11_004_compatibilidad_sexo(self, codigo_cie: str, sexo: str, line_number: int) -> List[ErrorResponse]:
        """
        CIE11_004: Validar que el diagnóstico principal sea compatible con el sexo del paciente.
        Ejemplo: Diagnósticos obstétricos solo para sexo femenino.
        """
        errors = []
        
        # Verificar diagnósticos obstétricos (capítulo O de CIE-10)
        if sexo == "M" and codigo_cie.upper().startswith("O"):
            errors.append(ErrorResponse(
                line=line_number,
                field="diagnostico_principal",
                error=f"[CIE11_004] Diagnóstico obstétrico '{codigo_cie}' no es compatible con sexo masculino."
            ))
        
        # Diagnósticos específicos de hombre
        codigos_masculinos = ["N40", "N41", "N42", "N43", "N44", "N45", "N46", "N47", "N48", "N49", "N50"]
        if sexo == "F" and any(codigo_cie.upper().startswith(cod) for cod in codigos_masculinos):
            errors.append(ErrorResponse(
                line=line_number,
                field="diagnostico_principal",
                error=f"[CIE11_004] Diagnóstico '{codigo_cie}' es específico del sexo masculino."
            ))
        
        return errors
    
    def validate_cie11_005_correspondencia_cie_cups(self, codigo_cie: str, codigo_cups: str, line_number: int) -> List[ErrorResponse]:
        """
        CIE11_005: Verificar correspondencia entre diagnóstico (CIE) y procedimiento (CUPS).
        Debe existir correspondencia clínica lógica entre diagnóstico y procedimiento.
        """
        errors = []
        
        # Esta validación requiere un mapeo de correspondencias CIE-CUPS
        # Por ahora validamos casos básicos
        
        # Ejemplo: Procedimientos obstétricos requieren diagnósticos obstétricos
        procedimientos_obstetricos = ["869", "870", "871", "872", "873", "874"]  # Códigos CUPS de partos
        if any(codigo_cups.startswith(proc) for proc in procedimientos_obstetricos):
            if not codigo_cie.upper().startswith("O"):
                errors.append(ErrorResponse(
                    line=line_number,
                    field="codigo_cie",
                    error=f"[CIE11_005] Procedimiento obstétrico '{codigo_cups}' requiere diagnóstico obstétrico (capítulo O), encontrado '{codigo_cie}'."
                ))
        
        return errors
    
    # ========================================================================
    # REGLAS CUPS - Resolución 2641 de 2024
    # ========================================================================
    
    def validate_r2641_d001_cups_existencia(self, codigo_cups: str, line_number: int) -> List[ErrorResponse]:
        """
        R2641-D001: Validar que el código CUPS exista en el catálogo oficial vigente.
        """
        errors = []
        
        if not self._is_valid_cups(codigo_cups):
            errors.append(ErrorResponse(
                line=line_number,
                field="codigo_cups",
                error=f"[R2641-D001] Código CUPS '{codigo_cups}' no existe en el catálogo oficial."
            ))
        
        return errors
    
    def validate_r2641_d002_cups_vigencia(self, codigo_cups: str, fecha_servicio: date, line_number: int) -> List[ErrorResponse]:
        """
        R2641-D002: Verificar que el CUPS esté vigente en la fecha del servicio.
        """
        errors = []
        
        # Validar si el código está vigente en la fecha indicada
        cups_info = self.codigos_cups_validos.get(codigo_cups)
        if cups_info:
            vigencia_inicio = cups_info.get("vigencia_inicio")
            vigencia_fin = cups_info.get("vigencia_fin")
            
            if vigencia_inicio and fecha_servicio < vigencia_inicio:
                errors.append(ErrorResponse(
                    line=line_number,
                    field="codigo_cups",
                    error=f"[R2641-D002] CUPS '{codigo_cups}' aún no estaba vigente en {fecha_servicio}. Vigencia desde {vigencia_inicio}."
                ))
            
            if vigencia_fin and fecha_servicio > vigencia_fin:
                errors.append(ErrorResponse(
                    line=line_number,
                    field="codigo_cups",
                    error=f"[R2641-D002] CUPS '{codigo_cups}' ya no está vigente en {fecha_servicio}. Vigencia hasta {vigencia_fin}."
                ))
        
        return errors
    
    def validate_r2641_d003_cups_tipo_servicio(self, codigo_cups: str, tipo_servicio: str, line_number: int) -> List[ErrorResponse]:
        """
        R2641-D003: Validar que el CUPS pertenezca al tipo de servicio reportado.
        """
        errors = []
        
        cups_info = self.codigos_cups_validos.get(codigo_cups)
        if cups_info:
            tipo_esperado = cups_info.get("tipo_servicio")
            if tipo_esperado and tipo_servicio and tipo_servicio != tipo_esperado:
                errors.append(ErrorResponse(
                    line=line_number,
                    field="codigo_cups",
                    error=f"[R2641-D003] CUPS '{codigo_cups}' no corresponde al tipo de servicio '{tipo_servicio}'. Tipo esperado: '{tipo_esperado}'."
                ))
        
        return errors
    
    def validate_r2641_d005_cups_grupo_etario(self, codigo_cups: str, edad: int, line_number: int) -> List[ErrorResponse]:
        """
        R2641-D005: Validar coherencia entre el grupo etario permitido y el CUPS.
        """
        errors = []
        
        cups_info = self.codigos_cups_validos.get(codigo_cups)
        if cups_info:
            edad_minima = cups_info.get("edad_minima")
            edad_maxima = cups_info.get("edad_maxima")
            
            if edad_minima is not None and edad < edad_minima:
                errors.append(ErrorResponse(
                    line=line_number,
                    field="codigo_cups",
                    error=f"[R2641-D005] CUPS '{codigo_cups}' requiere edad mínima de {edad_minima} años. Edad del paciente: {edad}."
                ))
            
            if edad_maxima is not None and edad > edad_maxima:
                errors.append(ErrorResponse(
                    line=line_number,
                    field="codigo_cups",
                    error=f"[R2641-D005] CUPS '{codigo_cups}' requiere edad máxima de {edad_maxima} años. Edad del paciente: {edad}."
                ))
        
        return errors
    
    def validate_r2641_d006_cups_sexo(self, codigo_cups: str, sexo: str, line_number: int) -> List[ErrorResponse]:
        """
        R2641-D006: Validar coherencia entre el sexo y el CUPS.
        Ejemplo: Partos solo aplican a sexo femenino.
        """
        errors = []
        
        # Procedimientos exclusivos de mujeres
        procedimientos_femeninos = ["869", "870", "871", "872", "873", "874"]  # Partos
        if any(codigo_cups.startswith(proc) for proc in procedimientos_femeninos):
            if sexo != "F":
                errors.append(ErrorResponse(
                    line=line_number,
                    field="codigo_cups",
                    error=f"[R2641-D006] CUPS '{codigo_cups}' (procedimiento ginecológico/obstétrico) solo aplica a sexo femenino."
                ))
        
        # Procedimientos exclusivos de hombres
        procedimientos_masculinos = ["770", "771", "772"]  # Urología masculina específica
        if any(codigo_cups.startswith(proc) for proc in procedimientos_masculinos):
            if sexo != "M":
                errors.append(ErrorResponse(
                    line=line_number,
                    field="codigo_cups",
                    error=f"[R2641-D006] CUPS '{codigo_cups}' (procedimiento urológico masculino) solo aplica a sexo masculino."
                ))
        
        return errors
    
    def validate_r2641_d004_cups_tarifa(self, codigo_cups: str, line_number: int) -> List[ErrorResponse]:
        """
        R2641-D004: Verificar que el CUPS tenga un valor tarifario definido en el catálogo.
        Severidad: Advertencia (algunos CUPS informativos pueden carecer de tarifa).
        """
        errors = []
        
        cups_info = self.codigos_cups_validos.get(codigo_cups)
        if cups_info:
            tarifa = cups_info.get("tarifa") or cups_info.get("valor")
            if tarifa is None or tarifa == 0:
                errors.append(ErrorResponse(
                    line=line_number,
                    field="codigo_cups",
                    error=f"[R2641-D004] ADVERTENCIA: CUPS '{codigo_cups}' no tiene valor tarifario definido."
                ))
        
        return errors
    
    def validate_r2641_d007_cups_cie_asociado(self, codigo_cups: str, codigo_cie: str, line_number: int) -> List[ErrorResponse]:
        """
        R2641-D007: Verificar que el CUPS esté asociado a un código CIE válido.
        Validación cruzada con diagnóstico principal.
        """
        errors = []
        
        # Validar que ambos códigos sean válidos
        if not self._is_valid_cups(codigo_cups):
            return errors  # Ya se validó en R2641-D001
        
        if not (self._is_valid_cie10(codigo_cie) or self._is_valid_cie11(codigo_cie)):
            return errors  # Ya se validó en CIE11_003
        
        # Si existe mapeo CIE-CUPS, verificar correspondencia
        if self.mapa_cie_cups and codigo_cups in self.mapa_cie_cups:
            codigos_cie_permitidos = self.mapa_cie_cups[codigo_cups]
            if codigo_cie not in codigos_cie_permitidos:
                errors.append(ErrorResponse(
                    line=line_number,
                    field="codigo_cups",
                    error=f"[R2641-D007] CUPS '{codigo_cups}' no está asociado con el diagnóstico CIE '{codigo_cie}'."
                ))
        
        return errors
    
    def validate_r2641_d008_cups_duplicados(self, registros: List[Dict], line_number: int) -> List[ErrorResponse]:
        """
        R2641-D008: Validar que el CUPS no se repita en un mismo episodio con igual fecha y diagnóstico.
        """
        errors = []
        
        # Esta validación requiere acceso a múltiples registros
        # Se implementará cuando se tenga el contexto completo del archivo
        
        return errors
    
    def validate_r2641_d009_cups_finalidad(self, codigo_cups: str, line_number: int) -> List[ErrorResponse]:
        """
        R2641-D009: Validar que el CUPS reportado tenga tipo de finalidad asignado.
        """
        errors = []
        
        cups_info = self.codigos_cups_validos.get(codigo_cups)
        if cups_info:
            finalidad = cups_info.get("finalidad") or cups_info.get("tipo_finalidad")
            if not finalidad:
                errors.append(ErrorResponse(
                    line=line_number,
                    field="codigo_cups",
                    error=f"[R2641-D009] CUPS '{codigo_cups}' no tiene tipo de finalidad asignado."
                ))
        
        return errors
    
    def validate_r2641_d010_cups_obligatorios(self, cups_presentes: List[str], tipo_evento: str, line_number: int) -> List[ErrorResponse]:
        """
        R2641-D010: Verificar que los CUPS obligatorios según tipo de evento estén presentes.
        Aplica para urgencias o control.
        """
        errors = []
        
        # Definir CUPS obligatorios por tipo de evento
        cups_obligatorios_por_evento = {
            "urgencia": ["890201", "890202"],  # Atención inicial urgencias
            "control": ["890301", "890302"],   # Consulta de control
            "hospitalizacion": ["890401"]      # Atención hospitalaria
        }
        
        if tipo_evento in cups_obligatorios_por_evento:
            cups_requeridos = cups_obligatorios_por_evento[tipo_evento]
            cups_faltantes = [cup for cup in cups_requeridos if cup not in cups_presentes]
            
            if cups_faltantes:
                errors.append(ErrorResponse(
                    line=line_number,
                    field="codigo_cups",
                    error=f"[R2641-D010] ADVERTENCIA: Faltan CUPS obligatorios para tipo de evento '{tipo_evento}': {', '.join(cups_faltantes)}."
                ))
        
        return errors
    
    # ========================================================================
    # REGLAS DE CATÁLOGOS BÁSICOS - CUPS/CIE10/DANE
    # ========================================================================
    
    def validate_us001_tipo_documento_catalogo(self, tipo_documento: str, line_number: int) -> List[ErrorResponse]:
        """
        US-001: Validar que el tipo de documento esté en el catálogo DIAN/MinSalud.
        Valores permitidos: CC, TI, RC, CE, PA, NUIP, MS
        Severidad: Bloqueante
        """
        errors = []
        
        if tipo_documento not in self.valid_document_types:
            errors.append(ErrorResponse(
                line=line_number,
                field="tipo_documento_usuario",
                error=f"[US-001] Tipo de documento '{tipo_documento}' no válido. Valores permitidos: {', '.join(self.valid_document_types)}."
            ))
        
        return errors
    
    def validate_ac012_diagnostico_principal_vigencia(self, codigo_cie: str, fecha_servicio: date, line_number: int) -> List[ErrorResponse]:
        """
        AC-012: Validar existencia y vigencia del diagnóstico principal CIE.
        Debe existir en catálogos CIE-10/CIE-11 según vigencia y tener coherencia clínica.
        Severidad: Bloqueante
        """
        errors = []
        
        # Validar existencia en catálogo
        if not (self._is_valid_cie10(codigo_cie) or self._is_valid_cie11(codigo_cie)):
            errors.append(ErrorResponse(
                line=line_number,
                field="diagnostico_principal_cie",
                error=f"[AC-012] Diagnóstico principal '{codigo_cie}' no existe en catálogos CIE-10/CIE-11."
            ))
            return errors
        
        # Validar vigencia según fecha
        # Antes del 14/08/2024: solo CIE-10
        if fecha_servicio < self.fecha_inicio_cie11:
            if not self._is_valid_cie10(codigo_cie):
                errors.append(ErrorResponse(
                    line=line_number,
                    field="diagnostico_principal_cie",
                    error=f"[AC-012] Diagnóstico '{codigo_cie}' no es CIE-10 válido. Solo CIE-10 permitido antes del 14/08/2024."
                ))
        
        # Después del 14/08/2027: solo CIE-11
        if fecha_servicio > self.fecha_fin_coexistencia:
            if not self._is_valid_cie11(codigo_cie):
                errors.append(ErrorResponse(
                    line=line_number,
                    field="diagnostico_principal_cie",
                    error=f"[AC-012] Diagnóstico '{codigo_cie}' no es CIE-11 válido. Solo CIE-11 permitido después del 14/08/2027."
                ))
        
        return errors
    
    def validate_ap001_cups_existencia_vigencia(self, codigo_cups: str, fecha_servicio: date, line_number: int) -> List[ErrorResponse]:
        """
        AP-001: Validar existencia en catálogo CUPS y vigencia.
        El código CUPS debe existir y estar vigente en la fecha del servicio.
        Severidad: Bloqueante
        """
        errors = []
        
        # Validar existencia
        if not self._is_valid_cups(codigo_cups):
            errors.append(ErrorResponse(
                line=line_number,
                field="codigo_cups",
                error=f"[AP-001] Código CUPS '{codigo_cups}' no existe en el catálogo oficial."
            ))
            return errors
        
        # Validar vigencia
        cups_info = self.codigos_cups_validos.get(codigo_cups)
        if cups_info:
            vigencia_inicio = cups_info.get("vigencia_inicio")
            vigencia_fin = cups_info.get("vigencia_fin")
            
            if vigencia_inicio and fecha_servicio < vigencia_inicio:
                errors.append(ErrorResponse(
                    line=line_number,
                    field="codigo_cups",
                    error=f"[AP-001] CUPS '{codigo_cups}' no estaba vigente en {fecha_servicio}. Vigencia desde {vigencia_inicio}."
                ))
            
            if vigencia_fin and fecha_servicio > vigencia_fin:
                errors.append(ErrorResponse(
                    line=line_number,
                    field="codigo_cups",
                    error=f"[AP-001] CUPS '{codigo_cups}' ya no está vigente en {fecha_servicio}. Vigencia hasta {vigencia_fin}."
                ))
        
        return errors
    
    def validate_am001_codigo_producto_catalogo(self, codigo_producto: str, line_number: int) -> List[ErrorResponse]:
        """
        AM-001: Validar existencia del código de producto en catálogos POS/GTIN/Código IPS.
        El código debe existir en al menos uno de los catálogos de medicamentos.
        Severidad: Bloqueante
        """
        errors = []
        
        # Validación básica de formato
        if not codigo_producto or len(codigo_producto) < 3 or len(codigo_producto) > 20:
            errors.append(ErrorResponse(
                line=line_number,
                field="codigo_producto",
                error=f"[AM-001] Código de producto '{codigo_producto}' tiene longitud inválida (mínimo 3, máximo 20 caracteres)."
            ))
            return errors
        
        # Aquí se debería validar contra catálogos POS/GTIN
        # Por ahora solo validación de formato básica
        if not re.match(r'^[A-Za-z0-9\-]+$', codigo_producto):
            errors.append(ErrorResponse(
                line=line_number,
                field="codigo_producto",
                error=f"[AM-001] Código de producto '{codigo_producto}' contiene caracteres no permitidos. Solo alfanuméricos y guiones."
            ))
        
        return errors
    
    # ========================================================================
    # VALIDACIONES CRUZADAS ENTRE CAMPOS
    # ========================================================================
    
    def validate_edad_sexo_diagnostico(self, edad: int, sexo: str, codigo_cie: str, line_number: int) -> List[ErrorResponse]:
        """
        Validar coherencia entre edad, sexo y diagnóstico.
        Combina validaciones de múltiples reglas.
        """
        errors = []
        
        # Validar diagnósticos obstétricos
        if sexo == "M" and codigo_cie.upper().startswith("O"):
            errors.append(ErrorResponse(
                line=line_number,
                field="diagnostico_principal",
                error=f"[CRUZADA] Diagnóstico obstétrico '{codigo_cie}' no es compatible con sexo masculino."
            ))
        
        # Validar diagnósticos pediátricos en adultos mayores
        diagnosticos_pediatricos = ["P00", "P01", "P02", "P03", "P04", "P05", "P07", "P08", "P10", "P15"]
        if edad > 18 and any(codigo_cie.upper().startswith(cod) for cod in diagnosticos_pediatricos):
            errors.append(ErrorResponse(
                line=line_number,
                field="diagnostico_principal",
                error=f"[CRUZADA] ADVERTENCIA: Diagnóstico pediátrico '{codigo_cie}' en paciente de {edad} años."
            ))
        
        # Validar diagnósticos geriátricos en menores
        if edad < 60:
            diagnosticos_geriatricos = ["R54"]  # Senilidad
            if any(codigo_cie.upper().startswith(cod) for cod in diagnosticos_geriatricos):
                errors.append(ErrorResponse(
                    line=line_number,
                    field="diagnostico_principal",
                    error=f"[CRUZADA] ADVERTENCIA: Diagnóstico geriátrico '{codigo_cie}' en paciente de {edad} años."
                ))
        
        return errors
    
    def validate_diagnostico_procedimiento(self, codigo_cie: str, codigo_cups: str, line_number: int) -> List[ErrorResponse]:
        """
        Validar coherencia entre diagnóstico y procedimiento.
        Verifica que exista correspondencia clínica lógica.
        """
        errors = []
        
        # Procedimientos quirúrgicos con diagnósticos incompatibles
        # Ejemplo: Cirugía cardíaca con diagnóstico dermatológico
        procedimientos_cardiovasculares = ["373", "374", "375", "376"]  # Cirugía cardíaca
        if any(codigo_cups.startswith(proc) for proc in procedimientos_cardiovasculares):
            if not codigo_cie.upper().startswith("I"):  # CIE-10 capítulo I: Enfermedades cardiovasculares
                errors.append(ErrorResponse(
                    line=line_number,
                    field="codigo_cups",
                    error=f"[CRUZADA] ADVERTENCIA: Procedimiento cardiovascular '{codigo_cups}' con diagnóstico no cardiovascular '{codigo_cie}'."
                ))
        
        return errors
    
    # ========================================================================
    # MÉTODOS AUXILIARES PARA CONSULTA DE CATÁLOGOS
    # ========================================================================
    
    def _is_valid_cie10(self, codigo: str) -> bool:
        """Verificar si un código es CIE-10 válido"""
        if not codigo:
            return False
        
        # Si hay catálogo cargado, usar el catálogo
        if self.codigos_cie10_validos:
            return codigo.upper() in self.codigos_cie10_validos
        
        # Validación básica de formato CIE-10
        # Formatos válidos: A00, A00.1, A001 (letra + 2-3 dígitos + opcional .X)
        # CIE-10 puede tener hasta 4 caracteres después de la letra (ej: O80.1)
        pattern = r'^[A-Z]\d{2,3}(\.\d{1,2})?$'
        return bool(re.match(pattern, codigo.upper()))
    
    def _is_valid_cie11(self, codigo: str) -> bool:
        """Verificar si un código es CIE-11 válido"""
        if not codigo:
            return False
        
        # Si hay catálogo cargado, usar el catálogo
        if self.codigos_cie11_validos:
            return codigo.upper() in self.codigos_cie11_validos
        
        # Validación básica de formato CIE-11 (diferente de CIE-10)
        # CIE-11 comienza con dígito o tiene formato específico: 1A00, 2E65.0, etc.
        # Para distinguir de CIE-10, CIE-11 típicamente comienza con número
        # Sin catálogo cargado, asumimos que si hay catálogo se validará correctamente
        # Formato flexible: dígito al inicio o formato alfanumérico complejo
        codigo_upper = codigo.upper()
        
        # Si comienza con letra mayúscula seguida de 2-3 dígitos, probablemente es CIE-10
        if re.match(r'^[A-Z]\d{2,3}', codigo_upper):
            return False  # Formato CIE-10, no CIE-11
        
        # CIE-11 puede comenzar con número o tener formato complejo
        pattern = r'^[0-9][A-Z0-9]{1,}(\.[0-9A-Z]+)?$'
        return bool(re.match(pattern, codigo_upper))
    
    def _is_valid_cups(self, codigo: str) -> bool:
        """Verificar si un código CUPS es válido"""
        if not codigo:
            return False
        
        # Si hay catálogo cargado, usar el catálogo
        if self.codigos_cups_validos:
            return codigo in self.codigos_cups_validos
        
        # Validación básica de formato CUPS (numérico de 3-7 dígitos)
        return bool(re.match(r'^\d{3,7}$', codigo))
    
    def load_cie10_catalog(self, cie10_codes: set):
        """Cargar catálogo de códigos CIE-10"""
        self.codigos_cie10_validos = cie10_codes
        # Identificar códigos obstétricos (capítulo O)
        self.codigos_obstetricos = {code for code in cie10_codes if code.startswith('O')}
    
    def load_cie11_catalog(self, cie11_codes: set):
        """Cargar catálogo de códigos CIE-11"""
        self.codigos_cie11_validos = cie11_codes
    
    def load_cups_catalog(self, cups_data: Dict[str, Dict]):
        """
        Cargar catálogo de códigos CUPS con información adicional
        cups_data: {código: {vigencia_inicio, vigencia_fin, tipo_servicio, edad_minima, edad_maxima, ...}}
        """
        self.codigos_cups_validos = cups_data
    
    def load_cie_cups_mapping(self, mapping: Dict[str, List[str]]):
        """
        Cargar mapeo de correspondencia CIE-CUPS
        mapping: {codigo_cups: [lista_de_codigos_cie_compatibles]}
        """
        self.mapa_cie_cups = mapping
