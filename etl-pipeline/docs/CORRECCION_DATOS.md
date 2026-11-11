# Procedimiento de corrección de los datos de origen

Este documento describe cómo se corrigen y normalizan los datos de origen (Expofinder)
antes de transformarlos al grafo de conocimiento Complexhibit (ontología OntoExhibit).

## Principio de trabajo

Los datos de origen **no se editan a mano en el origen**. La base de datos de origen
(`pathwise.db`, SQLite, publicada por iArtHis Lab) se descarga en cada ejecución y **todas las
correcciones se reaplican mediante scripts versionados**. Así el proceso es reproducible:
con la misma versión de `pathwise.db` y del código se obtiene el mismo grafo.

```
pathwise.db (origen)
   │  1. descarga                          src/pipeline.py
   ▼
copia local de pathwise.db
   │  2. normalización SQL + Python        sql/normalize_schema.sql
   │                                       src/normalization/normalize_db.py
   │  3. normalización de lugares          src/normalization/normalize_places.py
   ▼
pathwise.db corregida (copia local)
   │  4. transformación a RDF              src/transformation/transform_data.py
   ▼
result.nt (N-Triples)  →  carga en Virtuoso (backend/scripts/load_data.sh)
```

Las correcciones se aplican sobre la **copia local descargada**, nunca sobre el origen.

## Qué corrige cada paso

### 1. `sql/normalize_schema.sql` — esquema y correcciones puntuales
- Reconstruye las tablas normalizadas (`DROP TABLE IF EXISTS` + `CREATE TABLE` + `INSERT … SELECT`)
  a partir de las tablas originales del origen (EXPOSICION, PERSONA, INSTITUCION, OBRA DE ARTE…).
- Contiene al principio las **correcciones manuales puntuales** detectadas en la revisión de los
  datos, como `UPDATE tax SET value = … WHERE value LIKE …` (unificación de valores de taxonomía)
  o `UPDATE REL SET RID = … WHERE ID = …` (relaciones erróneas concretas).
- Añade los índices necesarios para las consultas posteriores.
- Las sentencias se ejecutan una a una; si alguna falla (p. ej. una tabla que aún no existe) se
  informa y se continúa (`Command skipped`).

### 2. `src/normalization/normalize_db.py` — normalización en Python
Se ejecuta tras el SQL y trabaja sobre la misma base:
- `insert_propietarios_personas_obras` / `insert_propietarios_instituciones_obras`:
  completan las relaciones de propiedad de las obras.
- `insert_personas_maximos_responsables` / `update_personas_maximos_responsables`:
  crean y actualizan las personas que figuran como máximo responsable de instituciones.
- `poner_a_null_maximos_responsables_erroneos`: pone a `NULL` el campo «máximo responsable»
  de las instituciones cuando contiene datos que no son un nombre (correos, URL, teléfonos
  como `+34…` o texto entre paréntesis).
- (`insert_ediciones` está desactivada en el código.)

### 3. `src/normalization/normalize_places.py` — lugares
Normaliza los topónimos de PERSONA, EXPOSICION, INSTITUCION, EMPRESA y OBRA DE ARTE:
capitalización, normalización Unicode y unificación de variantes y abreviaturas
(p. ej. `Usa`, `EEUU`, `United States` → `Estados Unidos`; `Uk` → `Reino Unido`; `New York` → `Nueva York`).
Solo actualiza los registros cuyo valor cambia e informa del número de registros modificados.

### 4. Detección de duplicados (apoyo a la revisión manual)
`tools/find_similar_exhibitions.py` compara los nombres de exposiciones por similitud
(Levenshtein, umbral 0,85) y genera un CSV con los posibles duplicados para su revisión.
No modifica los datos: la decisión de fusionar o corregir se traslada después a
`sql/normalize_schema.sql` como corrección puntual.

## Cómo añadir o cambiar una corrección
1. Identificar el error (consulta SQL sobre `pathwise.db` o revisión en la web).
2. Si es un caso puntual, añadir un `UPDATE` comentado en `sql/normalize_schema.sql`.
   Si es un patrón general (formato, abreviaturas), implementarlo en `normalize_db.py`
   o `normalize_places.py`.
3. Ejecutar el pipeline completo y comprobar que el cambio aparece en el grafo.
4. Registrar el cambio en el control de versiones con un mensaje descriptivo.

## Ejecución

```bash
cd etl-pipeline
pip install -r requirements.txt
python -m src.pipeline          # descarga, normaliza, transforma y genera result.nt
python -m pytest tests/ -v      # pruebas de las transformaciones
```

La carga del resultado en Virtuoso se describe en `README.md` y en `backend/scripts/load_data.sh`.

## Historial
Las versiones iniciales de estos scripts se mantuvieron en repositorios previos
(`transformAndLoadDataToExhibitum`, ramas `master` y `version_definitiva`). Este repositorio los
unifica y refactoriza: los scripts de normalización y la transformación a RDF viven ahora en
`etl-pipeline/`.
