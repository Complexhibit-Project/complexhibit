# ETL Pipeline - OntoExhibit

Pipeline para transformar datos relacionales de exposiciones (pathwise.db) a RDF siguiendo la ontología OntoExhibit.

## Estructura

```
etl-pipeline/
├── config/
│   └── settings.py           # Configuración centralizada
├── ontology/
│   └── ontoExhibit.rdf       # Ontología OWL 2 (mantenida en Protégé)
├── sql/
│   └── normalize_schema.sql  # Script SQL de normalización + índices
├── src/
│   ├── pipeline.py           # Orquestador principal
│   ├── loaders/
│   │   └── virtuoso_loader.py  # Carga a Virtuoso
│   ├── normalization/
│   │   ├── normalize_db.py     # Normalización Python
│   │   └── normalize_places.py # Normalización de lugares
│   ├── transformation/
│   │   ├── transform_data.py   # Transformación RDF principal
│   │   ├── rdf_builder.py      # Grafo RDF compartido + helpers
│   │   └── utils.py            # Utilidades (fechas, hash, etc.)
│   └── utils/
│       └── commons.py          # Utilidades comunes
├── tools/
│   └── find_similar_exhibitions.py  # Detectar duplicados
├── tests/
│   └── test_transformers.py    # Tests unitarios
├── output/                     # Directorio para result.nt
└── requirements.txt
```

## Uso

### Ejecutar el pipeline completo

```bash
cd etl-pipeline
python -m src.pipeline
```

El pipeline:
1. Descarga `pathwise.db` actualizado
2. Ejecuta normalización SQL y Python
3. Transforma a RDF (genera `result.nt`)
4. Copia `result.nt` a `/backend`

### Cargar datos en Virtuoso

```bash
python -m src.loaders.virtuoso_loader output/result.nt
```

O reiniciar Virtuoso (el docker-compose monta `result.nt`):

```bash
docker-compose restart virtuoso
```

## Configuración

Variables de entorno (`.env`):

```env
URI_ONTOLOGIA=https://w3id.org/OntoExhibit#
VIRTUOSO_URL=http://localhost:8890/sparql
VIRTUOSO_GRAPH_URI=http://localhost:8890/DAV/home/dba/rdf_sink
VIRTUOSO_DBA_PASSWORD=dba
```

## Ontología

La ontología `ontoExhibit.rdf` se mantiene manualmente en Protégé. No se genera desde código.

## Tests

```bash
cd etl-pipeline
python -m pytest tests/ -v
```
