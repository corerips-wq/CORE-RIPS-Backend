-- Script SQL para crear tablas RIPS en Supabase
-- Ejecutar en: Supabase Dashboard → SQL Editor

-- Crear tipos ENUM
CREATE TYPE user_role AS ENUM ('admin', 'validator', 'auditor');
CREATE TYPE file_status AS ENUM ('uploaded', 'processing', 'validated', 'error');
CREATE TYPE validation_status AS ENUM ('passed', 'failed', 'warning');

-- Tabla: users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role user_role DEFAULT 'validator' NOT NULL,
    is_active VARCHAR(10) DEFAULT 'true' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla: files
CREATE TABLE files (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    status file_status DEFAULT 'uploaded' NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla: validations
CREATE TABLE validations (
    id SERIAL PRIMARY KEY,
    file_id INTEGER NOT NULL REFERENCES files(id),
    line_number INTEGER NOT NULL,
    field_name VARCHAR(100) NOT NULL,
    rule_name VARCHAR(100) NOT NULL,
    error_message TEXT NOT NULL,
    status validation_status NOT NULL,
    validator_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Crear índices para mejor rendimiento
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_files_user_id ON files(user_id);
CREATE INDEX idx_files_status ON files(status);
CREATE INDEX idx_validations_file_id ON validations(file_id);
CREATE INDEX idx_validations_status ON validations(status);

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para actualizar updated_at
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_files_updated_at 
    BEFORE UPDATE ON files 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insertar usuario administrador por defecto
-- Nota: La contraseña 'admin123' debe ser hasheada en tu aplicación
INSERT INTO users (username, email, hashed_password, role) 
VALUES (
    'admin', 
    'admin@rips.com', 
    '$2b$12$placeholder_hash_for_admin123', -- Cambiar por hash real
    'admin'
) ON CONFLICT (username) DO NOTHING;

-- Insertar usuarios de prueba
INSERT INTO users (username, email, hashed_password, role) VALUES
    ('validator1', 'validator1@rips.com', '$2b$12$placeholder_hash_for_validator123', 'validator'),
    ('auditor1', 'auditor1@rips.com', '$2b$12$placeholder_hash_for_auditor123', 'auditor')
ON CONFLICT (username) DO NOTHING;

-- Verificar que las tablas se crearon correctamente
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE schemaname = 'public' 
    AND tablename IN ('users', 'files', 'validations')
ORDER BY tablename;

-- ========================================
-- TABLAS PARA DATOS RIPS
-- ========================================

-- Tabla: rips_consultas (AC - Consultas)
CREATE TABLE rips_consultas (
    id SERIAL PRIMARY KEY,
    archivo_consecutivo VARCHAR(20),
    numero_factura VARCHAR(50),
    codigo_prestador VARCHAR(12) NOT NULL,
    tipo_identificacion VARCHAR(2),
    numero_identificacion VARCHAR(20),
    fecha_consulta DATE,
    numero_autorizacion VARCHAR(20),
    codigo_consulta VARCHAR(10),
    finalidad_consulta VARCHAR(2),
    causa_externa VARCHAR(2),
    diagnostico_principal VARCHAR(7),
    diagnostico_relacionado_1 VARCHAR(7),
    diagnostico_relacionado_2 VARCHAR(7),
    diagnostico_relacionado_3 VARCHAR(7),
    tipo_diagnostico_principal VARCHAR(2),
    valor_consulta DECIMAL(15,2),
    valor_cuota_moderadora DECIMAL(15,2),
    valor_neto_pagar DECIMAL(15,2),
    file_id INTEGER REFERENCES files(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla: rips_procedimientos (AP - Procedimientos)
CREATE TABLE rips_procedimientos (
    id SERIAL PRIMARY KEY,
    archivo_consecutivo VARCHAR(20),
    numero_factura VARCHAR(50),
    codigo_prestador VARCHAR(12) NOT NULL,
    tipo_identificacion VARCHAR(2),
    numero_identificacion VARCHAR(20),
    fecha_procedimiento DATE,
    numero_autorizacion VARCHAR(20),
    codigo_procedimiento VARCHAR(7),
    ambito_realizacion VARCHAR(2),
    finalidad_procedimiento VARCHAR(2),
    personal_que_atendio VARCHAR(2),
    diagnostico_principal VARCHAR(7),
    diagnostico_relacionado VARCHAR(7),
    complicacion VARCHAR(2),
    forma_realizacion_acto_quirurgico VARCHAR(2),
    valor_procedimiento DECIMAL(15,2),
    file_id INTEGER REFERENCES files(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla: rips_usuarios (US - Usuarios)
CREATE TABLE rips_usuarios (
    id SERIAL PRIMARY KEY,
    tipo_documento VARCHAR(2) NOT NULL,
    numero_documento VARCHAR(20) NOT NULL,
    codigo_entidad_administradora VARCHAR(6),
    tipo_usuario VARCHAR(2),
    apellido_primero VARCHAR(60),
    apellido_segundo VARCHAR(60),
    nombre_primero VARCHAR(60),
    nombre_segundo VARCHAR(60),
    edad_medida VARCHAR(2),
    edad VARCHAR(3),
    unidad_medida_edad VARCHAR(2),
    codigo_departamento VARCHAR(2),
    codigo_municipio VARCHAR(3),
    zona_residencial VARCHAR(1),
    file_id INTEGER REFERENCES files(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla: rips_medicamentos (AM - Medicamentos)
CREATE TABLE rips_medicamentos (
    id SERIAL PRIMARY KEY,
    archivo_consecutivo VARCHAR(20),
    numero_factura VARCHAR(50),
    codigo_prestador VARCHAR(12) NOT NULL,
    tipo_identificacion VARCHAR(2),
    numero_identificacion VARCHAR(20),
    fecha_consulta DATE,
    numero_autorizacion VARCHAR(20),
    codigo_medicamento VARCHAR(20),
    tipo_medicamento VARCHAR(2),
    nombre_generico VARCHAR(255),
    forma_farmaceutica VARCHAR(2),
    concentracion_medicamento VARCHAR(255),
    unidad_medida VARCHAR(2),
    numero_unidad VARCHAR(10),
    valor_unitario DECIMAL(15,2),
    valor_total DECIMAL(15,2),
    file_id INTEGER REFERENCES files(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla: rips_otros_servicios (AT - Otros Servicios)
CREATE TABLE rips_otros_servicios (
    id SERIAL PRIMARY KEY,
    archivo_consecutivo VARCHAR(20),
    numero_factura VARCHAR(50),
    codigo_prestador VARCHAR(12) NOT NULL,
    tipo_identificacion VARCHAR(2),
    numero_identificacion VARCHAR(20),
    fecha_servicio DATE,
    numero_autorizacion VARCHAR(20),
    codigo_servicio VARCHAR(7),
    nombre_servicio VARCHAR(255),
    cantidad DECIMAL(10,2),
    valor_unitario DECIMAL(15,2),
    valor_total DECIMAL(15,2),
    file_id INTEGER REFERENCES files(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla: rips_urgencias (AU - Urgencias)
CREATE TABLE rips_urgencias (
    id SERIAL PRIMARY KEY,
    archivo_consecutivo VARCHAR(20),
    numero_factura VARCHAR(50),
    codigo_prestador VARCHAR(12) NOT NULL,
    tipo_identificacion VARCHAR(2),
    numero_identificacion VARCHAR(20),
    fecha_ingreso DATE,
    hora_ingreso TIME,
    numero_autorizacion VARCHAR(20),
    causa_externa VARCHAR(2),
    diagnostico_ingreso VARCHAR(7),
    diagnostico_egreso VARCHAR(7),
    diagnostico_relacionado_1 VARCHAR(7),
    diagnostico_relacionado_2 VARCHAR(7),
    diagnostico_relacionado_3 VARCHAR(7),
    diagnostico_relacionado_4 VARCHAR(7),
    tipo_diagnostico_principal VARCHAR(2),
    valor_servicio DECIMAL(15,2),
    valor_cuota_moderadora DECIMAL(15,2),
    valor_neto DECIMAL(15,2),
    file_id INTEGER REFERENCES files(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla: rips_hospitalizacion (AH - Hospitalización)
CREATE TABLE rips_hospitalizacion (
    id SERIAL PRIMARY KEY,
    archivo_consecutivo VARCHAR(20),
    numero_factura VARCHAR(50),
    codigo_prestador VARCHAR(12) NOT NULL,
    tipo_identificacion VARCHAR(2),
    numero_identificacion VARCHAR(20),
    via_ingreso VARCHAR(2),
    fecha_ingreso DATE,
    hora_ingreso TIME,
    numero_autorizacion VARCHAR(20),
    causa_externa VARCHAR(2),
    diagnostico_ingreso VARCHAR(7),
    diagnostico_egreso VARCHAR(7),
    diagnostico_relacionado_1 VARCHAR(7),
    diagnostico_relacionado_2 VARCHAR(7),
    diagnostico_relacionado_3 VARCHAR(7),
    diagnostico_relacionado_4 VARCHAR(7),
    tipo_diagnostico_principal VARCHAR(2),
    dias_estancia INTEGER,
    tipo_egreso VARCHAR(2),
    condicion_destino_usuario VARCHAR(2),
    causa_muerte_obstetrica VARCHAR(2),
    fecha_egreso DATE,
    hora_egreso TIME,
    valor_servicio DECIMAL(15,2),
    valor_cuota_moderadora DECIMAL(15,2),
    valor_neto DECIMAL(15,2),
    file_id INTEGER REFERENCES files(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla: rips_recien_nacidos (AN - Recién Nacidos)
CREATE TABLE rips_recien_nacidos (
    id SERIAL PRIMARY KEY,
    archivo_consecutivo VARCHAR(20),
    numero_factura VARCHAR(50),
    codigo_prestador VARCHAR(12) NOT NULL,
    tipo_identificacion_madre VARCHAR(2),
    numero_identificacion_madre VARCHAR(20),
    fecha_nacimiento DATE,
    hora_nacimiento TIME,
    edad_gestacional INTEGER,
    control_prenatal VARCHAR(1),
    sexo VARCHAR(1),
    peso_nacimiento DECIMAL(5,2),
    diagnostico_principal VARCHAR(7),
    diagnostico_relacionado_1 VARCHAR(7),
    diagnostico_relacionado_2 VARCHAR(7),
    diagnostico_relacionado_3 VARCHAR(7),
    causa_basica_muerte VARCHAR(7),
    fecha_muerte DATE,
    hora_muerte TIME,
    file_id INTEGER REFERENCES files(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla: rips_facturacion (AF - Facturación)
CREATE TABLE rips_facturacion (
    id SERIAL PRIMARY KEY,
    archivo_consecutivo VARCHAR(20),
    numero_factura VARCHAR(50) NOT NULL,
    codigo_prestador VARCHAR(12) NOT NULL,
    fecha_expedicion_factura DATE,
    fecha_inicio_periodo DATE,
    fecha_fin_periodo DATE,
    codigo_entidad_administradora VARCHAR(6),
    nombre_entidad_administradora VARCHAR(100),
    numero_contrato VARCHAR(50),
    plan_beneficios VARCHAR(50),
    numero_poliza VARCHAR(50),
    copago DECIMAL(15,2),
    valor_comision DECIMAL(15,2),
    valor_descuentos DECIMAL(15,2),
    valor_neto_factura DECIMAL(15,2),
    file_id INTEGER REFERENCES files(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla: rips_ajustes (AD - Ajustes/Notas)
CREATE TABLE rips_ajustes (
    id SERIAL PRIMARY KEY,
    archivo_consecutivo VARCHAR(20),
    numero_factura VARCHAR(50) NOT NULL,
    codigo_prestador VARCHAR(12) NOT NULL,
    tipo_nota VARCHAR(2) NOT NULL,
    numero_nota VARCHAR(50),
    fecha_expedicion_nota DATE,
    codigo_concepto VARCHAR(2),
    descripcion_concepto VARCHAR(255),
    valor_ajuste DECIMAL(15,2),
    file_id INTEGER REFERENCES files(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla: rips_control (CT - Control)
CREATE TABLE rips_control (
    id SERIAL PRIMARY KEY,
    tipo_registro VARCHAR(1) NOT NULL,
    codigo_prestador VARCHAR(12) NOT NULL,
    fecha_generacion DATE NOT NULL,
    archivo_rips VARCHAR(20),
    total_registros INTEGER,
    codigo_entidad_administradora VARCHAR(6),
    nombre_entidad_administradora VARCHAR(100),
    numero_contrato VARCHAR(50),
    plan_beneficios VARCHAR(50),
    version_anexo_tecnico VARCHAR(20),
    file_id INTEGER REFERENCES files(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Crear índices para las tablas RIPS
CREATE INDEX idx_rips_consultas_file_id ON rips_consultas(file_id);
CREATE INDEX idx_rips_consultas_codigo_prestador ON rips_consultas(codigo_prestador);
CREATE INDEX idx_rips_consultas_fecha ON rips_consultas(fecha_consulta);

CREATE INDEX idx_rips_procedimientos_file_id ON rips_procedimientos(file_id);
CREATE INDEX idx_rips_procedimientos_codigo_prestador ON rips_procedimientos(codigo_prestador);
CREATE INDEX idx_rips_procedimientos_fecha ON rips_procedimientos(fecha_procedimiento);

CREATE INDEX idx_rips_usuarios_file_id ON rips_usuarios(file_id);
CREATE INDEX idx_rips_usuarios_documento ON rips_usuarios(tipo_documento, numero_documento);

CREATE INDEX idx_rips_medicamentos_file_id ON rips_medicamentos(file_id);
CREATE INDEX idx_rips_medicamentos_codigo_prestador ON rips_medicamentos(codigo_prestador);

CREATE INDEX idx_rips_otros_servicios_file_id ON rips_otros_servicios(file_id);
CREATE INDEX idx_rips_otros_servicios_codigo_prestador ON rips_otros_servicios(codigo_prestador);

CREATE INDEX idx_rips_urgencias_file_id ON rips_urgencias(file_id);
CREATE INDEX idx_rips_urgencias_codigo_prestador ON rips_urgencias(codigo_prestador);

CREATE INDEX idx_rips_hospitalizacion_file_id ON rips_hospitalizacion(file_id);
CREATE INDEX idx_rips_hospitalizacion_codigo_prestador ON rips_hospitalizacion(codigo_prestador);

CREATE INDEX idx_rips_recien_nacidos_file_id ON rips_recien_nacidos(file_id);
CREATE INDEX idx_rips_recien_nacidos_codigo_prestador ON rips_recien_nacidos(codigo_prestador);

CREATE INDEX idx_rips_facturacion_file_id ON rips_facturacion(file_id);
CREATE INDEX idx_rips_facturacion_numero_factura ON rips_facturacion(numero_factura);

CREATE INDEX idx_rips_ajustes_file_id ON rips_ajustes(file_id);
CREATE INDEX idx_rips_ajustes_numero_factura ON rips_ajustes(numero_factura);

CREATE INDEX idx_rips_control_file_id ON rips_control(file_id);
CREATE INDEX idx_rips_control_codigo_prestador ON rips_control(codigo_prestador);

-- Verificar que todas las tablas se crearon correctamente
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE schemaname = 'public' 
    AND tablename IN (
        'users', 'files', 'validations',
        'rips_consultas', 'rips_procedimientos', 'rips_usuarios',
        'rips_medicamentos', 'rips_otros_servicios', 'rips_urgencias',
        'rips_hospitalizacion', 'rips_recien_nacidos', 'rips_facturacion',
        'rips_ajustes', 'rips_control'
    )
ORDER BY tablename;

