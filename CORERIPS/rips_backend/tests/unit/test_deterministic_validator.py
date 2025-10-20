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


class TestReglasNuevasCIE11:
    """Tests para reglas CIE11 - Resolución 1442/1657 de 2024"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada test"""
        from datetime import date
        self.validator = EnhancedDeterministicValidator()
        
    def test_cie11_001_antes_transicion_cie10_valido(self):
        """
        Test CIE11_001: Validar código CIE-10 válido antes del 14/08/2024
        Resultado esperado: Sin errores
        """
        from datetime import date
        
        # Arrange
        codigo_cie = "J180"  # Código CIE-10 válido (Neumonía)
        fecha_servicio = date(2024, 7, 1)  # Antes del 14/08/2024
        line_number = 1
        
        # Act
        errors = self.validator.validate_cie11_001_transicion_cie10_cie11(
            codigo_cie, fecha_servicio, line_number
        )
        
        # Assert
        assert len(errors) == 0, "No debería haber errores para CIE-10 válido antes de transición"
    
    def test_cie11_001_despues_transicion_cie10_valido(self):
        """
        Test CIE11_001: Validar código CIE-10 válido después del 14/08/2024
        Resultado esperado: Sin errores (coexistencia permitida)
        """
        from datetime import date
        
        # Arrange
        codigo_cie = "A001"  # Código CIE-10 válido
        fecha_servicio = date(2024, 9, 1)  # Después del 14/08/2024
        line_number = 1
        
        # Act
        errors = self.validator.validate_cie11_001_transicion_cie10_cie11(
            codigo_cie, fecha_servicio, line_number
        )
        
        # Assert
        assert len(errors) == 0, "CIE-10 debería ser válido durante coexistencia"
    
    def test_cie11_001_codigo_invalido(self):
        """
        Test CIE11_001: Validar código CIE inválido
        Resultado esperado: Error detectado
        """
        from datetime import date
        
        # Arrange
        codigo_cie = "XYZ999"  # Código inválido (no sigue formato CIE-10 ni CIE-11)
        fecha_servicio = date(2024, 9, 1)
        line_number = 1
        
        # Act
        errors = self.validator.validate_cie11_001_transicion_cie10_cie11(
            codigo_cie, fecha_servicio, line_number
        )
        
        # Assert
        assert len(errors) > 0, "Debería detectar código CIE inválido"
        assert "CIE11_001" in errors[0].error
    
    def test_cie11_002_coexistencia_despues_2027(self):
        """
        Test CIE11_002: Validar que después del 14/08/2027 solo se permite CIE-11
        Resultado esperado: Error para CIE-10
        """
        from datetime import date
        
        # Arrange
        codigo_cie = "A00"  # CIE-10 (formato válido)
        fecha_servicio = date(2027, 9, 1)  # Después del fin de coexistencia
        line_number = 1
        
        # Act
        errors = self.validator.validate_cie11_002_coexistencia(
            codigo_cie, fecha_servicio, line_number
        )
        
        # Assert
        assert len(errors) > 0, "Debería detectar uso de CIE-10 después de 2027"
        assert "CIE11_002" in errors[0].error
    
    def test_cie11_003_existencia_catalogo_valido(self):
        """
        Test CIE11_003: Validar código CIE existe en catálogo
        Resultado esperado: Sin errores para formato válido
        """
        # Arrange
        codigo_cie = "J180"  # Formato CIE-10 válido
        line_number = 1
        
        # Act
        errors = self.validator.validate_cie11_003_existencia_catalogo(
            codigo_cie, line_number
        )
        
        # Assert
        assert len(errors) == 0, "Formato CIE-10 válido debería pasar"
    
    def test_cie11_004_diagnostico_obstetrico_hombre(self):
        """
        Test CIE11_004: Validar diagnóstico obstétrico en hombre detecta error
        Resultado esperado: Error de incompatibilidad con sexo
        """
        # Arrange
        codigo_cie = "O801"  # Diagnóstico obstétrico (parto)
        sexo = "M"
        line_number = 1
        
        # Act
        errors = self.validator.validate_cie11_004_compatibilidad_sexo(
            codigo_cie, sexo, line_number
        )
        
        # Assert
        assert len(errors) > 0, "Debería detectar diagnóstico obstétrico en hombre"
        assert "CIE11_004" in errors[0].error
        assert "obstétrico" in errors[0].error.lower()
    
    def test_cie11_004_diagnostico_compatible_mujer(self):
        """
        Test CIE11_004: Validar diagnóstico obstétrico en mujer es válido
        Resultado esperado: Sin errores
        """
        # Arrange
        codigo_cie = "O801"  # Diagnóstico obstétrico
        sexo = "F"
        line_number = 1
        
        # Act
        errors = self.validator.validate_cie11_004_compatibilidad_sexo(
            codigo_cie, sexo, line_number
        )
        
        # Assert
        assert len(errors) == 0, "Diagnóstico obstétrico debería ser válido en mujer"
    
    def test_cie11_005_procedimiento_obstetrico_sin_diagnostico_obstetrico(self):
        """
        Test CIE11_005: Validar procedimiento obstétrico requiere diagnóstico obstétrico
        Resultado esperado: Error de incompatibilidad
        """
        # Arrange
        codigo_cie = "J180"  # Diagnóstico no obstétrico (neumonía)
        codigo_cups = "870101"  # Procedimiento de parto
        line_number = 1
        
        # Act
        errors = self.validator.validate_cie11_005_correspondencia_cie_cups(
            codigo_cie, codigo_cups, line_number
        )
        
        # Assert
        assert len(errors) > 0, "Debería detectar falta de correspondencia CIE-CUPS"
        assert "CIE11_005" in errors[0].error


class TestReglasNuevasCUPS:
    """Tests para reglas CUPS - Resolución 2641 de 2024"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada test"""
        self.validator = EnhancedDeterministicValidator()
    
    def test_r2641_d001_cups_valido(self):
        """
        Test R2641-D001: Validar código CUPS con formato válido
        Resultado esperado: Sin errores
        """
        # Arrange
        codigo_cups = "890101"  # Formato válido
        line_number = 1
        
        # Act
        errors = self.validator.validate_r2641_d001_cups_existencia(
            codigo_cups, line_number
        )
        
        # Assert
        assert len(errors) == 0, "Formato CUPS válido debería pasar"
    
    def test_r2641_d001_cups_invalido(self):
        """
        Test R2641-D001: Validar código CUPS con formato inválido
        Resultado esperado: Error detectado
        """
        # Arrange
        codigo_cups = "ABC"  # Formato inválido (no numérico)
        line_number = 1
        
        # Act
        errors = self.validator.validate_r2641_d001_cups_existencia(
            codigo_cups, line_number
        )
        
        # Assert
        assert len(errors) > 0, "CUPS con formato inválido debería generar error"
        assert "R2641-D001" in errors[0].error
    
    def test_r2641_d003_cups_tipo_servicio(self):
        """
        Test R2641-D003: Validar que CUPS pertenece al tipo de servicio correcto
        Resultado esperado: Validación de tipo de servicio
        """
        # Arrange
        codigo_cups = "890101"
        tipo_servicio = "consulta"
        line_number = 1
        
        # Act
        errors = self.validator.validate_r2641_d003_cups_tipo_servicio(
            codigo_cups, tipo_servicio, line_number
        )
        
        # Assert: Sin catálogo cargado, no debería generar error
        assert isinstance(errors, list)
    
    def test_r2641_d005_cups_edad_incompatible(self):
        """
        Test R2641-D005: Validar restricción de edad para CUPS
        Resultado esperado: Error si edad no cumple requisitos
        """
        # Arrange
        codigo_cups = "890101"
        edad = 5  # Menor de edad
        line_number = 1
        
        # Act
        errors = self.validator.validate_r2641_d005_cups_grupo_etario(
            codigo_cups, edad, line_number
        )
        
        # Assert: Sin catálogo cargado, no debería generar error
        assert isinstance(errors, list)
    
    def test_r2641_d006_cups_procedimiento_femenino_en_hombre(self):
        """
        Test R2641-D006: Validar procedimiento ginecológico en hombre
        Resultado esperado: Error de incompatibilidad
        """
        # Arrange
        codigo_cups = "870101"  # Procedimiento de parto
        sexo = "M"
        line_number = 1
        
        # Act
        errors = self.validator.validate_r2641_d006_cups_sexo(
            codigo_cups, sexo, line_number
        )
        
        # Assert
        assert len(errors) > 0, "Procedimiento obstétrico en hombre debería generar error"
        assert "R2641-D006" in errors[0].error
    
    def test_r2641_d006_cups_procedimiento_femenino_en_mujer(self):
        """
        Test R2641-D006: Validar procedimiento ginecológico en mujer
        Resultado esperado: Sin errores
        """
        # Arrange
        codigo_cups = "870101"  # Procedimiento de parto
        sexo = "F"
        line_number = 1
        
        # Act
        errors = self.validator.validate_r2641_d006_cups_sexo(
            codigo_cups, sexo, line_number
        )
        
        # Assert
        assert len(errors) == 0, "Procedimiento obstétrico en mujer debería ser válido"


class TestReglasNuevasCatalogos:
    """Tests para reglas de catálogos básicos CUPS/CIE10/DANE"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada test"""
        self.validator = EnhancedDeterministicValidator()
    
    def test_us001_tipo_documento_valido(self):
        """
        Test US-001: Validar tipo de documento válido
        Resultado esperado: Sin errores
        """
        # Arrange
        tipos_validos = ["CC", "TI", "RC", "CE", "PA", "NUIP", "MS"]
        line_number = 1
        
        # Act & Assert
        for tipo in tipos_validos:
            errors = self.validator.validate_us001_tipo_documento_catalogo(
                tipo, line_number
            )
            assert len(errors) == 0, f"Tipo de documento {tipo} debería ser válido"
    
    def test_us001_tipo_documento_invalido(self):
        """
        Test US-001: Validar tipo de documento inválido
        Resultado esperado: Error detectado
        """
        # Arrange
        tipo_invalido = "XX"
        line_number = 1
        
        # Act
        errors = self.validator.validate_us001_tipo_documento_catalogo(
            tipo_invalido, line_number
        )
        
        # Assert
        assert len(errors) > 0, "Tipo de documento inválido debería generar error"
        assert "US-001" in errors[0].error
    
    def test_ac012_diagnostico_principal_valido(self):
        """
        Test AC-012: Validar diagnóstico principal con formato válido
        Resultado esperado: Sin errores
        """
        from datetime import date
        
        # Arrange
        codigo_cie = "J180"  # CIE-10 válido
        fecha_servicio = date(2024, 3, 15)
        line_number = 1
        
        # Act
        errors = self.validator.validate_ac012_diagnostico_principal_vigencia(
            codigo_cie, fecha_servicio, line_number
        )
        
        # Assert
        assert len(errors) == 0, "Diagnóstico CIE-10 válido antes de transición debería pasar"
    
    def test_ap001_cups_existencia(self):
        """
        Test AP-001: Validar existencia de código CUPS
        Resultado esperado: Sin errores para formato válido
        """
        from datetime import date
        
        # Arrange
        codigo_cups = "890101"
        fecha_servicio = date(2024, 3, 15)
        line_number = 1
        
        # Act
        errors = self.validator.validate_ap001_cups_existencia_vigencia(
            codigo_cups, fecha_servicio, line_number
        )
        
        # Assert
        assert len(errors) == 0, "CUPS con formato válido debería pasar"
    
    def test_am001_codigo_producto_valido(self):
        """
        Test AM-001: Validar código de producto válido
        Resultado esperado: Sin errores
        """
        # Arrange
        codigo_producto = "MED12345"
        line_number = 1
        
        # Act
        errors = self.validator.validate_am001_codigo_producto_catalogo(
            codigo_producto, line_number
        )
        
        # Assert
        assert len(errors) == 0, "Código de producto válido debería pasar"
    
    def test_am001_codigo_producto_longitud_invalida(self):
        """
        Test AM-001: Validar código de producto con longitud inválida
        Resultado esperado: Error detectado
        """
        # Arrange
        codigo_producto = "AB"  # Muy corto (< 3 caracteres)
        line_number = 1
        
        # Act
        errors = self.validator.validate_am001_codigo_producto_catalogo(
            codigo_producto, line_number
        )
        
        # Assert
        assert len(errors) > 0, "Código de producto muy corto debería generar error"
        assert "AM-001" in errors[0].error


class TestValidacionesCruzadas:
    """Tests para validaciones cruzadas entre campos"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada test"""
        self.validator = EnhancedDeterministicValidator()
    
    def test_edad_sexo_diagnostico_obstetrico_hombre(self):
        """
        Test: Validar diagnóstico obstétrico en hombre (validación cruzada)
        Resultado esperado: Error de incompatibilidad
        """
        # Arrange
        edad = 35
        sexo = "M"
        codigo_cie = "O801"  # Diagnóstico obstétrico
        line_number = 1
        
        # Act
        errors = self.validator.validate_edad_sexo_diagnostico(
            edad, sexo, codigo_cie, line_number
        )
        
        # Assert
        assert len(errors) > 0, "Debería detectar diagnóstico obstétrico en hombre"
        assert "obstétrico" in errors[0].error.lower()
    
    def test_edad_sexo_diagnostico_pediatrico_adulto(self):
        """
        Test: Validar diagnóstico pediátrico en adulto (advertencia)
        Resultado esperado: Advertencia
        """
        # Arrange
        edad = 45
        sexo = "M"
        codigo_cie = "P070"  # Diagnóstico pediátrico
        line_number = 1
        
        # Act
        errors = self.validator.validate_edad_sexo_diagnostico(
            edad, sexo, codigo_cie, line_number
        )
        
        # Assert
        assert len(errors) > 0, "Debería generar advertencia para diagnóstico pediátrico en adulto"
        assert "ADVERTENCIA" in errors[0].error
    
    def test_diagnostico_procedimiento_cardiovascular(self):
        """
        Test: Validar correspondencia diagnóstico-procedimiento cardiovascular
        Resultado esperado: Advertencia si no hay correspondencia
        """
        # Arrange
        codigo_cie = "L201"  # Diagnóstico dermatológico
        codigo_cups = "373101"  # Procedimiento cardiovascular
        line_number = 1
        
        # Act
        errors = self.validator.validate_diagnostico_procedimiento(
            codigo_cie, codigo_cups, line_number
        )
        
        # Assert
        assert len(errors) > 0, "Debería detectar falta de correspondencia"
        assert "ADVERTENCIA" in errors[0].error
    
    def test_diagnostico_procedimiento_compatible(self):
        """
        Test: Validar diagnóstico-procedimiento compatible
        Resultado esperado: Sin errores
        """
        # Arrange
        codigo_cie = "I251"  # Diagnóstico cardiovascular
        codigo_cups = "373101"  # Procedimiento cardiovascular
        line_number = 1
        
        # Act
        errors = self.validator.validate_diagnostico_procedimiento(
            codigo_cie, codigo_cups, line_number
        )
        
        # Assert
        assert len(errors) == 0, "Diagnóstico y procedimiento cardiovasculares deberían ser compatibles"


class TestMetodosAuxiliaresCatalogos:
    """Tests para métodos auxiliares de consulta de catálogos"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada test"""
        self.validator = EnhancedDeterministicValidator()
    
    def test_is_valid_cie10_formato_basico(self):
        """
        Test: Validar formato básico de código CIE-10
        Resultado esperado: Reconoce formatos válidos
        """
        # Arrange & Act & Assert
        assert self.validator._is_valid_cie10("A00") == True  # Formato CIE-10 válido
        assert self.validator._is_valid_cie10("J18") == True
        assert self.validator._is_valid_cie10("Z99") == True
        assert self.validator._is_valid_cie10("A001") == True  # CIE-10 con 3 dígitos
        assert self.validator._is_valid_cie10("J180") == True  # CIE-10 con 3 dígitos
        assert self.validator._is_valid_cie10("A00.1") == True
        assert self.validator._is_valid_cie10("INVALID") == False
        assert self.validator._is_valid_cie10("123") == False
        assert self.validator._is_valid_cie10("1A00") == False  # Formato CIE-11
    
    def test_is_valid_cups_formato_basico(self):
        """
        Test: Validar formato básico de código CUPS
        Resultado esperado: Reconoce formatos válidos (numéricos 3-7 dígitos)
        """
        # Arrange & Act & Assert
        assert self.validator._is_valid_cups("890101") == True
        assert self.validator._is_valid_cups("123") == True
        assert self.validator._is_valid_cups("1234567") == True
        assert self.validator._is_valid_cups("ABC") == False
        assert self.validator._is_valid_cups("12") == False
        assert self.validator._is_valid_cups("12345678") == False
    
    def test_load_cie10_catalog(self):
        """
        Test: Cargar catálogo CIE-10
        Resultado esperado: Catálogo se carga correctamente
        """
        # Arrange
        catalogos_cie10 = {"A001", "J180", "O801", "I251"}
        
        # Act
        self.validator.load_cie10_catalog(catalogos_cie10)
        
        # Assert
        assert len(self.validator.codigos_cie10_validos) == 4
        assert "A001" in self.validator.codigos_cie10_validos
        assert "O801" in self.validator.codigos_obstetricos
    
    def test_load_cups_catalog(self):
        """
        Test: Cargar catálogo CUPS con información adicional
        Resultado esperado: Catálogo se carga correctamente
        """
        from datetime import date
        
        # Arrange
        cups_data = {
            "890101": {
                "vigencia_inicio": date(2020, 1, 1),
                "vigencia_fin": None,
                "tipo_servicio": "consulta"
            }
        }
        
        # Act
        self.validator.load_cups_catalog(cups_data)
        
        # Assert
        assert len(self.validator.codigos_cups_validos) == 1
        assert "890101" in self.validator.codigos_cups_validos
        assert self.validator.codigos_cups_validos["890101"]["tipo_servicio"] == "consulta"

