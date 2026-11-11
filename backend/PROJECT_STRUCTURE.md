# Estructura del Proyecto

```
backend/
│
├── 📁 .github/
│   └── workflows/
│       └── ci-cd.yml                 # Pipeline CI/CD de GitHub Actions
│
├── 📁 app/                           # Directorio principal de la aplicación
│   ├── 📁 core/                      # Configuración core
│   │   ├── __init__.py
│   │   ├── config.py                 # Configuración Pydantic
│   │   └── exceptions.py             # Excepciones personalizadas
│   │
│   ├── 📁 models/                    # Modelos de datos
│   │   ├── __init__.py
│   │   ├── domain.py                 # Entidades de dominio (Persona, Exposicion, etc.)
│   │   └── responses.py              # Modelos de respuesta API
│   │
│   ├── 📁 routers/                   # Endpoints de API
│   │   ├── __init__.py
│   │   ├── persons.py                # /all_personas, /post_persona, etc.
│   │   ├── institutions.py           # /all_instituciones, etc.
│   │   ├── exhibitions.py            # /all_exposiciones, etc.
│   │   ├── artworks.py               # /all_obras, etc.
│   │   └── misc.py                   # /semantic_search, /all_classes, etc.
│   │
│   ├── 📁 services/                  # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── sparql_client.py          # Cliente SPARQL asíncrono (httpx)
│   │   └── 📁 queries/               # Constructores de queries SPARQL
│   │       ├── __init__.py
│   │       ├── base.py               # Prefijos comunes y constantes
│   │       ├── persons.py            # Queries de personas
│   │       ├── institutions.py       # Queries de instituciones
│   │       ├── exhibitions.py        # Queries de exposiciones
│   │       ├── artworks.py           # Queries de obras
│   │       ├── misc.py               # Queries de búsqueda
│   │       └── utils.py              # Helpers de generación de queries
│   │
│   ├── 📁 utils/                     # Funciones helper
│   │   ├── __init__.py
│   │   ├── helpers.py                # Conversión de fechas, hashing, etc.
│   │   └── parsers.py                # Parseo de respuestas SPARQL
│   │
│   ├── __init__.py
│   ├── dependencies.py               # Dependencias de FastAPI (auth, etc.)
│   └── main.py                       # Punto de entrada de la aplicación
│
├── 📄 .env.template                  # Template de variables de entorno
├── 📄 .env                           # Entorno local (gitignored)
├── 📄 .gitignore                     # Reglas de Git ignore
├── 📄 .gitattributes                 # Atributos de Git (line endings)
├── 📄 .pre-commit-config.yaml        # Pre-commit hooks
│
├── 📄 ARCHITECTURE.md                # Documentación de arquitectura del sistema
├── 📄 CHANGELOG.md                   # Historial de versiones y cambios
├── 📄 CONTRIBUTING.md                # Guías de contribución
├── 📄 DEPLOYMENT.md                  # Instrucciones de despliegue
├── 📄 LICENSE.md                     # Licencia MIT
├── 📄 QUICK_START.md                 # Guía de inicio rápido para nuevos desarrolladores
├── 📄 VIRTUOSO_SETUP.md              # Guía detallada para configurar y depurar Virtuoso

├── 📄 README.md                      # Resumen del proyecto
├── 📄 ROUTES.md                      # Referencia de rutas de API
├── 📄 SECURITY.md                    # Política de seguridad
├── 📄 QUICK_START.md                 # Guía de inicio rápido
├── 📄 VIRTUOSO_SETUP.md              # Configuración de Virtuoso
│
├── 📁 scripts/                       # Scripts de utilidad (carga de datos, etc.)
│   ├── load_data.sh                  # Script de carga para Linux/Mac
│   └── load_data.ps1                 # Script de carga para Windows
│
├── 📄 ontoExhibit.ttl                # Archivo de ontología Turtle
├── 📄 Dockerfile                     # Definición de imagen Docker
├── 📄 docker-compose.yml             # Configuración Docker Compose
├── 📄 pyproject.toml                 # Configuración del proyecto Python
├── 📄 requirements.txt               # Dependencias de producción
├── 📄 requirements-dev.txt           # Dependencias de desarrollo
└── 📄 test_main.http                 # Peticiones HTTP de prueba
```

## Descripción de Archivos

### Código de Aplicación (`app/`)

| Archivo/Directorio | Propósito |
|----------------|---------| 
| `core/config.py` | Configuración basada en entorno usando Pydantic Settings |
| `core/exceptions.py` | Clases de excepción personalizadas (SparqlError, ResourceNotFoundError) |
| `models/domain.py` | Modelos Pydantic para entidades (Persona, Exposicion, ObraDeArte, etc.) |
| `models/responses.py` | Modelos de respuesta API estandarizados |
| `routers/*.py` | Routers de FastAPI para diferentes tipos de recursos |
| `services/sparql_client.py` | Cliente SPARQL asíncrono usando httpx |
| `services/queries/*.py` | Constructores de queries SPARQL organizados por dominio |
| `utils/helpers.py` | Funciones helper (hashing, conversión de fechas, normalización) |
| `utils/parsers.py` | Utilidades de parseo de respuestas SPARQL |
| `dependencies.py` | Inyección de dependencias de FastAPI (autenticación, cliente) |
| `main.py` | Instancia de aplicación FastAPI y registro de routers |

### Documentación

| Archivo | Propósito |
|------|---------| 
| `README.md` | Resumen del proyecto, inicio rápido, características |
| `ARCHITECTURE.md` | Diseño del sistema, diagramas de arquitectura, decisiones de diseño |
| `CONTRIBUTING.md` | Configuración de desarrollo, estándares de código, proceso PR |
| `DEPLOYMENT.md` | Guías de despliegue para varias plataformas |
| `ROUTES.md` | Referencia completa de endpoints de API |
| `CHANGELOG.md` | Historial de versiones y guías de migración |
| `SECURITY.md` | Política de seguridad y reporte de vulnerabilidades |
| `LICENSE.md` | Licencia MIT |

### Configuración

| Archivo | Propósito |
|------|---------| 
| `.env.template` | Template para variables de entorno |
| `.gitignore` | Archivos a ignorar en control de versiones |
| `.gitattributes` | Atributos de Git (line endings, etc.) |
| `.pre-commit-config.yaml` | Pre-commit hooks para calidad de código |
| `pyproject.toml` | Metadatos del proyecto Python y configuración de herramientas |
| `requirements.txt` | Dependencias Python de producción |
| `requirements-dev.txt` | Dependencias de desarrollo (testing, linting) |

### Docker

| Archivo | Propósito |
|------|---------| 
| `Dockerfile` | Definición de imagen Docker multi-stage |
| `docker-compose.yml` | Despliegue de stack completo (API + Virtuoso) |

### CI/CD

| Archivo | Propósito |
|------|---------| 
| `.github/workflows/ci-cd.yml` | Pipeline de GitHub Actions (test, lint, build, deploy) |

## Directorios Clave

### `app/routers/` - Endpoints de API

Cada archivo router maneja un tipo de recurso específico:
- **persons.py**: Gestión de personas/artistas
- **institutions.py**: Gestión de museos, galerías, instituciones
- **exhibitions.py**: Gestión de eventos de exposiciones
- **artworks.py**: Gestión de obras de arte
- **misc.py**: Búsqueda, endpoints de utilidad

### `app/services/queries/` - Queries SPARQL

Organizadas por dominio para mantenibilidad:
- **base.py**: Prefijos SPARQL comunes y constantes
- **persons.py**: Queries relacionadas con personas (SELECT, INSERT)
- **institutions.py**: Queries de instituciones
- **exhibitions.py**: Queries de exposiciones
- **artworks.py**: Queries de obras de arte
- **misc.py**: Queries de búsqueda y utilidad
- **utils.py**: Helpers de generación de queries

## Stack Tecnológico

| Capa | Tecnología |
|-------|-----------| 
| **Framework** | FastAPI 0.122.0 |
| **Servidor** | Uvicorn (ASGI) |
| **Cliente HTTP** | httpx (async) |
| **Validación** | Pydantic v2 |
| **Autenticación** | python-jose (JWT) |
| **Base de Datos** | Virtuoso (SPARQL) |
| **Ontología** | OntoExhibit + CIDOC-CRM |
| **Contenedor** | Docker |
| **CI/CD** | GitHub Actions |

## Flujo de Trabajo de Desarrollo

```
1. Clonar repositorio
2. Crear entorno virtual
3. Instalar dependencias (requirements.txt + requirements-dev.txt)
4. Configurar archivo .env
5. Ejecutar servidor de desarrollo (uvicorn --reload)
6. Hacer cambios
7. Ejecutar tests (pytest)
8. Formatear código (black, isort)
9. Commit (pre-commit hooks corren automáticamente)
10. Push y crear PR
```

## Opciones de Despliegue

- **Local**: `uvicorn app.main:app --reload`
- **Docker**: `docker build` + `docker run`
- **Docker Compose**: `docker-compose up`
- **Nube**: AWS ECS, Google Cloud Run, Heroku, DigitalOcean

## Próximos Pasos

1. Leer [README.md](README.md) para resumen del proyecto
2. Revisar [ARCHITECTURE.md](ARCHITECTURE.md) para diseño del sistema
3. Seguir [CONTRIBUTING.md](CONTRIBUTING.md) para desarrollo
4. Usar [DEPLOYMENT.md](DEPLOYMENT.md) para despliegue
5. Consultar [ROUTES.md](ROUTES.md) para endpoints de API

---

**Última Actualización**: 2025-11-26
**Versión**: 1.0.0
