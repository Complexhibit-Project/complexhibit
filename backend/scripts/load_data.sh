#!/bin/bash
# Script Bash para cargar datos RDF en Virtuoso (Linux/MacOS)

echo "=== Cargando datos en Virtuoso ==="

# Configuración
VIRTUOSO_HOST="localhost"
VIRTUOSO_PORT="1111"
VIRTUOSO_USER="dba"
VIRTUOSO_PASSWORD=${VIRTUOSO_DBA_PASSWORD:-dba}
GRAPH_URI="https://w3id.org/OntoExhibit/Data"
DATA_FILE="/database/result.nt"

# Esperar a que Virtuoso esté listo
echo "Esperando a que Virtuoso esté disponible..."
max_attempts=30
attempt=0
connected=false

while [ $attempt -lt $max_attempts ]; do
    attempt=$((attempt+1))
    if nc -z $VIRTUOSO_HOST $VIRTUOSO_PORT; then
        connected=true
        echo "Virtuoso está disponible!"
        break
    else
        echo "Intento $attempt/$max_attempts - Esperando..."
        sleep 2
    fi
done

if [ "$connected" = false ]; then
    echo "Error: Virtuoso no está disponible después de $max_attempts intentos"
    exit 1
fi

# Cargar datos usando docker exec
echo "Cargando datos desde $DATA_FILE al grafo $GRAPH_URI..."

# Comandos ISQL para cargar datos Y optimizar índices
docker exec -i complexhibit-virtuoso isql $VIRTUOSO_PORT $VIRTUOSO_USER $VIRTUOSO_PASSWORD <<EOF
SPARQL CLEAR GRAPH <$GRAPH_URI>;
DELETE FROM DB.DBA.load_list;
ld_dir('/database', 'result.nt', '$GRAPH_URI');
SELECT * FROM DB.DBA.load_list;
rdf_loader_run();
checkpoint;
RDF_OBJ_FT_RULE_ADD(null, null, 'All');
VT_INC_INDEX_DB_DBA_RDF_OBJ();
checkpoint;
SELECT COUNT(*) FROM DB.DBA.RDF_QUAD WHERE G = iri_to_id('$GRAPH_URI');
EXIT;
EOF

echo ""
echo "=== Carga de datos completada ==="
