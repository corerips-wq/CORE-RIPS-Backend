"""
Script de prueba para verificar el mapeo de campos JSON → Base de Datos
Usa el archivo de prueba de la carpeta TEST
"""

import json
import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from validators.field_mappings import (
    map_json_to_db,
    get_table_name,
    FILE_TYPE_MAPPINGS
)


def test_field_mapping():
    """Prueba el mapeo de campos usando archivo real de TEST"""
    
    # Ruta al archivo de prueba
    test_file = Path(__file__).parent.parent.parent.parent / "TEST" / "archivo_completo_prueba.json"
    
    print("=" * 80)
    print("PRUEBA DE MAPEO DE CAMPOS RIPS: JSON → BASE DE DATOS")
    print("=" * 80)
    print(f"\nArchivo de prueba: {test_file}")
    
    if not test_file.exists():
        print(f"❌ ERROR: Archivo no encontrado: {test_file}")
        return
    
    # Leer archivo JSON
    with open(test_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("\n✅ Archivo cargado exitosamente")
    print(f"Tipo de documento: {data.get('numDocumentoIdObligado')}")
    print(f"Número de factura: {data.get('numFactura')}")
    
    # =========================================================================
    # PRUEBA 1: Usuarios
    # =========================================================================
    print("\n" + "=" * 80)
    print("PRUEBA 1: MAPEO DE USUARIOS (US)")
    print("=" * 80)
    
    if "usuarios" in data and len(data["usuarios"]) > 0:
        usuario_json = data["usuarios"][0]
        print("\n📥 DATOS DE ENTRADA (JSON en español):")
        print(json.dumps(usuario_json, indent=2, ensure_ascii=False))
        
        usuario_db = map_json_to_db(usuario_json, "US")
        print("\n📤 DATOS MAPEADOS (BD en inglés):")
        print(json.dumps(usuario_db, indent=2, ensure_ascii=False))
        
        print(f"\n📊 Tabla destino: {get_table_name('US')}")
        print(f"✅ Campos mapeados: {len(usuario_db)}")
    
    # =========================================================================
    # PRUEBA 2: Consultas
    # =========================================================================
    print("\n" + "=" * 80)
    print("PRUEBA 2: MAPEO DE CONSULTAS (AC)")
    print("=" * 80)
    
    if "usuarios" in data and len(data["usuarios"]) > 0:
        usuario = data["usuarios"][0]
        if "servicios" in usuario and "consultas" in usuario["servicios"]:
            consultas = usuario["servicios"]["consultas"]
            if len(consultas) > 0:
                consulta_json = consultas[0]
                print("\n📥 DATOS DE ENTRADA (JSON en español):")
                print(json.dumps(consulta_json, indent=2, ensure_ascii=False))
                
                consulta_db = map_json_to_db(consulta_json, "AC")
                print("\n📤 DATOS MAPEADOS (BD en inglés):")
                print(json.dumps(consulta_db, indent=2, ensure_ascii=False))
                
                print(f"\n📊 Tabla destino: {get_table_name('AC')}")
                print(f"✅ Campos mapeados: {len(consulta_db)}")
                
                # Verificar campos críticos
                print("\n🔍 VERIFICACIÓN DE CAMPOS CRÍTICOS:")
                critical_fields = {
                    "codPrestador": "provider_code",
                    "tipoDocumentoIdentificacion": "identification_type",
                    "numDocumentoIdentificacion": "identification_number",
                    "codDiagnosticoPrincipal": "primary_diagnosis",
                    "fechaInicioAtencion": "consultation_date"
                }
                
                for json_field, db_field in critical_fields.items():
                    if json_field in consulta_json:
                        if db_field in consulta_db:
                            print(f"  ✅ {json_field} → {db_field} = {consulta_db[db_field]}")
                        else:
                            print(f"  ❌ {json_field} NO MAPEADO a {db_field}")
    
    # =========================================================================
    # PRUEBA 3: Procedimientos
    # =========================================================================
    print("\n" + "=" * 80)
    print("PRUEBA 3: MAPEO DE PROCEDIMIENTOS (AP)")
    print("=" * 80)
    
    if "usuarios" in data and len(data["usuarios"]) > 0:
        usuario = data["usuarios"][0]
        if "servicios" in usuario and "procedimientos" in usuario["servicios"]:
            procedimientos = usuario["servicios"]["procedimientos"]
            if len(procedimientos) > 0:
                procedimiento_json = procedimientos[0]
                print("\n📥 DATOS DE ENTRADA (JSON en español):")
                print(json.dumps(procedimiento_json, indent=2, ensure_ascii=False))
                
                procedimiento_db = map_json_to_db(procedimiento_json, "AP")
                print("\n📤 DATOS MAPEADOS (BD en inglés):")
                print(json.dumps(procedimiento_db, indent=2, ensure_ascii=False))
                
                print(f"\n📊 Tabla destino: {get_table_name('AP')}")
                print(f"✅ Campos mapeados: {len(procedimiento_db)}")
    
    # =========================================================================
    # PRUEBA 4: Medicamentos
    # =========================================================================
    print("\n" + "=" * 80)
    print("PRUEBA 4: MAPEO DE MEDICAMENTOS (AM)")
    print("=" * 80)
    
    if "usuarios" in data and len(data["usuarios"]) > 0:
        usuario = data["usuarios"][0]
        if "servicios" in usuario and "medicamentos" in usuario["servicios"]:
            medicamentos = usuario["servicios"]["medicamentos"]
            if len(medicamentos) > 0:
                medicamento_json = medicamentos[0]
                print("\n📥 DATOS DE ENTRADA (JSON en español):")
                print(json.dumps(medicamento_json, indent=2, ensure_ascii=False))
                
                medicamento_db = map_json_to_db(medicamento_json, "AM")
                print("\n📤 DATOS MAPEADOS (BD en inglés):")
                print(json.dumps(medicamento_db, indent=2, ensure_ascii=False))
                
                print(f"\n📊 Tabla destino: {get_table_name('AM')}")
                print(f"✅ Campos mapeados: {len(medicamento_db)}")
    
    # =========================================================================
    # RESUMEN FINAL
    # =========================================================================
    print("\n" + "=" * 80)
    print("RESUMEN DE MAPEOS DISPONIBLES")
    print("=" * 80)
    
    for file_type, mapping in FILE_TYPE_MAPPINGS.items():
        table_name = get_table_name(file_type)
        print(f"\n{file_type} → {table_name}")
        print(f"  Campos mapeados: {len(mapping)}")
        print(f"  Ejemplos:")
        for i, (json_field, db_field) in enumerate(list(mapping.items())[:3]):
            print(f"    - {json_field} → {db_field}")
        if len(mapping) > 3:
            print(f"    ... y {len(mapping) - 3} campos más")
    
    # =========================================================================
    # GENERACIÓN DE INSERT EXAMPLE
    # =========================================================================
    print("\n" + "=" * 80)
    print("EJEMPLO DE INSERT A SUPABASE")
    print("=" * 80)
    
    if "usuarios" in data and len(data["usuarios"]) > 0:
        usuario = data["usuarios"][0]
        if "servicios" in usuario and "consultas" in usuario["servicios"]:
            consultas = usuario["servicios"]["consultas"]
            if len(consultas) > 0:
                consulta_json = consultas[0]
                consulta_db = map_json_to_db(consulta_json, "AC")
                
                print("\n# Código Python para insertar en Supabase:")
                print("```python")
                print("from supabase import create_client")
                print("from validators.field_mappings import map_json_to_db, get_table_name")
                print()
                print("# Datos de la consulta (del JSON)")
                print(f"consulta_json = {json.dumps(consulta_json, indent=2, ensure_ascii=False)}")
                print()
                print("# Mapear a formato de BD")
                print('consulta_db = map_json_to_db(consulta_json, "AC")')
                print()
                print("# Insertar en Supabase")
                print('table_name = get_table_name("AC")  # "rips_consultations"')
                print('result = supabase.table(table_name).insert(consulta_db).execute()')
                print("```")
    
    print("\n" + "=" * 80)
    print("✅ PRUEBA COMPLETADA EXITOSAMENTE")
    print("=" * 80)


if __name__ == "__main__":
    test_field_mapping()

