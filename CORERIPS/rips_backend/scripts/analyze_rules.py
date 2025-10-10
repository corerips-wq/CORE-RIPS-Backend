#!/usr/bin/env python3
"""
Script para analizar los archivos Excel de reglas RIPS
y generar las validaciones correspondientes
"""

import pandas as pd
import os
import sys
from pathlib import Path

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def analyze_excel_file(file_path, file_name):
    """Analizar un archivo Excel de reglas RIPS"""
    print(f"\n📊 Analizando: {file_name}")
    print("-" * 50)
    
    try:
        # Leer todas las hojas del archivo Excel
        excel_file = pd.ExcelFile(file_path)
        
        print(f"📋 Hojas encontradas: {len(excel_file.sheet_names)}")
        for sheet_name in excel_file.sheet_names:
            print(f"   - {sheet_name}")
        
        # Analizar cada hoja
        rules_data = {}
        for sheet_name in excel_file.sheet_names:
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                print(f"\n📄 Hoja '{sheet_name}':")
                print(f"   Filas: {len(df)}, Columnas: {len(df.columns)}")
                print(f"   Columnas: {list(df.columns)}")
                
                # Mostrar primeras filas para entender la estructura
                if not df.empty:
                    print(f"   Primeras 3 filas:")
                    for i, row in df.head(3).iterrows():
                        print(f"     Fila {i+1}: {dict(row)}")
                
                rules_data[sheet_name] = df
                
            except Exception as e:
                print(f"   ❌ Error leyendo hoja '{sheet_name}': {e}")
        
        return rules_data
        
    except Exception as e:
        print(f"❌ Error leyendo archivo {file_name}: {e}")
        return {}

def categorize_rules(rules_data, file_name):
    """Categorizar reglas en determinísticas vs IA"""
    print(f"\n🔍 Categorizando reglas de {file_name}")
    print("-" * 50)
    
    deterministic_rules = []
    ai_rules = []
    
    # Palabras clave para identificar reglas determinísticas
    deterministic_keywords = [
        'longitud', 'formato', 'obligatorio', 'numérico', 'fecha', 'código',
        'catálogo', 'lista', 'rango', 'mínimo', 'máximo', 'estructura',
        'campo', 'tipo', 'validar', 'verificar'
    ]
    
    # Palabras clave para identificar reglas de IA
    ai_keywords = [
        'coherencia', 'consistencia', 'anomalía', 'patrón', 'relación',
        'contexto', 'semántica', 'inteligencia', 'aprendizaje', 'predicción',
        'análisis', 'correlación', 'comportamiento'
    ]
    
    for sheet_name, df in rules_data.items():
        if df.empty:
            continue
            
        for index, row in df.iterrows():
            rule_text = ' '.join([str(val).lower() for val in row.values if pd.notna(val)])
            
            # Clasificar regla
            is_deterministic = any(keyword in rule_text for keyword in deterministic_keywords)
            is_ai = any(keyword in rule_text for keyword in ai_keywords)
            
            rule_info = {
                'file': file_name,
                'sheet': sheet_name,
                'row': index + 1,
                'content': dict(row),
                'text': rule_text
            }
            
            if is_deterministic and not is_ai:
                deterministic_rules.append(rule_info)
            elif is_ai:
                ai_rules.append(rule_info)
            else:
                # Por defecto, considerar como determinística
                deterministic_rules.append(rule_info)
    
    print(f"✅ Reglas determinísticas: {len(deterministic_rules)}")
    print(f"🤖 Reglas de IA: {len(ai_rules)}")
    
    return deterministic_rules, ai_rules

def generate_validation_code(deterministic_rules, ai_rules):
    """Generar código de validación basado en las reglas"""
    print(f"\n💻 Generando código de validación...")
    print("-" * 50)
    
    # Generar validaciones determinísticas
    det_code = generate_deterministic_code(deterministic_rules)
    
    # Generar validaciones de IA
    ai_code = generate_ai_code(ai_rules)
    
    return det_code, ai_code

def generate_deterministic_code(rules):
    """Generar código para validaciones determinísticas"""
    code_lines = []
    
    code_lines.append("# Validaciones determinísticas generadas automáticamente")
    code_lines.append("# Basadas en archivos Excel de reglas RIPS")
    code_lines.append("")
    
    for rule in rules[:10]:  # Mostrar solo las primeras 10 como ejemplo
        code_lines.append(f"# Regla de {rule['file']} - {rule['sheet']}")
        code_lines.append(f"# {rule['text'][:100]}...")
        code_lines.append("def validate_rule_example(self, value: str) -> bool:")
        code_lines.append("    # TODO: Implementar validación específica")
        code_lines.append("    return True")
        code_lines.append("")
    
    return "\n".join(code_lines)

def generate_ai_code(rules):
    """Generar código para validaciones de IA"""
    code_lines = []
    
    code_lines.append("# Validaciones de IA generadas automáticamente")
    code_lines.append("# Basadas en archivos Excel de reglas RIPS")
    code_lines.append("")
    
    for rule in rules[:5]:  # Mostrar solo las primeras 5 como ejemplo
        code_lines.append(f"# Regla de IA de {rule['file']} - {rule['sheet']}")
        code_lines.append(f"# {rule['text'][:100]}...")
        code_lines.append("def ai_validate_rule_example(self, data: dict) -> List[ErrorResponse]:")
        code_lines.append("    # TODO: Implementar validación con IA")
        code_lines.append("    return []")
        code_lines.append("")
    
    return "\n".join(code_lines)

def main():
    """Función principal"""
    print("📋 Analizador de Reglas RIPS")
    print("=" * 60)
    
    # Directorio de archivos Excel
    rules_dir = Path("/Users/ub-col-tec-t2q/Documents/Yully/RULESRIPS")
    
    if not rules_dir.exists():
        print("❌ Directorio RULESRIPS no encontrado")
        return
    
    # Archivos Excel a analizar
    excel_files = list(rules_dir.glob("*.xlsx"))
    
    if not excel_files:
        print("❌ No se encontraron archivos Excel")
        return
    
    print(f"📁 Archivos encontrados: {len(excel_files)}")
    
    all_deterministic_rules = []
    all_ai_rules = []
    
    # Analizar cada archivo
    for excel_file in excel_files:
        rules_data = analyze_excel_file(excel_file, excel_file.name)
        
        if rules_data:
            det_rules, ai_rules = categorize_rules(rules_data, excel_file.name)
            all_deterministic_rules.extend(det_rules)
            all_ai_rules.extend(ai_rules)
    
    # Generar código de validación
    det_code, ai_code = generate_validation_code(all_deterministic_rules, all_ai_rules)
    
    # Guardar resultados
    output_dir = Path("analysis_output")
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / "deterministic_rules.py", "w", encoding="utf-8") as f:
        f.write(det_code)
    
    with open(output_dir / "ai_rules.py", "w", encoding="utf-8") as f:
        f.write(ai_code)
    
    # Resumen final
    print(f"\n" + "=" * 60)
    print("📊 RESUMEN DEL ANÁLISIS")
    print(f"📁 Archivos analizados: {len(excel_files)}")
    print(f"✅ Reglas determinísticas: {len(all_deterministic_rules)}")
    print(f"🤖 Reglas de IA: {len(all_ai_rules)}")
    print(f"💾 Código generado en: analysis_output/")
    
    # Mostrar distribución por archivo
    print(f"\n📋 Distribución por archivo:")
    file_stats = {}
    for rule in all_deterministic_rules + all_ai_rules:
        file_name = rule['file']
        if file_name not in file_stats:
            file_stats[file_name] = {'det': 0, 'ai': 0}
        
        if rule in all_deterministic_rules:
            file_stats[file_name]['det'] += 1
        else:
            file_stats[file_name]['ai'] += 1
    
    for file_name, stats in file_stats.items():
        print(f"   {file_name}: {stats['det']} determinísticas, {stats['ai']} IA")

if __name__ == "__main__":
    main()
