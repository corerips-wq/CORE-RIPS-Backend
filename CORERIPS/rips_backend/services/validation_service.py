from typing import List
from sqlalchemy.orm import Session
from models.models import File, Validation
from models.types import ValidationStatus, FileStatus
from models.schemas import ValidationResultsResponse, ValidationResponse, ErrorResponse
from validators.deterministic_enhanced import EnhancedDeterministicValidator
from validators.ai_validator_enhanced import EnhancedAIValidator

class ValidationService:
    """Servicio para validación de archivos RIPS"""
    
    def __init__(self):
        self.deterministic_validator = EnhancedDeterministicValidator()
        self.ai_validator = EnhancedAIValidator()
    
    def validate_file(self, file_id: int, validation_types: List[str], db: Session) -> ValidationResultsResponse:
        """
        Validar archivo RIPS
        Args:
            file_id: ID del archivo a validar
            validation_types: Tipos de validación a ejecutar ['deterministic', 'ai']
            db: Sesión de base de datos
        """
        
        # Obtener archivo
        db_file = db.query(File).filter(File.id == file_id).first()
        if not db_file:
            raise ValueError("Archivo no encontrado")
        
        # Actualizar estado a procesando
        db_file.status = FileStatus.PROCESSING
        db.commit()
        
        all_errors = []
        
        try:
            # Ejecutar validaciones determinísticas
            if "deterministic" in validation_types:
                det_errors = self.deterministic_validator.validate_file(
                    db_file.file_path, 
                    self._get_file_type(db_file.original_filename)
                )
                all_errors.extend(det_errors)
                
                # Guardar errores en base de datos
                self._save_validation_errors(db_file.id, det_errors, "deterministic", db)
            
            # Ejecutar validaciones de IA
            if "ai" in validation_types:
                ai_errors = self.ai_validator.validate_file(
                    db_file.file_path,
                    self._get_file_type(db_file.original_filename)
                )
                all_errors.extend(ai_errors)
                
                # Guardar errores en base de datos
                self._save_validation_errors(db_file.id, ai_errors, "ai", db)
            
            # Actualizar estado del archivo
            db_file.status = FileStatus.VALIDATED
            db.commit()
            
            # Contar líneas del archivo
            total_lines = self._count_file_lines(db_file.file_path)
            
            # Obtener validaciones de la base de datos
            validations = db.query(Validation).filter(Validation.file_id == file_id).all()
            validation_responses = [ValidationResponse.from_orm(v) for v in validations]
            
            # Contar errores y warnings
            total_errors = sum(1 for v in validations if v.status == ValidationStatus.FAILED)
            total_warnings = sum(1 for v in validations if v.status == ValidationStatus.WARNING)
            
            return ValidationResultsResponse(
                file_id=file_id,
                filename=db_file.original_filename,
                total_lines=total_lines,
                total_errors=total_errors,
                total_warnings=total_warnings,
                validations=validation_responses
            )
            
        except Exception as e:
            # Actualizar estado a error
            db_file.status = FileStatus.ERROR
            db.commit()
            raise ValueError(f"Error durante validación: {str(e)}")
    
    def get_validation_results(self, file_id: int, db: Session) -> ValidationResultsResponse:
        """Obtener resultados de validación de un archivo"""
        
        db_file = db.query(File).filter(File.id == file_id).first()
        if not db_file:
            raise ValueError("Archivo no encontrado")
        
        validations = db.query(Validation).filter(Validation.file_id == file_id).all()
        validation_responses = [ValidationResponse.from_orm(v) for v in validations]
        
        total_lines = self._count_file_lines(db_file.file_path)
        total_errors = sum(1 for v in validations if v.status == ValidationStatus.FAILED)
        total_warnings = sum(1 for v in validations if v.status == ValidationStatus.WARNING)
        
        return ValidationResultsResponse(
            file_id=file_id,
            filename=db_file.original_filename,
            total_lines=total_lines,
            total_errors=total_errors,
            total_warnings=total_warnings,
            validations=validation_responses
        )
    
    def _save_validation_errors(self, file_id: int, errors: List[ErrorResponse], validator_type: str, db: Session):
        """Guardar errores de validación en base de datos"""
        
        for error in errors:
            validation = Validation(
                file_id=file_id,
                line_number=error.line,
                field_name=error.field,
                rule_name=f"{validator_type}_validation",
                error_message=error.error,
                status=ValidationStatus.FAILED,
                validator_type=validator_type
            )
            db.add(validation)
        
        db.commit()
    
    def _get_file_type(self, filename: str) -> str:
        """Determinar tipo de archivo RIPS basado en el nombre"""
        filename_upper = filename.upper()
        
        if "AC" in filename_upper:
            return "AC"  # Consultas
        elif "AP" in filename_upper:
            return "AP"  # Procedimientos
        elif "AM" in filename_upper:
            return "AM"  # Medicamentos
        elif "AT" in filename_upper:
            return "AT"  # Otros servicios
        elif "AU" in filename_upper:
            return "AU"  # Urgencias
        elif "AH" in filename_upper:
            return "AH"  # Hospitalización
        elif "AN" in filename_upper:
            return "AN"  # Recién nacidos
        elif "US" in filename_upper:
            return "US"  # Usuarios
        else:
            return "AC"  # Por defecto
    
    def _count_file_lines(self, file_path: str) -> int:
        """Contar líneas de un archivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return sum(1 for line in file if line.strip())
        except Exception:
            return 0
