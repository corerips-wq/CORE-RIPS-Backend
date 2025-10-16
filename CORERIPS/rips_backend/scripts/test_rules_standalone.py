#!/usr/bin/env python3
"""
Script standalone para probar reglas determinísticas RIPS
No requiere dependencias externas, solo librerías estándar de Python
"""

import os
import json
import zipfile
import tempfile
from pathlib import Path
from datetime import datetime, date
from collections import defaultdict
import re


class SimpleError:
    """Clase simple para errores"""
    def __init__(self, line, field, error):
        self.line = line
        self.field = field
        self.error = error


class SimpleValidator:
    """Validador determinístico simple sin dependencias externas"""
    
    def __init__(self):
        # Catálogos
        self.valid_document_types = ["CC", "TI", "RC", "CE", "PA", "NUIP", "MS"]
        self.valid_sexes = ["M", "F"]
        
    def validate_file(self, file_path: str, file_type: str = "AC"):
        """Validar archivo RIPS"""
        errors = []
        
        file_extension = file_path.lower().split('.')[-1]
        
        if file_extension == 'json':
            return self._validate_json_file(file_path)
        elif file_extension == 'zip':
            return self._validate_zip_file(file_path)
        elif file_extension in ['txt', 'csv']:
            return self._validate_text_file(file_path, file_type)
        else:
            errors.append(SimpleError(
                0, "archivo",
                f"Formato no soportado (.{file_extension})"
            ))
            return errors
    
    def _validate_json_file(self, file_path: str):
        """Validar archivo JSON RIPS"""
        errors = []
        rules_tested = {
            # Reglas de formato general
            "GEN-002": {"tested": False, "passed": False, "name": "Estructura archivo válida"},
            "GEN-003": {"tested": False, "passed": False, "name": "Codificación UTF-8"},
            
            # Reglas de Control (CT)
            "CT-001": {"tested": False, "passed": False, "name": "Tipo registro válido"},
            "CT-002": {"tested": False, "passed": False, "name": "Fecha generación válida"},
            "CT-003": {"tested": False, "passed": False, "name": "Número factura presente"},
            
            # Reglas de Usuarios (US)
            "US-001": {"tested": False, "passed": False, "name": "Tipo documento válido"},
            "US-002": {"tested": False, "passed": False, "name": "Número documento presente"},
            "US-003": {"tested": False, "passed": False, "name": "Tipo usuario válido"},
            "US-004": {"tested": False, "passed": False, "name": "Código país residencia válido"},
            "US-005": {"tested": False, "passed": False, "name": "Código municipio residencia válido"},
            "US-007": {"tested": False, "passed": False, "name": "Fecha nacimiento válida"},
            "US-008": {"tested": False, "passed": False, "name": "Sexo válido"},
            
            # Reglas de Consultas (AC)
            "AC-001": {"tested": False, "passed": False, "name": "Código prestador válido"},
            "AC-002": {"tested": False, "passed": False, "name": "Fecha inicio atención válida"},
            "AC-003": {"tested": False, "passed": False, "name": "Número autorización presente"},
            "AC-004": {"tested": False, "passed": False, "name": "Código consulta válido"},
            "AC-005": {"tested": False, "passed": False, "name": "Finalidad tecnología salud válida"},
            "AC-012": {"tested": False, "passed": False, "name": "Diagnóstico CIE válido"},
            
            # Reglas de Procedimientos (AP)
            "AP-001": {"tested": False, "passed": False, "name": "Código CUPS válido"},
            "AP-002": {"tested": False, "passed": False, "name": "Fecha procedimiento válida"},
            "AP-003": {"tested": False, "passed": False, "name": "Vía ingreso servicio válida"},
            "AP-004": {"tested": False, "passed": False, "name": "Modalidad grupo servicio válida"},
            "AP-005": {"tested": False, "passed": False, "name": "Grupo servicios válido"},
            
            # Reglas de Medicamentos (AM)
            "AM-001": {"tested": False, "passed": False, "name": "Código producto válido"},
            "AM-002": {"tested": False, "passed": False, "name": "Tipo medicamento válido"},
            "AM-003": {"tested": False, "passed": False, "name": "Concentración presente"},
            "AM-004": {"tested": False, "passed": False, "name": "Unidad medida válida"},
            
            # Reglas de Facturación (AF)
            "AF-001": {"tested": False, "passed": False, "name": "Número factura presente"},
            "AF-002": {"tested": False, "passed": False, "name": "Tipo factura válido"},
            "AF-004": {"tested": False, "passed": False, "name": "CUV presente cuando aplica"},
            
            # Reglas de Ajustes (AD)
            "AD-001": {"tested": False, "passed": False, "name": "Tipo nota válido"},
            "AD-002": {"tested": False, "passed": False, "name": "Número nota presente"},
            
            # Reglas generales adicionales
            "GEN-001": {"tested": False, "passed": False, "name": "Versión anexo técnico presente"},
            "FMT-006": {"tested": False, "passed": False, "name": "Fechas coherentes"},
        }
        
        try:
            # Leer con UTF-8-sig para manejar BOM automáticamente
            with open(file_path, 'r', encoding='utf-8-sig') as file:
                data = json.load(file)
            
            rules_tested["GEN-002"]["tested"] = True
            rules_tested["GEN-002"]["passed"] = True
            rules_tested["GEN-003"]["tested"] = True
            rules_tested["GEN-003"]["passed"] = True
            
            # Verificar estructura básica y campos de control/facturación
            # CT-003 / AF-001: Número de factura
            rules_tested["CT-003"]["tested"] = True
            rules_tested["AF-001"]["tested"] = True
            num_factura = data.get("numFactura", "")
            if num_factura:
                rules_tested["CT-003"]["passed"] = True
                rules_tested["AF-001"]["passed"] = True
            else:
                errors.append(SimpleError(0, "numFactura", "Número de factura obligatorio"))
            
            # CT-001: Tipo registro
            tipo_registro = data.get("tipoRegistro", "")
            if tipo_registro:
                rules_tested["CT-001"]["tested"] = True
                if tipo_registro == "1":
                    rules_tested["CT-001"]["passed"] = True
                else:
                    errors.append(SimpleError(0, "tipoRegistro", f"Tipo registro debe ser '1', encontrado: '{tipo_registro}'"))
            
            # CT-002: Fecha generación
            fecha_gen = data.get("fechaGeneracion", "")
            if fecha_gen:
                rules_tested["CT-002"]["tested"] = True
                try:
                    datetime.strptime(fecha_gen, '%Y-%m-%d')
                    rules_tested["CT-002"]["passed"] = True
                except:
                    errors.append(SimpleError(0, "fechaGeneracion", f"Formato de fecha inválido: '{fecha_gen}'"))
            
            # AF-002: Tipo factura
            tipo_factura = data.get("tipoFactura", "")
            if tipo_factura:
                rules_tested["AF-002"]["tested"] = True
                if len(tipo_factura) >= 1:
                    rules_tested["AF-002"]["passed"] = True
            
            # AF-004: CUV
            cuv = data.get("cuv", "")
            if cuv:
                rules_tested["AF-004"]["tested"] = True
                if 10 <= len(cuv) <= 64:
                    rules_tested["AF-004"]["passed"] = True
                else:
                    errors.append(SimpleError(0, "cuv", f"CUV debe tener 10-64 caracteres, encontrado: {len(cuv)}"))
            
            # GEN-001: Versión anexo técnico
            version_anexo = data.get("versionAnexoTecnico", "")
            if version_anexo:
                rules_tested["GEN-001"]["tested"] = True
                if len(version_anexo) >= 1:
                    rules_tested["GEN-001"]["passed"] = True
            
            # Tipo de nota (si existe)
            tipo_nota = data.get("tipoNota", None)
            
            # AD-001: Tipo nota (solo validar si no es null)
            if tipo_nota is not None and tipo_nota != "":
                rules_tested["AD-001"]["tested"] = True
                if tipo_nota in ["NC", "ND"]:
                    rules_tested["AD-001"]["passed"] = True
                else:
                    errors.append(SimpleError(0, "tipoNota", f"Tipo nota '{tipo_nota}' inválido. Debe ser NC o ND"))
            
            # AD-002: Número de nota
            num_nota = data.get("numNota", "")
            if num_nota:
                rules_tested["AD-002"]["tested"] = True
                if len(num_nota) >= 1:
                    rules_tested["AD-002"]["passed"] = True
            
            # Verificar usuarios
            if "usuarios" not in data:
                errors.append(SimpleError(0, "estructura", "JSON no contiene campo 'usuarios'"))
                return errors
            
            usuarios = data.get("usuarios", [])
            
            for idx, usuario in enumerate(usuarios, 1):
                # US-001: Tipo documento
                rules_tested["US-001"]["tested"] = True
                tipo_doc = usuario.get("tipoDocumentoIdentificacion", "")
                if tipo_doc:
                    if tipo_doc in self.valid_document_types:
                        rules_tested["US-001"]["passed"] = True
                    else:
                        errors.append(SimpleError(
                            idx, "tipoDocumentoIdentificacion",
                            f"Tipo documento '{tipo_doc}' no válido. Valores permitidos: {', '.join(self.valid_document_types)}"
                        ))
                else:
                    errors.append(SimpleError(idx, "tipoDocumentoIdentificacion", "Campo obligatorio vacío"))
                
                # US-002: Número documento
                rules_tested["US-002"]["tested"] = True
                num_doc = usuario.get("numDocumentoIdentificacion", "")
                if num_doc:
                    rules_tested["US-002"]["passed"] = True
                else:
                    errors.append(SimpleError(idx, "numDocumentoIdentificacion", "Campo obligatorio vacío"))
                
                # US-007: Fecha nacimiento
                rules_tested["US-007"]["tested"] = True
                fecha_nac = usuario.get("fechaNacimiento", "")
                if fecha_nac:
                    if self._validate_date_format(fecha_nac):
                        rules_tested["US-007"]["passed"] = True
                        # Validar fecha no futura
                        rules_tested["FMT-006"]["tested"] = True
                        try:
                            parsed_date = datetime.strptime(fecha_nac, '%Y-%m-%d').date()
                            if parsed_date <= date.today():
                                rules_tested["FMT-006"]["passed"] = True
                            else:
                                errors.append(SimpleError(idx, "fechaNacimiento", "Fecha de nacimiento no puede ser futura"))
                        except:
                            pass
                    else:
                        errors.append(SimpleError(idx, "fechaNacimiento", "Formato de fecha inválido (esperado: YYYY-MM-DD)"))
                else:
                    errors.append(SimpleError(idx, "fechaNacimiento", "Campo obligatorio vacío"))
                
                # US-008: Sexo
                rules_tested["US-008"]["tested"] = True
                sexo = usuario.get("codSexo", "")
                if sexo:
                    if sexo in self.valid_sexes:
                        rules_tested["US-008"]["passed"] = True
                    else:
                        errors.append(SimpleError(
                            idx, "codSexo",
                            f"Sexo '{sexo}' no válido. Valores permitidos: {', '.join(self.valid_sexes)}"
                        ))
                else:
                    errors.append(SimpleError(idx, "codSexo", "Campo obligatorio vacío"))
                
                # US-003: Tipo usuario
                rules_tested["US-003"]["tested"] = True
                tipo_usuario = usuario.get("tipoUsuario", "")
                if tipo_usuario:
                    # Tipo usuario es código de 2 dígitos
                    if len(tipo_usuario) == 2 and tipo_usuario.isdigit():
                        rules_tested["US-003"]["passed"] = True
                    else:
                        errors.append(SimpleError(idx, "tipoUsuario", f"Tipo usuario debe ser código de 2 dígitos"))
                
                # US-004: Código país residencia
                rules_tested["US-004"]["tested"] = True
                cod_pais = usuario.get("codPaisResidencia", "")
                if cod_pais:
                    # Código país es 3 dígitos
                    if len(cod_pais) == 3 and cod_pais.isdigit():
                        rules_tested["US-004"]["passed"] = True
                    else:
                        errors.append(SimpleError(idx, "codPaisResidencia", f"Código país debe ser 3 dígitos"))
                
                # US-005: Código municipio residencia
                rules_tested["US-005"]["tested"] = True
                cod_municipio = usuario.get("codMunicipioResidencia", "")
                if cod_municipio:
                    # Código municipio es 5 dígitos
                    if len(cod_municipio) == 5 and cod_municipio.isdigit():
                        rules_tested["US-005"]["passed"] = True
                    else:
                        errors.append(SimpleError(idx, "codMunicipioResidencia", f"Código municipio debe ser 5 dígitos"))
                
                # Validar servicios/consultas
                servicios = usuario.get("servicios", {})
                consultas = servicios.get("consultas", [])
                
                for cons_idx, consulta in enumerate(consultas, 1):
                    # AC-001: Código prestador
                    rules_tested["AC-001"]["tested"] = True
                    cod_prest = consulta.get("codPrestador", "")
                    if cod_prest:
                        if len(cod_prest) == 12 and cod_prest.isdigit():
                            rules_tested["AC-001"]["passed"] = True
                        else:
                            errors.append(SimpleError(
                                idx, f"consulta{cons_idx}.codPrestador",
                                f"Código prestador debe ser 12 dígitos numéricos, encontrado: '{cod_prest}'"
                            ))
                    
                    # AC-002: Fecha inicio atención
                    rules_tested["AC-002"]["tested"] = True
                    fecha_atencion = consulta.get("fechaInicioAtencion", "")
                    if fecha_atencion:
                        # Extraer solo la fecha si tiene hora
                        fecha_parte = fecha_atencion.split()[0] if ' ' in fecha_atencion else fecha_atencion
                        try:
                            parsed_date = datetime.strptime(fecha_parte, '%Y-%m-%d').date()
                            rules_tested["AC-002"]["passed"] = True
                            # Validar fecha no futura (FMT-006)
                            if parsed_date > date.today():
                                errors.append(SimpleError(
                                    idx, f"consulta{cons_idx}.fechaInicioAtencion",
                                    f"Fecha de atención '{fecha_atencion}' es futura"
                                ))
                        except:
                            errors.append(SimpleError(
                                idx, f"consulta{cons_idx}.fechaInicioAtencion",
                                f"Formato de fecha inválido: '{fecha_atencion}'"
                            ))
                    
                    # AC-003: Número autorización
                    rules_tested["AC-003"]["tested"] = True
                    num_autorizacion = consulta.get("numAutorizacion", "")
                    if num_autorizacion:
                        rules_tested["AC-003"]["passed"] = True
                    
                    # AC-004: Código consulta
                    rules_tested["AC-004"]["tested"] = True
                    cod_consulta = consulta.get("codConsulta", "")
                    if cod_consulta:
                        # Código consulta es código de 6 dígitos
                        if len(cod_consulta) == 6 and cod_consulta.isdigit():
                            rules_tested["AC-004"]["passed"] = True
                        else:
                            errors.append(SimpleError(
                                idx, f"consulta{cons_idx}.codConsulta",
                                f"Código consulta debe ser 6 dígitos"
                            ))
                    
                    # AC-005: Finalidad tecnología salud
                    rules_tested["AC-005"]["tested"] = True
                    finalidad = consulta.get("finalidadTecnologiaSalud", "")
                    if finalidad:
                        # Finalidad es código de 2 dígitos
                        if len(finalidad) == 2 and finalidad.isdigit():
                            rules_tested["AC-005"]["passed"] = True
                        else:
                            errors.append(SimpleError(
                                idx, f"consulta{cons_idx}.finalidadTecnologiaSalud",
                                f"Finalidad debe ser código de 2 dígitos"
                            ))
                    
                    # AC-012: Diagnóstico principal
                    rules_tested["AC-012"]["tested"] = True
                    diag = consulta.get("codDiagnosticoPrincipal", "")
                    if diag:
                        if 3 <= len(diag) <= 7:
                            rules_tested["AC-012"]["passed"] = True
                        else:
                            errors.append(SimpleError(
                                idx, f"consulta{cons_idx}.codDiagnosticoPrincipal",
                                f"Código CIE debe tener 3-7 caracteres, encontrado: '{diag}' ({len(diag)} caracteres)"
                            ))
                
                # Validar procedimientos
                procedimientos = servicios.get("procedimientos", [])
                for proc_idx, proc in enumerate(procedimientos, 1):
                    # Validar código prestador en procedimientos
                    cod_prest = proc.get("codPrestador", "")
                    if cod_prest:
                        if len(cod_prest) == 12 and cod_prest.isdigit():
                            rules_tested["AC-001"]["passed"] = True
                        else:
                            errors.append(SimpleError(
                                idx, f"procedimiento{proc_idx}.codPrestador",
                                f"Código prestador debe ser 12 dígitos numéricos"
                            ))
                    
                    # AP-001: Código CUPS (codProcedimiento)
                    rules_tested["AP-001"]["tested"] = True
                    cod_cups = proc.get("codProcedimiento", "")
                    if cod_cups:
                        if 3 <= len(cod_cups) <= 7:
                            rules_tested["AP-001"]["passed"] = True
                        else:
                            errors.append(SimpleError(
                                idx, f"procedimiento{proc_idx}.codProcedimiento",
                                f"Código CUPS debe tener 3-7 caracteres"
                            ))
                    
                    # AP-002: Fecha procedimiento
                    rules_tested["AP-002"]["tested"] = True
                    fecha_proc = proc.get("fechaInicioAtencion", "")
                    if fecha_proc:
                        fecha_parte = fecha_proc.split()[0] if ' ' in fecha_proc else fecha_proc
                        try:
                            datetime.strptime(fecha_parte, '%Y-%m-%d')
                            rules_tested["AP-002"]["passed"] = True
                        except:
                            errors.append(SimpleError(
                                idx, f"procedimiento{proc_idx}.fechaInicioAtencion",
                                f"Formato de fecha inválido"
                            ))
                    
                    # AP-003: Vía ingreso servicio salud
                    rules_tested["AP-003"]["tested"] = True
                    via_ingreso = proc.get("viaIngresoServicioSalud", "")
                    if via_ingreso:
                        if len(via_ingreso) == 2 and via_ingreso.isdigit():
                            rules_tested["AP-003"]["passed"] = True
                        else:
                            errors.append(SimpleError(
                                idx, f"procedimiento{proc_idx}.viaIngresoServicioSalud",
                                f"Vía ingreso debe ser código de 2 dígitos"
                            ))
                    
                    # AP-004: Modalidad grupo servicio
                    rules_tested["AP-004"]["tested"] = True
                    modalidad = proc.get("modalidadGrupoServicioTecSal", "")
                    if modalidad:
                        if len(modalidad) == 2 and modalidad.isdigit():
                            rules_tested["AP-004"]["passed"] = True
                        else:
                            errors.append(SimpleError(
                                idx, f"procedimiento{proc_idx}.modalidadGrupoServicioTecSal",
                                f"Modalidad debe ser código de 2 dígitos"
                            ))
                    
                    # AP-005: Grupo servicios
                    rules_tested["AP-005"]["tested"] = True
                    grupo_serv = proc.get("grupoServicios", "")
                    if grupo_serv:
                        if len(grupo_serv) == 2 and grupo_serv.isdigit():
                            rules_tested["AP-005"]["passed"] = True
                        else:
                            errors.append(SimpleError(
                                idx, f"procedimiento{proc_idx}.grupoServicios",
                                f"Grupo servicios debe ser código de 2 dígitos"
                            ))
                
                # Validar medicamentos
                medicamentos = servicios.get("medicamentos", [])
                for med_idx, med in enumerate(medicamentos, 1):
                    # AM-001: Código producto
                    rules_tested["AM-001"]["tested"] = True
                    cod_producto = med.get("codProducto", "")
                    if cod_producto:
                        if 3 <= len(cod_producto) <= 20:
                            rules_tested["AM-001"]["passed"] = True
                        else:
                            errors.append(SimpleError(
                                idx, f"medicamento{med_idx}.codProducto",
                                f"Código producto debe tener 3-20 caracteres"
                            ))
                    
                    # AM-002: Tipo medicamento
                    rules_tested["AM-002"]["tested"] = True
                    tipo_med = med.get("tipoMedicamento", "")
                    if tipo_med:
                        if len(tipo_med) == 2 and tipo_med.isdigit():
                            rules_tested["AM-002"]["passed"] = True
                        else:
                            errors.append(SimpleError(
                                idx, f"medicamento{med_idx}.tipoMedicamento",
                                f"Tipo medicamento debe ser código de 2 dígitos"
                            ))
                    
                    # AM-003: Concentración
                    rules_tested["AM-003"]["tested"] = True
                    concentracion = med.get("concentracion", "")
                    if concentracion:
                        if 1 <= len(concentracion) <= 20:
                            rules_tested["AM-003"]["passed"] = True
                        else:
                            errors.append(SimpleError(
                                idx, f"medicamento{med_idx}.concentracion",
                                f"Concentración debe tener 1-20 caracteres"
                            ))
                    
                    # AM-004: Unidad medida
                    rules_tested["AM-004"]["tested"] = True
                    unidad_medida = med.get("unidadMedida", "")
                    if unidad_medida:
                        if len(unidad_medida) >= 1:
                            rules_tested["AM-004"]["passed"] = True
                        else:
                            errors.append(SimpleError(
                                idx, f"medicamento{med_idx}.unidadMedida",
                                f"Unidad medida debe estar presente"
                            ))
            
            if not errors:
                errors.append(SimpleError(0, "validación", "✅ Archivo JSON validado correctamente"))
            
        except json.JSONDecodeError as e:
            errors.append(SimpleError(0, "archivo", f"Error de formato JSON: {str(e)}"))
            rules_tested["GEN-002"]["tested"] = True
            rules_tested["GEN-002"]["passed"] = False
        except Exception as e:
            errors.append(SimpleError(0, "archivo", f"Error al leer archivo: {str(e)}"))
        
        # Agregar información de reglas probadas
        errors.append(SimpleError(0, "RULES_TESTED", json.dumps(rules_tested)))
        
        return errors
    
    def _validate_zip_file(self, file_path: str):
        """Validar archivo ZIP"""
        errors = []
        
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                txt_files = [f for f in file_list if f.lower().endswith('.txt')]
                
                if not txt_files:
                    errors.append(SimpleError(0, "archivo", "El ZIP no contiene archivos .txt"))
                    return errors
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    for txt_file in txt_files[:10]:
                        try:
                            zip_ref.extract(txt_file, temp_dir)
                            extracted_path = os.path.join(temp_dir, txt_file)
                            txt_errors = self._validate_text_file(extracted_path, "AC")
                            
                            for error in txt_errors:
                                error.field = f"{txt_file}:{error.field}"
                            
                            errors.extend(txt_errors)
                        except Exception as e:
                            errors.append(SimpleError(0, txt_file, f"Error al procesar: {str(e)}"))
                
                if not errors or all("✅" in e.error for e in errors if hasattr(e, 'error')):
                    errors.append(SimpleError(0, "validación", f"✅ ZIP procesado: {len(txt_files)} archivo(s)"))
        
        except zipfile.BadZipFile:
            errors.append(SimpleError(0, "archivo", "Archivo ZIP corrupto"))
        except Exception as e:
            errors.append(SimpleError(0, "archivo", f"Error: {str(e)}"))
        
        return errors
    
    def _validate_text_file(self, file_path: str, file_type: str):
        """Validar archivo de texto"""
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                
                if not lines:
                    errors.append(SimpleError(0, "archivo", "Archivo vacío"))
                    return errors
                
                for line_number, line in enumerate(lines, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Detectar separador (pipe o coma)
                    if '|' in line:
                        separator = '|'
                    elif ',' in line:
                        separator = ','
                    else:
                        errors.append(SimpleError(
                            line_number, "formato",
                            "Debe usar '|' o ',' como separador"
                        ))
                        continue
                    
                    if line_number <= 10:  # Solo primeras 10 líneas para ejemplo
                        fields = line.split(separator)
                        if len(fields) < 3:
                            errors.append(SimpleError(
                                line_number, "estructura",
                                f"Número insuficiente de campos: {len(fields)}"
                            ))
                
                if not errors:
                    errors.append(SimpleError(0, "validación", "✅ Archivo TXT validado"))
        
        except UnicodeDecodeError:
            errors.append(SimpleError(0, "archivo", "Error de codificación (debe ser UTF-8)"))
        except Exception as e:
            errors.append(SimpleError(0, "archivo", f"Error: {str(e)}"))
        
        return errors
    
    def _validate_date_format(self, date_str: str) -> bool:
        """Validar formato de fecha"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False


def main():
    """Función principal"""
    print("\n" + "="*100)
    print("🧪 PRUEBA DE REGLAS DETERMINÍSTICAS RIPS - VERSIÓN STANDALONE")
    print("="*100)
    
    # Directorio de pruebas
    test_dir = Path(__file__).parent.parent.parent.parent / "TEST"
    
    if not test_dir.exists():
        print(f"❌ Error: Directorio TEST no encontrado en {test_dir}")
        return
    
    print(f"\n📁 Directorio de pruebas: {test_dir}")
    
    # Listar archivos
    test_files = list(test_dir.glob("*"))
    print(f"📋 Archivos encontrados: {len(test_files)}\n")
    
    for f in test_files:
        print(f"   • {f.name}")
    
    validator = SimpleValidator()
    all_results = []
    
    # Probar cada archivo
    for test_file in test_files:
        file_str = str(test_file)
        
        print(f"\n{'='*100}")
        print(f"🔍 Probando: {test_file.name}")
        print(f"{'='*100}")
        
        errors = validator.validate_file(file_str, "AC")
        
        # Extraer reglas probadas
        rules_tested = {}
        errors_without_rules = []
        for error in errors:
            if error.field == "RULES_TESTED":
                rules_tested = json.loads(error.error)
            else:
                errors_without_rules.append(error)
        
        errors = errors_without_rules
        
        # Clasificar errores
        success = any("✅" in e.error for e in errors)
        error_count = len([e for e in errors if "✅" not in e.error])
        
        print(f"\n📊 RESULTADOS:")
        print(f"{'─'*100}")
        
        if success and error_count == 0:
            print(f"✅ Estado: EXITOSO - Sin errores detectados")
        elif success and error_count > 0:
            print(f"⚠️  Estado: PARCIAL - {error_count} advertencias/errores")
        else:
            print(f"❌ Estado: FALLIDO - {error_count} errores")
        
        # Mostrar reglas probadas
        if rules_tested:
            print(f"\n🔍 REGLAS DETERMINÍSTICAS PROBADAS:")
            print(f"{'─'*100}")
            
            for rule_id, rule_info in sorted(rules_tested.items()):
                if rule_info["tested"]:
                    status = "✅ PASÓ" if rule_info["passed"] else "❌ FALLÓ"
                    print(f"   {status}  | {rule_id:<10} | {rule_info['name']}")
                else:
                    print(f"   ⚪ NO PROBADA | {rule_id:<10} | {rule_info['name']}")
        
        # Mostrar errores
        if error_count > 0:
            print(f"\n❌ ERRORES ENCONTRADOS:")
            print(f"{'─'*100}")
            
            for i, error in enumerate(errors[:20], 1):
                if "✅" not in error.error:
                    print(f"   {i}. Línea {error.line:>4} | {error.field:<30} | {error.error}")
            
            if error_count > 20:
                print(f"\n   ... y {error_count - 20} errores más")
        
        all_results.append({
            "file": test_file.name,
            "success": success,
            "error_count": error_count,
            "rules_tested": rules_tested,
            "errors": errors
        })
    
    # Resumen final
    print(f"\n\n{'='*100}")
    print(f"📊 RESUMEN GENERAL DE PRUEBAS")
    print(f"{'='*100}\n")
    
    total_files = len(all_results)
    successful_files = len([r for r in all_results if r["success"] and r["error_count"] == 0])
    files_with_warnings = len([r for r in all_results if r["success"] and r["error_count"] > 0])
    failed_files = len([r for r in all_results if not r["success"]])
    
    print(f"📁 Archivos probados: {total_files}")
    print(f"   ✅ Exitosos: {successful_files}")
    print(f"   ⚠️  Con advertencias: {files_with_warnings}")
    print(f"   ❌ Fallidos: {failed_files}")
    
    # Consolidar reglas probadas
    print(f"\n📋 RESUMEN DE REGLAS DETERMINÍSTICAS:")
    print(f"{'─'*100}")
    
    all_rules = {}
    for result in all_results:
        for rule_id, rule_info in result.get("rules_tested", {}).items():
            if rule_id not in all_rules:
                all_rules[rule_id] = {
                    "name": rule_info["name"],
                    "tested": False,
                    "passed": False,
                    "times_tested": 0,
                    "times_passed": 0
                }
            
            if rule_info["tested"]:
                all_rules[rule_id]["tested"] = True
                all_rules[rule_id]["times_tested"] += 1
            
            if rule_info["passed"]:
                all_rules[rule_id]["passed"] = True
                all_rules[rule_id]["times_passed"] += 1
    
    # Agregar reglas adicionales no probadas aún (las 33 reglas completas)
    additional_rules = {
        # Control
        "CT-001": "TIPO_REGISTRO válido",
        "CT-002": "FECHA_GENERACION válida",
        "CT-003": "NUM_FACTURA presente",
        
        # Usuarios
        "US-001": "TIPO_DOCUMENTO válido",
        "US-002": "NUMERO_DOCUMENTO presente",
        "US-003": "TIPO_USUARIO válido",
        "US-004": "COD_PAIS_RESIDENCIA válido",
        "US-005": "COD_MUNICIPIO_RESIDENCIA válido",
        "US-007": "FECHA_NACIMIENTO válida",
        "US-008": "SEXO válido",
        
        # Consultas
        "AC-001": "CODIGO_PRESTADOR válido",
        "AC-002": "FECHA_INICIO_ATENCION válida",
        "AC-003": "NUM_AUTORIZACION presente",
        "AC-004": "COD_CONSULTA válido",
        "AC-005": "FINALIDAD_TECNOLOGIA_SALUD válida",
        "AC-012": "DIAGNOSTICO_PRINCIPAL_CIE válido",
        
        # Procedimientos
        "AP-001": "CODIGO_CUPS válido",
        "AP-002": "FECHA_PROCEDIMIENTO válida",
        "AP-003": "VIA_INGRESO_SERVICIO válida",
        "AP-004": "MODALIDAD_GRUPO_SERVICIO válida",
        "AP-005": "GRUPO_SERVICIOS válido",
        
        # Medicamentos
        "AM-001": "CODIGO_PRODUCTO válido",
        "AM-002": "TIPO_MEDICAMENTO válido",
        "AM-003": "CONCENTRACION presente",
        "AM-004": "UNIDAD_MEDIDA válida",
        
        # Facturación
        "AF-001": "NUM_FACTURA presente",
        "AF-002": "TIPO_FACTURA válido",
        "AF-004": "CUV presente cuando aplica",
        
        # Ajustes
        "AD-001": "TIPO_NOTA válido",
        "AD-002": "NUM_NOTA presente",
        
        # Generales
        "GEN-001": "VERSION_ANEXO_TECNICO presente",
        "GEN-002": "ESTRUCTURA_ARCHIVO válida",
        "GEN-003": "CODIFICACION_UTF8 válida",
        "FMT-006": "FECHAS coherentes y no futuras",
    }
    
    for rule_id, rule_name in additional_rules.items():
        if rule_id not in all_rules:
            all_rules[rule_id] = {
                "name": rule_name,
                "tested": False,
                "passed": False,
                "times_tested": 0,
                "times_passed": 0
            }
    
    # Mostrar reglas ordenadas
    tested_rules = [(rid, info) for rid, info in all_rules.items() if info["tested"]]
    not_tested_rules = [(rid, info) for rid, info in all_rules.items() if not info["tested"]]
    
    print(f"\n✅ Reglas probadas ({len(tested_rules)}):")
    for rule_id, info in sorted(tested_rules):
        status = "✅ PASÓ" if info["passed"] else "❌ FALLÓ"
        print(f"   {status}  | {rule_id:<10} | {info['name']:<50} | Probada {info['times_tested']} vez/veces")
    
    print(f"\n⚪ Reglas NO probadas ({len(not_tested_rules)}):")
    for rule_id, info in sorted(not_tested_rules):
        print(f"   ⚪ NO PROBADA | {rule_id:<10} | {info['name']}")
    
    # Estadísticas finales
    total_rules = len(all_rules)
    tested_count = len(tested_rules)
    passed_count = len([r for r, i in tested_rules if i["passed"]])
    
    print(f"\n📊 ESTADÍSTICAS DE REGLAS:")
    print(f"{'─'*100}")
    print(f"   • Total de reglas definidas: {total_rules}")
    print(f"   • Reglas probadas: {tested_count} ({tested_count/total_rules*100:.1f}%)")
    print(f"   • Reglas que pasaron: {passed_count} ({passed_count/total_rules*100:.1f}%)")
    print(f"   • Cobertura de pruebas: {tested_count/total_rules*100:.1f}%")
    
    # Guardar reporte
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = test_dir / f"reporte_reglas_{timestamp}.txt"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("="*100 + "\n")
        f.write("REPORTE DETALLADO DE PRUEBAS - REGLAS DETERMINÍSTICAS RIPS\n")
        f.write("="*100 + "\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Archivos probados: {total_files}\n\n")
        
        f.write("RESUMEN:\n")
        f.write(f"  • Archivos exitosos: {successful_files}\n")
        f.write(f"  • Archivos con advertencias: {files_with_warnings}\n")
        f.write(f"  • Archivos fallidos: {failed_files}\n")
        f.write(f"  • Reglas probadas: {tested_count}/{total_rules}\n")
        f.write(f"  • Cobertura: {tested_count/total_rules*100:.1f}%\n\n")
        
        f.write("REGLAS PROBADAS:\n")
        f.write("-"*100 + "\n")
        for rule_id, info in sorted(tested_rules):
            status = "PASÓ" if info["passed"] else "FALLÓ"
            f.write(f"{status:6} | {rule_id:10} | {info['name']}\n")
        
        f.write("\nREGLAS NO PROBADAS:\n")
        f.write("-"*100 + "\n")
        for rule_id, info in sorted(not_tested_rules):
            f.write(f"NO PROBADA | {rule_id:10} | {info['name']}\n")
        
        f.write("\nDETALLE POR ARCHIVO:\n")
        f.write("="*100 + "\n")
        for result in all_results:
            f.write(f"\nArchivo: {result['file']}\n")
            f.write("-"*100 + "\n")
            f.write(f"Estado: {'EXITOSO' if result['success'] and result['error_count'] == 0 else 'CON ERRORES'}\n")
            f.write(f"Errores: {result['error_count']}\n")
            
            if result['error_count'] > 0:
                f.write("\nPrimeros errores:\n")
                for i, error in enumerate(result['errors'][:10], 1):
                    if "✅" not in error.error:
                        f.write(f"  {i}. Línea {error.line} | {error.field} | {error.error}\n")
            f.write("\n")
    
    print(f"\n💾 Reporte guardado en: {report_path}")
    print(f"\n✅ Prueba completada exitosamente")
    print(f"{'='*100}\n")


if __name__ == "__main__":
    main()

