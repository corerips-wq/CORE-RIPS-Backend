from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    VALIDATOR = "validator"
    AUDITOR = "auditor"

class FileStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    VALIDATED = "validated"
    ERROR = "error"

class ValidationStatus(str, enum.Enum):
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.VALIDATOR, nullable=False)
    is_active = Column(String(10), default="true", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    files = relationship("File", back_populates="user")

class File(Base):
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    status = Column(Enum(FileStatus), default=FileStatus.UPLOADED, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    user = relationship("User", back_populates="files")
    validations = relationship("Validation", back_populates="file")

class Validation(Base):
    __tablename__ = "validations"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    line_number = Column(Integer, nullable=False)
    field_name = Column(String(100), nullable=False)
    rule_name = Column(String(100), nullable=False)
    error_message = Column(Text, nullable=False)
    status = Column(Enum(ValidationStatus), nullable=False)
    validator_type = Column(String(50), nullable=False)  # 'deterministic' o 'ai'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    file = relationship("File", back_populates="validations")
