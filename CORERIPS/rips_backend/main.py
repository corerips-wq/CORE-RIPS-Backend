from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.supabase_routes import router
from db.database import test_connection

# Verificar conexión a Supabase
if not test_connection():
    print("⚠️  Advertencia: No se pudo conectar a Supabase")
else:
    print("✅ Conexión a Supabase exitosa")

app = FastAPI(
    title="RIPS Validator API",
    description="API para validación de archivos RIPS (Registros Individuales de Prestación de Servicios de Salud)",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "RIPS Validator API - Sistema de validación de archivos RIPS"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "rips-validator"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
