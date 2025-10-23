from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from db.database import get_db
from supabase import Client
import os
import hashlib
import secrets
import json
from typing import List, Optional
from services.rips_data_service import RIPSDataService
import logging

logger = logging.getLogger(__name__)

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
    """Subir archivo RIPS y procesar datos"""
    file_id = None
    try:
        # Validar que sea archivo JSON
        if not file.filename.endswith('.json'):
            raise HTTPException(
                status_code=400, 
                detail="Solo se permiten archivos JSON. Por favor suba un archivo .json"
            )
        
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
        file_id = result.data[0]["id"]
        
        logger.info(f"Archivo guardado con ID: {file_id}")
        
        # Actualizar estado a procesando
        db.table("files").update({"status": "processing"}).eq("id", file_id).execute()
        
        # PROCESAR E INSERTAR DATOS RIPS
        try:
            logger.info(f"Iniciando procesamiento de datos RIPS del archivo {file_id}")
            rips_service = RIPSDataService(db)
            stats = rips_service.process_rips_file(file_path, file_id)
            
            # Actualizar estado a procesado exitosamente
            db.table("files").update({"status": "validated"}).eq("id", file_id).execute()
            
            logger.info(f"Datos RIPS insertados exitosamente: {stats}")
            
            return {
                "message": "Archivo procesado e insertado exitosamente",
                "file_id": file_id,
                "filename": file.filename,
                "status": "validated",
                "data_inserted": {
                    "usuarios": stats.get("usuarios", 0),
                    "consultas": stats.get("consultas", 0),
                    "procedimientos": stats.get("procedimientos", 0),
                    "medicamentos": stats.get("medicamentos", 0),
                    "otros_servicios": stats.get("otros_servicios", 0),
                    "urgencias": stats.get("urgencias", 0),
                    "hospitalizaciones": stats.get("hospitalizaciones", 0),
                    "recien_nacidos": stats.get("recien_nacidos", 0),
                    "facturacion": stats.get("facturacion", 0),
                    "ajustes": stats.get("ajustes", 0),
                    "control": stats.get("control", 0)
                },
                "errores": stats.get("errores", [])
            }
            
        except Exception as processing_error:
            # Si hay error en el procesamiento, actualizar estado
            db.table("files").update({"status": "error"}).eq("id", file_id).execute()
            logger.error(f"Error procesando datos RIPS: {str(processing_error)}")
            
            return {
                "message": "Archivo subido pero con errores al procesar datos",
                "file_id": file_id,
                "filename": file.filename,
                "status": "error",
                "error": str(processing_error)
            }
        
    except HTTPException:
        raise
    except Exception as e:
        # Si el archivo ya fue creado, actualizar estado a error
        if file_id:
            try:
                db.table("files").update({"status": "error"}).eq("id", file_id).execute()
            except:
                pass
        
        logger.error(f"Error al subir archivo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al subir archivo: {str(e)}")

@router.get("/files")
async def get_files(db: Client = Depends(get_db)):
    """Listar archivos del usuario"""
    try:
        result = db.table("files").select("*").eq("user_id", 1).execute()
        return {"files": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener archivos: {str(e)}")

class ValidateRequest(BaseModel):
    file_id: int
    validation_types: Optional[List[str]] = ["deterministic"]

@router.post("/validate")
async def validate_file(request: ValidateRequest, db: Client = Depends(get_db)):
    """Validar archivo RIPS"""
    try:
        file_id = request.file_id
        validation_types = request.validation_types
        # Obtener archivo
        result = db.table("files").select("*").eq("id", file_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Archivo no encontrado")
        
        file_info = result.data[0]
        
        # Actualizar estado a procesando
        db.table("files").update({"status": "processing"}).eq("id", file_id).execute()
        
        # Ejecutar validaciones reales
        from validators.deterministic_enhanced import EnhancedDeterministicValidator
        
        validator = EnhancedDeterministicValidator()
        file_path = file_info["file_path"]
        
        # Determinar tipo de archivo
        filename_upper = file_info["filename"].upper()
        if "AC" in filename_upper:
            file_type = "AC"
        elif "AP" in filename_upper:
            file_type = "AP"
        elif "AM" in filename_upper:
            file_type = "AM"
        elif "AT" in filename_upper:
            file_type = "AT"
        elif "AU" in filename_upper:
            file_type = "AU"
        elif "AH" in filename_upper:
            file_type = "AH"
        elif "AN" in filename_upper:
            file_type = "AN"
        elif "US" in filename_upper:
            file_type = "US"
        else:
            file_type = "AC"
        
        # Ejecutar validación
        errors = validator.validate_file(file_path, file_type)
        
        # Guardar resultados en la base de datos
        total_errors = 0
        total_warnings = 0
        
        for error in errors:
            validation_data = {
                "file_id": file_id,
                "line_number": error.line,
                "field_name": error.field,
                "rule_name": "deterministic_validation",
                "error_message": error.error,
                "status": "failed",
                "validator_type": "deterministic"
            }
            db.table("validations").insert(validation_data).execute()
            total_errors += 1
        
        # Actualizar estado a validado
        db.table("files").update({"status": "validated"}).eq("id", file_id).execute()
        
        return {
            "message": "Validación completada",
            "file_id": file_id,
            "status": "validated",
            "errors": total_errors,
            "warnings": total_warnings,
            "total_validations": len(errors)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Actualizar estado a error
        db.table("files").update({"status": "error"}).eq("id", file_id).execute()
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
