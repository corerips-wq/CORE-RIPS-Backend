import pytest
import tempfile
import os
from validators.deterministic import DeterministicValidator

class TestDeterministicValidator:
    """Pruebas para el validador determinístico"""
    
    def setup_method(self):
        """Configuración antes de cada prueba"""
        self.validator = DeterministicValidator()
    
    def test_validate_prestador_code_valid(self):
        """Probar validación de código de prestador válido"""
        valid_code = "123456789012"
        assert self.validator._validate_prestador_code(valid_code) == True
    
    def test_validate_prestador_code_invalid_length(self):
        """Probar validación de código de prestador con longitud inválida"""
        invalid_code = "12345"
        assert self.validator._validate_prestador_code(invalid_code) == False
    
    def test_validate_prestador_code_non_numeric(self):
        """Probar validación de código de prestador no numérico"""
        invalid_code = "12345678901A"
        assert self.validator._validate_prestador_code(invalid_code) == False
    
    def test_validate_document_number_valid(self):
        """Probar validación de número de documento válido"""
        valid_doc = "12345678"
        assert self.validator._validate_document_number(valid_doc) == True
    
    def test_validate_document_number_too_long(self):
        """Probar validación de número de documento muy largo"""
        invalid_doc = "123456789012345678901"  # 21 caracteres
        assert self.validator._validate_document_number(invalid_doc) == False
    
    def test_validate_document_number_empty(self):
        """Probar validación de número de documento vacío"""
        invalid_doc = ""
        assert self.validator._validate_document_number(invalid_doc) == False
    
    def test_validate_date_valid(self):
        """Probar validación de fecha válida"""
        valid_date = "15/03/1990"
        assert self.validator._validate_date(valid_date) == True
    
    def test_validate_date_invalid_format(self):
        """Probar validación de fecha con formato inválido"""
        invalid_date = "1990-03-15"
        assert self.validator._validate_date(invalid_date) == False
    
    def test_validate_date_invalid_date(self):
        """Probar validación de fecha inválida"""
        invalid_date = "32/13/1990"
        assert self.validator._validate_date(invalid_date) == False
    
    def test_validate_ac_line_valid(self):
        """Probar validación de línea AC válida"""
        # Línea AC con 17 campos válidos
        fields = [
            "123456789012",  # código prestador
            "1",             # razón social
            "CC",            # tipo documento
            "12345678",      # número documento
            "1",             # primer apellido
            "15/03/1990",    # fecha nacimiento
            "M",             # sexo
            "1",             # código municipio
            "1",             # zona residencial
            "1",             # incapacidad
            "15/03/2024",    # fecha consulta
            "1",             # número autorización
            "1",             # código consulta
            "1",             # finalidad consulta
            "1",             # causa externa
            "Z000",          # diagnóstico principal
            "Z001"           # diagnóstico relacionado
        ]
        
        errors = self.validator._validate_ac_line(fields, 1)
        assert len(errors) == 0
    
    def test_validate_ac_line_invalid_fields_count(self):
        """Probar validación de línea AC con número incorrecto de campos"""
        fields = ["123456789012", "1", "CC"]  # Solo 3 campos en lugar de 17
        
        errors = self.validator._validate_ac_line(fields, 1)
        assert len(errors) == 1
        assert "Número incorrecto de campos" in errors[0].error
    
    def test_validate_ac_line_invalid_prestador(self):
        """Probar validación de línea AC con código de prestador inválido"""
        fields = [
            "12345",         # código prestador inválido (muy corto)
            "1", "CC", "12345678", "1", "15/03/1990", "M", "1", "1", "1",
            "15/03/2024", "1", "1", "1", "1", "Z000", "Z001"
        ]
        
        errors = self.validator._validate_ac_line(fields, 1)
        assert any("Código de prestador" in error.error for error in errors)
    
    def test_validate_ac_line_invalid_document_type(self):
        """Probar validación de línea AC con tipo de documento inválido"""
        fields = [
            "123456789012", "1", "XX", "12345678", "1", "15/03/1990", "M", "1", "1", "1",
            "15/03/2024", "1", "1", "1", "1", "Z000", "Z001"
        ]
        
        errors = self.validator._validate_ac_line(fields, 1)
        assert any("Tipo de documento inválido" in error.error for error in errors)
    
    def test_validate_ac_line_invalid_sex(self):
        """Probar validación de línea AC con sexo inválido"""
        fields = [
            "123456789012", "1", "CC", "12345678", "1", "15/03/1990", "X", "1", "1", "1",
            "15/03/2024", "1", "1", "1", "1", "Z000", "Z001"
        ]
        
        errors = self.validator._validate_ac_line(fields, 1)
        assert any("Sexo inválido" in error.error for error in errors)
    
    def test_validate_file_with_temp_file(self):
        """Probar validación de archivo completo usando archivo temporal"""
        # Crear archivo temporal con contenido de prueba
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
            # Línea válida
            temp_file.write("123456789012|1|CC|12345678|1|15/03/1990|M|1|1|1|15/03/2024|1|1|1|1|Z000|Z001\n")
            # Línea con error (código prestador inválido)
            temp_file.write("12345|1|CC|12345678|1|15/03/1990|M|1|1|1|15/03/2024|1|1|1|1|Z000|Z001\n")
            temp_file_path = temp_file.name
        
        try:
            errors = self.validator.validate_file(temp_file_path, "AC")
            
            # Debe haber al menos un error (código prestador inválido en línea 2)
            assert len(errors) > 0
            assert any(error.line == 2 for error in errors)
            assert any("Código de prestador" in error.error for error in errors)
            
        finally:
            # Limpiar archivo temporal
            os.unlink(temp_file_path)
    
    def test_validate_numeric_field_valid(self):
        """Probar validación de campo numérico válido"""
        assert self.validator._validate_numeric_field("12345") == True
        assert self.validator._validate_numeric_field("12345", 10) == True
    
    def test_validate_numeric_field_invalid(self):
        """Probar validación de campo numérico inválido"""
        assert self.validator._validate_numeric_field("12345A") == False
        assert self.validator._validate_numeric_field("12345", 3) == False
    
    def test_validate_text_field_valid(self):
        """Probar validación de campo de texto válido"""
        assert self.validator._validate_text_field("Texto", 10) == True
        assert self.validator._validate_text_field("", 10, required=False) == True
    
    def test_validate_text_field_invalid(self):
        """Probar validación de campo de texto inválido"""
        assert self.validator._validate_text_field("", 10, required=True) == False
        assert self.validator._validate_text_field("Texto muy largo", 5) == False
