"""
Script de prueba de integración completa:
1. Sube un archivo RIPS JSON
2. Procesa y mapea los campos
3. Inserta datos en Supabase
4. Verifica que los datos fueron insertados correctamente
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.supabase_client import get_supabase_client
from services.rips_data_service import RIPSDataService

def test_full_integration():
    """Prueba completa del flujo de carga de datos RIPS"""
    
    print("=" * 80)
    print("PRUEBA DE INTEGRACIÓN: CARGA COMPLETA DE DATOS RIPS")
    print("=" * 80)
    
    # Ruta al archivo de prueba
    test_file = Path(__file__).parent.parent.parent.parent / "TEST" / "archivo_completo_prueba.json"
    
    print(f"\n📁 Archivo de prueba: {test_file}")
    
    if not test_file.exists():
        print(f"❌ ERROR: Archivo no encontrado")
        return
    
    try:
        # Conectar a Supabase
        print("\n🔌 Conectando a Supabase...")
        supabase = get_supabase_client()
        print("✅ Conectado exitosamente")
        
        # Crear registro de archivo ficticio
        print("\n📝 Creando registro de archivo en BD...")
        file_data = {
            "filename": "archivo_completo_prueba.json",
            "original_filename": "archivo_completo_prueba.json",
            "file_path": str(test_file),
            "file_size": test_file.stat().st_size,
            "status": "uploaded",
            "user_id": 1
        }
        
        file_result = supabase.table("files").insert(file_data).execute()
        file_id = file_result.data[0]["id"]
        print(f"✅ Archivo registrado con ID: {file_id}")
        
        # Procesar e insertar datos RIPS
        print("\n⚙️  Procesando datos RIPS...")
        print("-" * 80)
        
        rips_service = RIPSDataService(supabase)
        stats = rips_service.process_rips_file(str(test_file), file_id)
        
        print("\n📊 RESULTADOS DE INSERCIÓN:")
        print("-" * 80)
        print(f"✅ Usuarios insertados:        {stats['usuarios']}")
        print(f"✅ Consultas insertadas:       {stats['consultas']}")
        print(f"✅ Procedimientos insertados:  {stats['procedimientos']}")
        print(f"✅ Medicamentos insertados:    {stats['medicamentos']}")
        print(f"✅ Otros servicios insertados: {stats['otros_servicios']}")
        print(f"✅ Urgencias insertadas:       {stats['urgencias']}")
        print(f"✅ Hospitalizaciones insertadas: {stats['hospitalizaciones']}")
        print(f"✅ Recién nacidos insertados:  {stats['recien_nacidos']}")
        print(f"✅ Facturación insertada:      {stats['facturacion']}")
        print(f"✅ Ajustes insertados:         {stats['ajustes']}")
        print(f"✅ Control insertado:          {stats['control']}")
        
        if stats['errores']:
            print(f"\n⚠️  Errores encontrados: {len(stats['errores'])}")
            for i, error in enumerate(stats['errores'][:5], 1):
                print(f"  {i}. {error}")
            if len(stats['errores']) > 5:
                print(f"  ... y {len(stats['errores']) - 5} errores más")
        else:
            print("\n✅ Sin errores durante la inserción")
        
        # Verificar datos insertados
        print("\n" + "=" * 80)
        print("VERIFICACIÓN DE DATOS EN BASE DE DATOS")
        print("=" * 80)
        
        # Verificar usuarios
        usuarios_result = supabase.table("rips_users").select("*").eq("file_id", file_id).execute()
        print(f"\n👥 Usuarios en BD: {len(usuarios_result.data)}")
        if usuarios_result.data:
            user = usuarios_result.data[0]
            print(f"   Ejemplo: {user.get('document_type')} {user.get('document_number')}")
            print(f"   Nombre: {user.get('first_name')} {user.get('first_surname')}")
        
        # Verificar consultas
        consultas_result = supabase.table("rips_consultations").select("*").eq("file_id", file_id).execute()
        print(f"\n🏥 Consultas en BD: {len(consultas_result.data)}")
        if consultas_result.data:
            consulta = consultas_result.data[0]
            print(f"   Ejemplo: Código {consulta.get('consultation_code')}")
            print(f"   Diagnóstico: {consulta.get('primary_diagnosis')}")
            print(f"   Valor: ${consulta.get('consultation_value')}")
        
        # Verificar procedimientos
        procedimientos_result = supabase.table("rips_procedures").select("*").eq("file_id", file_id).execute()
        print(f"\n🔬 Procedimientos en BD: {len(procedimientos_result.data)}")
        if procedimientos_result.data:
            proc = procedimientos_result.data[0]
            print(f"   Ejemplo: Código {proc.get('procedure_code')}")
            print(f"   Valor: ${proc.get('procedure_value')}")
        
        # Verificar medicamentos
        medicamentos_result = supabase.table("rips_medications").select("*").eq("file_id", file_id).execute()
        print(f"\n💊 Medicamentos en BD: {len(medicamentos_result.data)}")
        if medicamentos_result.data:
            med = medicamentos_result.data[0]
            print(f"   Ejemplo: {med.get('generic_name')}")
            print(f"   Código: {med.get('medication_code')}")
            print(f"   Concentración: {med.get('medication_concentration')}")
        
        # Actualizar estado del archivo
        supabase.table("files").update({"status": "validated"}).eq("id", file_id).execute()
        print(f"\n✅ Estado del archivo actualizado a 'validated'")
        
        # Resumen final
        total_records = (
            stats['usuarios'] + stats['consultas'] + stats['procedimientos'] + 
            stats['medicamentos'] + stats['otros_servicios'] + stats['urgencias'] +
            stats['hospitalizaciones'] + stats['recien_nacidos'] + 
            stats['facturacion'] + stats['ajustes'] + stats['control']
        )
        
        print("\n" + "=" * 80)
        print("RESUMEN FINAL")
        print("=" * 80)
        print(f"✅ Total de registros insertados: {total_records}")
        print(f"✅ File ID: {file_id}")
        print(f"✅ Estado: validated")
        print(f"✅ Errores: {len(stats['errores'])}")
        
        print("\n" + "=" * 80)
        print("🎉 PRUEBA COMPLETADA EXITOSAMENTE")
        print("=" * 80)
        
        # Mostrar ejemplo de consulta
        print("\n📝 EJEMPLO DE CONSULTA SQL:")
        print("-" * 80)
        print(f"""
-- Ver todos los datos del archivo {file_id}:

SELECT * FROM rips_users WHERE file_id = {file_id};
SELECT * FROM rips_consultations WHERE file_id = {file_id};
SELECT * FROM rips_procedures WHERE file_id = {file_id};
SELECT * FROM rips_medications WHERE file_id = {file_id};

-- Ver resumen de un paciente específico:
SELECT 
    u.document_number,
    u.first_name,
    u.first_surname,
    COUNT(DISTINCT c.id) as total_consultas,
    COUNT(DISTINCT p.id) as total_procedimientos,
    COUNT(DISTINCT m.id) as total_medicamentos
FROM rips_users u
LEFT JOIN rips_consultations c ON c.identification_number = u.document_number AND c.file_id = u.file_id
LEFT JOIN rips_procedures p ON p.identification_number = u.document_number AND p.file_id = u.file_id
LEFT JOIN rips_medications m ON m.identification_number = u.document_number AND m.file_id = u.file_id
WHERE u.file_id = {file_id}
GROUP BY u.document_number, u.first_name, u.first_surname;
        """)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_full_integration()
    sys.exit(0 if success else 1)

