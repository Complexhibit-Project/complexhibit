# Registro de Cambios

Todos los cambios notables de este proyecto se documentarán en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto adhiere a [Versionado Semántico](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-12-29

### Añadido

- **Sistema de Diseño Premium UX/UI**: Renovación visual completa con estética moderna y premium
  - Paleta de colores personalizada con matices primarios/accent (50-900)
  - Integración de Google Fonts (Inter para cuerpo, Playfair Display para encabezados)
  - Efectos de glassmorphism para profundidad y aspecto moderno
  - Animaciones CSS personalizadas (gradient-shift, float, pulse-slow, shimmer)
  - Scrollbar personalizado con colores de marca
  - Sombras mejoradas, estados de focus y estilos de selección

- **Rediseño de la Página de Inicio**: Página de aterrizaje moderna y atractiva
  - Sección hero con texto de gradiente animado
  - Badge flotante con glassmorphism
  - Blobs de fondo animados en gradientes suaves
  - Botones CTA mejorados con fondos de gradiente
  - Tarjetas de categoría mejoradas con efectos hover y elementos decorativos

- **Mejoras de Componentes**:
  - Componente ItemCard con estilos premium y micro-animaciones
  - Navbar con efecto de scroll dinámico (glassmorphism al hacer scroll)
  - Componente AsyncFilterSelect para filtrado mejorado de datos
  - Componente UI DatePicker

### Cambiado

- **Queries SPARQL**: Estructura de queries mejorada para obras, exposiciones, instituciones y personas
- **Respuestas de API**: Respuestas mejor formateadas y manejo de errores
- **Definiciones de Tipos**: Tipos TypeScript mejorados para mejor seguridad de tipos
- **Comportamiento del Navbar**: Glassmorphism ligero al hacer scroll para mejor visibilidad de los enlaces

### Corregido

- **Contraste del Navbar**: Resuelto problema donde los enlaces de navigación eran difíciles de leer con efecto glassmorphism oscuro

## [1.0.0] - 2024-11-26

### 🎉 Refactorización Mayor

Esta versión representa una revisión arquitectónica completa de la API Complexhibit.

### Añadido

- **Arquitectura Modular**: Separación de responsabilidades en routers, services, models y utilities
- **Cliente SPARQL Asíncrono**: Reemplazado `SPARQLWrapper` síncrono por `httpx` asíncrono
- **Organización de Queries**: Queries SPARQL estructuradas en módulos específicos de dominio
- **Seguridad de Tipos**: Modelos Pydantic v2 completos con type hints en toda la aplicación
- **Gestión de Configuración**: Configuración basada en entorno con `pydantic-settings`
- **Modelos de Respuesta**: Respuestas de API estandarizadas con `StandardResponseModel` y `ErrorResponseModel`
- **Documentación Completa**: 
  - README.md actualizado con formato moderno
  - Añadido ARCHITECTURE.md con diseño del sistema
  - Añadido CONTRIBUTING.md con guías de desarrollo
  - Añadido LICENSE.md (MIT)
  - Añadido CHANGELOG.md (este archivo)
  - ROUTES.md mejorado con todos los endpoints
- **Mejoras de Docker**: Dockerfile multi-stage con mejores prácticas de seguridad
- **Docker Compose**: Despliegue de stack completo con Virtuoso
- **Tests HTTP**: Archivo de tests completo para todos los endpoints
- **Herramientas de Desarrollo**: requirements-dev.txt con herramientas de testing y linting

### Cambiado

- **Estructura del Proyecto**: Reorganizado en directorio `app/` con clara separación
  - `app/core/` - Configuración y excepciones
  - `app/models/` - Modelos Pydantic
  - `app/routers/` - Endpoints de API
  - `app/services/` - Lógica de negocio y cliente SPARQL
  - `app/utils/` - Funciones helper
- **Queries SPARQL**: Refactorizado de `queries.py` monolítico a módulos organizados
- **Parseo de Respuestas**: Reemplazado complejo `desglozarJSON` con utilidades de parser más limpias
- **Dependencias**: Actualizado a versiones estables más recientes
  - FastAPI 0.122.0
  - Pydantic 2.12.4
  - httpx 0.28.1
  - Python 3.11+ recomendado

### Eliminado

- **Archivos Legacy**: Removida estructura monolítica antigua
  - `main.py` (raíz) → `app/main.py`
  - `queries.py` → `app/services/queries/*`
  - `commons.py` → `app/utils/helpers.py` + `app/core/config.py`
  - `models.py` → `app/models/domain.py`
  - `main_virtuoso.py` y `main_stardog.py` (obsoletos)
- **SPARQLWrapper**: Removido en favor de httpx asíncrono

### Corregido

- **Operaciones Asíncronas**: Todas las queries SPARQL ahora no bloqueantes
- **Organización de Imports**: Imports limpios con estructura de módulos apropiada
- **Variables de Entorno**: Validación y chequeo de tipos apropiados
- **Manejo de Errores**: Respuestas de error consistentes en todos los endpoints

### Seguridad

- **Autenticación JWT**: Mantenida y mejorada autenticación basada en tokens
- **Validación de Entrada**: Mejorada con modelos Pydantic
- **Inyección SPARQL**: Mejor parametrización de queries
- **Seguridad de Docker**: Usuario no-root en contenedor

### Rendimiento

- **I/O Asíncrono**: Operaciones no bloqueantes para mejor concurrencia
- **Pool de Conexiones**: Gestión eficiente de cliente httpx
- **Imagen Docker Más Pequeña**: Build multi-stage reduce tamaño de imagen

## [0.9.0] - 2024-XX-XX (Versión Anterior)

### Implementación Inicial

- Aplicación FastAPI básica
- Queries SPARQL con SPARQLWrapper
- Soporte para Stardog y Virtuoso
- Autenticación básica

---

## Guía de Migración (0.9.0 → 1.0.0)

### Breaking Changes

1. **Rutas de Import Cambiadas**
   ```python
   # Antiguo
   from models import Persona
   from queries import Query
   
   # Nuevo
   from app.models.domain import Persona
   from app.services.queries.persons import PersonQueries
   ```

2. **Cliente SPARQL**
   ```python
   # Antiguo (síncrono)
   from SPARQLWrapper import SPARQLWrapper
   sparql = SPARQLWrapper(endpoint)
   results = sparql.query()
   
   # Nuevo (asíncrono)
   from app.services.sparql_client import sparql_client
   results = await sparql_client.query(query_string)
   ```

3. **Configuración**
   ```python
   # Antiguo
   from commons import URI_ONTOLOGIA
   
   # Nuevo
   from app.core.config import settings
   uri = settings.URI_ONTOLOGIA
   ```

4. **Formato de Respuesta**
   - Todas las respuestas ahora usan `StandardResponseModel` o `ErrorResponseModel`
   - Estructura consistente en todos los endpoints

### Pasos de Actualización

1. Actualizar imports
2. Actualizar archivo `.env` con nueva estructura
3. Instalar nuevas dependencias: `pip install -r requirements.txt`
4. Actualizar configuración de Docker si se usan contenedores
5. Testear todos los endpoints con nueva estructura
