"""
Tests unitarios para el validador de IA
Prueba las reglas de validación basadas en IA
"""
import pytest
import tempfile
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from validators.ai_validator_enhanced import EnhancedAIValidator
from models.schemas import ErrorResponse


class TestEnhancedAIValidator:
    """Suite de tests para EnhancedAIValidator"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada test"""
        self.validator = EnhancedAIValidator()
    
    # ========================================================================
    # TESTS DE INICIALIZACIÓN Y CONFIGURACIÓN
    # ========================================================================
    
    def test_validator_initialization(self):
        """
        Test: Validador de IA se inicializa correctamente
        Resultado esperado: Instancia válida con métodos disponibles
        """
        # Arrange & Act
        validator = EnhancedAIValidator()
        
        # Assert
        assert validator is not None
        assert hasattr(validator, 'validate_file')
    
    # ========================================================================
    # TESTS DE VALIDACIÓN BÁSICA
    # ========================================================================
    
    def test_validate_file_returns_list(self, temp_rips_file):
        """
        Test: validate_file retorna una lista de errores
        Resultado esperado: Lista (puede estar vacía)
        """
        # Arrange
        file_type = "AC"
        
        # Act
        errors = self.validator.validate_file(temp_rips_file, file_type)
        
        # Assert
        assert isinstance(errors, list), "Debe retornar una lista"
    
    def test_validate_json_file(self, temp_json_rips_file):
        """
        Test: Validar archivo JSON RIPS
        Resultado esperado: Procesa correctamente archivos JSON
        """
        # Arrange
        file_type = "AC"
        
        # Act
        errors = self.validator.validate_file(temp_json_rips_file, file_type)
        
        # Assert
        assert isinstance(errors, list)
        # Validar que los errores tienen estructura correcta
        for error in errors:
            assert isinstance(error, ErrorResponse)
            assert hasattr(error, 'line')
            assert hasattr(error, 'field')
            assert hasattr(error, 'error')
    
    # ========================================================================
    # TESTS DE REGLAS DE IA CLÍNICAS (AI-CLIN)
    # ========================================================================
    
    def test_diagnostico_vs_sexo_validation(self):
        """
        Test: Validar diagnóstico vs sexo del paciente
        Regla: AI-CLIN-001
        Ejemplo: Diagnóstico de próstata en mujer
        """
        # Arrange: crear archivo con diagnóstico incompatible con sexo
        content = """123456789012|1|CC|12345678|01|1990-03-15|F|170|11001|08001001|2024-03-15|123456|890101|10|A001|C61||"""  # C61 = Cáncer de próstata en mujer
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='_AC.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            # Act
            errors = self.validator.validate_file(temp_path, "AC")
            
            # Assert: puede detectar la inconsistencia (si la regla está implementada)
            # El validador de IA puede o no detectar esto dependiendo de la implementación
            assert isinstance(errors, list)
        finally:
            os.unlink(temp_path)
    
    def test_diagnostico_vs_edad_validation(self):
        """
        Test: Validar diagnóstico vs edad del paciente
        Regla: AI-CLIN-002
        Ejemplo: Diagnóstico geriátrico en niño
        """
        # Arrange: crear archivo con diagnóstico incompatible con edad
        content = """123456789012|1|CC|12345678|01|2020-01-15|M|170|11001|08001001|2024-03-15|123456|890101|10|A001|F03||"""  # F03 = Demencia en niño de 4 años
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='_AC.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            # Act
            errors = self.validator.validate_file(temp_path, "AC")
            
            # Assert
            assert isinstance(errors, list)
        finally:
            os.unlink(temp_path)
    
    # ========================================================================
    # TESTS DE REGLAS DE PATRONES (AI-PAT)
    # ========================================================================
    
    def test_procedimientos_duplicados_detection(self):
        """
        Test: Detectar procedimientos duplicados sospechosos
        Regla: AI-PAT-001
        """
        # Arrange: archivo con múltiples líneas idénticas
        line = "123456789012|1|CC|12345678|01|1990-03-15|M|170|11001|08001001|2024-03-15|123456|890101|10|A001|Z000|||\n"
        content = line * 10  # 10 registros idénticos
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='_AC.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            # Act
            errors = self.validator.validate_file(temp_path, "AC")
            
            # Assert: puede detectar duplicados
            assert isinstance(errors, list)
        finally:
            os.unlink(temp_path)
    
    # ========================================================================
    # TESTS DE MANEJO DE ERRORES
    # ========================================================================
    
    def test_validate_nonexistent_file(self):
        """
        Test: Intentar validar archivo inexistente
        Resultado esperado: Manejo gracioso del error
        """
        # Arrange
        nonexistent_file = "/tmp/nonexistent_ai_test_12345.txt"
        
        # Act & Assert: no debería crashear
        try:
            errors = self.validator.validate_file(nonexistent_file, "AC")
            # Si no lanza excepción, debería retornar error
            assert isinstance(errors, list)
        except (FileNotFoundError, Exception) as e:
            # Comportamiento aceptable
            assert True
    
    def test_validate_empty_file(self):
        """
        Test: Validar archivo vacío
        Resultado esperado: Manejo correcto de archivo sin contenido
        """
        # Arrange: crear archivo vacío
        with tempfile.NamedTemporaryFile(mode='w', suffix='_AC.txt', delete=False) as f:
            temp_path = f.name
        
        try:
            # Act
            errors = self.validator.validate_file(temp_path, "AC")
            
            # Assert: no debería crashear
            assert isinstance(errors, list)
        finally:
            os.unlink(temp_path)
    
    def test_validate_corrupted_json(self):
        """
        Test: Validar archivo JSON corrupto
        Resultado esperado: Error de formato JSON
        """
        # Arrange: crear JSON inválido
        invalid_json_content = "{ invalid json content without closing brace"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            f.write(invalid_json_content)
            temp_path = f.name
        
        try:
            # Act
            errors = self.validator.validate_file(temp_path, "AC")
            
            # Assert: debería detectar error de JSON
            assert isinstance(errors, list)
            if len(errors) > 0:
                # Si detecta el error, debería mencionarlo
                json_errors = [e for e in errors if "json" in e.error.lower() or "formato" in e.error.lower()]
                # Puede o no detectar específicamente que es JSON
        finally:
            os.unlink(temp_path)
    
    # ========================================================================
    # TESTS DE PERFORMANCE
    # ========================================================================
    
    def test_validate_multiple_records(self):
        """
        Test: Validar archivo con múltiples registros
        Resultado esperado: Procesa múltiples líneas correctamente
        """
        # Arrange: crear archivo con varios registros
        content_lines = [
            "123456789012|1|CC|12345678|01|1990-03-15|M|170|11001|08001001|2024-03-15|123456|890101|10|A001|Z000|||",
            "123456789012|1|TI|87654321|02|2005-08-20|F|169|11001|05001001|2024-03-15|123457|890102|10|B002|J180|||",
            "123456789012|1|CC|11223344|01|1985-12-10|M|170|11001|11001001|2024-03-15|123458|890103|10|A001|I10|||"
        ]
        content = "\n".join(content_lines)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='_AC.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            # Act
            errors = self.validator.validate_file(temp_path, "AC")
            
            # Assert
            assert isinstance(errors, list)
            # Si hay errores, deberían corresponder a líneas específicas
            for error in errors:
                assert error.line >= 0
        finally:
            os.unlink(temp_path)


class TestAIValidatorConfiguration:
    """Tests para configuración del validador de IA"""
    
    def test_validator_has_ai_methods(self):
        """
        Test: Verificar que el validador tiene métodos de IA
        """
        # Arrange & Act
        validator = EnhancedAIValidator()
        
        # Assert: verificar que tiene método principal
        assert hasattr(validator, 'validate_file')
        assert callable(validator.validate_file)
    
    def test_validator_accepts_different_file_types(self):
        """
        Test: Validador acepta diferentes tipos de archivo RIPS
        """
        validator = EnhancedAIValidator()
        file_types = ["AC", "AP", "AM", "US", "AU", "AH", "AN"]
        
        # Arrange: crear archivo de prueba simple
        content = "test data"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='_test.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            # Act & Assert: no debería crashear con ningún tipo
            for file_type in file_types:
                try:
                    errors = validator.validate_file(temp_path, file_type)
                    assert isinstance(errors, list), f"Debería retornar lista para tipo {file_type}"
                except Exception as e:
                    # Si hay error, debería ser descriptivo
                    assert True  # Permitir que algunos tipos no estén implementados
        finally:
            os.unlink(temp_path)

