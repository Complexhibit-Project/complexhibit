#!/bin/bash

# Script de inicialización completa del proyecto Complexhibit
# Ejecutar con: ./init.sh

set -e

SKIP_DATA_LOAD=false

# Procesar argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-data-load)
            SKIP_DATA_LOAD=true
            shift
            ;;
        *)
            echo "Argumento desconocido: $1"
            echo "Uso: ./init.sh [--skip-data-load]"
            exit 1
            ;;
    esac
done

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Complexhibit - Inicialización del Proyecto             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 1. Verificar Docker
echo "[1/6] Verificando Docker..."
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "✓ Docker está instalado"
else
    echo "✗ Error: Docker no está instalado o no está en el PATH"
    exit 1
fi

# 2. Verificar archivos necesarios
echo "[2/6] Verificando archivos necesarios..."
required_files=("docker-compose.yml" "backend/virtuoso.ini" "backend/result.nt")

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file encontrado"
    else
        echo "✗ Error: $file no encontrado"
        exit 1
    fi
done

# 3. Verificar/Crear archivo .env
echo "[3/6] Configurando variables de entorno..."
if [ ! -f ".env" ]; then
    if [ -f ".env.template" ]; then
        cp .env.template .env
        echo "✓ Archivo .env creado desde .env.template"
        echo "  ⚠ Recuerda editar .env con tus configuraciones"
    else
        echo "✗ Error: No se encontró .env.template"
        exit 1
    fi
else
    echo "✓ Archivo .env ya existe"
fi

# 4. Detener contenedores existentes
echo "[4/6] Limpiando contenedores existentes..."
docker-compose down -v 2>/dev/null || true
echo "✓ Contenedores detenidos"

# 5. Iniciar servicios
echo "[5/6] Iniciando servicios..."
docker-compose up -d

# Esperar a que Virtuoso esté listo
echo "  Esperando a que Virtuoso esté disponible..."
max_attempts=60
attempt=0
connected=false

while [ $connected = false ] && [ $attempt -lt $max_attempts ]; do
    attempt=$((attempt + 1))
    if nc -z localhost 1111 2>/dev/null; then
        connected=true
    else
        if [ $((attempt % 5)) -eq 0 ]; then
            echo "  Intento $attempt/$max_attempts..."
        fi
        sleep 2
    fi
done

if [ $connected = true ]; then
    echo "✓ Virtuoso está disponible"
else
    echo "✗ Error: Virtuoso no respondió después de $max_attempts intentos"
    echo "  Ejecuta: docker logs complexhibit-virtuoso"
    exit 1
fi

# 6. Cargar datos
if [ $SKIP_DATA_LOAD = false ]; then
    echo "[6/6] Cargando datos en Virtuoso..."
    echo "  Esto puede tardar varios minutos..."
    
    if bash backend/scripts/load_data.sh; then
        echo "✓ Datos cargados exitosamente"
    else
        echo "✗ Error al cargar datos"
        echo "  Puedes cargar los datos manualmente más tarde con:"
        echo "  ./backend/scripts/load_data.sh"
    fi
else
    echo "[6/6] Omitiendo carga de datos (--skip-data-load)"
fi

# Resumen
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              ✓ Inicialización Completada                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Servicios disponibles:"
echo "  • API:                http://localhost:8000/api/v1/"
echo "  • Virtuoso Conductor: http://localhost:8890/conductor"
echo "  • SPARQL Endpoint:    http://localhost:8890/sparql"
echo ""
echo "Credenciales Virtuoso:"
echo "  • Usuario:   dba"
echo "  • Contraseña: la definida en .env (VIRTUOSO_DBA_PASSWORD)"
echo ""
echo "Comandos útiles:"
echo "  • Ver logs:           docker-compose logs -f"
echo "  • Detener servicios:  docker-compose down"
echo "  • Reiniciar:          docker-compose restart"
echo "  • Cargar datos:       ./backend/scripts/load_data.sh"
echo ""
