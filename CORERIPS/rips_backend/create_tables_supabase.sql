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
-- RIPS DATA TABLES
-- ========================================

-- Table: rips_consultations (AC - Consultations)
CREATE TABLE rips_consultations (
    id SERIAL PRIMARY KEY,
    consecutive_file VARCHAR(20),
    invoice_number VARCHAR(50),
    provider_code VARCHAR(12) NOT NULL,
    identification_type VARCHAR(2),
    identification_number VARCHAR(20),
    consultation_date DATE,
    authorization_number VARCHAR(20),
    consultation_code VARCHAR(10),
    consultation_purpose VARCHAR(2),
    external_cause VARCHAR(2),
    primary_diagnosis VARCHAR(7),
    related_diagnosis_1 VARCHAR(7),
    related_diagnosis_2 VARCHAR(7),
    related_diagnosis_3 VARCHAR(7),
    primary_diagnosis_type VARCHAR(2),
    consultation_value DECIMAL(15,2),
    copayment_value DECIMAL(15,2),
    net_payment_value DECIMAL(15,2),
    file_id INTEGER REFERENCES files(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: rips_procedures (AP - Procedures)
CREATE TABLE rips_procedures (
    id SERIAL PRIMARY KEY,
    consecutive_file VARCHAR(20),
    invoice_number VARCHAR(50),
    provider_code VARCHAR(12) NOT NULL,
    identification_type VARCHAR(2),
    identification_number VARCHAR(20),
    procedure_date DATE,
    authorization_number VARCHAR(20),
    procedure_code VARCHAR(7),
    performance_scope VARCHAR(2),
    procedure_purpose VARCHAR(2),
    attending_personnel VARCHAR(2),
    primary_diagnosis VARCHAR(7),
    related_diagnosis VARCHAR(7),
    complication VARCHAR(2),
    surgical_act_performance_form VARCHAR(2),
    procedure_value DECIMAL(15,2),
    file_id INTEGER REFERENCES files(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: rips_users (US - Users)
CREATE TABLE rips_users (
    id SERIAL PRIMARY KEY,
    document_type VARCHAR(2) NOT NULL,
    document_number VARCHAR(20) NOT NULL,
    administrator_entity_code VARCHAR(6),
    user_type VARCHAR(2),
    first_surname VARCHAR(60),
    second_surname VARCHAR(60),
    first_name VARCHAR(60),
    second_name VARCHAR(60),
    age_measure VARCHAR(2),
    age VARCHAR(3),
    age_unit VARCHAR(2),
    department_code VARCHAR(2),
    municipality_code VARCHAR(3),
    residential_zone VARCHAR(1),
    file_id INTEGER REFERENCES files(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: rips_medications (AM - Medications)
CREATE TABLE rips_medications (
    id SERIAL PRIMARY KEY,
    consecutive_file VARCHAR(20),
    invoice_number VARCHAR(50),
    provider_code VARCHAR(12) NOT NULL,
    identification_type VARCHAR(2),
    identification_number VARCHAR(20),
    consultation_date DATE,
    authorization_number VARCHAR(20),
    medication_code VARCHAR(20),
    medication_type VARCHAR(2),
    generic_name VARCHAR(255),
    pharmaceutical_form VARCHAR(2),
    medication_concentration VARCHAR(255),
    unit_measure VARCHAR(2),
    unit_number VARCHAR(10),
    unit_value DECIMAL(15,2),
    total_value DECIMAL(15,2),
    file_id INTEGER REFERENCES files(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: rips_other_services (AT - Other Services)
CREATE TABLE rips_other_services (
    id SERIAL PRIMARY KEY,
    consecutive_file VARCHAR(20),
    invoice_number VARCHAR(50),
    provider_code VARCHAR(12) NOT NULL,
    identification_type VARCHAR(2),
    identification_number VARCHAR(20),
    service_date DATE,
    authorization_number VARCHAR(20),
    service_code VARCHAR(7),
    service_name VARCHAR(255),
    quantity DECIMAL(10,2),
    unit_value DECIMAL(15,2),
    total_value DECIMAL(15,2),
    file_id INTEGER REFERENCES files(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: rips_emergencies (AU - Emergencies)
CREATE TABLE rips_emergencies (
    id SERIAL PRIMARY KEY,
    consecutive_file VARCHAR(20),
    invoice_number VARCHAR(50),
    provider_code VARCHAR(12) NOT NULL,
    identification_type VARCHAR(2),
    identification_number VARCHAR(20),
    admission_date DATE,
    admission_time TIME,
    authorization_number VARCHAR(20),
    external_cause VARCHAR(2),
    admission_diagnosis VARCHAR(7),
    discharge_diagnosis VARCHAR(7),
    related_diagnosis_1 VARCHAR(7),
    related_diagnosis_2 VARCHAR(7),
    related_diagnosis_3 VARCHAR(7),
    related_diagnosis_4 VARCHAR(7),
    primary_diagnosis_type VARCHAR(2),
    service_value DECIMAL(15,2),
    copayment_value DECIMAL(15,2),
    net_value DECIMAL(15,2),
    file_id INTEGER REFERENCES files(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: rips_hospitalizations (AH - Hospitalizations)
CREATE TABLE rips_hospitalizations (
    id SERIAL PRIMARY KEY,
    consecutive_file VARCHAR(20),
    invoice_number VARCHAR(50),
    provider_code VARCHAR(12) NOT NULL,
    identification_type VARCHAR(2),
    identification_number VARCHAR(20),
    admission_route VARCHAR(2),
    admission_date DATE,
    admission_time TIME,
    authorization_number VARCHAR(20),
    external_cause VARCHAR(2),
    admission_diagnosis VARCHAR(7),
    discharge_diagnosis VARCHAR(7),
    related_diagnosis_1 VARCHAR(7),
    related_diagnosis_2 VARCHAR(7),
    related_diagnosis_3 VARCHAR(7),
    related_diagnosis_4 VARCHAR(7),
    primary_diagnosis_type VARCHAR(2),
    stay_days INTEGER,
    discharge_type VARCHAR(2),
    user_destination_condition VARCHAR(2),
    obstetric_death_cause VARCHAR(2),
    discharge_date DATE,
    discharge_time TIME,
    service_value DECIMAL(15,2),
    copayment_value DECIMAL(15,2),
    net_value DECIMAL(15,2),
    file_id INTEGER REFERENCES files(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: rips_newborns (AN - Newborns)
CREATE TABLE rips_newborns (
    id SERIAL PRIMARY KEY,
    consecutive_file VARCHAR(20),
    invoice_number VARCHAR(50),
    provider_code VARCHAR(12) NOT NULL,
    mother_identification_type VARCHAR(2),
    mother_identification_number VARCHAR(20),
    birth_date DATE,
    birth_time TIME,
    gestational_age INTEGER,
    prenatal_control VARCHAR(1),
    sex VARCHAR(1),
    birth_weight DECIMAL(5,2),
    primary_diagnosis VARCHAR(7),
    related_diagnosis_1 VARCHAR(7),
    related_diagnosis_2 VARCHAR(7),
    related_diagnosis_3 VARCHAR(7),
    basic_death_cause VARCHAR(7),
    death_date DATE,
    death_time TIME,
    file_id INTEGER REFERENCES files(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: rips_billing (AF - Billing)
CREATE TABLE rips_billing (
    id SERIAL PRIMARY KEY,
    consecutive_file VARCHAR(20),
    invoice_number VARCHAR(50) NOT NULL,
    provider_code VARCHAR(12) NOT NULL,
    invoice_issue_date DATE,
    period_start_date DATE,
    period_end_date DATE,
    administrator_entity_code VARCHAR(6),
    administrator_entity_name VARCHAR(100),
    contract_number VARCHAR(50),
    benefits_plan VARCHAR(50),
    policy_number VARCHAR(50),
    copayment DECIMAL(15,2),
    commission_value DECIMAL(15,2),
    discounts_value DECIMAL(15,2),
    net_invoice_value DECIMAL(15,2),
    file_id INTEGER REFERENCES files(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: rips_adjustments (AD - Adjustments/Notes)
CREATE TABLE rips_adjustments (
    id SERIAL PRIMARY KEY,
    consecutive_file VARCHAR(20),
    invoice_number VARCHAR(50) NOT NULL,
    provider_code VARCHAR(12) NOT NULL,
    note_type VARCHAR(2) NOT NULL,
    note_number VARCHAR(50),
    note_issue_date DATE,
    concept_code VARCHAR(2),
    concept_description VARCHAR(255),
    adjustment_value DECIMAL(15,2),
    file_id INTEGER REFERENCES files(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: rips_control (CT - Control)
CREATE TABLE rips_control (
    id SERIAL PRIMARY KEY,
    record_type VARCHAR(1) NOT NULL,
    provider_code VARCHAR(12) NOT NULL,
    generation_date DATE NOT NULL,
    rips_file VARCHAR(20),
    total_records INTEGER,
    administrator_entity_code VARCHAR(6),
    administrator_entity_name VARCHAR(100),
    contract_number VARCHAR(50),
    benefits_plan VARCHAR(50),
    technical_annex_version VARCHAR(20),
    file_id INTEGER REFERENCES files(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for RIPS tables
CREATE INDEX idx_rips_consultations_file_id ON rips_consultations(file_id);
CREATE INDEX idx_rips_consultations_provider_code ON rips_consultations(provider_code);
CREATE INDEX idx_rips_consultations_date ON rips_consultations(consultation_date);

CREATE INDEX idx_rips_procedures_file_id ON rips_procedures(file_id);
CREATE INDEX idx_rips_procedures_provider_code ON rips_procedures(provider_code);
CREATE INDEX idx_rips_procedures_date ON rips_procedures(procedure_date);

CREATE INDEX idx_rips_users_file_id ON rips_users(file_id);
CREATE INDEX idx_rips_users_document ON rips_users(document_type, document_number);

CREATE INDEX idx_rips_medications_file_id ON rips_medications(file_id);
CREATE INDEX idx_rips_medications_provider_code ON rips_medications(provider_code);

CREATE INDEX idx_rips_other_services_file_id ON rips_other_services(file_id);
CREATE INDEX idx_rips_other_services_provider_code ON rips_other_services(provider_code);

CREATE INDEX idx_rips_emergencies_file_id ON rips_emergencies(file_id);
CREATE INDEX idx_rips_emergencies_provider_code ON rips_emergencies(provider_code);

CREATE INDEX idx_rips_hospitalizations_file_id ON rips_hospitalizations(file_id);
CREATE INDEX idx_rips_hospitalizations_provider_code ON rips_hospitalizations(provider_code);

CREATE INDEX idx_rips_newborns_file_id ON rips_newborns(file_id);
CREATE INDEX idx_rips_newborns_provider_code ON rips_newborns(provider_code);

CREATE INDEX idx_rips_billing_file_id ON rips_billing(file_id);
CREATE INDEX idx_rips_billing_invoice_number ON rips_billing(invoice_number);

CREATE INDEX idx_rips_adjustments_file_id ON rips_adjustments(file_id);
CREATE INDEX idx_rips_adjustments_invoice_number ON rips_adjustments(invoice_number);

CREATE INDEX idx_rips_control_file_id ON rips_control(file_id);
CREATE INDEX idx_rips_control_provider_code ON rips_control(provider_code);

-- ========================================
-- OFFICIAL CATALOG TABLES
-- ========================================

-- Table: cups_catalog (Unique Classification of Health Procedures - CUPS)
CREATE TABLE IF NOT EXISTS cups_catalog (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    section VARCHAR(100),
    status VARCHAR(20) DEFAULT 'ACTIVE',
    enabled BOOLEAN DEFAULT TRUE,
    effective_date DATE,
    expiration_date DATE,
    last_updated TIMESTAMP WITH TIME ZONE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: icd10_catalog (International Classification of Diseases - ICD-10)
CREATE TABLE IF NOT EXISTS icd10_catalog (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    category VARCHAR(10),
    is_category BOOLEAN DEFAULT FALSE,
    enabled BOOLEAN DEFAULT TRUE,
    last_updated TIMESTAMP WITH TIME ZONE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: dane_municipalities
CREATE TABLE IF NOT EXISTS dane_municipalities (
    id SERIAL PRIMARY KEY,
    municipality_code VARCHAR(5) UNIQUE NOT NULL,
    municipality_name VARCHAR(100),
    department_code VARCHAR(2) NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: dane_departments
CREATE TABLE IF NOT EXISTS dane_departments (
    id SERIAL PRIMARY KEY,
    department_code VARCHAR(2) UNIQUE NOT NULL,
    department_name VARCHAR(100),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for fast catalog searches
CREATE INDEX IF NOT EXISTS idx_cups_catalog_code ON cups_catalog(code);
CREATE INDEX IF NOT EXISTS idx_cups_catalog_status ON cups_catalog(status);
CREATE INDEX IF NOT EXISTS idx_cups_catalog_enabled ON cups_catalog(enabled);
CREATE INDEX IF NOT EXISTS idx_cups_catalog_section ON cups_catalog(section);
CREATE INDEX IF NOT EXISTS idx_icd10_catalog_code ON icd10_catalog(code);
CREATE INDEX IF NOT EXISTS idx_icd10_catalog_category ON icd10_catalog(category);
CREATE INDEX IF NOT EXISTS idx_icd10_catalog_enabled ON icd10_catalog(enabled);
CREATE INDEX IF NOT EXISTS idx_dane_municipalities_code ON dane_municipalities(municipality_code);
CREATE INDEX IF NOT EXISTS idx_dane_municipalities_department ON dane_municipalities(department_code);
CREATE INDEX IF NOT EXISTS idx_dane_departments_code ON dane_departments(department_code);

-- Triggers for updated_at in catalog tables
CREATE TRIGGER update_cups_catalog_updated_at 
    BEFORE UPDATE ON cups_catalog 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_icd10_catalog_updated_at 
    BEFORE UPDATE ON icd10_catalog 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_dane_municipalities_updated_at 
    BEFORE UPDATE ON dane_municipalities 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_dane_departments_updated_at 
    BEFORE UPDATE ON dane_departments 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Verify that all tables were created correctly
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE schemaname = 'public' 
    AND tablename IN (
        'users', 'files', 'validations',
        'rips_consultations', 'rips_procedures', 'rips_users',
        'rips_medications', 'rips_other_services', 'rips_emergencies',
        'rips_hospitalizations', 'rips_newborns', 'rips_billing',
        'rips_adjustments', 'rips_control',
        'cups_catalog', 'icd10_catalog', 
        'dane_municipalities', 'dane_departments'
    )
ORDER BY tablename;

