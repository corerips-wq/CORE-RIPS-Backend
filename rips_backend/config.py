import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración para diferentes entornos"""
    
    # Configuración base
    SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Base de datos por entorno
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    
    if ENVIRONMENT == "development":
        # Desarrollo local
        DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:dev123@localhost:5432/rips_db")
        DEBUG = True
        SSL_REQUIRED = False
    elif ENVIRONMENT == "production":
        # Producción (Supabase o servidor cloud)
        DATABASE_URL = os.getenv("DATABASE_URL")
        DEBUG = False
        SSL_REQUIRED = True
        ENCRYPTION_ENABLED = True
    else:
        # Testing
        DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:test123@localhost:5432/rips_test")
        DEBUG = True
        SSL_REQUIRED = False

# Instancia de configuración
config = Config()


