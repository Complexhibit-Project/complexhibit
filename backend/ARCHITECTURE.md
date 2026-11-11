# Arquitectura del Sistema

## Visión General

La API Complexhibit sigue un patrón de **arquitectura en capas** con clara separación de responsabilidades. La aplicación está construida usando FastAPI y sigue las mejores prácticas modernas de Python con patrones async/await en toda la aplicación.

## Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                     Capa de Cliente                         │
│  (Navegador Web, App Móvil, Servicios Externos)            │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Capa de API Gateway                        │
│                    (FastAPI + CORS)                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Routers (persons, institutions, exhibitions, etc.)  │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Capa de Servicio                         │
│  ┌─────────────────┐  ┌──────────────────┐                  │
│  │ Cliente SPARQL  │  │ Constructores    │                  │
│  │  (httpx async)  │  │  de Queries      │                  │
│  └─────────────────┘  └──────────────────┘                  │
└────────────────────────┬────────────────────────────────────┘
                         │ Protocolo SPARQL
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Capa de Datos                             │
│              Virtuoso Triplestore                           │
│         (Grafo de Conocimiento RDF/OWL)                     │
└─────────────────────────────────────────────────────────────┘
```

## Descripción de Capas

### 1. Capa de API Gateway (`app/routers/`)

**Responsabilidad**: Manejar peticiones HTTP, enrutarlas a los manejadores apropiados, validar entrada/salida

**Componentes**:
- `persons.py` - Endpoints de personas/artistas
- `institutions.py` - Endpoints de instituciones
- `exhibitions.py` - Endpoints de exposiciones
- `artworks.py` - Endpoints de obras de arte
- `misc.py` - Endpoints de búsqueda y utilidad

**Características Clave**:
- Validación de peticiones con modelos Pydantic
- Serialización de respuestas
- Manejo de errores y códigos de estado HTTP
- Inyección de dependencias para autenticación

### 2. Capa de Servicio (`app/services/`)

**Responsabilidad**: Lógica de negocio, ejecución de queries SPARQL, transformación de datos

**Componentes**:

#### Cliente SPARQL (`sparql_client.py`)
- Cliente HTTP asíncrono usando `httpx`
- Gestión de pool de conexiones y timeouts
- Ejecución de queries SELECT y UPDATE
- Manejo de errores y lógica de reintentos

#### Constructores de Queries (`services/queries/`)
- `base.py` - Prefijos SPARQL comunes y constantes
- `persons.py` - Queries relacionadas con personas
- `institutions.py` - Queries de instituciones
- `exhibitions.py` - Queries de exposiciones
- `artworks.py` - Queries de obras de arte
- `misc.py` - Queries de búsqueda y utilidad
- `utils.py` - Helpers para generación de queries

**Patrón de Diseño**: Patrón Builder para construir queries SPARQL

### 3. Capa de Modelo (`app/models/`)

**Responsabilidad**: Validación de datos, serialización, seguridad de tipos

**Componentes**:
- `domain.py` - Entidades de dominio (Persona, Exposicion, ObraDeArte, etc.)
- `responses.py` - Modelos de respuesta API (StandardResponseModel, ErrorResponseModel)

**Tecnología**: Pydantic v2 con type hints completos

### 4. Capa Core (`app/core/`)

**Responsabilidad**: Configuración de aplicación, utilidades compartidas, excepciones

**Componentes**:
- `config.py` - Configuración basada en entorno usando Pydantic Settings
- `exceptions.py` - Clases de excepción personalizadas

### 5. Utilidades (`app/utils/`)

**Responsabilidad**: Funciones helper, transformación de datos

**Componentes**:
- `helpers.py` - Conversión de fechas, hashing, normalización de strings
- `parsers.py` - Parseo de respuestas SPARQL y agrupación

## Flujo de Datos

### Operación de Lectura (Petición GET)

```
1. Cliente → HTTP GET /api/v1/all_personas
2. Router → Validar petición, inyectar dependencias
3. Servicio → Construir query SPARQL SELECT
4. Cliente SPARQL → Ejecutar query contra Virtuoso
5. Parser → Transformar JSON SPARQL a dicts de Python
6. Router → Serializar a modelos Pydantic
7. Cliente ← Respuesta JSON
```

### Operación de Escritura (Petición POST)

```
1. Cliente → HTTP POST /api/v1/post_persona + cuerpo JSON
2. Router → Validar modelo Persona
3. Servicio → Construir query SPARQL INSERT
4. Cliente SPARQL → Ejecutar UPDATE contra Virtuoso
5. Router → Retornar respuesta de éxito/error
6. Cliente ← Respuesta JSON
```

## Decisiones de Diseño Clave

### 1. Arquitectura Asíncrona

**Por qué**: I/O no bloqueante para mejor rendimiento y escalabilidad

**Implementación**:
- `async/await` en toda la aplicación
- `httpx.AsyncClient` para queries SPARQL
- Soporte nativo async de FastAPI

### 2. Inyección de Dependencias

**Por qué**: Testabilidad, bajo acoplamiento, mocking más fácil

**Implementación**:
- `Depends()` de FastAPI para inyectar cliente SPARQL
- Patrón Singleton para instancia del cliente
- Fácil de mockear para testing

### 3. Modelos Pydantic

**Por qué**: Seguridad de tipos, validación automática, generación de esquema OpenAPI

**Implementación**:
- Modelos de dominio para entidades
- Modelos de respuesta para contratos de API
- Modelo de settings para configuración

### 4. Organización Modular de Queries

**Por qué**: Mantenibilidad, reusabilidad, separación de responsabilidades

**Implementación**:
- Queries organizadas por dominio (persons, institutions, etc.)
- Utilidades compartidas en `utils.py`
- Constantes en `base.py`

### 5. Configuración Basada en Entorno

**Por qué**: Seguridad, flexibilidad entre entornos

**Implementación**:
- Archivo `.env` para desarrollo local
- Variables de entorno para producción
- Pydantic Settings para validación

## Consideraciones de Seguridad

### Flujo de Autenticación

```
1. Cliente → Petición con token JWT en header Authorization
2. Middleware → Extraer y validar token
3. Dependencias → Decodificar JWT usando JWT_SECRET
4. Router → Acceder a info de usuario desde token decodificado
5. Servicio → Ejecutar operación autorizada
```

### Características de Seguridad

- Autenticación basada en JWT
- Middleware CORS para peticiones cross-origin
- Variable de entorno para secretos (no en código)
- Validación de entrada con Pydantic
- Prevención de inyección SPARQL (queries parametrizadas)

## Optimizaciones de Rendimiento

### Actuales

- I/O asíncrono paraconvocate peticiones concurrentes
- Pool de conexiones en cliente httpx
- Construcción eficiente de queries SPARQL

### Planificadas

- Capa de caché Redis para queries frecuentes
- Paginación de resultados de queries
- Endpoint GraphQL para consulta flexible
- Optimización de queries de base de datos

## Escalabilidad

### Escalado Horizontal

La aplicación es **sin estado** y puede escalarse horizontalmente:

```
┌─────────┐     ┌─────────┐     ┌─────────┐
│  API 1  │     │  API 2  │     │  API 3  │
└────┬────┘     └────┬────┘     └────┬────┘
     │               │               │
     └───────────────┼───────────────┘
                     │
              ┌──────▼──────┐
              │Load Balancer│
              └──────┬──────┘
                     │
              ┌──────▼──────┐
              │  Virtuoso   │
              └─────────────┘
```

### Opciones de Despliegue

1. **Contenedores Docker**: Múltiples contenedores detrás de un balanceador de carga
2. **Kubernetes**: Autoescalado de Pods basado en CPU/memoria
3. **Serverless**: AWS Lambda / Google Cloud Functions (con consideraciones de arranque en frío)

## Stack Tecnológico

| Capa | Tecnología | Propósito |
|-------|-----------|---------| 
| Framework Web | FastAPI | API async de alto rendimiento |
| Cliente HTTP | httpx | Queries SPARQL async |
| Validación | Pydantic v2 | Seguridad de tipos y validación |
| Autenticación | python-jose | Manejo de JWT |
| Triplestore | Virtuoso | Base de datos RDF/SPARQL |
| Ontología | OntoExhibit | Esquema de patrimonio cultural |
| Contenedor | Docker | Despliegue |
| Servidor | Uvicorn | Servidor ASGI |

## Mejoras Futuras

### Corto Plazo
- [ ] Suite completa de tests (pytest + httpx)
- [ ] Limitación de tasa de API
- [ ] Logging de peticiones/respuestas
- [ ] Endpoints de health check

### Mediano Plazo
- [ ] Endpoint GraphQL
- [ ] Capa de caché Redis
- [ ] Elasticsearch para búsqueda de texto completo
- [ ] Soporte WebSocket para actualizaciones en tiempo real

### Largo Plazo
- [ ] Arquitectura de microservicios
- [ ] Arquitectura event-driven con colas de mensajes
- [ ] Machine learning para recomendaciones
- [ ] Soporte multi-tenancy

## Monitoreo y Observabilidad

### Herramientas Recomendadas

- **Logging**: Logging estructurado con `structlog`
- **Métricas**: Prometheus + Grafana
- **Tracing**: OpenTelemetry
- **Seguimiento de Errores**: Sentry
- **APM**: New Relic o DataDog

## Flujo de Trabajo de Desarrollo

```
1. Feature Branch → Desarrollo Local
2. Tests Unitarios → pytest
3. Revisión de Código → Pull Request
4. CI/CD → GitHub Actions
5. Despliegue Staging → Docker Compose
6. Tests de Integración → Automatizados
7. Despliegue Producción → Kubernetes/Docker Swarm
```

---

**Última Actualización**: 2025-11-26
**Versión**: 1.0.0
