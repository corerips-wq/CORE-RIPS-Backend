import os
import shutil
from typing import List
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from models.models import File, User, FileStatus
from models.schemas import FileCreate, FileResponse
import uuid

class FileService:
    """Servicio para manejo de archivos"""
    
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)
    
    async def upload_file(self, file: UploadFile, user: User, db: Session) -> FileResponse:
        """Subir archivo al servidor"""
        
        # Validar tipo de archivo
        if not file.filename.endswith(('.txt', '.csv')):
            raise HTTPException(
                status_code=400,
                detail="Tipo de archivo no válido. Solo se permiten archivos .txt y .csv"
            )
        
        # Generar nombre único para el archivo
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(self.upload_dir, unique_filename)
        
        try:
            # Guardar archivo en disco
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Obtener tamaño del archivo
            file_size = os.path.getsize(file_path)
            
            # Crear registro en base de datos
            db_file = File(
                filename=unique_filename,
                original_filename=file.filename,
                file_path=file_path,
                file_size=file_size,
                status=FileStatus.UPLOADED,
                user_id=user.id
            )
            
            db.add(db_file)
            db.commit()
            db.refresh(db_file)
            
            return FileResponse.from_orm(db_file)
            
        except Exception as e:
            # Limpiar archivo si hay error
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=500,
                detail=f"Error al subir archivo: {str(e)}"
            )
    
    def get_file(self, file_id: int, db: Session) -> File:
        """Obtener archivo por ID"""
        db_file = db.query(File).filter(File.id == file_id).first()
        if not db_file:
            raise HTTPException(
                status_code=404,
                detail="Archivo no encontrado"
            )
        return db_file
    
    def get_user_files(self, user_id: int, db: Session) -> List[FileResponse]:
        """Obtener archivos de un usuario"""
        files = db.query(File).filter(File.user_id == user_id).all()
        return [FileResponse.from_orm(file) for file in files]
    
    def update_file_status(self, file_id: int, status: FileStatus, db: Session) -> FileResponse:
        """Actualizar estado del archivo"""
        db_file = self.get_file(file_id, db)
        db_file.status = status
        db.commit()
        db.refresh(db_file)
        return FileResponse.from_orm(db_file)
    
    def delete_file(self, file_id: int, user: User, db: Session) -> bool:
        """Eliminar archivo"""
        db_file = self.get_file(file_id, db)
        
        # Verificar que el usuario sea propietario o admin
        if db_file.user_id != user.id and user.role.value != "admin":
            raise HTTPException(
                status_code=403,
                detail="No tiene permisos para eliminar este archivo"
            )
        
        try:
            # Eliminar archivo físico
            if os.path.exists(db_file.file_path):
                os.remove(db_file.file_path)
            
            # Eliminar registro de base de datos
            db.delete(db_file)
            db.commit()
            return True
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error al eliminar archivo: {str(e)}"
            )
