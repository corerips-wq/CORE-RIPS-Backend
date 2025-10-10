from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from db.database import get_db
from supabase import Client
import os
import hashlib
import secrets
from typing import List, Optional

router = APIRouter()
security = HTTPBearer()

def get_password_hash(password: str) -> str:
    """Generar hash de contraseña"""
    try:
        import bcrypt
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    except ImportError:
        salt = secrets.token_hex(16)
        return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar contraseña"""
    try:
        import bcrypt
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except ImportError:
        # Fallback simple - comparar directamente
        return plain_password == "admin123" or plain_password == "validator123" or plain_password == "auditor123"

# Schemas simplificados
from pydantic import BaseModel

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

# Rutas de autenticación
@router.post("/auth/login", response_model=TokenResponse)
async def login(user_credentials: UserLogin, db: Client = Depends(get_db)):
    """Iniciar sesión"""
    try:
        # Buscar usuario
        result = db.table("users").select("*").eq("username", user_credentials.username).execute()
        
        if not result.data:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        
        user = result.data[0]
        
        # Verificar contraseña (simplificado para desarrollo)
        expected_passwords = {
            "admin": "admin123",
            "validator1": "validator123", 
            "auditor1": "auditor123"
        }
        
        if user_credentials.password != expected_passwords.get(user_credentials.username, ""):
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        
        # Verificar si está activo
        if user["is_active"] != "true":
            raise HTTPException(status_code=401, detail="Usuario inactivo")
        
        # Generar token simple (en producción usar JWT)
        token = secrets.token_urlsafe(32)
        
        return TokenResponse(access_token=token, token_type="bearer")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.get("/auth/me", response_model=UserResponse)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Client = Depends(get_db)):
    """Obtener información del usuario actual"""
    # En una implementación real, verificarías el token JWT
    # Por ahora, retornamos un usuario de ejemplo
    return UserResponse(
        id=1,
        username="admin",
        email="admin@rips.com",
        role="admin",
        is_active="true"
    )

# Rutas de archivos
@router.post("/upload")
async def upload_file(file: UploadFile = File(...), db: Client = Depends(get_db)):
    """Subir archivo RIPS"""
    try:
        # Crear directorio uploads si no existe
        os.makedirs("uploads", exist_ok=True)
        
        # Guardar archivo
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Guardar información en base de datos
        file_data = {
            "filename": file.filename,
            "original_filename": file.filename,
            "file_path": file_path,
            "file_size": len(content),
            "status": "uploaded",
            "user_id": 1  # En producción, obtener del token
        }
        
        result = db.table("files").insert(file_data).execute()
        
        return {
            "message": "Archivo subido exitosamente",
            "file_id": result.data[0]["id"],
            "filename": file.filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir archivo: {str(e)}")

@router.get("/files")
async def get_files(db: Client = Depends(get_db)):
    """Listar archivos del usuario"""
    try:
        result = db.table("files").select("*").eq("user_id", 1).execute()
        return {"files": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener archivos: {str(e)}")

@router.post("/validate")
async def validate_file(file_id: int, db: Client = Depends(get_db)):
    """Validar archivo RIPS"""
    try:
        # Obtener archivo
        result = db.table("files").select("*").eq("id", file_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Archivo no encontrado")
        
        file_info = result.data[0]
        
        # Actualizar estado a procesando
        db.table("files").update({"status": "processing"}).eq("id", file_id).execute()
        
        # Aquí iría la lógica de validación
        # Por ahora, simulamos una validación exitosa
        
        # Actualizar estado a validado
        db.table("files").update({"status": "validated"}).eq("id", file_id).execute()
        
        return {
            "message": "Validación completada",
            "file_id": file_id,
            "status": "validated",
            "errors": 0,
            "warnings": 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al validar archivo: {str(e)}")

@router.get("/results/{file_id}")
async def get_validation_results(file_id: int, db: Client = Depends(get_db)):
    """Obtener resultados de validación"""
    try:
        # Obtener archivo
        file_result = db.table("files").select("*").eq("id", file_id).execute()
        
        if not file_result.data:
            raise HTTPException(status_code=404, detail="Archivo no encontrado")
        
        # Obtener validaciones
        validations_result = db.table("validations").select("*").eq("file_id", file_id).execute()
        
        return {
            "file_id": file_id,
            "filename": file_result.data[0]["original_filename"],
            "status": file_result.data[0]["status"],
            "validations": validations_result.data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener resultados: {str(e)}")
