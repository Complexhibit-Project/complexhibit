# Configuración y Carga de Datos en Virtuoso

Este documento explica cómo configurar Virtuoso y cargar automáticamente los datos del grafo de conocimiento OntoExhibit.

## 📋 Resumen

- **Usuario Virtuoso**: `dba`
- **Contraseña por defecto**: `dba` (configurable con `VIRTUOSO_DBA_PASSWORD`)
- **Interfaz web (Conductor)**: http://localhost:8890/conductor
- **SPARQL Endpoint**: http://localhost:8890/sparql
- **Puerto SQL**: 1111

## 🔧 Configuración de Virtuoso

### Parámetros Optimizados

El archivo `virtuoso.ini` incluye las siguientes optimizaciones para manejar grandes volúmenes de datos:

#### Memoria
- **MaxMemPoolSize**: 24 GB (24000000000 bytes)
- **NumberOfBuffers**: 2,720,000 (configurado para sistemas con 32 GB RAM)
- **MaxDirtyBuffers**: 2,000,000
- **MaxQueryMem**: 2 GB

#### Threads y Concurrencia
- **ServerThreads**: 16 (vs 10 por defecto)
- **AsyncQueueMaxThreads**: 16 (vs 10 por defecto)
- **ThreadsPerQuery**: 8

#### SPARQL
- **ResultSetMaxRows**: 1,000,000 (vs 10,000 por defecto)
- **MaxQueryExecutionTime**: 60 segundos
- **MaxQueryCostEstimationTime**: 400 segundos

### Directorios Permitidos
```ini
DirsAllowed = ., /usr/share/virtuoso-opensource-7/vad, /database
```

## 🚀 Inicio Rápido

### 1. Iniciar los servicios

```bash
docker-compose up -d
```

Esto iniciará:
- Virtuoso con la configuración optimizada
- La API de Complexhibit

### 2. Cargar los datos

#### En Linux/Mac:
```bash
chmod +x backend/scripts/load_data.sh
./backend/scripts/load_data.sh
```

#### En Windows (PowerShell):
```powershell
.\backend\scripts\load_data.ps1
```

### 3. Verificar la carga

Accede a http://localhost:8890/conductor y ejecuta esta consulta SPARQL:

```sparql
SELECT COUNT(*) as ?total
FROM <http://localhost:8890/OntoExhibit>
WHERE {
  ?s ?p ?o
}
```

## 📊 Datos Cargados

El archivo `result.nt` contiene:
- **Formato**: N-Triples
- **Tamaño**: ~811 MB
- **Tripletas**: 2,793,042
- **Grafo**: `http://localhost:8890/OntoExhibit`

## 🔄 Proceso de Carga Automática

Los scripts de carga realizan las siguientes operaciones:

1. **Espera** a que Virtuoso esté disponible
2. **Limpia** el grafo existente (si existe)
3. **Registra** el archivo `result.nt` para carga
4. **Ejecuta** el cargador RDF (`rdf_loader_run()`)
5. **Hace checkpoint** para persistir los datos
6. **Verifica** el número de tripletas cargadas

## 🛠️ Carga Manual (Alternativa)

Si prefieres cargar los datos manualmente vía interfaz web:

### Opción 1: Via Conductor

1. Accede a http://localhost:8890/conductor
2. Login con `dba` / `dba`
3. Ve a **Linked Data** → **Quad Store Upload**
4. Selecciona el archivo `result.nt`
5. Especifica el grafo: `http://localhost:8890/OntoExhibit`
6. Click en **Upload**

### Opción 2: Via isql

```bash
docker exec -it complexhibit-virtuoso isql 1111 dba dba
```

Luego ejecuta:

```sql
SPARQL CLEAR GRAPH <http://localhost:8890/OntoExhibit>;
DELETE FROM DB.DBA.load_list;
ld_dir('/database', 'result.nt', 'http://localhost:8890/OntoExhibit');
rdf_loader_run();
checkpoint;
```

## 🔍 Consultas de Ejemplo

### Contar todas las tripletas
```sparql
SELECT COUNT(*) as ?total
FROM <http://localhost:8890/OntoExhibit>
WHERE {
  ?s ?p ?o
}
```

### Listar tipos de entidades
```sparql
SELECT DISTINCT ?type (COUNT(?s) as ?count)
FROM <http://localhost:8890/OntoExhibit>
WHERE {
  ?s a ?type
}
GROUP BY ?type
ORDER BY DESC(?count)
LIMIT 20
```

### Buscar exposiciones
```sparql
PREFIX oe: <https://w3id.org/OntoExhibit#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?exhibition ?label
FROM <http://localhost:8890/OntoExhibit>
WHERE {
  ?exhibition a oe:Exhibition ;
              rdfs:label ?label .
}
LIMIT 10
```

## 🐛 Solución de Problemas

### Virtuoso no inicia
```bash
# Ver logs
docker logs complexhibit-virtuoso

# Reiniciar el contenedor
docker-compose restart virtuoso
```

### Los datos no se cargan
```bash
# Verificar que el archivo existe
docker exec complexhibit-virtuoso ls -lh /database/result.nt

# Verificar la lista de carga
docker exec -it complexhibit-virtuoso isql 1111 dba dba exec="SELECT * FROM DB.DBA.load_list;"
```

### Memoria insuficiente
Si el sistema tiene menos de 32 GB de RAM, editar `virtuoso.ini`:

Para 16 GB:
```ini
NumberOfBuffers = 1360000
MaxDirtyBuffers = 1000000
MaxMemPoolSize = 12000000000
```

Para 8 GB:
```ini
NumberOfBuffers = 680000
MaxDirtyBuffers = 500000
MaxMemPoolSize = 6000000000
```

## 📝 Variables de Entorno

Crear un archivo `.env` con:

```env
# Virtuoso
VIRTUOSO_DBA_PASSWORD=contraseña_segura

# API
URI_ONTOLOGIA=https://w3id.org/OntoExhibit
JWT_SECRET=secret_key_aleatorio
USER_SERVICE_URL=http://user-service:8001
```

## 🔐 Seguridad

Para producción:
1. Cambiar la contraseña de `dba`
2. Restringir el acceso a los puertos 1111 y 8890
3. Usar HTTPS para el SPARQL endpoint
4. Configurar autenticación en el Conductor

## 📚 Referencias

- [Virtuoso Documentation](http://docs.openlinksw.com/virtuoso/)
- [RDF Bulk Loading](http://vos.openlinksw.com/owiki/wiki/VOS/VirtBulkRDFLoader)
- [SPARQL Query Language](https://www.w3.org/TR/sparql11-query/)
