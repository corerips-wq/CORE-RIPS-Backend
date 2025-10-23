"""
Mapeo de campos RIPS entre diferentes formatos:
- JSON de entrada (español camelCase)
- Base de datos Supabase (inglés snake_case)
- Procesamiento interno (español snake_case)

Este mapeo permite la traducción automática entre formatos.
"""

# =============================================================================
# MAPEO: JSON (Español) → Base de Datos (Inglés)
# =============================================================================

# Mapeo para Usuarios (US)
USERS_FIELD_MAPPING = {
    # JSON (español camelCase) → Database (inglés snake_case)
    "tipoDocumentoIdentificacion": "document_type",
    "numDocumentoIdentificacion": "document_number",
    "codEntidadAdministradora": "administrator_entity_code",
    "tipoUsuario": "user_type",
    "primerApellido": "first_surname",
    "segundoApellido": "second_surname",
    "primerNombre": "first_name",
    "segundoNombre": "second_name",
    "edadMedida": "age_measure",
    "edad": "age",
    "unidadMedidaEdad": "age_unit",
    "codDepartamento": "department_code",
    "codMunicipio": "municipality_code",
    "zonaResidencial": "residential_zone",
    # Campos adicionales del JSON
    "fechaNacimiento": "birth_date",
    "codSexo": "sex",
    "consecutivo": "consecutive_file"
}

# Mapeo para Consultas (AC)
CONSULTATIONS_FIELD_MAPPING = {
    # JSON (español camelCase) → Database (inglés snake_case)
    "consecutivo": "consecutive_file",
    "numFactura": "invoice_number",
    "codPrestador": "provider_code",
    "tipoDocumentoIdentificacion": "identification_type",
    "numDocumentoIdentificacion": "identification_number",
    "fechaInicioAtencion": "consultation_date",
    "numAutorizacion": "authorization_number",
    "codConsulta": "consultation_code",
    "finalidadTecnologiaSalud": "consultation_purpose",
    "causaMotivoAtencion": "external_cause",
    "codDiagnosticoPrincipal": "primary_diagnosis",
    "codDiagnosticoRelacionado1": "related_diagnosis_1",
    "codDiagnosticoRelacionado2": "related_diagnosis_2",
    "codDiagnosticoRelacionado3": "related_diagnosis_3",
    "tipoDiagnosticoPrincipal": "primary_diagnosis_type",
    "vrServicio": "consultation_value",
    "valorPagoModerador": "copayment_value",
    "valorNeto": "net_payment_value"
}

# Mapeo para Procedimientos (AP)
PROCEDURES_FIELD_MAPPING = {
    # JSON (español camelCase) → Database (inglés snake_case)
    "consecutivo": "consecutive_file",
    "numFactura": "invoice_number",
    "codPrestador": "provider_code",
    "tipoDocumentoIdentificacion": "identification_type",
    "numDocumentoIdentificacion": "identification_number",
    "fechaInicioAtencion": "procedure_date",
    "numAutorizacion": "authorization_number",
    "codProcedimiento": "procedure_code",
    "modalidadGrupoServicioTecSal": "performance_scope",
    "finalidadTecnologiaSalud": "procedure_purpose",
    "personalAtencion": "attending_personnel",
    "codDiagnosticoPrincipal": "primary_diagnosis",
    "codDiagnosticoRelacionado": "related_diagnosis",
    "codComplicacion": "complication",
    "formaRealizacionActoQx": "surgical_act_performance_form",
    "vrServicio": "procedure_value"
}

# Mapeo para Medicamentos (AM)
MEDICATIONS_FIELD_MAPPING = {
    # JSON (español camelCase) → Database (inglés snake_case)
    "consecutivo": "consecutive_file",
    "numFactura": "invoice_number",
    "codPrestador": "provider_code",
    "tipoDocumentoIdentificacion": "identification_type",
    "numDocumentoIdentificacion": "identification_number",
    "fechaDispensacion": "consultation_date",
    "numAutorizacion": "authorization_number",
    "codProducto": "medication_code",
    "tipoMedicamento": "medication_type",
    "nombreProducto": "generic_name",
    "formaFarmaceutica": "pharmaceutical_form",
    "concentracion": "medication_concentration",
    "unidadMedida": "unit_measure",
    "cantidadRecetada": "unit_number",
    "vrUnitario": "unit_value",
    "vrServicio": "total_value"
}

# Mapeo para Otros Servicios (AT)
OTHER_SERVICES_FIELD_MAPPING = {
    # JSON (español camelCase) → Database (inglés snake_case)
    "consecutivo": "consecutive_file",
    "numFactura": "invoice_number",
    "codPrestador": "provider_code",
    "tipoDocumentoIdentificacion": "identification_type",
    "numDocumentoIdentificacion": "identification_number",
    "fechaServicio": "service_date",
    "numAutorizacion": "authorization_number",
    "codServicio": "service_code",
    "nombreServicio": "service_name",
    "cantidad": "quantity",
    "vrUnitario": "unit_value",
    "vrServicio": "total_value"
}

# Mapeo para Urgencias (AU)
EMERGENCIES_FIELD_MAPPING = {
    # JSON (español camelCase) → Database (inglés snake_case)
    "consecutivo": "consecutive_file",
    "numFactura": "invoice_number",
    "codPrestador": "provider_code",
    "tipoDocumentoIdentificacion": "identification_type",
    "numDocumentoIdentificacion": "identification_number",
    "fechaIngreso": "admission_date",
    "horaIngreso": "admission_time",
    "numAutorizacion": "authorization_number",
    "causaMotivoAtencion": "external_cause",
    "codDiagnosticoIngreso": "admission_diagnosis",
    "codDiagnosticoEgreso": "discharge_diagnosis",
    "codDiagnosticoRelacionado1": "related_diagnosis_1",
    "codDiagnosticoRelacionado2": "related_diagnosis_2",
    "codDiagnosticoRelacionado3": "related_diagnosis_3",
    "codDiagnosticoRelacionado4": "related_diagnosis_4",
    "tipoDiagnosticoPrincipal": "primary_diagnosis_type",
    "vrServicio": "service_value",
    "valorPagoModerador": "copayment_value",
    "valorNeto": "net_value"
}

# Mapeo para Hospitalizaciones (AH)
HOSPITALIZATIONS_FIELD_MAPPING = {
    # JSON (español camelCase) → Database (inglés snake_case)
    "consecutivo": "consecutive_file",
    "numFactura": "invoice_number",
    "codPrestador": "provider_code",
    "tipoDocumentoIdentificacion": "identification_type",
    "numDocumentoIdentificacion": "identification_number",
    "viaIngreso": "admission_route",
    "fechaIngreso": "admission_date",
    "horaIngreso": "admission_time",
    "numAutorizacion": "authorization_number",
    "causaMotivoAtencion": "external_cause",
    "codDiagnosticoIngreso": "admission_diagnosis",
    "codDiagnosticoEgreso": "discharge_diagnosis",
    "codDiagnosticoRelacionado1": "related_diagnosis_1",
    "codDiagnosticoRelacionado2": "related_diagnosis_2",
    "codDiagnosticoRelacionado3": "related_diagnosis_3",
    "codDiagnosticoRelacionado4": "related_diagnosis_4",
    "tipoDiagnosticoPrincipal": "primary_diagnosis_type",
    "diasEstancia": "stay_days",
    "tipoEgreso": "discharge_type",
    "condicionDestinoUsuario": "user_destination_condition",
    "causaMuerteObstetrica": "obstetric_death_cause",
    "fechaEgreso": "discharge_date",
    "horaEgreso": "discharge_time",
    "vrServicio": "service_value",
    "valorPagoModerador": "copayment_value",
    "valorNeto": "net_value"
}

# Mapeo para Recién Nacidos (AN)
NEWBORNS_FIELD_MAPPING = {
    # JSON (español camelCase) → Database (inglés snake_case)
    "consecutivo": "consecutive_file",
    "numFactura": "invoice_number",
    "codPrestador": "provider_code",
    "tipoDocIdentificacionMadre": "mother_identification_type",
    "numDocIdentificacionMadre": "mother_identification_number",
    "fechaNacimiento": "birth_date",
    "horaNacimiento": "birth_time",
    "edadGestacional": "gestational_age",
    "controlPrenatal": "prenatal_control",
    "sexo": "sex",
    "pesoNacimiento": "birth_weight",
    "codDiagnosticoPrincipal": "primary_diagnosis",
    "codDiagnosticoRelacionado1": "related_diagnosis_1",
    "codDiagnosticoRelacionado2": "related_diagnosis_2",
    "codDiagnosticoRelacionado3": "related_diagnosis_3",
    "causaBasicaMuerte": "basic_death_cause",
    "fechaMuerte": "death_date",
    "horaMuerte": "death_time"
}

# Mapeo para Facturación (AF)
BILLING_FIELD_MAPPING = {
    # JSON (español camelCase) → Database (inglés snake_case)
    "consecutivo": "consecutive_file",
    "numFactura": "invoice_number",
    "codPrestador": "provider_code",
    "fechaExpedicionFactura": "invoice_issue_date",
    "fechaInicioPeriodo": "period_start_date",
    "fechaFinPeriodo": "period_end_date",
    "codEntidadAdministradora": "administrator_entity_code",
    "nombreEntidadAdministradora": "administrator_entity_name",
    "numContrato": "contract_number",
    "planBeneficios": "benefits_plan",
    "numPoliza": "policy_number",
    "copago": "copayment",
    "valorComision": "commission_value",
    "valorDescuentos": "discounts_value",
    "valorNetoFactura": "net_invoice_value"
}

# Mapeo para Ajustes (AD)
ADJUSTMENTS_FIELD_MAPPING = {
    # JSON (español camelCase) → Database (inglés snake_case)
    "consecutivo": "consecutive_file",
    "numFactura": "invoice_number",
    "codPrestador": "provider_code",
    "tipoNota": "note_type",
    "numNota": "note_number",
    "fechaExpedicionNota": "note_issue_date",
    "codConcepto": "concept_code",
    "descripcionConcepto": "concept_description",
    "valorAjuste": "adjustment_value"
}

# Mapeo para Control (CT)
CONTROL_FIELD_MAPPING = {
    # JSON (español camelCase) → Database (inglés snake_case)
    "tipoRegistro": "record_type",
    "codPrestador": "provider_code",
    "fechaGeneracion": "generation_date",
    "archivoRips": "rips_file",
    "totalRegistros": "total_records",
    "codEntidadAdministradora": "administrator_entity_code",
    "nombreEntidadAdministradora": "administrator_entity_name",
    "numContrato": "contract_number",
    "planBeneficios": "benefits_plan",
    "versionAnexoTecnico": "technical_annex_version"
}

# =============================================================================
# MAPEO POR TIPO DE ARCHIVO
# =============================================================================

FILE_TYPE_MAPPINGS = {
    "US": USERS_FIELD_MAPPING,
    "AC": CONSULTATIONS_FIELD_MAPPING,
    "AP": PROCEDURES_FIELD_MAPPING,
    "AM": MEDICATIONS_FIELD_MAPPING,
    "AT": OTHER_SERVICES_FIELD_MAPPING,
    "AU": EMERGENCIES_FIELD_MAPPING,
    "AH": HOSPITALIZATIONS_FIELD_MAPPING,
    "AN": NEWBORNS_FIELD_MAPPING,
    "AF": BILLING_FIELD_MAPPING,
    "AD": ADJUSTMENTS_FIELD_MAPPING,
    "CT": CONTROL_FIELD_MAPPING
}

# =============================================================================
# MAPEO DE NOMBRES DE TABLAS
# =============================================================================

TABLE_NAME_MAPPING = {
    "US": "rips_users",
    "AC": "rips_consultations",
    "AP": "rips_procedures",
    "AM": "rips_medications",
    "AT": "rips_other_services",
    "AU": "rips_emergencies",
    "AH": "rips_hospitalizations",
    "AN": "rips_newborns",
    "AF": "rips_billing",
    "AD": "rips_adjustments",
    "CT": "rips_control"
}

# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

def map_json_to_db(data: dict, file_type: str) -> dict:
    """
    Convierte campos de JSON (español camelCase) a formato de BD (inglés snake_case)
    
    Args:
        data: Diccionario con datos en formato JSON (español)
        file_type: Tipo de archivo RIPS (US, AC, AP, etc.)
    
    Returns:
        Diccionario con campos mapeados a nombres de BD
    """
    if file_type not in FILE_TYPE_MAPPINGS:
        return data
    
    mapping = FILE_TYPE_MAPPINGS[file_type]
    mapped_data = {}
    
    for json_field, value in data.items():
        # Si el campo está en el mapeo, usar el nombre de BD
        if json_field in mapping:
            db_field = mapping[json_field]
            mapped_data[db_field] = value
        else:
            # Si no está mapeado, mantener el nombre original
            mapped_data[json_field] = value
    
    return mapped_data


def map_db_to_json(data: dict, file_type: str) -> dict:
    """
    Convierte campos de BD (inglés snake_case) a formato JSON (español camelCase)
    
    Args:
        data: Diccionario con datos en formato BD (inglés)
        file_type: Tipo de archivo RIPS (US, AC, AP, etc.)
    
    Returns:
        Diccionario con campos mapeados a nombres JSON
    """
    if file_type not in FILE_TYPE_MAPPINGS:
        return data
    
    # Invertir el mapeo
    mapping = FILE_TYPE_MAPPINGS[file_type]
    reverse_mapping = {v: k for k, v in mapping.items()}
    
    mapped_data = {}
    
    for db_field, value in data.items():
        # Si el campo está en el mapeo inverso, usar el nombre JSON
        if db_field in reverse_mapping:
            json_field = reverse_mapping[db_field]
            mapped_data[json_field] = value
        else:
            # Si no está mapeado, mantener el nombre original
            mapped_data[db_field] = value
    
    return mapped_data


def get_table_name(file_type: str) -> str:
    """
    Obtiene el nombre de la tabla en la BD para un tipo de archivo RIPS
    
    Args:
        file_type: Tipo de archivo RIPS (US, AC, AP, etc.)
    
    Returns:
        Nombre de la tabla en la base de datos
    """
    return TABLE_NAME_MAPPING.get(file_type, "rips_unknown")


# =============================================================================
# EJEMPLO DE USO
# =============================================================================

if __name__ == "__main__":
    # Ejemplo: Datos de consulta en formato JSON (español)
    json_data = {
        "tipoDocumentoIdentificacion": "CC",
        "numDocumentoIdentificacion": "123456789",
        "codDiagnosticoPrincipal": "A09",
        "vrServicio": 50000
    }
    
    # Convertir a formato de BD (inglés)
    db_data = map_json_to_db(json_data, "AC")
    print("JSON → DB:")
    print(db_data)
    # Resultado: {'identification_type': 'CC', 'identification_number': '123456789', 
    #            'primary_diagnosis': 'A09', 'consultation_value': 50000}
    
    # Convertir de BD a JSON
    json_back = map_db_to_json(db_data, "AC")
    print("\nDB → JSON:")
    print(json_back)
    
    # Obtener nombre de tabla
    table = get_table_name("AC")
    print(f"\nTabla para AC: {table}")

