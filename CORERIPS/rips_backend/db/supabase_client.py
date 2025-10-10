from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

class SupabaseClient:
    """Cliente de Supabase para reemplazar SQLAlchemy"""
    
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_ANON_KEY")
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL y SUPABASE_ANON_KEY deben estar configurados en .env")
        
        self.client: Client = create_client(self.url, self.key)
    
    def test_connection(self) -> bool:
        """Probar conexión a Supabase"""
        try:
            # Probar una consulta simple
            result = self.client.table("users").select("id").limit(1).execute()
            return True
        except Exception as e:
            print(f"Error conectando a Supabase: {e}")
            return False
    
    def get_client(self) -> Client:
        """Obtener cliente de Supabase"""
        return self.client

# Instancia global del cliente
supabase_client = SupabaseClient()

def get_supabase() -> Client:
    """Dependency para obtener cliente de Supabase"""
    return supabase_client.get_client()

def test_supabase_connection() -> bool:
    """Probar conexión a Supabase"""
    return supabase_client.test_connection()


