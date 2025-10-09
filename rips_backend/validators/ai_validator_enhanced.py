from typing import List, Dict, Any, Optional, Tuple
from models.schemas import ErrorResponse
import re
from datetime import datetime, date
from collections import defaultdict

class EnhancedAIValidator:
    """Validador de IA mejorado basado en reglas específicas de coherencia clínica y detección de fraudes"""
    
    def __init__(self):
        self.model_loaded = False
        
        # Reglas de coherencia clínica basadas en el archivo RIPS_Validaciones_AI.xlsx
        self.clinical_coherence_rules = {
            "AI-CLIN-001": {
                "name": "Diagnóstico incompatible con sexo",
                "description": "Detectar diagnósticos que no corresponden al sexo del paciente",
                "severity": "Alta",
                "examples": ["Embarazo reportado en paciente masculino", "Cáncer de próstata en mujer"]
            },
            "AI-CLIN-002": {
                "name": "Diagnóstico incompatible con edad",
                "description": "Detectar diagnósticos que no corresponden a la edad del paciente",
                "severity": "Alta",
                "examples": ["Enfermedades pediátricas en adultos mayores", "Demencia senil en menores"]
            },
            "AI-CLIN-003": {
                "name": "Procedimiento incompatible con diagnóstico",
                "description": "Detectar procedimientos que no tienen relación clínica con el diagnóstico",
                "severity": "Media",
                "examples": ["Cirugía cardíaca para diagnóstico dermatológico"]
            }
        }
        
        # Reglas de detección de patrones atípicos
        self.pattern_detection_rules = {
            "AI-PAT-001": {
                "name": "Procedimientos duplicados en períodos cortos",
                "description": "Detectar procedimientos repetidos anómalamente",
                "severity": "Media",
                "examples": ["Dos cesáreas facturadas al mismo usuario en la misma semana"]
            },
            "AI-PAT-002": {
                "name": "Volumen atípico de servicios",
                "description": "Detectar prestadores con volúmenes anómalos de servicios",
                "severity": "Alta",
                "examples": ["Prestador factura 100 cirugías en un día"]
            }
        }
        
        # Reglas de detección de fraude
        self.fraud_detection_rules = {
            "AI-FRAUD-001": {
                "name": "Servicios costosos sin soporte clínico",
                "description": "Detectar servicios de alto costo sin justificación clínica",
                "severity": "Alta",
                "examples": ["Hospitalización facturada sin diagnóstico que la justifique"]
            },
            "AI-FRAUD-002": {
                "name": "Patrones de facturación sospechosos",
                "description": "Detectar patrones de facturación que sugieren fraude",
                "severity": "Alta",
                "examples": ["Siempre facturar el máximo permitido", "Servicios fantasma"]
            }
        }
        
        # Catálogos para validaciones de IA
        self.pregnancy_related_codes = [
            "O00", "O01", "O02", "O03", "O04", "O05", "O06", "O07", "O08", "O09",
            "O10", "O11", "O12", "O13", "O14", "O15", "O16", "O20", "O21", "O22",
            "O23", "O24", "O25", "O26", "O28", "O29", "O30", "O31", "O32", "O33",
            "O34", "O35", "O36", "O40", "O41", "O42", "O43", "O44", "O45", "O46",
            "O47", "O48", "O60", "O61", "O62", "O63", "O64", "O65", "O66", "O67",
            "O68", "O69", "O70", "O71", "O72", "O73", "O74", "O75", "O80", "O81",
            "O82", "O83", "O84", "O85", "O86", "O87", "O88", "O89", "O90", "O91",
            "O92", "O94", "O95", "O96", "O97", "O98", "O99", "Z32", "Z33", "Z34",
            "Z35", "Z36", "Z37", "Z38", "Z39"
        ]
        
        self.male_specific_codes = [
            "C61", "N40", "N41", "N42", "N43", "N44", "N45", "N46", "N47", "N48", "N49", "N50"
        ]
        
        self.pediatric_codes = [
            "P00", "P01", "P02", "P03", "P04", "P05", "P07", "P08", "P10", "P11",
            "P12", "P13", "P14", "P15", "P20", "P21", "P22", "P23", "P24", "P25",
            "P26", "P27", "P28", "P29", "P35", "P36", "P37", "P38", "P39", "P50",
            "P51", "P52", "P53", "P54", "P55", "P56", "P57", "P58", "P59", "P60",
            "P61", "P70", "P71", "P72", "P74", "P75", "P76", "P77", "P78", "P80",
            "P81", "P83", "P90", "P91", "P92", "P93", "P94", "P95", "P96"
        ]
    
    def validate_file(self, file_path: str, file_type: str = "AC") -> List[ErrorResponse]:
        """Validar archivo RIPS usando reglas de IA"""
        errors = []
        
        try:
            # Leer y procesar archivo
            records = self._parse_file(file_path, file_type)
            
            # Aplicar validaciones de IA
            errors.extend(self._validate_clinical_coherence(records, file_type))
            errors.extend(self._validate_pattern_detection(records, file_type))
            errors.extend(self._validate_fraud_detection(records, file_type))
            
        except Exception as e:
            errors.append(ErrorResponse(
                line=0,
                field="ai_validation",
                error=f"Error en validación IA: {str(e)}"
            ))
        
        return errors
    
    def _parse_file(self, file_path: str, file_type: str) -> List[Dict[str, Any]]:
        """Parsear archivo y convertir a estructura de datos para IA"""
        records = []
        
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_number, line in enumerate(file, 1):
                line = line.strip()
                if not line:
                    continue
                
                fields = line.split('|')
                record = self._map_fields_to_record(fields, file_type, line_number)
                records.append(record)
        
        return records
    
    def _map_fields_to_record(self, fields: List[str], file_type: str, line_number: int) -> Dict[str, Any]:
        """Mapear campos a estructura de registro"""
        record = {
            "line_number": line_number,
            "file_type": file_type,
            "raw_fields": fields
        }
        
        # Mapeo específico por tipo de archivo
        if file_type == "AC" and len(fields) >= 10:  # Consultas
            record.update({
                "codigo_prestador": fields[0] if len(fields) > 0 else "",
                "tipo_documento": fields[2] if len(fields) > 2 else "",
                "numero_documento": fields[3] if len(fields) > 3 else "",
                "fecha_nacimiento": fields[5] if len(fields) > 5 else "",
                "sexo": fields[6] if len(fields) > 6 else "",
                "fecha_consulta": fields[10] if len(fields) > 10 else "",
                "diagnostico_principal": fields[15] if len(fields) > 15 else "",
                "diagnostico_relacionado": fields[16] if len(fields) > 16 else ""
            })
        
        elif file_type == "AP" and len(fields) >= 5:  # Procedimientos
            record.update({
                "codigo_prestador": fields[0] if len(fields) > 0 else "",
                "codigo_cups": fields[12] if len(fields) > 12 else "",
                "fecha_procedimiento": fields[10] if len(fields) > 10 else "",
                "diagnostico_principal": fields[15] if len(fields) > 15 else ""
            })
        
        elif file_type == "US" and len(fields) >= 4:  # Usuarios
            record.update({
                "tipo_documento": fields[0] if len(fields) > 0 else "",
                "numero_documento": fields[1] if len(fields) > 1 else "",
                "fecha_nacimiento": fields[2] if len(fields) > 2 else "",
                "sexo": fields[3] if len(fields) > 3 else ""
            })
        
        return record
    
    def _validate_clinical_coherence(self, records: List[Dict], file_type: str) -> List[ErrorResponse]:
        """Validar coherencia clínica usando IA"""
        errors = []
        
        for record in records:
            # AI-CLIN-001: Diagnóstico incompatible con sexo
            sex_errors = self._validate_diagnosis_sex_coherence(record)
            errors.extend(sex_errors)
            
            # AI-CLIN-002: Diagnóstico incompatible con edad
            age_errors = self._validate_diagnosis_age_coherence(record)
            errors.extend(age_errors)
        
        return errors
    
    def _validate_diagnosis_sex_coherence(self, record: Dict) -> List[ErrorResponse]:
        """Validar coherencia entre diagnóstico y sexo"""
        errors = []
        
        sexo = record.get("sexo", "").upper()
        diagnostico = record.get("diagnostico_principal", "").upper()
        line_number = record.get("line_number", 0)
        
        if not sexo or not diagnostico:
            return errors
        
        # Validar diagnósticos relacionados con embarazo en hombres
        if sexo == "M":
            for pregnancy_code in self.pregnancy_related_codes:
                if diagnostico.startswith(pregnancy_code):
                    errors.append(ErrorResponse(
                        line=line_number,
                        field="diagnostico_principal",
                        error=f"Diagnóstico relacionado con embarazo ({diagnostico}) en paciente masculino"
                    ))
                    break
        
        # Validar diagnósticos específicos de hombres en mujeres
        if sexo == "F":
            for male_code in self.male_specific_codes:
                if diagnostico.startswith(male_code):
                    errors.append(ErrorResponse(
                        line=line_number,
                        field="diagnostico_principal",
                        error=f"Diagnóstico específico masculino ({diagnostico}) en paciente femenino"
                    ))
                    break
        
        return errors
    
    def _validate_diagnosis_age_coherence(self, record: Dict) -> List[ErrorResponse]:
        """Validar coherencia entre diagnóstico y edad"""
        errors = []
        
        fecha_nacimiento = record.get("fecha_nacimiento", "")
        diagnostico = record.get("diagnostico_principal", "").upper()
        line_number = record.get("line_number", 0)
        
        if not fecha_nacimiento or not diagnostico:
            return errors
        
        try:
            # Calcular edad
            if '-' in fecha_nacimiento:
                birth_date = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
            else:
                birth_date = datetime.strptime(fecha_nacimiento, '%d/%m/%Y').date()
            
            age = (date.today() - birth_date).days // 365
            
            # Validar diagnósticos pediátricos en adultos
            if age >= 18:
                for pediatric_code in self.pediatric_codes:
                    if diagnostico.startswith(pediatric_code):
                        errors.append(ErrorResponse(
                            line=line_number,
                            field="diagnostico_principal",
                            error=f"Diagnóstico pediátrico ({diagnostico}) en paciente adulto (edad: {age} años)"
                        ))
                        break
            
            # Validar diagnósticos geriátricos en jóvenes
            geriatric_codes = ["F03", "G30", "G31"]  # Demencias
            if age < 50:
                for geriatric_code in geriatric_codes:
                    if diagnostico.startswith(geriatric_code):
                        errors.append(ErrorResponse(
                            line=line_number,
                            field="diagnostico_principal",
                            error=f"Diagnóstico geriátrico ({diagnostico}) en paciente joven (edad: {age} años)"
                        ))
                        break
        
        except ValueError:
            # Error de formato de fecha, ya se maneja en validaciones determinísticas
            pass
        
        return errors
    
    def _validate_pattern_detection(self, records: List[Dict], file_type: str) -> List[ErrorResponse]:
        """Detectar patrones atípicos usando IA"""
        errors = []
        
        # AI-PAT-001: Procedimientos duplicados
        duplicate_errors = self._detect_duplicate_procedures(records)
        errors.extend(duplicate_errors)
        
        # AI-PAT-002: Volumen atípico de servicios
        volume_errors = self._detect_atypical_volumes(records)
        errors.extend(volume_errors)
        
        return errors
    
    def _detect_duplicate_procedures(self, records: List[Dict]) -> List[ErrorResponse]:
        """Detectar procedimientos duplicados sospechosos"""
        errors = []
        
        # Agrupar por usuario y procedimiento
        user_procedures = defaultdict(list)
        
        for record in records:
            user_key = f"{record.get('tipo_documento', '')}_{record.get('numero_documento', '')}"
            procedure_code = record.get('codigo_cups', '')
            date_str = record.get('fecha_procedimiento', record.get('fecha_consulta', ''))
            
            if user_key and procedure_code and date_str:
                user_procedures[user_key].append({
                    'procedure': procedure_code,
                    'date': date_str,
                    'line': record.get('line_number', 0)
                })
        
        # Detectar duplicados sospechosos
        for user_key, procedures in user_procedures.items():
            procedure_dates = defaultdict(list)
            
            for proc in procedures:
                procedure_dates[proc['procedure']].append(proc)
            
            for procedure_code, proc_list in procedure_dates.items():
                if len(proc_list) > 1:
                    # Verificar si son en fechas muy cercanas
                    dates = []
                    for proc in proc_list:
                        try:
                            if '-' in proc['date']:
                                parsed_date = datetime.strptime(proc['date'], '%Y-%m-%d').date()
                            else:
                                parsed_date = datetime.strptime(proc['date'], '%d/%m/%Y').date()
                            dates.append((parsed_date, proc['line']))
                        except ValueError:
                            continue
                    
                    # Verificar duplicados en menos de 7 días
                    dates.sort()
                    for i in range(1, len(dates)):
                        days_diff = (dates[i][0] - dates[i-1][0]).days
                        if days_diff <= 7:
                            errors.append(ErrorResponse(
                                line=dates[i][1],
                                field="codigo_cups",
                                error=f"Procedimiento duplicado ({procedure_code}) en {days_diff} días para el mismo usuario"
                            ))
        
        return errors
    
    def _detect_atypical_volumes(self, records: List[Dict]) -> List[ErrorResponse]:
        """Detectar volúmenes atípicos de servicios por prestador"""
        errors = []
        
        # Contar servicios por prestador por día
        provider_daily_counts = defaultdict(lambda: defaultdict(int))
        provider_records = defaultdict(list)
        
        for record in records:
            provider = record.get('codigo_prestador', '')
            date_str = record.get('fecha_procedimiento', record.get('fecha_consulta', ''))
            
            if provider and date_str:
                try:
                    if '-' in date_str:
                        service_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    else:
                        service_date = datetime.strptime(date_str, '%d/%m/%Y').date()
                    
                    provider_daily_counts[provider][service_date] += 1
                    provider_records[provider].append(record)
                
                except ValueError:
                    continue
        
        # Detectar volúmenes anómalos (más de 50 servicios por día)
        for provider, daily_counts in provider_daily_counts.items():
            for service_date, count in daily_counts.items():
                if count > 50:  # Umbral configurable
                    # Encontrar una línea representativa para reportar el error
                    representative_record = next(
                        (r for r in provider_records[provider] 
                         if r.get('fecha_procedimiento', r.get('fecha_consulta', '')) and 
                         service_date.strftime('%Y-%m-%d') in r.get('fecha_procedimiento', r.get('fecha_consulta', ''))),
                        provider_records[provider][0]
                    )
                    
                    errors.append(ErrorResponse(
                        line=representative_record.get('line_number', 0),
                        field="codigo_prestador",
                        error=f"Volumen atípico: {count} servicios en un día ({service_date}) para prestador {provider}"
                    ))
        
        return errors
    
    def _validate_fraud_detection(self, records: List[Dict], file_type: str) -> List[ErrorResponse]:
        """Detectar posibles fraudes usando IA"""
        errors = []
        
        # AI-FRAUD-001: Servicios costosos sin soporte clínico
        # Esta validación requeriría una base de datos de costos y protocolos clínicos
        # Por ahora, implementamos una versión básica
        
        # AI-FRAUD-002: Patrones de facturación sospechosos
        pattern_errors = self._detect_suspicious_billing_patterns(records)
        errors.extend(pattern_errors)
        
        return errors
    
    def _detect_suspicious_billing_patterns(self, records: List[Dict]) -> List[ErrorResponse]:
        """Detectar patrones de facturación sospechosos"""
        errors = []
        
        # Ejemplo: Detectar si un prestador siempre factura los mismos códigos
        provider_procedures = defaultdict(list)
        
        for record in records:
            provider = record.get('codigo_prestador', '')
            procedure = record.get('codigo_cups', '')
            
            if provider and procedure:
                provider_procedures[provider].append({
                    'procedure': procedure,
                    'line': record.get('line_number', 0)
                })
        
        # Detectar prestadores con muy poca variabilidad en procedimientos
        for provider, procedures in provider_procedures.items():
            if len(procedures) >= 10:  # Solo analizar prestadores con suficientes registros
                unique_procedures = set(p['procedure'] for p in procedures)
                variability_ratio = len(unique_procedures) / len(procedures)
                
                # Si la variabilidad es muy baja (menos del 10%), es sospechoso
                if variability_ratio < 0.1:
                    representative_line = procedures[0]['line']
                    errors.append(ErrorResponse(
                        line=representative_line,
                        field="codigo_prestador",
                        error=f"Patrón sospechoso: Prestador {provider} con baja variabilidad en procedimientos ({variability_ratio:.2%})"
                    ))
        
        return errors
    
    def get_ai_validation_summary(self, errors: List[ErrorResponse]) -> Dict[str, Any]:
        """Generar resumen de validaciones de IA"""
        if not errors:
            return {
                "status": "success",
                "total_ai_errors": 0,
                "categories": {
                    "clinical_coherence": 0,
                    "pattern_detection": 0,
                    "fraud_detection": 0
                }
            }
        
        categories = {
            "clinical_coherence": 0,
            "pattern_detection": 0,
            "fraud_detection": 0
        }
        
        for error in errors:
            error_msg = error.error.lower()
            if any(keyword in error_msg for keyword in ["diagnóstico", "sexo", "edad", "coherencia"]):
                categories["clinical_coherence"] += 1
            elif any(keyword in error_msg for keyword in ["duplicado", "volumen", "patrón"]):
                categories["pattern_detection"] += 1
            elif any(keyword in error_msg for keyword in ["sospechoso", "fraude", "facturación"]):
                categories["fraud_detection"] += 1
        
        return {
            "status": "warning" if errors else "success",
            "total_ai_errors": len(errors),
            "categories": categories,
            "risk_level": self._calculate_risk_level(categories)
        }
    
    def _calculate_risk_level(self, categories: Dict[str, int]) -> str:
        """Calcular nivel de riesgo basado en los errores encontrados"""
        total_errors = sum(categories.values())
        
        if total_errors == 0:
            return "bajo"
        elif total_errors <= 5:
            return "medio"
        elif categories["fraud_detection"] > 0:
            return "muy_alto"
        else:
            return "alto"
