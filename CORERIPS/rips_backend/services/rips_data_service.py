"""
Servicio para procesar e insertar datos RIPS en Supabase
Maneja la conversión de JSON (español) a formato de Base de Datos (inglés)
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from supabase import Client
import logging

# Importar mapeos de campos
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from validators.field_mappings import map_json_to_db, get_table_name

logger = logging.getLogger(__name__)


class RIPSDataService:
    """Servicio para procesar y almacenar datos RIPS en Supabase"""
    
    def __init__(self, supabase_client: Client):
        """
        Inicializar servicio
        
        Args:
            supabase_client: Cliente de Supabase configurado
        """
        self.supabase = supabase_client
    
    def process_rips_file(self, file_path: str, file_id: int) -> Dict[str, Any]:
        """
        Procesar archivo RIPS JSON completo e insertar en Supabase
        
        Args:
            file_path: Ruta al archivo JSON
            file_id: ID del archivo en la tabla files
        
        Returns:
            Diccionario con estadísticas de inserción
        """
        logger.info(f"Procesando archivo RIPS: {file_path}")
        
        # Leer archivo JSON
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        stats = {
            "file_id": file_id,
            "usuarios": 0,
            "consultas": 0,
            "procedimientos": 0,
            "medicamentos": 0,
            "otros_servicios": 0,
            "urgencias": 0,
            "hospitalizaciones": 0,
            "recien_nacidos": 0,
            "facturacion": 0,
            "ajustes": 0,
            "control": 0,
            "errores": []
        }
        
        try:
            # Procesar datos de control si existen
            if self._is_control_data(data):
                self._insert_control(data, file_id, stats)
            
            # Procesar usuarios
            if "usuarios" in data:
                for usuario in data["usuarios"]:
                    self._insert_user(usuario, file_id, stats)
                    
                    # Procesar servicios del usuario
                    if "servicios" in usuario:
                        servicios = usuario["servicios"]
                        
                        # Consultas
                        if "consultas" in servicios:
                            for consulta in servicios["consultas"]:
                                self._insert_consultation(consulta, file_id, stats)
                        
                        # Procedimientos
                        if "procedimientos" in servicios:
                            for proc in servicios["procedimientos"]:
                                self._insert_procedure(proc, file_id, stats)
                        
                        # Medicamentos
                        if "medicamentos" in servicios:
                            for med in servicios["medicamentos"]:
                                self._insert_medication(med, file_id, stats)
                        
                        # Otros servicios
                        if "otros_servicios" in servicios:
                            for serv in servicios["otros_servicios"]:
                                self._insert_other_service(serv, file_id, stats)
                        
                        # Urgencias
                        if "urgencias" in servicios:
                            for urg in servicios["urgencias"]:
                                self._insert_emergency(urg, file_id, stats)
                        
                        # Hospitalizaciones
                        if "hospitalizaciones" in servicios:
                            for hosp in servicios["hospitalizaciones"]:
                                self._insert_hospitalization(hosp, file_id, stats)
                        
                        # Recién nacidos
                        if "recien_nacidos" in servicios:
                            for rn in servicios["recien_nacidos"]:
                                self._insert_newborn(rn, file_id, stats)
            
            # Procesar facturación si existe
            if "facturacion" in data:
                self._insert_billing(data["facturacion"], file_id, stats)
            
            # Procesar ajustes si existen
            if "ajustes" in data:
                for ajuste in data["ajustes"]:
                    self._insert_adjustment(ajuste, file_id, stats)
            
            logger.info(f"Archivo procesado exitosamente: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error procesando archivo RIPS: {str(e)}")
            stats["errores"].append(str(e))
            raise
    
    def _is_control_data(self, data: Dict) -> bool:
        """Verificar si los datos incluyen información de control"""
        control_fields = ["tipoRegistro", "fechaGeneracion", "versionAnexoTecnico"]
        return any(field in data for field in control_fields)
    
    def _insert_user(self, user_data: Dict, file_id: int, stats: Dict):
        """Insertar usuario en rips_users"""
        try:
            # Mapear campos a formato de BD
            user_db = map_json_to_db(user_data, "US")
            user_db["file_id"] = file_id
            
            # Insertar en Supabase
            table_name = get_table_name("US")
            result = self.supabase.table(table_name).insert(user_db).execute()
            
            stats["usuarios"] += 1
            logger.debug(f"Usuario insertado: {user_db.get('document_number')}")
            
        except Exception as e:
            error_msg = f"Error insertando usuario: {str(e)}"
            logger.error(error_msg)
            stats["errores"].append(error_msg)
    
    def _insert_consultation(self, consultation_data: Dict, file_id: int, stats: Dict):
        """Insertar consulta en rips_consultations"""
        try:
            # Mapear campos a formato de BD
            consultation_db = map_json_to_db(consultation_data, "AC")
            consultation_db["file_id"] = file_id
            
            # Insertar en Supabase
            table_name = get_table_name("AC")
            result = self.supabase.table(table_name).insert(consultation_db).execute()
            
            stats["consultas"] += 1
            logger.debug(f"Consulta insertada: {consultation_db.get('consultation_code')}")
            
        except Exception as e:
            error_msg = f"Error insertando consulta: {str(e)}"
            logger.error(error_msg)
            stats["errores"].append(error_msg)
    
    def _insert_procedure(self, procedure_data: Dict, file_id: int, stats: Dict):
        """Insertar procedimiento en rips_procedures"""
        try:
            # Mapear campos a formato de BD
            procedure_db = map_json_to_db(procedure_data, "AP")
            procedure_db["file_id"] = file_id
            
            # Insertar en Supabase
            table_name = get_table_name("AP")
            result = self.supabase.table(table_name).insert(procedure_db).execute()
            
            stats["procedimientos"] += 1
            logger.debug(f"Procedimiento insertado: {procedure_db.get('procedure_code')}")
            
        except Exception as e:
            error_msg = f"Error insertando procedimiento: {str(e)}"
            logger.error(error_msg)
            stats["errores"].append(error_msg)
    
    def _insert_medication(self, medication_data: Dict, file_id: int, stats: Dict):
        """Insertar medicamento en rips_medications"""
        try:
            # Mapear campos a formato de BD
            medication_db = map_json_to_db(medication_data, "AM")
            medication_db["file_id"] = file_id
            
            # Insertar en Supabase
            table_name = get_table_name("AM")
            result = self.supabase.table(table_name).insert(medication_db).execute()
            
            stats["medicamentos"] += 1
            logger.debug(f"Medicamento insertado: {medication_db.get('medication_code')}")
            
        except Exception as e:
            error_msg = f"Error insertando medicamento: {str(e)}"
            logger.error(error_msg)
            stats["errores"].append(error_msg)
    
    def _insert_other_service(self, service_data: Dict, file_id: int, stats: Dict):
        """Insertar otro servicio en rips_other_services"""
        try:
            # Mapear campos a formato de BD
            service_db = map_json_to_db(service_data, "AT")
            service_db["file_id"] = file_id
            
            # Insertar en Supabase
            table_name = get_table_name("AT")
            result = self.supabase.table(table_name).insert(service_db).execute()
            
            stats["otros_servicios"] += 1
            logger.debug(f"Otro servicio insertado: {service_db.get('service_code')}")
            
        except Exception as e:
            error_msg = f"Error insertando otro servicio: {str(e)}"
            logger.error(error_msg)
            stats["errores"].append(error_msg)
    
    def _insert_emergency(self, emergency_data: Dict, file_id: int, stats: Dict):
        """Insertar urgencia en rips_emergencies"""
        try:
            # Mapear campos a formato de BD
            emergency_db = map_json_to_db(emergency_data, "AU")
            emergency_db["file_id"] = file_id
            
            # Insertar en Supabase
            table_name = get_table_name("AU")
            result = self.supabase.table(table_name).insert(emergency_db).execute()
            
            stats["urgencias"] += 1
            logger.debug(f"Urgencia insertada")
            
        except Exception as e:
            error_msg = f"Error insertando urgencia: {str(e)}"
            logger.error(error_msg)
            stats["errores"].append(error_msg)
    
    def _insert_hospitalization(self, hospitalization_data: Dict, file_id: int, stats: Dict):
        """Insertar hospitalización en rips_hospitalizations"""
        try:
            # Mapear campos a formato de BD
            hospitalization_db = map_json_to_db(hospitalization_data, "AH")
            hospitalization_db["file_id"] = file_id
            
            # Insertar en Supabase
            table_name = get_table_name("AH")
            result = self.supabase.table(table_name).insert(hospitalization_db).execute()
            
            stats["hospitalizaciones"] += 1
            logger.debug(f"Hospitalización insertada")
            
        except Exception as e:
            error_msg = f"Error insertando hospitalización: {str(e)}"
            logger.error(error_msg)
            stats["errores"].append(error_msg)
    
    def _insert_newborn(self, newborn_data: Dict, file_id: int, stats: Dict):
        """Insertar recién nacido en rips_newborns"""
        try:
            # Mapear campos a formato de BD
            newborn_db = map_json_to_db(newborn_data, "AN")
            newborn_db["file_id"] = file_id
            
            # Insertar en Supabase
            table_name = get_table_name("AN")
            result = self.supabase.table(table_name).insert(newborn_db).execute()
            
            stats["recien_nacidos"] += 1
            logger.debug(f"Recién nacido insertado")
            
        except Exception as e:
            error_msg = f"Error insertando recién nacido: {str(e)}"
            logger.error(error_msg)
            stats["errores"].append(error_msg)
    
    def _insert_billing(self, billing_data: Dict, file_id: int, stats: Dict):
        """Insertar facturación en rips_billing"""
        try:
            # Mapear campos a formato de BD
            billing_db = map_json_to_db(billing_data, "AF")
            billing_db["file_id"] = file_id
            
            # Insertar en Supabase
            table_name = get_table_name("AF")
            result = self.supabase.table(table_name).insert(billing_db).execute()
            
            stats["facturacion"] += 1
            logger.debug(f"Facturación insertada: {billing_db.get('invoice_number')}")
            
        except Exception as e:
            error_msg = f"Error insertando facturación: {str(e)}"
            logger.error(error_msg)
            stats["errores"].append(error_msg)
    
    def _insert_adjustment(self, adjustment_data: Dict, file_id: int, stats: Dict):
        """Insertar ajuste en rips_adjustments"""
        try:
            # Mapear campos a formato de BD
            adjustment_db = map_json_to_db(adjustment_data, "AD")
            adjustment_db["file_id"] = file_id
            
            # Insertar en Supabase
            table_name = get_table_name("AD")
            result = self.supabase.table(table_name).insert(adjustment_db).execute()
            
            stats["ajustes"] += 1
            logger.debug(f"Ajuste insertado: {adjustment_db.get('note_number')}")
            
        except Exception as e:
            error_msg = f"Error insertando ajuste: {str(e)}"
            logger.error(error_msg)
            stats["errores"].append(error_msg)
    
    def _insert_control(self, control_data: Dict, file_id: int, stats: Dict):
        """Insertar información de control en rips_control"""
        try:
            # Mapear campos a formato de BD
            control_db = map_json_to_db(control_data, "CT")
            control_db["file_id"] = file_id
            
            # Insertar en Supabase
            table_name = get_table_name("CT")
            result = self.supabase.table(table_name).insert(control_db).execute()
            
            stats["control"] += 1
            logger.debug(f"Control insertado")
            
        except Exception as e:
            error_msg = f"Error insertando control: {str(e)}"
            logger.error(error_msg)
            stats["errores"].append(error_msg)
    
    def get_rips_data(self, file_id: int, data_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtener datos RIPS de Supabase
        
        Args:
            file_id: ID del archivo
            data_type: Tipo de datos a obtener (US, AC, AP, etc.) o None para todos
        
        Returns:
            Diccionario con los datos solicitados
        """
        results = {}
        
        try:
            if data_type:
                # Obtener solo un tipo de datos
                table_name = get_table_name(data_type)
                data = self.supabase.table(table_name).select("*").eq("file_id", file_id).execute()
                results[data_type] = data.data
            else:
                # Obtener todos los tipos de datos
                types = ["US", "AC", "AP", "AM", "AT", "AU", "AH", "AN", "AF", "AD", "CT"]
                for tipo in types:
                    table_name = get_table_name(tipo)
                    data = self.supabase.table(table_name).select("*").eq("file_id", file_id).execute()
                    results[tipo] = data.data
            
            return results
            
        except Exception as e:
            logger.error(f"Error obteniendo datos RIPS: {str(e)}")
            raise


# Función de utilidad para uso directo
def process_rips_json_file(file_path: str, file_id: int, supabase_client: Client) -> Dict[str, Any]:
    """
    Función helper para procesar un archivo RIPS JSON
    
    Args:
        file_path: Ruta al archivo JSON
        file_id: ID del archivo en la BD
        supabase_client: Cliente de Supabase
    
    Returns:
        Estadísticas de inserción
    """
    service = RIPSDataService(supabase_client)
    return service.process_rips_file(file_path, file_id)

