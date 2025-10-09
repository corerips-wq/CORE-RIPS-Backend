#!/usr/bin/env python3
"""
Script interactivo para configurar Supabase
"""

import os
import re
from pathlib import Path

def main():
    print("🚀 CONFIGURADOR INTERACTIVO DE SUPABASE")
    print("=" * 50)
    
    print("\n📋 PASOS PARA OBTENER CREDENCIALES:")
    print("1. Ve a https://supabase.com")
    print("2. Crea cuenta y nuevo proyecto")
    print("3. Ve a Settings → Database")
    print("4. Copia la 'Connection string'")
    print("5. Ve a Settings → API")
    print("6. Copia 'Project URL' y 'anon public key'")
    
    print("\n" + "="*50)
    
    # Solicitar credenciales
    print("\n🔐 INGRESA TUS CREDENCIALES DE SUPABASE:")
    
    database_url = input("\n1️⃣  DATABASE_URL (Connection string completa): ").strip()
    supabase_url = input("2️⃣  SUPABASE_URL (Project URL): ").strip()
    anon_key = input("3️⃣  SUPABASE_ANON_KEY (anon public): ").strip()
    
    # Generar secret key
    import secrets
    secret_key = secrets.token_urlsafe(32)
    print(f"4️⃣  SECRET_KEY generada automáticamente: {secret_key}")
    
    # Validar inputs básicos
    if not database_url or not supabase_url or not anon_key:
        print("❌ Error: Todos los campos son obligatorios")
        return
    
    if not database_url.startswith("postgresql://"):
        print("❌ Error: DATABASE_URL debe empezar con 'postgresql://'")
        return
    
    if not supabase_url.startswith("https://"):
        print("❌ Error: SUPABASE_URL debe empezar con 'https://'")
        return
    
    # Crear archivo .env
    env_content = f"""# Configuración de Supabase
DATABASE_URL={database_url}
SUPABASE_URL={supabase_url}
SUPABASE_ANON_KEY={anon_key}
SUPABASE_SERVICE_ROLE_KEY=optional-service-role-key

# JWT Configuration
SECRET_KEY={secret_key}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development
"""
    
    # Escribir archivo .env
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("\n✅ Archivo .env creado exitosamente")
    except Exception as e:
        print(f"❌ Error creando .env: {e}")
        return
    
    # Probar conexión
    print("\n🔄 Probando conexión a Supabase...")
    try:
        test_connection()
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print("\n💡 POSIBLES SOLUCIONES:")
        print("- Verificar que la DATABASE_URL sea correcta")
        print("- Verificar que el proyecto de Supabase esté activo")
        print("- Verificar conexión a internet")
        return
    
    print("\n🎉 ¡CONFIGURACIÓN COMPLETADA!")
    print("="*50)
    print("✅ Supabase configurado correctamente")
    print("✅ Conexión probada exitosamente")
    print("✅ Archivo .env creado")
    print("\n🚀 PRÓXIMOS PASOS:")
    print("1. Ejecutar: python scripts/init_db.py")
    print("2. Ejecutar: python start.py")
    print("3. Ir a: http://localhost:8000/docs")

def test_connection():
    """Probar conexión a Supabase"""
    from db.database import engine
    from sqlalchemy import text
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1 as test"))
        row = result.fetchone()
        if row and row[0] == 1:
            print("✅ Conexión a Supabase exitosa")
        else:
            raise Exception("Respuesta inesperada de la base de datos")

if __name__ == "__main__":
    main()
