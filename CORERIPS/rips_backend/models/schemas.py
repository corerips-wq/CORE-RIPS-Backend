from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from models.models import UserRole, FileStatus, ValidationStatus

# Esquemas de Usuario
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRole = UserRole.VALIDATOR

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Esquemas de Autenticación
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

# Esquemas de Archivo
class FileBase(BaseModel):
    filename: str
    original_filename: str

class FileCreate(FileBase):
    file_path: str
    file_size: int

class FileResponse(FileBase):
    id: int
    status: FileStatus
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Esquemas de Validación
class ValidationBase(BaseModel):
    line_number: int
    field_name: str
    rule_name: str
    error_message: str
    status: ValidationStatus
    validator_type: str

class ValidationCreate(ValidationBase):
    file_id: int

class ValidationResponse(ValidationBase):
    id: int
    file_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Esquemas de respuesta para endpoints
class UploadResponse(BaseModel):
    message: str
    file_id: int
    filename: str

class ValidationRequest(BaseModel):
    file_id: int
    validation_types: List[str] = ["deterministic"]  # ["deterministic", "ai"]

class ValidationResultsResponse(BaseModel):
    file_id: int
    filename: str
    total_lines: int
    total_errors: int
    total_warnings: int
    validations: List[ValidationResponse]
    
class ErrorResponse(BaseModel):
    line: int
    field: str
    error: str
