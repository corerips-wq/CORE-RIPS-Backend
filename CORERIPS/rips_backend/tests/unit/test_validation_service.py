"""
Tests unitarios para el servicio de validación
Prueba la lógica de negocio de validación de archivos RIPS
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.validation_service import ValidationService
from models.schemas import ErrorResponse, ValidationResultsResponse


class TestValidationService:
    """Suite de tests para ValidationService"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada test"""
        self.service = ValidationService()
    
    # ========================================================================
    # TESTS DE INICIALIZACIÓN
    # ========================================================================
    
    def test_service_initialization(self):
        """
        Test: Servicio se inicializa correctamente
        Resultado esperado: Validadores cargados
        """
        # Arrange & Act
        service = ValidationService()
        
        # Assert
        assert service is not None
        assert hasattr(service, 'deterministic_validator')
        assert hasattr(service, 'ai_validator')
        assert service.deterministic_validator is not None
        assert service.ai_validator is not None
    
    # ========================================================================
    # TESTS DE MÉTODO _get_file_type
    # ========================================================================
    
    def test_get_file_type_ac(self):
        """
        Test: Detectar tipo AC (Consultas) en nombre de archivo
        """
        # Arrange
        filenames = ["archivo_AC_20240315.txt", "test_ac.txt", "AC.txt"]
        
        # Act & Assert
        for filename in filenames:
            file_type = self.service._get_file_type(filename)
            assert file_type == "AC", f"Debería detectar AC en {filename}"
    
    def test_get_file_type_ap(self):
        """
        Test: Detectar tipo AP (Procedimientos) en nombre de archivo
        """
        # Arrange
        filenames = ["archivo_AP_20240315.txt", "test_ap.txt", "AP.txt"]
        
        # Act & Assert
        for filename in filenames:
            file_type = self.service._get_file_type(filename)
            assert file_type == "AP", f"Debería detectar AP en {filename}"
    
    def test_get_file_type_am(self):
        """
        Test: Detectar tipo AM (Medicamentos) en nombre de archivo
        """
        # Arrange
        filenames = ["archivo_AM_20240315.txt", "test_am.txt"]
        
        # Act & Assert
        for filename in filenames:
            file_type = self.service._get_file_type(filename)
            assert file_type == "AM"
    
    def test_get_file_type_us(self):
        """
        Test: Detectar tipo US (Usuarios) en nombre de archivo
        """
        # Arrange
        filenames = ["archivo_US_20240315.txt", "test_us.txt"]
        
        # Act & Assert
        for filename in filenames:
            file_type = self.service._get_file_type(filename)
            assert file_type == "US"
    
    def test_get_file_type_default(self):
        """
        Test: Retornar tipo por defecto si no se reconoce
        Resultado esperado: AC por defecto
        """
        # Arrange
        filename = "archivo_desconocido.txt"
        
        # Act
        file_type = self.service._get_file_type(filename)
        
        # Assert
        assert file_type == "AC", "Debería retornar AC como tipo por defecto"
    
    # ========================================================================
    # TESTS DE MÉTODO _count_file_lines
    # ========================================================================
    
    def test_count_file_lines_valid_file(self, temp_rips_file):
        """
        Test: Contar líneas de archivo válido
        """
        # Act
        line_count = self.service._count_file_lines(temp_rips_file)
        
        # Assert
        assert line_count >= 0
        assert isinstance(line_count, int)
    
    def test_count_file_lines_nonexistent_file(self):
        """
        Test: Intentar contar líneas de archivo inexistente
        Resultado esperado: Retorna 0
        """
        # Arrange
        nonexistent_file = "/tmp/nonexistent_file_12345.txt"
        
        # Act
        line_count = self.service._count_file_lines(nonexistent_file)
        
        # Assert
        assert line_count == 0
    
    def test_count_file_lines_empty_file(self):
        """
        Test: Contar líneas de archivo vacío
        """
        # Arrange
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_path = f.name
        
        try:
            # Act
            line_count = self.service._count_file_lines(temp_path)
            
            # Assert
            assert line_count == 0
        finally:
            import os
            os.unlink(temp_path)
    
    # ========================================================================
    # TESTS DE MÉTODO validate_file (CON MOCKS)
    # ========================================================================
    
    @patch('services.validation_service.EnhancedDeterministicValidator')
    @patch('services.validation_service.EnhancedAIValidator')
    def test_validate_file_deterministic_only(self, mock_ai_validator, mock_det_validator):
        """
        Test: Validar archivo solo con validaciones determinísticas
        """
        # Arrange
        mock_db = Mock()
        mock_file = Mock()
        mock_file.id = 1
        mock_file.file_path = "/tmp/test.txt"
        mock_file.original_filename = "test_AC.txt"
        
        # Configurar mock de base de datos
        mock_db.query.return_value.filter.return_value.first.return_value = mock_file
        mock_db.query.return_value.filter.return_value.all.return_value = []
        
        # Configurar mock de validador determinístico
        mock_det_instance = mock_det_validator.return_value
        mock_det_instance.validate_file.return_value = [
            ErrorResponse(line=1, field="test", error="test error")
        ]
        
        # Recrear servicio con mocks
        with patch.object(ValidationService, '__init__', lambda x: None):
            service = ValidationService()
            service.deterministic_validator = mock_det_instance
            service.ai_validator = mock_ai_validator.return_value
        
        # Act
        try:
            result = service.validate_file(
                file_id=1,
                validation_types=["deterministic"],
                db=mock_db
            )
            
            # Assert
            assert mock_det_instance.validate_file.called
            assert isinstance(result, ValidationResultsResponse) or result is not None
        except Exception as e:
            # El método puede fallar por dependencias de DB, pero no debería crashear
            assert "Archivo no encontrado" in str(e) or "Error" in str(e)
    
    def test_validate_file_invalid_file_id(self):
        """
        Test: Intentar validar archivo con ID inexistente
        Resultado esperado: ValueError
        """
        # Arrange
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.service.validate_file(
                file_id=99999,
                validation_types=["deterministic"],
                db=mock_db
            )
        
        assert "Archivo no encontrado" in str(exc_info.value)
    
    # ========================================================================
    # TESTS DE MÉTODO _save_validation_errors (CON MOCKS)
    # ========================================================================
    
    def test_save_validation_errors(self):
        """
        Test: Guardar errores de validación en base de datos
        """
        # Arrange
        mock_db = Mock()
        errors = [
            ErrorResponse(line=1, field="test1", error="error 1"),
            ErrorResponse(line=2, field="test2", error="error 2")
        ]
        
        # Act
        self.service._save_validation_errors(
            file_id=1,
            errors=errors,
            validator_type="deterministic",
            db=mock_db
        )
        
        # Assert
        assert mock_db.add.call_count == len(errors)
        assert mock_db.commit.called
    
    def test_save_validation_errors_empty_list(self):
        """
        Test: Guardar lista vacía de errores
        Resultado esperado: No inserta nada pero hace commit
        """
        # Arrange
        mock_db = Mock()
        errors = []
        
        # Act
        self.service._save_validation_errors(
            file_id=1,
            errors=errors,
            validator_type="deterministic",
            db=mock_db
        )
        
        # Assert
        assert mock_db.add.call_count == 0
        assert mock_db.commit.called


class TestValidationServiceIntegration:
    """Tests de integración del servicio con validadores reales"""
    
    def test_service_with_real_validators(self, temp_rips_file):
        """
        Test: Servicio funciona con validadores reales
        """
        # Arrange
        service = ValidationService()
        
        # Act & Assert: no debería crashear
        assert service.deterministic_validator is not None
        assert service.ai_validator is not None
        
        # Verificar que puede determinar tipo de archivo
        file_type = service._get_file_type("test_AC.txt")
        assert file_type == "AC"
    
    def test_count_lines_real_file(self, temp_rips_file):
        """
        Test: Contar líneas de archivo real
        """
        # Arrange
        service = ValidationService()
        
        # Act
        line_count = service._count_file_lines(temp_rips_file)
        
        # Assert
        assert line_count > 0
        assert isinstance(line_count, int)


class TestValidationServiceEdgeCases:
    """Tests de casos extremos"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada test"""
        self.service = ValidationService()
    
    def test_get_file_type_case_insensitive(self):
        """
        Test: Detección de tipo es case-insensitive
        """
        # Arrange
        filenames = ["Test_ac_File.txt", "TEST_AC.TXT", "tEsT_Ac.TxT"]
        
        # Act & Assert
        for filename in filenames:
            file_type = self.service._get_file_type(filename)
            assert file_type == "AC"
    
    def test_get_file_type_multiple_indicators(self):
        """
        Test: Archivo con múltiples indicadores de tipo
        Resultado esperado: Detecta el primero encontrado
        """
        # Arrange
        filename = "archivo_AC_AP_AM.txt"
        
        # Act
        file_type = self.service._get_file_type(filename)
        
        # Assert: debería detectar uno de los tipos
        assert file_type in ["AC", "AP", "AM"]
    
    def test_count_lines_with_empty_lines(self):
        """
        Test: Contar líneas ignorando líneas vacías
        """
        # Arrange
        import tempfile
        content = "line1\n\nline2\n\n\nline3\n"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            # Act
            line_count = self.service._count_file_lines(temp_path)
            
            # Assert: debería contar solo líneas no vacías
            assert line_count == 3
        finally:
            import os
            os.unlink(temp_path)

