from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta

from db.database import get_db
from models.models import User
from models.schemas import (
    UserCreate, UserResponse, LoginRequest, Token,
    UploadResponse, ValidationRequest, ValidationResultsResponse,
    FileResponse
)
from services.auth import (
    authenticate_user, create_access_token, get_current_active_user,
    get_password_hash, require_role, ACCESS_TOKEN_EXPIRE_MINUTES
)
from services.file_service import FileService
from services.validation_service import ValidationService
from models.models import User as UserModel

router = APIRouter()
security = HTTPBearer()

# Servicios
file_service = FileService()
validation_service = ValidationService()

# Endpoints de autenticación
@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Registrar nuevo usuario"""
    
    # Verificar si el usuario ya existe
    db_user = db.query(UserModel).filter(UserModel.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="El nombre de usuario ya está registrado"
        )
    
    # Verificar si el email ya existe
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="El email ya está registrado"
        )
    
    # Crear nuevo usuario
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserResponse.from_orm(db_user)

@router.post("/auth/login", response_model=Token)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Iniciar sesión"""
    
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/auth/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Obtener información del usuario actual"""
    return UserResponse.from_orm(current_user)

# Endpoints de archivos
@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Subir archivo RIPS"""
    
    try:
        file_response = await file_service.upload_file(file, current_user, db)
        
        return UploadResponse(
            message="Archivo subido exitosamente",
            file_id=file_response.id,
            filename=file_response.original_filename
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al subir archivo: {str(e)}"
        )

@router.get("/files", response_model=List[FileResponse])
async def get_user_files(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener archivos del usuario actual"""
    return file_service.get_user_files(current_user.id, db)

@router.delete("/files/{file_id}")
async def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Eliminar archivo"""
    
    success = file_service.delete_file(file_id, current_user, db)
    if success:
        return {"message": "Archivo eliminado exitosamente"}
    else:
        raise HTTPException(
            status_code=500,
            detail="Error al eliminar archivo"
        )

# Endpoints de validación
@router.post("/validate", response_model=ValidationResultsResponse)
async def validate_file(
    validation_request: ValidationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Validar archivo RIPS"""
    
    try:
        results = validation_service.validate_file(
            validation_request.file_id,
            validation_request.validation_types,
            db
        )
        return results
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error durante validación: {str(e)}"
        )

@router.get("/results/{file_id}", response_model=ValidationResultsResponse)
async def get_validation_results(
    file_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener resultados de validación"""
    
    try:
        results = validation_service.get_validation_results(file_id, db)
        return results
        
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener resultados: {str(e)}"
        )

# Endpoints administrativos
@router.get("/admin/users", response_model=List[UserResponse])
async def get_all_users(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Obtener todos los usuarios (solo admin)"""
    users = db.query(UserModel).all()
    return [UserResponse.from_orm(user) for user in users]

@router.get("/admin/files", response_model=List[FileResponse])
async def get_all_files(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Obtener todos los archivos (solo admin)"""
    from models.models import File as FileModel
    files = db.query(FileModel).all()
    return [FileResponse.from_orm(file) for file in files]
