"""
Tests unitarios para el validador determinístico
Prueba las reglas de validación determinísticas sin dependencias externas
"""
import pytest
import tempfile
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from validators.deterministic_enhanced import EnhancedDeterministicValidator
from models.schemas import ErrorResponse


class TestEnhancedDeterministicValidator:
    """Suite de tests para EnhancedDeterministicValidator"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada test"""
        self.validator = EnhancedDeterministicValidator()
    
    # ========================================================================
    # TESTS DE VALIDACIÓN DE ARCHIVOS VÁLIDOS
    # ========================================================================
    
    def test_validate_valid_rips_ac_file(self, temp_rips_file):
        """
        Test: Validar archivo RIPS AC válido
        Resultado esperado: Sin errores críticos
        """
        # Arrange: archivo ya creado en fixture
        file_type = "AC"
        
        # Act: ejecutar validación
        errors = self.validator.validate_file(temp_rips_file, file_type)
        
        # Assert: validar resultados
        assert isinstance(errors, list)
        assert len(errors) >= 0  # Puede tener warnings pero no errores críticos
        
        # Verificar que no hay errores críticos de formato
        critical_errors = [e for e in errors if "obligatorio" in e.error.lower()]
        assert len(critical_errors) == 0, f"No debería haber errores críticos, encontrados: {critical_errors}"
    
    def test_validate_json_rips_file(self, temp_json_rips_file):
        """
        Test: Validar archivo JSON RIPS válido
        Resultado esperado: Validación exitosa
        """
        # Arrange
        file_type = "AC"
        
        # Act
        errors = self.validator.validate_file(temp_json_rips_file, file_type)
        
        # Assert
        assert isinstance(errors, list)
        # Para JSON válido, no deberían haber errores de estructura
        structure_errors = [e for e in errors if "estructura" in e.error.lower()]
        assert len(structure_errors) == 0
    
    # ========================================================================
    # TESTS DE VALIDACIÓN DE ARCHIVOS INVÁLIDOS
    # ========================================================================
    
    def test_validate_invalid_rips_file(self, temp_invalid_rips_file):
        """
        Test: Validar archivo RIPS con contenido inválido
        Resultado esperado: Detectar errores de formato
        """
        # Arrange
        file_type = "AC"
        
        # Act
        errors = self.validator.validate_file(temp_invalid_rips_file, file_type)
        
        # Assert: debería detectar errores
        assert len(errors) > 0, "Debería detectar errores en archivo inválido"
        assert isinstance(errors[0], ErrorResponse)
    
    def test_validate_nonexistent_file(self):
        """
        Test: Intentar validar archivo que no existe
        Resultado esperado: Error de archivo no encontrado
        """
        # Arrange
        nonexistent_file = "/tmp/nonexistent_file_12345.txt"
        file_type = "AC"
        
        # Act & Assert: debería lanzar excepción o retornar error
        try:
            errors = self.validator.validate_file(nonexistent_file, file_type)
            # Si no lanza excepción, debería retornar error
            assert len(errors) > 0
            assert any("no encontrado" in e.error.lower() or "error" in e.error.lower() 
                      for e in errors)
        except FileNotFoundError:
            # Comportamiento esperado alternativo
            pass
        except Exception as e:
            # Cualquier excepción relacionada con archivo es válida
            assert "file" in str(e).lower() or "archivo" in str(e).lower()
    
    # ========================================================================
    # TESTS DE REGLAS ESPECÍFICAS
    # ========================================================================
    
    def test_validate_codigo_prestador_format(self):
        """
        Test: Validar formato de código prestador (12 dígitos)
        Regla: AC-001
        """
        # Arrange: crear archivo con código prestador inválido
        invalid_content = "12345|1|CC|12345678|01|1990-03-15|M|170|11001|08001001|2024-03-15|123456|890101|10|A001|Z000|||"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='_AC.txt', delete=False) as f:
            f.write(invalid_content)
            temp_path = f.name
        
        try:
            # Act
            errors = self.validator.validate_file(temp_path, "AC")
            
            # Assert: debería detectar código prestador inválido
            prestador_errors = [e for e in errors if "prestador" in e.field.lower() or "prestador" in e.error.lower()]
            assert len(prestador_errors) > 0, "Debería detectar código prestador con longitud incorrecta"
        finally:
            os.unlink(temp_path)
    
    def test_validate_fecha_format(self):
        """
        Test: Validar formato de fecha (YYYY-MM-DD)
        Regla: FMT-006
        """
        # Arrange: crear archivo con fecha inválida
        invalid_content = "123456789012|1|CC|12345678|01|15/03/1990|M|170|11001|08001001|2024-03-15|123456|890101|10|A001|Z000|||"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='_AC.txt', delete=False) as f:
            f.write(invalid_content)
            temp_path = f.name
        
        try:
            # Act
            errors = self.validator.validate_file(temp_path, "AC")
            
            # Assert: debería detectar formato de fecha inválido
            fecha_errors = [e for e in errors if "fecha" in e.error.lower() or "formato" in e.error.lower()]
            assert len(fecha_errors) > 0, "Debería detectar formato de fecha incorrecto"
        finally:
            os.unlink(temp_path)
    
    def test_validate_diagnostico_cie_length(self):
        """
        Test: Validar longitud de código CIE (3-7 caracteres)
        Regla: AC-012
        """
        # Arrange: crear archivo con código CIE demasiado corto
        invalid_content = "123456789012|1|CC|12345678|01|1990-03-15|M|170|11001|08001001|2024-03-15|123456|890101|10|A001|Z0|||"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='_AC.txt', delete=False) as f:
            f.write(invalid_content)
            temp_path = f.name
        
        try:
            # Act
            errors = self.validator.validate_file(temp_path, "AC")
            
            # Assert: debería detectar código CIE con longitud incorrecta
            cie_errors = [e for e in errors if "cie" in e.error.lower() or "diagnóstico" in e.error.lower()]
            assert len(cie_errors) > 0, "Debería detectar código CIE con longitud incorrecta"
        finally:
            os.unlink(temp_path)
    
    # ========================================================================
    # TESTS DE DIFERENTES TIPOS DE ARCHIVO
    # ========================================================================
    
    def test_validate_different_file_types(self):
        """
        Test: Validar que el validador maneja diferentes tipos RIPS
        Tipos: AC, AP, AM, US, etc.
        """
        file_types = ["AC", "AP", "AM", "US", "AU", "AH"]
        
        for file_type in file_types:
            # Arrange: crear archivo básico
            content = "123456789012|test|data|for|validation"
            
            with tempfile.NamedTemporaryFile(mode='w', suffix=f'_{file_type}.txt', delete=False) as f:
                f.write(content)
                temp_path = f.name
            
            try:
                # Act: validar archivo
                errors = self.validator.validate_file(temp_path, file_type)
                
                # Assert: debería procesar sin crash
                assert isinstance(errors, list), f"Debería retornar lista para tipo {file_type}"
            finally:
                os.unlink(temp_path)
    
    # ========================================================================
    # TESTS DE CASOS EDGE
    # ========================================================================
    
    def test_validate_empty_file(self):
        """
        Test: Validar archivo vacío
        Resultado esperado: Error de archivo vacío
        """
        # Arrange: crear archivo vacío
        with tempfile.NamedTemporaryFile(mode='w', suffix='_AC.txt', delete=False) as f:
            temp_path = f.name
        
        try:
            # Act
            errors = self.validator.validate_file(temp_path, "AC")
            
            # Assert: debería detectar archivo vacío
            assert len(errors) > 0
            empty_errors = [e for e in errors if "vacío" in e.error.lower() or "empty" in e.error.lower()]
            assert len(empty_errors) > 0, "Debería detectar archivo vacío"
        finally:
            os.unlink(temp_path)
    
    def test_validate_file_with_special_characters(self):
        """
        Test: Validar archivo con caracteres especiales
        Resultado esperado: Manejo correcto de encoding
        """
        # Arrange: crear archivo con caracteres especiales
        content = "123456789012|1|CC|12345678|01|1990-03-15|M|170|11001|08001001|2024-03-15|123456|890101|10|A001|Z000|ñáéíóú||"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='_AC.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            # Act: no debería lanzar error de encoding
            errors = self.validator.validate_file(temp_path, "AC")
            
            # Assert: debería procesar correctamente
            assert isinstance(errors, list)
        finally:
            os.unlink(temp_path)
    
    def test_validate_large_file_performance(self):
        """
        Test: Validar que el validador maneja archivos grandes
        Resultado esperado: Completar en tiempo razonable
        """
        import time
        
        # Arrange: crear archivo con muchas líneas
        content_line = "123456789012|1|CC|12345678|01|1990-03-15|M|170|11001|08001001|2024-03-15|123456|890101|10|A001|Z000|||\n"
        content = content_line * 1000  # 1000 líneas
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='_AC.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            # Act: medir tiempo de ejecución
            start_time = time.time()
            errors = self.validator.validate_file(temp_path, "AC")
            elapsed_time = time.time() - start_time
            
            # Assert: debería completar en menos de 30 segundos
            assert elapsed_time < 30, f"Validación tomó demasiado tiempo: {elapsed_time}s"
            assert isinstance(errors, list)
        finally:
            os.unlink(temp_path)


class TestValidatorHelperMethods:
    """Tests para métodos auxiliares del validador"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada test"""
        self.validator = EnhancedDeterministicValidator()
    
    def test_error_response_creation(self):
        """
        Test: Crear ErrorResponse correctamente
        """
        # Arrange
        error = ErrorResponse(
            line=1,
            field="testField",
            error="Test error message"
        )
        
        # Assert
        assert error.line == 1
        assert error.field == "testField"
        assert error.error == "Test error message"
    
    def test_validator_initialization(self):
        """
        Test: Validador se inicializa correctamente
        """
        # Arrange & Act
        validator = EnhancedDeterministicValidator()
        
        # Assert
        assert validator is not None
        assert hasattr(validator, 'validate_file')

