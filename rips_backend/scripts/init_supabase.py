#!/usr/bin/env python3
"""
Script para inicializar usuarios en Supabase
"""

import sys
import os
import hashlib
import secrets

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import supabase

def get_password_hash(password: str) -> str:
    """Generar hash de contraseña"""
    # Usar bcrypt si está disponible, sino usar hashlib
    try:
        import bcrypt
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    except ImportError:
        # Fallback simple
        salt = secrets.token_hex(16)
        return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()

def create_admin_user():
    """Crear usuario administrador por defecto"""
    try:
        # Verificar si ya existe un admin
        existing_admin = supabase.table("users").select("*").eq("role", "admin").execute()
        if existing_admin.data:
            print(f"⚠️  Usuario admin ya existe: {existing_admin.data[0]['username']}")
            return
        
        # Crear usuario admin
        admin_user = {
            "username": "admin",
            "email": "admin@rips.com",
            "hashed_password": get_password_hash("admin123"),
            "role": "admin",
            "is_active": "true"
        }
        
        result = supabase.table("users").insert(admin_user).execute()
        
        print("✅ Usuario administrador creado:")
        print(f"   Username: admin")
        print(f"   Password: admin123")
        print(f"   Email: admin@rips.com")
        
    except Exception as e:
        print(f"❌ Error al crear usuario admin: {e}")

def create_test_users():
    """Crear usuarios de prueba"""
    test_users = [
        {
            "username": "validator1",
            "email": "validator1@rips.com",
            "password": "validator123",
            "role": "validator"
        },
        {
            "username": "auditor1",
            "email": "auditor1@rips.com",
            "password": "auditor123",
            "role": "auditor"
        }
    ]
    
    try:
        for user_data in test_users:
            # Verificar si el usuario ya existe
            existing_user = supabase.table("users").select("*").eq("username", user_data["username"]).execute()
            if existing_user.data:
                print(f"⚠️  Usuario ya existe: {user_data['username']}")
                continue
            
            # Crear usuario
            user = {
                "username": user_data["username"],
                "email": user_data["email"],
                "hashed_password": get_password_hash(user_data["password"]),
                "role": user_data["role"],
                "is_active": "true"
            }
            
            result = supabase.table("users").insert(user).execute()
            
            print(f"✅ Usuario creado: {user_data['username']} ({user_data['role']})")
            
    except Exception as e:
        print(f"❌ Error al crear usuarios de prueba: {e}")

def test_supabase_connection():
    """Probar conexión a Supabase"""
    print("🔗 Probando conexión a Supabase...")
    
    try:
        from db.database import test_connection
        if test_connection():
            print("✅ Conexión a Supabase exitosa")
            return True
        else:
            print("❌ Error de conexión a Supabase")
            return False
    except Exception as e:
        print(f"❌ Error al conectar con Supabase: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Inicializando usuarios en Supabase...")
    print("=" * 60)
    
    # Probar conexión a Supabase
    if not test_supabase_connection():
        print("\n⚠️  No se pudo conectar a Supabase. Verifica tu configuración.")
        return
    
    # Crear usuarios
    print("\n📝 Creando usuarios...")
    create_admin_user()
    create_test_users()
    
    print("\n" + "=" * 60)
    print("✅ Inicialización completada!")
    print("\n📋 Usuarios disponibles:")
    print("   - admin / admin123 (Administrador)")
    print("   - validator1 / validator123 (Validador)")
    print("   - auditor1 / auditor123 (Auditor)")
    print("\n🌐 Inicia el servidor con: python main.py")
    print("📖 Documentación: http://localhost:8000/docs")

if __name__ == "__main__":
    main()


