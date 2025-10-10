"""
Mapeos de reglas RIPS basados en análisis de archivos Excel
Este módulo contiene las definiciones estructuradas de todas las reglas de validación
"""

from typing import Dict, List, Any
from enum import Enum

class ValidationSeverity(str, Enum):
    BLOQUEANTE = "bloqueante"
    ADVERTENCIA = "advertencia"
    INFORMATIVO = "informativo"

class ValidationType(str, Enum):
    DETERMINISTIC = "deterministic"
    AI = "ai"

class RuleCategory(str, Enum):
    STRUCTURE = "structure"
    FORMAT = "format"
    BUSINESS = "business"
    CLINICAL_COHERENCE = "clinical_coherence"
    PATTERN_DETECTION = "pattern_detection"
    FRAUD_DETECTION = "fraud_detection"

# Mapeo completo de reglas extraídas de los archivos Excel
RIPS_VALIDATION_RULES = {
    # Reglas determinísticas de estructura
    "CT-001": {
        "id": "CT-001",
        "file_type": "CT",
        "field": "TIPO_REGISTRO",
        "data_type": "Numeric",
        "min_length": 1,
        "max_length": 1,
        "cardinality": "1..1",
        "mandatory": True,
        "allowed_values": ["1"],
        "validation_rule": "Debe ser 1 (control)",
        "severity": ValidationSeverity.BLOQUEANTE,
        "type": ValidationType.DETERMINISTIC,
        "category": RuleCategory.STRUCTURE,
        "normative_reference": "Resolución 2275 de 2023 - Anexo Técnico (estructura RIPS/FEV); Resolución 1884 de 2024"
    },
    
    "CT-002": {
        "id": "CT-002",
        "file_type": "CT",
        "field": "FECHA_GENERACION",
        "data_type": "Date",
        "min_length": 10,
        "max_length": 10,
        "cardinality": "1..1",
        "mandatory": True,
        "allowed_values": ["YYYY-MM-DD"],
        "validation_rule": "Formato fecha; <= fecha envío",
        "severity": ValidationSeverity.BLOQUEANTE,
        "type": ValidationType.DETERMINISTIC,
        "category": RuleCategory.FORMAT,
        "normative_reference": "Resolución 2275 de 2023 - Anexo Técnico; Lineamientos FEV RIPS"
    },
    
    "US-001": {
        "id": "US-001",
        "file_type": "US",
        "field": "TIPO_DOCUMENTO_USUARIO",
        "data_type": "Code",
        "min_length": 1,
        "max_length": 2,
        "cardinality": "1..1",
        "mandatory": True,
        "allowed_values": ["CC", "TI", "RC", "CE", "PA", "NUIP", "MS"],
        "validation_rule": "Valor en catálogo DIAN/MinSalud",
        "severity": ValidationSeverity.BLOQUEANTE,
        "type": ValidationType.DETERMINISTIC,
        "category": RuleCategory.BUSINESS,
        "normative_reference": "Catálogos oficiales DIAN/MinSalud"
    },
    
    "US-007": {
        "id": "US-007",
        "file_type": "US",
        "field": "FECHA_NACIMIENTO",
        "data_type": "Date",
        "min_length": 10,
        "max_length": 10,
        "cardinality": "1..1",
        "mandatory": True,
        "allowed_values": ["YYYY-MM-DD"],
        "validation_rule": "<= fecha atención; edad coherente",
        "severity": ValidationSeverity.BLOQUEANTE,
        "type": ValidationType.DETERMINISTIC,
        "category": RuleCategory.FORMAT,
        "normative_reference": "Lineamientos generación/validación/envío RIPS-FEV"
    },
    
    "AC-012": {
        "id": "AC-012",
        "file_type": "AC",
        "field": "DIAGNOSTICO_PRINCIPAL_CIE",
        "data_type": "Code",
        "min_length": 3,
        "max_length": 7,
        "cardinality": "1..1",
        "mandatory": True,
        "allowed_values": ["CIE-10/CIE-11 según vigencia"],
        "validation_rule": "Validar existencia y vigencia; coherencia clínica",
        "severity": ValidationSeverity.BLOQUEANTE,
        "type": ValidationType.AI,  # Coherencia clínica requiere IA
        "category": RuleCategory.CLINICAL_COHERENCE,
        "normative_reference": "Catálogos oficiales CIE-10/CIE-11 MinSalud/SISPRO"
    },
    
    "AP-001": {
        "id": "AP-001",
        "file_type": "AP",
        "field": "CODIGO_CUPS",
        "data_type": "String",
        "min_length": 3,
        "max_length": 7,
        "cardinality": "1..1",
        "mandatory": True,
        "allowed_values": ["CUPS vigente"],
        "validation_rule": "Existencia en catálogo CUPS; vigencia",
        "severity": ValidationSeverity.BLOQUEANTE,
        "type": ValidationType.DETERMINISTIC,
        "category": RuleCategory.BUSINESS,
        "normative_reference": "Catálogos oficiales CUPS MinSalud"
    },
    
    "AM-001": {
        "id": "AM-001",
        "file_type": "AM",
        "field": "CODIGO_PRODUCTO",
        "data_type": "String",
        "min_length": 3,
        "max_length": 20,
        "cardinality": "1..1",
        "mandatory": True,
        "allowed_values": ["POS/GTIN/Código IPS"],
        "validation_rule": "Validar existencia en catálogos",
        "severity": ValidationSeverity.BLOQUEANTE,
        "type": ValidationType.DETERMINISTIC,
        "category": RuleCategory.BUSINESS,
        "normative_reference": "Catálogos oficiales medicamentos"
    },
    
    "AF-004": {
        "id": "AF-004",
        "file_type": "AF",
        "field": "CUV",
        "data_type": "String",
        "min_length": 10,
        "max_length": 64,
        "cardinality": "0..1",
        "mandatory": False,  # Condicional
        "allowed_values": ["Código único de validación"],
        "validation_rule": "Si aplica, validar existencia y formato",
        "severity": ValidationSeverity.ADVERTENCIA,
        "type": ValidationType.DETERMINISTIC,
        "category": RuleCategory.FORMAT,
        "normative_reference": "Resolución 1884 de 2024"
    },
    
    "AD-001": {
        "id": "AD-001",
        "file_type": "AD",
        "field": "TIPO_NOTA",
        "data_type": "Code",
        "min_length": 1,
        "max_length": 2,
        "cardinality": "1..1",
        "mandatory": True,
        "allowed_values": ["NC", "ND"],
        "validation_rule": "Debe referenciar factura original; incluir motivo",
        "severity": ValidationSeverity.BLOQUEANTE,
        "type": ValidationType.DETERMINISTIC,
        "category": RuleCategory.BUSINESS,
        "normative_reference": "Resolución 1884 de 2024"
    },
    
    "GEN-001": {
        "id": "GEN-001",
        "file_type": "ALL",
        "field": "VERSION_ANEXO_TECNICO",
        "data_type": "String",
        "min_length": 1,
        "max_length": 20,
        "cardinality": "1..1",
        "mandatory": True,
        "allowed_values": ["2275/2023", "1884/2024"],
        "validation_rule": "Indicar versión usada; validar vigencia",
        "severity": ValidationSeverity.BLOQUEANTE,
        "type": ValidationType.DETERMINISTIC,
        "category": RuleCategory.STRUCTURE,
        "normative_reference": "Resoluciones vigentes"
    }
}

# Reglas específicas de IA
AI_VALIDATION_RULES = {
    "AI-CLIN-001": {
        "id": "AI-CLIN-001",
        "category": "Coherencia clínica",
        "validation": "Diagnóstico incompatible con sexo",
        "example": "Embarazo reportado en paciente masculino",
        "severity": ValidationSeverity.BLOQUEANTE,
        "detection": "Modelo IA basado en reglas clínicas y aprendizaje supervisado",
        "type": ValidationType.AI,
        "rule_category": RuleCategory.CLINICAL_COHERENCE
    },
    
    "AI-CLIN-002": {
        "id": "AI-CLIN-002",
        "category": "Coherencia clínica",
        "validation": "Diagnóstico incompatible con edad",
        "example": "Enfermedades pediátricas reportadas en adultos mayores",
        "severity": ValidationSeverity.BLOQUEANTE,
        "detection": "IA con cruces de edad, diagnóstico y prevalencia epidemiológica",
        "type": ValidationType.AI,
        "rule_category": RuleCategory.CLINICAL_COHERENCE
    },
    
    "AI-PAT-001": {
        "id": "AI-PAT-001",
        "category": "Patrones atípicos",
        "validation": "Procedimientos duplicados en períodos cortos",
        "example": "Dos cesáreas facturadas al mismo usuario en la misma semana",
        "severity": ValidationSeverity.ADVERTENCIA,
        "detection": "IA detecta patrones de facturación anómalos comparando históricos",
        "type": ValidationType.AI,
        "rule_category": RuleCategory.PATTERN_DETECTION
    },
    
    "AI-PAT-002": {
        "id": "AI-PAT-002",
        "category": "Patrones atípicos",
        "validation": "Volumen atípico de servicios por prestador",
        "example": "Prestador factura volumen anómalo de servicios en período corto",
        "severity": ValidationSeverity.ADVERTENCIA,
        "detection": "Análisis estadístico de volúmenes por prestador y período",
        "type": ValidationType.AI,
        "rule_category": RuleCategory.PATTERN_DETECTION
    },
    
    "AI-FRAUD-001": {
        "id": "AI-FRAUD-001",
        "category": "Fraude administrativo",
        "validation": "Servicios costosos sin soporte clínico",
        "example": "Hospitalización facturada sin diagnóstico que la justifique",
        "severity": ValidationSeverity.BLOQUEANTE,
        "detection": "IA analiza correlación costo-diagnóstico-procedimiento",
        "type": ValidationType.AI,
        "rule_category": RuleCategory.FRAUD_DETECTION
    },
    
    "AI-FRAUD-002": {
        "id": "AI-FRAUD-002",
        "category": "Fraude administrativo",
        "validation": "Patrones de facturación sospechosos",
        "example": "Baja variabilidad en procedimientos facturados por prestador",
        "severity": ValidationSeverity.BLOQUEANTE,
        "detection": "Análisis de patrones mediante machine learning",
        "type": ValidationType.AI,
        "rule_category": RuleCategory.FRAUD_DETECTION
    }
}

# Mapeo de tipos de archivo RIPS y sus campos principales
RIPS_FILE_STRUCTURES = {
    "CT": {
        "name": "Control",
        "description": "Archivo de control con información general del lote",
        "required_fields": ["TIPO_REGISTRO", "FECHA_GENERACION", "VERSION_ANEXO_TECNICO"],
        "optional_fields": ["NUMERO_LOTE", "OBSERVACIONES"]
    },
    
    "US": {
        "name": "Usuarios",
        "description": "Información demográfica de usuarios",
        "required_fields": ["TIPO_DOCUMENTO_USUARIO", "NUMERO_DOCUMENTO_USUARIO", "FECHA_NACIMIENTO", "SEXO"],
        "optional_fields": ["PRIMER_APELLIDO", "SEGUNDO_APELLIDO", "PRIMER_NOMBRE", "SEGUNDO_NOMBRE"]
    },
    
    "AC": {
        "name": "Consultas",
        "description": "Registros de consultas médicas",
        "required_fields": ["CODIGO_PRESTADOR", "TIPO_DOCUMENTO_USUARIO", "NUMERO_DOCUMENTO_USUARIO", 
                           "FECHA_CONSULTA", "DIAGNOSTICO_PRINCIPAL_CIE"],
        "optional_fields": ["DIAGNOSTICO_RELACIONADO", "CAUSA_EXTERNA", "FINALIDAD_CONSULTA"]
    },
    
    "AP": {
        "name": "Procedimientos",
        "description": "Registros de procedimientos realizados",
        "required_fields": ["CODIGO_PRESTADOR", "CODIGO_CUPS", "FECHA_PROCEDIMIENTO"],
        "optional_fields": ["DIAGNOSTICO_PRINCIPAL", "DIAGNOSTICO_RELACIONADO", "COMPLICACION"]
    },
    
    "AM": {
        "name": "Medicamentos",
        "description": "Registros de medicamentos dispensados",
        "required_fields": ["CODIGO_PRESTADOR", "CODIGO_PRODUCTO"],
        "optional_fields": ["CANTIDAD", "VALOR_UNITARIO", "VALOR_TOTAL"]
    },
    
    "AF": {
        "name": "Facturación",
        "description": "Información de facturación",
        "required_fields": ["CODIGO_PRESTADOR", "NUMERO_FACTURA"],
        "optional_fields": ["CUV", "VALOR_TOTAL", "VALOR_COPAGO"]
    },
    
    "AD": {
        "name": "Ajustes",
        "description": "Notas de ajuste (crédito/débito)",
        "required_fields": ["TIPO_NOTA", "NUMERO_FACTURA_ORIGINAL"],
        "optional_fields": ["MOTIVO_AJUSTE", "VALOR_AJUSTE"]
    }
}

def get_rules_by_file_type(file_type: str) -> List[Dict[str, Any]]:
    """Obtener reglas específicas para un tipo de archivo"""
    rules = []
    
    # Reglas determinísticas
    for rule_id, rule in RIPS_VALIDATION_RULES.items():
        if rule["file_type"] == file_type or rule["file_type"] == "ALL":
            rules.append(rule)
    
    # Reglas de IA (aplican a todos los tipos de archivo)
    for rule_id, rule in AI_VALIDATION_RULES.items():
        rules.append(rule)
    
    return rules

def get_rules_by_category(category: RuleCategory) -> List[Dict[str, Any]]:
    """Obtener reglas por categoría"""
    rules = []
    
    # Reglas determinísticas
    for rule_id, rule in RIPS_VALIDATION_RULES.items():
        if rule["category"] == category:
            rules.append(rule)
    
    # Reglas de IA
    for rule_id, rule in AI_VALIDATION_RULES.items():
        if rule["rule_category"] == category:
            rules.append(rule)
    
    return rules

def get_validation_summary() -> Dict[str, Any]:
    """Obtener resumen de todas las validaciones"""
    total_deterministic = len(RIPS_VALIDATION_RULES)
    total_ai = len(AI_VALIDATION_RULES)
    
    severity_count = {
        ValidationSeverity.BLOQUEANTE: 0,
        ValidationSeverity.ADVERTENCIA: 0,
        ValidationSeverity.INFORMATIVO: 0
    }
    
    category_count = {
        RuleCategory.STRUCTURE: 0,
        RuleCategory.FORMAT: 0,
        RuleCategory.BUSINESS: 0,
        RuleCategory.CLINICAL_COHERENCE: 0,
        RuleCategory.PATTERN_DETECTION: 0,
        RuleCategory.FRAUD_DETECTION: 0
    }
    
    # Contar por severidad y categoría
    all_rules = list(RIPS_VALIDATION_RULES.values()) + list(AI_VALIDATION_RULES.values())
    
    for rule in all_rules:
        severity = rule.get("severity", ValidationSeverity.INFORMATIVO)
        category = rule.get("category", rule.get("rule_category", RuleCategory.STRUCTURE))
        
        severity_count[severity] += 1
        category_count[category] += 1
    
    return {
        "total_rules": total_deterministic + total_ai,
        "deterministic_rules": total_deterministic,
        "ai_rules": total_ai,
        "severity_distribution": severity_count,
        "category_distribution": category_count,
        "file_types_supported": list(RIPS_FILE_STRUCTURES.keys())
    }
