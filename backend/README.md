# Complexhibit API

API REST para consultar el grafo de conocimiento OntoExhibit usando SPARQL sobre Virtuoso.

## 🚀 Inicio Rápido

### Requisitos Previos

- Docker y Docker Compose
- 32 GB de RAM recomendados (mínimo 8 GB)
- ~1 GB de espacio en disco para los datos

### Instalación Automática

El script de inicialización:
1. ✓ Verifica que Docker esté instalado
2. ✓ Crea el archivo `.env` si no existe
3. ✓ Inicia los servicios (Virtuoso + API)
4. ✓ Espera a que Virtuoso esté listo
5. ✓ Carga automáticamente los 2.7M de tripletas

### Instalación Manual

1. **Crear archivo de configuración**
   ```bash
   cp env.example .env
   # Editar .env con las configuraciones necesarias
   ```

2. **Iniciar servicios**
   Desde la raíz del monorepo (`../`):
   ```bash
   docker-compose up -d
   ```

3. **Cargar datos** (Windows)
   ```powershell
   .\scripts\load_data.ps1
   ```
   
   O (Linux/Mac)
   ```bash
   ./scripts/load_data.sh
   ```

## 📊 Servicios

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **API** | http://localhost:8000/api/v1/ | API REST de Complexhibit |
| **Virtuoso Conductor** | http://localhost:8890/conductor | Interfaz web de administración |
| **SPARQL Endpoint** | http://localhost:8890/sparql | Endpoint SPARQL público |

## 🔐 Credenciales

### Virtuoso
- **Usuario**: `dba`
- **Contraseña**: `dba` (por defecto, configurable en `.env`)

### Administrador de la Aplicación
- **Email**: `admin@example.com` (configurable con `ADMIN_EMAIL`)
- **Contraseña**: `admin123` (¡CAMBIAR EN PRODUCCIÓN! configurable con `ADMIN_PASSWORD`)

## 🛡️ Seguridad y Autenticación

Los endpoints de **escritura** (creación de recursos) están protegidos y requieren autenticación JWT.

1. **Obtener Token**:
   `POST /api/v1/auth/login` con email y contraseña.
2. **Usar Token**:
   Enviar header `Authorization: Bearer <token>` en las peticiones `POST` a `/create_*`.

Los endpoints de **lectura** (consultas, contadores) son públicos.


## 📁 Estructura del Proyecto

```
complexhibit-api/
├── app/                    # Código de la API FastAPI
│   ├── models/            # Modelos Pydantic
│   ├── routers/           # Endpoints de la API
│   ├── services/          # Lógica de negocio y queries SPARQL
│   └── utils/             # Utilidades (cursor, parsers, etc.)
├── scripts/
│   ├── load_data.ps1      # Script de carga (Windows)
│   └── load_data.sh       # Script de carga (Linux/Mac)
├── tests/                  # Tests unitarios
├── docker-compose.yml      # Configuración de servicios
├── Dockerfile             # Imagen de la API
├── virtuoso.ini           # Configuración optimizada de Virtuoso
├── init.ps1               # Inicialización automática (Windows)
├── init.sh                # Inicialización automática (Linux/Mac)
├── VIRTUOSO_SETUP.md      # Documentación detallada de Virtuoso
└── README.md              # Este archivo
```

## 🔧 Configuración de Virtuoso

El archivo `virtuoso.ini` incluye optimizaciones para grandes volúmenes de datos:

- **Memoria**: 24 GB pool, 2.7M buffers
- **SPARQL**: 1M resultados máximos
- **Threads**: 16 threads HTTP, 8 threads por query

Ver [VIRTUOSO_SETUP.md](VIRTUOSO_SETUP.md) para detalles completos.

## 📝 Datos RDF

### Archivo `result.nt`

**⚠️ Importante**: El archivo `result.nt` **NO está incluido en el repositorio** debido a su gran tamaño (~811 MB). Debe ser colocado manualmente en la raíz del proyecto antes de iniciar los servicios.

#### Ubicación
```
frontend-next/             # Raíz del monorepo
├── backend/
│   ├── result.nt          # ← Colocar aquí
│   └── ...
├── docker-compose.yml
└── ...
```

#### Uso en Docker
El archivo es montado como volumen de solo lectura en el contenedor de Virtuoso
```yaml
# docker-compose.yml (en la raíz)
volumes:
  - ./backend/result.nt:/database/result.nt:ro
```

Los scripts de inicialización (`init.ps1` / `init.sh`) y carga (`scripts/load_data.ps1` / `scripts/load_data.sh`) utilizan este archivo para poblar el grafo de conocimiento en Virtuoso.

#### Especificaciones
- **Formato**: N-Triples (`.nt`)
- **Tamaño**: ~811 MB
- **Tripletas**: 2,793,042
- **Grafo destino**: `http://localhost:8890/OntoExhibit`
- **Ontología**: https://w3id.org/OntoExhibit

#### ¿Por qué no está en el repositorio?
GitHub tiene un límite de 100 MB por archivo. Los archivos de datos RDF grandes se excluyen mediante `.gitignore` para mantener el repositorio limpio y enfocado en el código fuente.

## 🔍 Consultas de Ejemplo

### Via SPARQL Endpoint

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

### Via API REST

```bash
# Listar exposiciones
curl http://localhost:8000/api/v1/exhibitions

# Buscar por término
curl http://localhost:8000/api/v1/search?q=Picasso

# Obtener detalles de una exposición
curl http://localhost:8000/api/v1/exhibitions/{id}

# Obtener contadores (Catálogos, etc.)
curl http://localhost:8000/api/v1/count_catalogs

# Consultas SPARQL de ejemplo (nuevo)
curl http://localhost:8000/api/v1/example-queries
```

## 🛠️ Comandos Útiles

### Docker

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f virtuoso
docker-compose logs -f api

# Reiniciar servicios
docker-compose restart

# Detener servicios
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v
```

### Virtuoso

```bash
# Acceder a isql
docker exec -it complexhibit-virtuoso isql 1111 dba dba

# Ver estado
docker exec complexhibit-virtuoso isql 1111 dba dba exec="status();"

# Contar tripletas
docker exec complexhibit-virtuoso isql 1111 dba dba exec="SPARQL SELECT COUNT(*) FROM <http://localhost:8890/OntoExhibit> WHERE {?s ?p ?o};"
```

## 🐛 Solución de Problemas

### Virtuoso no inicia

```bash
# Ver logs detallados
docker logs complexhibit-virtuoso

# Verificar configuración
docker exec complexhibit-virtuoso cat /database/virtuoso.ini
```

### Datos no se cargan

```bash
# Verificar que el archivo existe
docker exec complexhibit-virtuoso ls -lh /database/result.nt

# Recargar datos manualmente
docker exec -it complexhibit-virtuoso isql 1111 dba dba
```

### Memoria insuficiente

Si el sistema tiene menos RAM, editar `virtuoso.ini`:

**Para 16 GB:**
```ini
NumberOfBuffers = 1360000
MaxDirtyBuffers = 1000000
MaxMemPoolSize = 12000000000
```

**Para 8 GB:**
```ini
NumberOfBuffers = 680000
MaxDirtyBuffers = 500000
MaxMemPoolSize = 6000000000
```

Luego reiniciar:
```bash
docker-compose restart virtuoso
```

## 📚 Documentación Adicional

- [VIRTUOSO_SETUP.md](VIRTUOSO_SETUP.md) - Configuración detallada de Virtuoso
- [Virtuoso Documentation](http://docs.openlinksw.com/virtuoso/)
- [SPARQL 1.1 Query Language](https://www.w3.org/TR/sparql11-query/)
- [OntoExhibit Ontology](https://w3id.org/OntoExhibit)

## 🤝 Contribuir

1. Fork el proyecto
2. Crear una rama para el feature (`git checkout -b feature/AmazingFeature`)
3. Commit de los cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT.

## ✨ Características

- ✅ **Consultas SPARQL Dinámicas**: Sistema de gestión y ejecución de consultas de ejemplo desde la base de datos.
- ✅ Carga automática de 2.7M tripletas
- ✅ Configuración optimizada de Virtuoso
- ✅ API REST sobre SPARQL
- ✅ Scripts de inicialización multiplataforma
- ✅ Docker Compose para fácil despliegue
- ✅ Healthchecks automáticos
- ✅ Healthchecks automáticos
- ✅ Documentación completa
- ✅ **Sistema de Métricas**: Endpoints para registrar y consultar analíticas de uso (descargas, page views).
- ✅ **Gestión de Usuarios Extendida**: Soporte para tipos de institución en el registro de usuarios.

## 🔄 Actualizar Datos

Para actualizar los datos del grafo:

1. Reemplazar `result.nt` con el nuevo archivo
2. Ejecutar el script de carga:
   ```bash
   # Windows
   .\scripts\load_data.ps1
   
   # Linux/Mac
   ./scripts/load_data.sh
   ```

El script limpiará el grafo existente y cargará los nuevos datos.

