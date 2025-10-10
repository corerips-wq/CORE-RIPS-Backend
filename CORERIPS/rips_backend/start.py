#!/usr/bin/env python3
"""
Script de inicio rápido para el sistema RIPS Validator
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Verificar versión de Python"""
    if sys.version_info < (3, 8):
        print("❌ Se requiere Python 3.8 o superior")
        print(f"   Versión actual: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} - OK")

def check_dependencies():
    """Verificar si las dependencias están instaladas"""
    try:
        import fastapi
        import sqlalchemy
        import psycopg2
        print("✅ Dependencias principales - OK")
        return True
    except ImportError as e:
        print(f"❌ Dependencias faltantes: {e}")
        print("   Ejecuta: pip install -r requirements.txt")
        return False

def check_env_file():
    """Verificar archivo de configuración"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  Archivo .env no encontrado")
        print("   Copiando .env.example a .env...")
        
        example_file = Path(".env.example")
        if example_file.exists():
            import shutil
            shutil.copy(".env.example", ".env")
            print("✅ Archivo .env creado")
            print("   📝 Edita .env con tus configuraciones de base de datos")
        else:
            print("❌ Archivo .env.example no encontrado")
            return False
    else:
        print("✅ Archivo .env - OK")
    return True

def check_database():
    """Verificar conexión a base de datos"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        from db.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Conexión a base de datos - OK")
        return True
    except Exception as e:
        print(f"❌ Error de conexión a base de datos: {e}")
        print("   Verifica la configuración DATABASE_URL en .env")
        return False

def initialize_database():
    """Inicializar base de datos"""
    print("\n🔄 Inicializando base de datos...")
    try:
        from scripts.init_db import main as init_db_main
        init_db_main()
        return True
    except Exception as e:
        print(f"❌ Error al inicializar base de datos: {e}")
        return False

def start_server():
    """Iniciar servidor"""
    print("\n🚀 Iniciando servidor RIPS Validator...")
    print("   URL: http://localhost:8000")
    print("   Docs: http://localhost:8000/docs")
    print("   Presiona Ctrl+C para detener")
    print("-" * 50)
    
    try:
        import uvicorn
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido")
    except Exception as e:
        print(f"❌ Error al iniciar servidor: {e}")

def main():
    """Función principal"""
    print("🏥 RIPS Validator - Sistema de Validación")
    print("=" * 50)
    
    # Verificaciones previas
    print("\n🔍 Verificando sistema...")
    check_python_version()
    
    if not check_dependencies():
        return
    
    if not check_env_file():
        return
    
    # Verificar base de datos
    print("\n🗄️  Verificando base de datos...")
    db_ok = check_database()
    
    if not db_ok:
        print("\n❓ ¿Deseas inicializar la base de datos? (y/n): ", end="")
        response = input().lower().strip()
        
        if response in ['y', 'yes', 's', 'si']:
            if not initialize_database():
                return
        else:
            print("⚠️  Base de datos no inicializada. El servidor puede fallar.")
    
    # Iniciar servidor
    start_server()

if __name__ == "__main__":
    main()
