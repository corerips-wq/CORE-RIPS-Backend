#!/usr/bin/env python3
"""
Script para ejecutar las pruebas del proyecto
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Ejecutar comando y mostrar resultado"""
    print(f"\n🔄 {description}...")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Warnings:", result.stderr)
        print(f"✅ {description} completado exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}:")
        print(e.stdout)
        print(e.stderr)
        return False

def main():
    """Función principal"""
    print("🧪 Ejecutando pruebas del proyecto RIPS Validator")
    print("=" * 60)
    
    # Cambiar al directorio del proyecto
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_dir)
    
    success = True
    
    # Ejecutar pruebas unitarias
    if not run_command("python -m pytest tests/ -v", "Pruebas unitarias"):
        success = False
    
    # Ejecutar pruebas con cobertura
    if not run_command("python -m pytest tests/ --cov=. --cov-report=term-missing", "Pruebas con cobertura"):
        success = False
    
    # Ejecutar linting (si está disponible)
    try:
        subprocess.run("flake8 --version", shell=True, check=True, capture_output=True)
        if not run_command("flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics", "Linting básico"):
            success = False
    except subprocess.CalledProcessError:
        print("⚠️  flake8 no está instalado, saltando linting")
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Todas las pruebas pasaron exitosamente!")
    else:
        print("❌ Algunas pruebas fallaron. Revisa los errores arriba.")
        sys.exit(1)

if __name__ == "__main__":
    main()
