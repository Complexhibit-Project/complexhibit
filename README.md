# Complexhibit

Este es el monorepo del proyecto Complexhibit, que consiste en un backend FastAPI y un frontend Next.js.

## Estructura del Proyecto

- **`backend/`**: Contiene la aplicación FastAPI, archivos de ontología y scripts de procesamiento de datos.
- **`frontend/`**: Contiene la aplicación web Next.js.
- **`docker-compose.yml`**: Orquesta los servicios (Backend, Frontend, Virtuoso).

## Inicio Rápido

### Requisitos Previos

- [Docker](https://www.docker.com/) y [Docker Compose](https://docs.docker.com/compose/) instalados.

### Configuración (.env)

El proyecto utiliza un único archivo `.env` consolidado para toda la configuración.

1.  **`.env` en la raíz**: Copia `.env.template` a `.env` en el directorio raíz.
    - Este archivo contiene todas las variables de configuración tanto para Docker como para desarrollo local
    - Variables clave:
        - `URI_ONTOLOGIA`: URI base para la ontología.
        - `JWT_SECRET`: Clave secreta para autenticación JWT en el backend FastAPI.
        - `VIRTUOSO_DBA_PASSWORD`: Contraseña para la base de datos Virtuoso.
        - `POSTGRES_*`: Credenciales de la base de datos PostgreSQL.
        - `NEXT_PUBLIC_API_URL`: URL para la API del backend (lado cliente).
        - `API_URL`: URL para la API del backend (lado servidor/Docker interno).
    - ¡Para producción, asegúrate de cambiar todos los secretos y contraseñas!

2.  **Desarrollo Local**: Si ejecutas el backend localmente (sin Docker), copia el `.env` de la raíz a `backend/.env`.

### Ejecutar la Aplicación

Puedes usar los scripts de inicialización proporcionados para una configuración rápida (verifica Docker, crea .env, inicia servicios, carga datos):

**Windows:**
```powershell
.\init.ps1
```

**Linux/Mac:**
```bash
chmod +x init.sh
./init.sh
```

O manualmente con Docker Compose:

```bash
docker-compose up -d --build
```

### Acceder a los Servicios

- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:8000/api/v1/](http://localhost:8000/api/v1/)
- **Virtuoso SPARQL Endpoint**: [http://localhost:8890/sparql](http://localhost:8890/sparql)
- **Virtuoso Conductor**: [http://localhost:8890/conductor](http://localhost:8890/conductor)

## 🛡️ Seguridad y Características Nuevas
+ **Exportación de Datos**: Las páginas de detalle ahora permiten exportar información en formatos PDF, JSON y HTML.
+ **Consultas SPARQL de Ejemplo**: Integración de un catálogo dinámico de consultas SPARQL para facilitar la exploración del grafo.
- **Autenticación JWT**: Los endpoints de escritura del backend ahora están protegidos.
- **Contadores en Home**: Visualización en tiempo real de estadísticas del grafo en el frontend.
- **Configuración Automática**: Scripts de inicialización mejorados y automatizados con Docker.

## Desarrollo

### Backend
Consulta [backend/README.md](backend/README.md) para instrucciones detalladas de desarrollo del backend.

### Frontend
Consulta [frontend/README.md](frontend/README.md) para instrucciones detalladas de desarrollo del frontend.

## Licencia

Este software es propietario y pertenece a **iArtHis Lab**. © 2025 iArtHis Lab. Todos los derechos reservados.

Para consultas sobre licencias, contacta a iArtHis Lab.
