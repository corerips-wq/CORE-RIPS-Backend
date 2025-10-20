from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración para Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# Configuración temporal para despliegue sin Supabase
if not SUPABASE_URL or not SUPABASE_ANON_KEY or SUPABASE_URL == "https://placeholder.supabase.co":
    print("⚠️  Modo desarrollo: Supabase no configurado, usando mock")
    supabase = None
else:
    # Cliente de Supabase
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def get_db():
    """Dependency para obtener cliente de Supabase"""
    return supabase

def test_connection():
    """Probar conexión a Supabase"""
    try:
        # Probar una consulta simple
        result = supabase.table("users").select("id").limit(1).execute()
        return True
    except Exception as e:
        print(f"Error conectando a Supabase: {e}")
        return False
