#!/usr/bin/env python3
"""
Script para probar todas las reglas determinísticas RIPS contra archivos de prueba
Genera un reporte detallado de cada regla y su resultado
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, List, Any
from collections import defaultdict

# Agregar el directorio padre al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from validators.deterministic_enhanced import EnhancedDeterministicValidator
from models.schemas import ErrorResponse


class RulesTestReport:
    """Generador de reportes detallados de pruebas de reglas"""
    
    def __init__(self):
        self.validator = EnhancedDeterministicValidator()
        self.test_results = []
        self.rules_tested = defaultdict(int)
        self.rules_passed = defaultdict(int)
        self.rules_failed = defaultdict(int)
        
    def test_file(self, file_path: str, file_type: str = "AC") -> Dict[str, Any]:
        """Probar un archivo y retornar resultados detallados"""
        print(f"\n{'='*80}")
        print(f"🔍 Probando archivo: {os.path.basename(file_path)}")
        print(f"   Tipo de archivo: {file_type}")
        print(f"{'='*80}\n")
        
        # Ejecutar validación
        errors = self.validator.validate_file(file_path, file_type)
        
        # Analizar resultados
        result = {
            "file": os.path.basename(file_path),
            "file_path": file_path,
            "file_type": file_type,
            "timestamp": datetime.now().isoformat(),
            "total_errors": len(errors),
            "errors_by_type": defaultdict(list),
            "errors_by_rule": defaultdict(int),
            "validation_success": len([e for e in errors if "✅" in e.error]) > 0,
            "errors": []
        }
        
        # Clasificar errores
        for error in errors:
            error_dict = {
                "line": error.line,
                "field": error.field,
                "error": error.error
            }
            result["errors"].append(error_dict)
            result["errors_by_type"][error.field].append(error_dict)
            
            # Identificar regla aplicada
            if "✅" in error.error:
                result["errors_by_rule"]["VALIDATION_SUCCESS"] += 1
            elif "Campo obligatorio" in error.error:
                result["errors_by_rule"]["MANDATORY_FIELD"] += 1
            elif "Formato" in error.error or "formato" in error.error:
                result["errors_by_rule"]["FORMAT_ERROR"] += 1
            elif "Longitud" in error.error:
                result["errors_by_rule"]["LENGTH_ERROR"] += 1
            elif "Valor no permitido" in error.error:
                result["errors_by_rule"]["VALUE_NOT_ALLOWED"] += 1
            elif "Fecha" in error.error or "fecha" in error.error:
                result["errors_by_rule"]["DATE_ERROR"] += 1
            elif "numérico" in error.error or "Numérico" in error.error:
                result["errors_by_rule"]["NUMERIC_ERROR"] += 1
            else:
                result["errors_by_rule"]["OTHER"] += 1
        
        self.test_results.append(result)
        return result
    
    def print_file_results(self, result: Dict[str, Any]):
        """Imprimir resultados de un archivo"""
        print(f"\n📊 RESULTADOS - {result['file']}")
        print(f"{'─'*80}")
        
        if result["validation_success"]:
            print(f"✅ Estado: EXITOSO")
        else:
            print(f"❌ Estado: CON ERRORES ({result['total_errors']} errores)")
        
        print(f"\n📋 Errores por tipo de regla:")
        for rule_type, count in sorted(result["errors_by_rule"].items()):
            if rule_type != "VALIDATION_SUCCESS":
                icon = "❌" if count > 0 else "✅"
                print(f"   {icon} {rule_type}: {count}")
        
        if result["errors_by_type"]:
            print(f"\n📝 Errores por campo:")
            for field, errors_list in sorted(result["errors_by_type"].items()):
                if field not in ["validación", "archivo"]:
                    print(f"   • {field}: {len(errors_list)} error(es)")
        
        # Mostrar primeros errores detallados
        if result["errors"] and not result["validation_success"]:
            print(f"\n🔍 Primeros errores detectados:")
            for i, error in enumerate(result["errors"][:5], 1):
                if "✅" not in error["error"]:
                    print(f"   {i}. Línea {error['line']} | Campo '{error['field']}': {error['error']}")
            
            if result['total_errors'] > 5:
                print(f"   ... y {result['total_errors'] - 5} errores más")
    
    def generate_rules_summary(self) -> Dict[str, Any]:
        """Generar resumen de todas las reglas probadas"""
        
        # Definir todas las reglas determinísticas según la documentación
        all_rules = {
            # Reglas de Control (CT)
            "CT-001": {
                "name": "TIPO_REGISTRO válido",
                "description": "TIPO_REGISTRO debe ser '1'",
                "file_type": "CT",
                "category": "Estructura",
                "tested": False,
                "passed": False
            },
            "CT-002": {
                "name": "FECHA_GENERACION válida",
                "description": "FECHA_GENERACION formato YYYY-MM-DD",
                "file_type": "CT",
                "category": "Fecha",
                "tested": False,
                "passed": False
            },
            "GEN-001": {
                "name": "VERSION_ANEXO_TECNICO",
                "description": "Versión normativa presente",
                "file_type": "CT",
                "category": "Estructura",
                "tested": False,
                "passed": False
            },
            
            # Reglas de Usuarios (US)
            "US-001": {
                "name": "TIPO_DOCUMENTO_USUARIO válido",
                "description": "Valores: CC,TI,RC,CE,PA,NUIP,MS",
                "file_type": "US",
                "category": "Catálogo",
                "tested": False,
                "passed": False
            },
            "US-002": {
                "name": "NUMERO_DOCUMENTO_USUARIO presente",
                "description": "Campo obligatorio alfanumérico",
                "file_type": "US",
                "category": "Estructura",
                "tested": False,
                "passed": False
            },
            "US-007": {
                "name": "FECHA_NACIMIENTO válida",
                "description": "Formato YYYY-MM-DD, no futura",
                "file_type": "US",
                "category": "Fecha",
                "tested": False,
                "passed": False
            },
            "US-008": {
                "name": "SEXO válido",
                "description": "Valores: M,F",
                "file_type": "US",
                "category": "Catálogo",
                "tested": False,
                "passed": False
            },
            
            # Reglas de Consultas (AC)
            "AC-001": {
                "name": "CODIGO_PRESTADOR válido",
                "description": "12 dígitos numéricos",
                "file_type": "AC",
                "category": "Formato",
                "tested": False,
                "passed": False
            },
            "AC-012": {
                "name": "DIAGNOSTICO_PRINCIPAL_CIE válido",
                "description": "Código CIE-10/CIE-11 (3-7 caracteres)",
                "file_type": "AC",
                "category": "Catálogo",
                "tested": False,
                "passed": False
            },
            
            # Reglas de Procedimientos (AP)
            "AP-001": {
                "name": "CODIGO_CUPS válido",
                "description": "Código CUPS vigente",
                "file_type": "AP",
                "category": "Catálogo",
                "tested": False,
                "passed": False
            },
            "AP-002": {
                "name": "FECHA_PROCEDIMIENTO válida",
                "description": "Formato YYYY-MM-DD",
                "file_type": "AP",
                "category": "Fecha",
                "tested": False,
                "passed": False
            },
            
            # Reglas de Medicamentos (AM)
            "AM-001": {
                "name": "CODIGO_PRODUCTO válido",
                "description": "Código POS/GTIN/IPS",
                "file_type": "AM",
                "category": "Catálogo",
                "tested": False,
                "passed": False
            },
            
            # Reglas de Facturación (AF)
            "AF-004": {
                "name": "CUV presente cuando aplica",
                "description": "Código Único de Validación",
                "file_type": "AF",
                "category": "Condicional",
                "tested": False,
                "passed": False
            },
            
            # Reglas de Ajustes (AD)
            "AD-001": {
                "name": "TIPO_NOTA válido",
                "description": "Valores: NC,ND",
                "file_type": "AD",
                "category": "Catálogo",
                "tested": False,
                "passed": False
            },
            
            # Reglas generales de formato
            "FMT-001": {
                "name": "Formato de archivo válido",
                "description": "Extensión y estructura correcta",
                "file_type": "ALL",
                "category": "Formato",
                "tested": False,
                "passed": False
            },
            "FMT-002": {
                "name": "Codificación UTF-8",
                "description": "Archivo en UTF-8",
                "file_type": "ALL",
                "category": "Formato",
                "tested": False,
                "passed": False
            },
            "FMT-003": {
                "name": "Campos obligatorios presentes",
                "description": "Todos los campos requeridos",
                "file_type": "ALL",
                "category": "Estructura",
                "tested": False,
                "passed": False
            },
            "FMT-004": {
                "name": "Longitud de campos",
                "description": "Respeta min/max caracteres",
                "file_type": "ALL",
                "category": "Formato",
                "tested": False,
                "passed": False
            },
            "FMT-005": {
                "name": "Tipos de datos",
                "description": "Campos numéricos son números",
                "file_type": "ALL",
                "category": "Formato",
                "tested": False,
                "passed": False
            },
            "FMT-006": {
                "name": "Fechas coherentes",
                "description": "Fechas no futuras (excepto programadas)",
                "file_type": "ALL",
                "category": "Fecha",
                "tested": False,
                "passed": False
            },
            "FMT-007": {
                "name": "Caracteres permitidos",
                "description": "Sin caracteres especiales no permitidos",
                "file_type": "ALL",
                "category": "Formato",
                "tested": False,
                "passed": False
            },
        }
        
        # Analizar qué reglas se probaron
        for result in self.test_results:
            # Formato de archivo
            all_rules["FMT-001"]["tested"] = True
            all_rules["FMT-002"]["tested"] = True
            
            if result["validation_success"]:
                all_rules["FMT-001"]["passed"] = True
                all_rules["FMT-002"]["passed"] = True
            
            # Analizar errores específicos
            for error in result["errors"]:
                error_text = error["error"].lower()
                field = error["field"]
                
                # Mapear errores a reglas
                if "campo obligatorio" in error_text:
                    all_rules["FMT-003"]["tested"] = True
                elif "longitud" in error_text:
                    all_rules["FMT-004"]["tested"] = True
                elif "numérico" in error_text or "debe ser número" in error_text:
                    all_rules["FMT-005"]["tested"] = True
                elif "fecha" in error_text and "futura" in error_text:
                    all_rules["FMT-006"]["tested"] = True
                elif "caracteres no permitidos" in error_text:
                    all_rules["FMT-007"]["tested"] = True
                elif "✅" in error["error"]:
                    # Validación exitosa - marcar reglas aplicables como pasadas
                    all_rules["FMT-001"]["passed"] = True
                    all_rules["FMT-002"]["passed"] = True
                    all_rules["FMT-003"]["passed"] = True
        
        return all_rules
    
    def print_rules_summary(self):
        """Imprimir resumen de todas las reglas"""
        rules = self.generate_rules_summary()
        
        print(f"\n{'='*80}")
        print(f"📊 RESUMEN DE REGLAS DETERMINÍSTICAS PROBADAS")
        print(f"{'='*80}\n")
        
        # Agrupar por categoría
        by_category = defaultdict(list)
        for rule_id, rule_info in rules.items():
            by_category[rule_info["category"]].append((rule_id, rule_info))
        
        total_rules = len(rules)
        tested_rules = len([r for r in rules.values() if r["tested"]])
        passed_rules = len([r for r in rules.values() if r["passed"]])
        
        print(f"📈 ESTADÍSTICAS GENERALES:")
        print(f"   • Total de reglas definidas: {total_rules}")
        print(f"   • Reglas probadas: {tested_rules}")
        print(f"   • Reglas que pasaron: {passed_rules}")
        print(f"   • Cobertura: {(tested_rules/total_rules*100):.1f}%")
        
        print(f"\n📋 REGLAS POR CATEGORÍA:\n")
        
        for category in sorted(by_category.keys()):
            rules_in_cat = by_category[category]
            print(f"   🔹 {category}:")
            
            for rule_id, rule_info in sorted(rules_in_cat):
                if rule_info["tested"]:
                    if rule_info["passed"]:
                        status = "✅ PASÓ"
                    else:
                        status = "❌ FALLÓ"
                else:
                    status = "⚪ NO PROBADA"
                
                print(f"      {status} | {rule_id}: {rule_info['name']}")
                print(f"               └─ {rule_info['description']}")
            print()
    
    def generate_detailed_report(self) -> str:
        """Generar reporte detallado completo"""
        report_lines = []
        report_lines.append("=" * 100)
        report_lines.append("REPORTE DETALLADO DE PRUEBAS - REGLAS DETERMINÍSTICAS RIPS")
        report_lines.append("=" * 100)
        report_lines.append(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Archivos probados: {len(self.test_results)}")
        report_lines.append("")
        
        # Resumen por archivo
        report_lines.append("📁 ARCHIVOS PROBADOS:")
        report_lines.append("-" * 100)
        for i, result in enumerate(self.test_results, 1):
            status = "✅ EXITOSO" if result["validation_success"] else f"❌ {result['total_errors']} ERRORES"
            report_lines.append(f"{i}. {result['file']:<50} | {status}")
        report_lines.append("")
        
        # Detalles de cada archivo
        report_lines.append("\n" + "=" * 100)
        report_lines.append("DETALLES POR ARCHIVO")
        report_lines.append("=" * 100)
        
        for result in self.test_results:
            report_lines.append(f"\n📄 ARCHIVO: {result['file']}")
            report_lines.append("-" * 100)
            report_lines.append(f"   Ruta: {result['file_path']}")
            report_lines.append(f"   Tipo: {result['file_type']}")
            report_lines.append(f"   Estado: {'✅ VÁLIDO' if result['validation_success'] else '❌ CON ERRORES'}")
            report_lines.append(f"   Total errores: {result['total_errors']}")
            
            if result["errors_by_rule"]:
                report_lines.append(f"\n   🔍 Errores por tipo de regla:")
                for rule_type, count in sorted(result["errors_by_rule"].items()):
                    if rule_type != "VALIDATION_SUCCESS":
                        report_lines.append(f"      • {rule_type}: {count}")
            
            if result["errors"] and not result["validation_success"]:
                report_lines.append(f"\n   📝 Detalles de errores:")
                for error in result["errors"][:10]:  # Primeros 10
                    if "✅" not in error["error"]:
                        report_lines.append(f"      Línea {error['line']:>4} | {error['field']:<30} | {error['error']}")
                
                if result['total_errors'] > 10:
                    report_lines.append(f"      ... y {result['total_errors'] - 10} errores más")
            
            report_lines.append("")
        
        # Resumen de reglas
        report_lines.append("\n" + "=" * 100)
        report_lines.append("RESUMEN DE REGLAS DETERMINÍSTICAS")
        report_lines.append("=" * 100)
        
        rules = self.generate_rules_summary()
        
        # Estadísticas
        total_rules = len(rules)
        tested_rules = len([r for r in rules.values() if r["tested"]])
        passed_rules = len([r for r in rules.values() if r["passed"]])
        
        report_lines.append(f"\n📊 ESTADÍSTICAS:")
        report_lines.append(f"   • Total de reglas definidas: {total_rules}")
        report_lines.append(f"   • Reglas probadas: {tested_rules} ({tested_rules/total_rules*100:.1f}%)")
        report_lines.append(f"   • Reglas que pasaron: {passed_rules} ({passed_rules/total_rules*100:.1f}%)")
        
        # Lista de reglas
        report_lines.append(f"\n📋 LISTA DE REGLAS:")
        by_category = defaultdict(list)
        for rule_id, rule_info in rules.items():
            by_category[rule_info["category"]].append((rule_id, rule_info))
        
        for category in sorted(by_category.keys()):
            report_lines.append(f"\n   🔹 {category}:")
            rules_in_cat = by_category[category]
            
            for rule_id, rule_info in sorted(rules_in_cat):
                if rule_info["tested"]:
                    status = "✅ PASÓ" if rule_info["passed"] else "❌ FALLÓ"
                else:
                    status = "⚪ NO PROBADA"
                
                report_lines.append(f"      {status} | {rule_id:<10} | {rule_info['name']:<40} | {rule_info['description']}")
        
        report_lines.append("\n" + "=" * 100)
        report_lines.append("FIN DEL REPORTE")
        report_lines.append("=" * 100)
        
        return "\n".join(report_lines)
    
    def save_report(self, output_path: str):
        """Guardar reporte en archivo"""
        report_content = self.generate_detailed_report()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"\n💾 Reporte guardado en: {output_path}")


def main():
    """Función principal"""
    print("\n" + "="*80)
    print("🧪 PRUEBA DE REGLAS DETERMINÍSTICAS RIPS")
    print("="*80)
    
    # Directorio de pruebas
    test_dir = Path(__file__).parent.parent.parent.parent / "TEST"
    
    if not test_dir.exists():
        print(f"❌ Error: Directorio TEST no encontrado en {test_dir}")
        return
    
    print(f"\n📁 Directorio de pruebas: {test_dir}")
    
    # Listar archivos
    test_files = list(test_dir.glob("*"))
    print(f"📋 Archivos encontrados: {len(test_files)}")
    
    for f in test_files:
        print(f"   • {f.name}")
    
    # Crear reporte
    reporter = RulesTestReport()
    
    # Probar cada archivo
    for test_file in test_files:
        file_str = str(test_file)
        
        # Determinar tipo de archivo
        if test_file.suffix == '.zip':
            file_type = "AC"  # Asumimos consultas
        elif test_file.suffix == '.json':
            file_type = "AC"
        elif test_file.suffix == '.txt':
            file_type = "AC"
        else:
            print(f"\n⚠️  Saltando archivo no soportado: {test_file.name}")
            continue
        
        # Probar archivo
        result = reporter.test_file(file_str, file_type)
        reporter.print_file_results(result)
    
    # Imprimir resumen de reglas
    reporter.print_rules_summary()
    
    # Guardar reporte
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = test_dir / f"reporte_reglas_determinísticas_{timestamp}.txt"
    reporter.save_report(str(report_path))
    
    print(f"\n✅ Prueba completada exitosamente")
    print(f"📄 Reporte guardado en: {report_path}")


if __name__ == "__main__":
    main()


