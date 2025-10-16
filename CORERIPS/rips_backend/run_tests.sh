#!/bin/bash
# Script para ejecutar tests del backend RIPS
# Uso: ./run_tests.sh [opción]

set -e  # Salir si algún comando falla

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}   RIPS Backend Test Suite${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Verificar si está en el directorio correcto
if [ ! -f "pytest.ini" ]; then
    echo -e "${RED}❌ Error: Ejecutar desde el directorio rips_backend/${NC}"
    exit 1
fi

# Verificar virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment no activado${NC}"
    echo -e "${YELLOW}   Activando venv...${NC}"
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo -e "${RED}❌ Error: venv no encontrado. Ejecutar: python -m venv venv${NC}"
        exit 1
    fi
fi

# Función para ejecutar tests
run_tests() {
    local test_type=$1
    local test_path=$2
    
    echo -e "${BLUE}🧪 Ejecutando $test_type...${NC}"
    echo ""
    
    if pytest $test_path -v; then
        echo ""
        echo -e "${GREEN}✅ $test_type completados exitosamente${NC}"
        echo ""
        return 0
    else
        echo ""
        echo -e "${RED}❌ $test_type fallaron${NC}"
        echo ""
        return 1
    fi
}

# Función para tests con cobertura
run_tests_with_coverage() {
    local test_path=$1
    
    echo -e "${BLUE}🧪 Ejecutando tests con cobertura...${NC}"
    echo ""
    
    pytest $test_path \
        --cov=validators \
        --cov=services \
        --cov=api \
        --cov=models \
        --cov-report=html \
        --cov-report=term-missing \
        -v
    
    echo ""
    echo -e "${GREEN}✅ Tests completados${NC}"
    echo -e "${BLUE}📊 Reporte de cobertura generado en: htmlcov/index.html${NC}"
    echo ""
}

# Parsear argumentos
case "${1:-all}" in
    "unit")
        run_tests "Tests Unitarios" "tests/unit/"
        ;;
    "integration")
        run_tests "Tests de Integración" "tests/integration/"
        ;;
    "validators")
        run_tests "Tests de Validadores" "tests/unit/test_*_validator.py"
        ;;
    "services")
        run_tests "Tests de Servicios" "tests/unit/test_*_service.py"
        ;;
    "api")
        run_tests "Tests de API" "tests/integration/test_api_*.py"
        ;;
    "coverage")
        run_tests_with_coverage "tests/"
        ;;
    "fast")
        echo -e "${BLUE}⚡ Ejecutando tests rápidos (solo unitarios)...${NC}"
        pytest tests/unit/ -v --tb=short
        ;;
    "verbose")
        echo -e "${BLUE}📋 Ejecutando todos los tests (modo verbose)...${NC}"
        pytest tests/ -vv -s
        ;;
    "specific")
        if [ -z "$2" ]; then
            echo -e "${RED}❌ Error: Especificar archivo de test${NC}"
            echo -e "${YELLOW}Uso: ./run_tests.sh specific tests/unit/test_file.py${NC}"
            exit 1
        fi
        run_tests "Test Específico" "$2"
        ;;
    "all")
        echo -e "${BLUE}🎯 Ejecutando TODA la suite de tests...${NC}"
        echo ""
        
        # Tests unitarios
        if run_tests "Tests Unitarios" "tests/unit/"; then
            unit_passed=true
        else
            unit_passed=false
        fi
        
        # Tests de integración
        if run_tests "Tests de Integración" "tests/integration/"; then
            integration_passed=true
        else
            integration_passed=false
        fi
        
        # Resumen
        echo -e "${BLUE}================================${NC}"
        echo -e "${BLUE}      RESUMEN DE TESTS${NC}"
        echo -e "${BLUE}================================${NC}"
        echo ""
        
        if [ "$unit_passed" = true ]; then
            echo -e "${GREEN}✅ Tests Unitarios: PASSED${NC}"
        else
            echo -e "${RED}❌ Tests Unitarios: FAILED${NC}"
        fi
        
        if [ "$integration_passed" = true ]; then
            echo -e "${GREEN}✅ Tests de Integración: PASSED${NC}"
        else
            echo -e "${RED}❌ Tests de Integración: FAILED${NC}"
        fi
        
        echo ""
        
        if [ "$unit_passed" = true ] && [ "$integration_passed" = true ]; then
            echo -e "${GREEN}🎉 ¡TODOS LOS TESTS PASARON!${NC}"
            exit 0
        else
            echo -e "${RED}⚠️  Algunos tests fallaron. Revisar errores arriba.${NC}"
            exit 1
        fi
        ;;
    "help"|"-h"|"--help")
        echo "Uso: ./run_tests.sh [opción]"
        echo ""
        echo "Opciones:"
        echo "  all           - Ejecutar todos los tests (por defecto)"
        echo "  unit          - Solo tests unitarios"
        echo "  integration   - Solo tests de integración"
        echo "  validators    - Solo tests de validadores"
        echo "  services      - Solo tests de servicios"
        echo "  api           - Solo tests de API"
        echo "  coverage      - Tests con reporte de cobertura"
        echo "  fast          - Solo tests unitarios (rápido)"
        echo "  verbose       - Tests con salida detallada"
        echo "  specific FILE - Ejecutar archivo específico"
        echo "  help          - Mostrar esta ayuda"
        echo ""
        echo "Ejemplos:"
        echo "  ./run_tests.sh"
        echo "  ./run_tests.sh unit"
        echo "  ./run_tests.sh coverage"
        echo "  ./run_tests.sh specific tests/unit/test_deterministic_validator.py"
        ;;
    *)
        echo -e "${RED}❌ Opción no reconocida: $1${NC}"
        echo -e "${YELLOW}Usar './run_tests.sh help' para ver opciones disponibles${NC}"
        exit 1
        ;;
esac

