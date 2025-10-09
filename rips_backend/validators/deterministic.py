import re
from datetime import datetime
from typing import List, Dict, Any
from models.schemas import ErrorResponse

class DeterministicValidator:
    """Validador determinístico para archivos RIPS"""
    
    def __init__(self):
        # Catálogos básicos para validación
        self.valid_sexes = ["M", "F"]
        self.valid_document_types = ["CC", "TI", "CE", "PA", "RC", "AS", "MS", "NU"]
        self.valid_regimes = ["C", "S", "E", "P"]  # Contributivo, Subsidiado, Especial, Particular
        
    def validate_file(self, file_path: str, file_type: str = "AC") -> List[ErrorResponse]:
        """
        Validar archivo RIPS completo
        Args:
            file_path: Ruta del archivo
            file_type: Tipo de archivo RIPS (AC, AP, AM, AT, AU, AH, AN, US)
        """
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line_number, line in enumerate(file, 1):
                    line = line.strip()
                    if not line:  # Saltar líneas vacías
                        continue
                        
                    fields = line.split('|')
                    line_errors = self._validate_line(fields, line_number, file_type)
                    errors.extend(line_errors)
                    
        except Exception as e:
            errors.append(ErrorResponse(
                line=0,
                field="file",
                error=f"Error al leer archivo: {str(e)}"
            ))
            
        return errors
    
    def _validate_line(self, fields: List[str], line_number: int, file_type: str) -> List[ErrorResponse]:
        """Validar una línea específica según el tipo de archivo"""
        errors = []
        
        if file_type == "AC":  # Archivo de Consultas
            errors.extend(self._validate_ac_line(fields, line_number))
        elif file_type == "AP":  # Archivo de Procedimientos
            errors.extend(self._validate_ap_line(fields, line_number))
        elif file_type == "US":  # Archivo de Usuarios
            errors.extend(self._validate_us_line(fields, line_number))
        
        return errors
    
    def _validate_ac_line(self, fields: List[str], line_number: int) -> List[ErrorResponse]:
        """Validar línea de archivo AC (Consultas)"""
        errors = []
        expected_fields = 17  # Número esperado de campos para AC
        
        if len(fields) != expected_fields:
            errors.append(ErrorResponse(
                line=line_number,
                field="estructura",
                error=f"Número incorrecto de campos. Esperado: {expected_fields}, Encontrado: {len(fields)}"
            ))
            return errors
        
        # Validaciones específicas para AC
        # Campo 0: Código prestador (12 dígitos)
        if not self._validate_prestador_code(fields[0]):
            errors.append(ErrorResponse(
                line=line_number,
                field="codigo_prestador",
                error="Código de prestador debe tener 12 dígitos numéricos"
            ))
        
        # Campo 2: Tipo de documento
        if fields[2] not in self.valid_document_types:
            errors.append(ErrorResponse(
                line=line_number,
                field="tipo_documento",
                error=f"Tipo de documento inválido. Valores válidos: {', '.join(self.valid_document_types)}"
            ))
        
        # Campo 3: Número de documento (máximo 20 caracteres)
        if not self._validate_document_number(fields[3]):
            errors.append(ErrorResponse(
                line=line_number,
                field="numero_documento",
                error="Número de documento inválido (máximo 20 caracteres alfanuméricos)"
            ))
        
        # Campo 5: Fecha de nacimiento
        if not self._validate_date(fields[5]):
            errors.append(ErrorResponse(
                line=line_number,
                field="fecha_nacimiento",
                error="Fecha de nacimiento inválida. Formato esperado: DD/MM/AAAA"
            ))
        
        # Campo 6: Sexo
        if fields[6] not in self.valid_sexes:
            errors.append(ErrorResponse(
                line=line_number,
                field="sexo",
                error=f"Sexo inválido. Valores válidos: {', '.join(self.valid_sexes)}"
            ))
        
        # Campo 10: Fecha de consulta
        if not self._validate_date(fields[10]):
            errors.append(ErrorResponse(
                line=line_number,
                field="fecha_consulta",
                error="Fecha de consulta inválida. Formato esperado: DD/MM/AAAA"
            ))
        
        return errors
    
    def _validate_ap_line(self, fields: List[str], line_number: int) -> List[ErrorResponse]:
        """Validar línea de archivo AP (Procedimientos)"""
        errors = []
        expected_fields = 19
        
        if len(fields) != expected_fields:
            errors.append(ErrorResponse(
                line=line_number,
                field="estructura",
                error=f"Número incorrecto de campos. Esperado: {expected_fields}, Encontrado: {len(fields)}"
            ))
        
        return errors
    
    def _validate_us_line(self, fields: List[str], line_number: int) -> List[ErrorResponse]:
        """Validar línea de archivo US (Usuarios)"""
        errors = []
        expected_fields = 11
        
        if len(fields) != expected_fields:
            errors.append(ErrorResponse(
                line=line_number,
                field="estructura",
                error=f"Número incorrecto de campos. Esperado: {expected_fields}, Encontrado: {len(fields)}"
            ))
        
        return errors
    
    def _validate_prestador_code(self, code: str) -> bool:
        """Validar código de prestador (12 dígitos)"""
        return bool(re.match(r'^\d{12}$', code))
    
    def _validate_document_number(self, doc_number: str) -> bool:
        """Validar número de documento (máximo 20 caracteres alfanuméricos)"""
        if not doc_number or len(doc_number) > 20:
            return False
        return bool(re.match(r'^[A-Za-z0-9]+$', doc_number))
    
    def _validate_date(self, date_str: str) -> bool:
        """Validar formato de fecha DD/MM/AAAA"""
        if not date_str:
            return False
        
        try:
            datetime.strptime(date_str, '%d/%m/%Y')
            return True
        except ValueError:
            return False
    
    def _validate_numeric_field(self, value: str, max_length: int = None) -> bool:
        """Validar campo numérico"""
        if not value.isdigit():
            return False
        if max_length and len(value) > max_length:
            return False
        return True
    
    def _validate_text_field(self, value: str, max_length: int, required: bool = True) -> bool:
        """Validar campo de texto"""
        if required and not value:
            return False
        if len(value) > max_length:
            return False
        return True
