"""
Tipos y Enumeraciones para el sistema RIPS
Estos tipos se usan con Supabase directamente
"""
import enum

class UserRole(str, enum.Enum):
    """Roles de usuario en el sistema"""
    ADMIN = "admin"
    VALIDATOR = "validator"
    AUDITOR = "auditor"

class FileStatus(str, enum.Enum):
    """Estados de un archivo RIPS"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    VALIDATED = "validated"
    ERROR = "error"

class ValidationStatus(str, enum.Enum):
    """Estados de una validación"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"


