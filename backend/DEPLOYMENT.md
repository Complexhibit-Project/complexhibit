# Guía de Despliegue

Esta guía cubre diferentes estrategias de despliegue para la API Complexhibit.

## Tabla de Contenidos

- [Desarrollo Local](#desarrollo-local)
- [Despliegue con Docker](#despliegue-con-docker)
- [Docker Compose (Stack Completo)](#docker-compose-stack-completo)
- [Despliegue en la Nube](#despliegue-en-la-nube)
- [Lista de Verificación de Producción](#lista-de-verificación-de-producción)

## Inicialización Automática

El backend incluye un script de entrada (`entrypoint.sh`) que realiza las siguientes tareas automáticamente al iniciar el contenedor:
1. Espera a que la base de datos PostgreSQL esté lista.
2. Ejecuta `init_admin.py` para asegurar que existe un usuario administrador (crea uno si no existe, o actualiza sus roles).
3. Inicia la aplicación FastAPI.

### Configuración del Admin

El usuario administrador se crea a partir de las variables de entorno (sin valores por defecto):
- **Email**: `ADMIN_EMAIL`
- **Password**: `ADMIN_PASSWORD`

> ⚠️ **IMPORTANTE**: `ADMIN_EMAIL` y `ADMIN_PASSWORD` son **obligatorias**. Si no están
> definidas, `init_admin.py` aborta. Usa siempre una contraseña fuerte y cámbiala tras el primer login.

## Desarrollo Local


### Inicio Rápido

```bash
# Clonar repositorio
git clone <repository-url>
cd frontend-next/backend

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar entorno
# Copiar desde .env.template de la raíz a backend/.env
cp ../.env.template .env
# Editar .env con tu configuración

# Ejecutar servidor de desarrollo
python -m uvicorn app.main:app --reload --port 8000
```

Acceder a la API en http://localhost:8000/api/v1/docs

## Despliegue con Docker

### Construir y Ejecutar

```bash
# Construir imagen
docker build -t complexhibit-api .

# Ejecutar contenedor
docker run -d \
  --name complexhibit-api \
  -p 8000:8000 \
  --env-file .env \
  complexhibit-api
```

### Con Puerto Personalizado

```bash
docker run -d \
  --name complexhibit-api \
  -p 9000:8000 \
  --env-file .env \
  complexhibit-api
```

## Docker Compose (Stack Completo)

Desplegar API + Virtuoso triplestore:

```bash
# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v
```

### Servicios

- **API**: http://localhost:8000/api/v1/
- **Virtuoso**: http://localhost:8890/sparql
- **Virtuoso Conductor**: http://localhost:8890/conductor

### Configuración de Virtuoso (Rendimiento)

El proyecto incluye dos configuraciones para Virtuoso en `backend/`:

1. **`virtuoso.dev.ini` (Por defecto)**:
   - Optimizado para desarrollo local y Docker Desktop.
   - Configurado para sistemas con 4-8 GB de RAM.
   - Usado por defecto como `virtuoso.ini`.

2. **`virtuoso.prod.ini`**:
   - Optimizado para servidores de producción dedicados.
   - Requiere 32GB+ de RAM.
   - Habilita buffers grandes para máximo rendimiento.

**Para pasar a Producción:**
```bash
cp backend/virtuoso.prod.ini backend/virtuoso.ini
# Reiniciar contenedor
docker-compose restart virtuoso
```

**Nota sobre Índices:**
Los scripts de carga (`load_data.ps1` y `load_data.sh`) ejecutan automáticamente la optimización de índices. Si cargas datos manualmente, ejecuta estos comandos en Virtuoso para asegurar el rendimiento:
```sql
RDF_OBJ_FT_RULE_ADD(null, null, 'All');
VT_INC_INDEX_DB_DBA_RDF_OBJ();
```

## Despliegue en la Nube

### AWS (Elastic Beanstalk)

1. **Instalar EB CLI**
   ```bash
   pip install awsebcli
   ```

2. **Inicializar EB**
   ```bash
   eb init -p docker complexhibit-api
   ```

3. **Crear Entorno**
   ```bash
   eb create complexhibit-prod
   ```

4. **Desplegar**
   ```bash
   eb deploy
   ```

5. **Configurar Variables de Entorno**
   ```bash
   eb setenv URI_ONTOLOGIA=https://w3id.org/OntoExhibit/ \
            VIRTUOSO_URL=your-virtuoso-url \
            JWT_SECRET=your-secret-key
   ```

### AWS (ECS/Fargate)

1. **Subir a ECR**
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ECR_URL
   docker tag complexhibit-api:latest YOUR_ECR_URL/complexhibit-api:latest
   docker push YOUR_ECR_URL/complexhibit-api:latest
   ```

2. **Crear Definición de Tarea** (JSON)
   ```json
   {
     "family": "complexhibit-api",
     "containerDefinitions": [{
       "name": "api",
       "image": "YOUR_ECR_URL/complexhibit-api:latest",
       "portMappings": [{
         "containerPort": 8000,
         "protocol": "tcp"
       }],
       "environment": [
         {"name": "DEPLOY_PATH", "value": "/api/v1"}
       ],
       "secrets": [
         {"name": "JWT_SECRET", "valueFrom": "arn:aws:secretsmanager:..."}
       ]
     }]
   }
   ```

3. **Crear Servicio**
   ```bash
   aws ecs create-service \
     --cluster your-cluster \
     --service-name complexhibit-api \
     --task-definition complexhibit-api \
     --desired-count 2 \
     --launch-type FARGATE
   ```

### Google Cloud (Cloud Run)

```bash
# Construir y subir a GCR
gcloud builds submit --tag gcr.io/YOUR_PROJECT/complexhibit-api

# Desplegar
gcloud run deploy complexhibit-api \
  --image gcr.io/YOUR_PROJECT/complexhibit-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DEPLOY_PATH=/api/v1
```

### Heroku

```bash
# Login
heroku login

# Crear app
heroku create complexhibit-api

# Configurar variables de entorno
heroku config:set URI_ONTOLOGIA=https://w3id.org/OntoExhibit/
heroku config:set VIRTUOSO_URL=your-virtuoso-url

# Desplegar
git push heroku main
```

### DigitalOcean App Platform

1. Conectar repositorio GitHub
2. Configurar ajustes de build:
   - **Tipo**: Docker
   - **Dockerfile**: `Dockerfile`
3. Configurar variables de entorno en el dashboard
4. Desplegar

## Recomendaciones para Producción (On-Premises / VPS)

Si vas a desplegar en una **Máquina Virtual (VM) "pelada"** (por ejemplo, proporcionada por una universidad o AWS EC2) donde tienes control total pero debes gestionar tú mismo los certificados y servicios, esta es la configuración "ligera" recomendada para complementar Docker:

### 1. Gestión de Contenedores: Portainer CE

Evita usar paneles de control pesados (cPanel, Plesk). Portainer te ofrece una interfaz gráfica web para gestionar tus contenedores Docker (ver logs, reiniciar servicios, monitorizar recursos) sin "ensuciar" el sistema operativo.

**Instalación rápida:**
```bash
docker volume create portainer_data
docker run -d -p 9000:9000 --name portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:latest
```
Accede en `http://tu-servidor:9000`.

### 2. Gestión de SSL y Dominios: Nginx Proxy Manager

Si la institución te proporciona los certificados SSL (archivos `.crt` y `.key`) y te da acceso a los puertos 80/443, **Nginx Proxy Manager** (NPM) es la forma más sencilla de gestionarlos.

1. Añade este servicio a tu `docker-compose.yml` (o ejecútalo aparte).
2. Sube tus certificados en la interfaz web de NPM ("Custom SSL").
3. Crea un "Proxy Host" que apunte `tu-dominio.com` -> `complexhibit-frontend:3000`.
4. ¡Listo! NPM gestionará las redirecciones HTTPS automáticamente.

Esta combinación (Docker + Portainer + NPM) es ideal porque mantiene el servidor limpio y delega todo a contenedores, facilitando las actualizaciones y migraciones.

### 3. Estrategia de Auto-Reinicio (Disaster Recovery)

El proyecto ya está configurado para manejar caídas y reinicios del servidor automáticamente mediante la política `restart: unless-stopped` en `docker-compose.yml`.

**¿Qué significa esto?**
1. **Si un contenedor crashea**: Docker intentará reiniciarlo automáticamente (por ejemplo, si la API falla por un error de código momentáneo).
2. **Si el servidor se reinicia**: Cuando la máquina (VM) arranca de nuevo, el demonio de Docker se inicia y levanta automáticamente todos los contenedores que estaban corriendo antes de apagarse.

**Verificación:**
Para asegurarte de que esto funcionará en tu servidor Linux, solo debes verificar que el servicio Docker esté habilitado para iniciar con el sistema (esto es lo estándar al instalar Docker):
```bash
sudo systemctl enable docker
```
Con esto, tu aplicación es resiliente a reinicios inesperados sin necesidad de scripts adicionales.

## Lista de Verificación de Producción

### Seguridad

- [ ] Usar HTTPS (certificados SSL/TLS)
- [ ] Configurar `JWT_SECRET` fuerte
- [ ] Configurar CORS correctamente (no `["*"]`)
- [ ] Usar variables de entorno para secretos
- [ ] Habilitar limitación de tasa
- [ ] Implementar autenticación de API key
- [ ] Actualizaciones de seguridad regulares

### Rendimiento

- [ ] Habilitar caché (Redis)
- [ ] Usar CDN para assets estáticos
- [ ] Configurar pool de conexiones
- [ ] Configurar balanceador de carga
- [ ] Habilitar compresión gzip
- [ ] Optimizar queries de base de datos

### Monitoreo

- [ ] Configurar logging (CloudWatch, Stackdriver, etc.)
- [ ] Configurar seguimiento de errores (Sentry)
- [ ] Configurar monitoreo de uptime
- [ ] Configurar alertas
- [ ] Habilitar APM (Application Performance Monitoring)

### Confiabilidad

- [ ] Configurar health checks
- [ ] Configurar auto-escalado
- [ ] Implementar circuit breakers
- [ ] Configurar estrategia de backup
- [ ] Testear recuperación ante desastres

### Documentación

- [ ] Actualizar documentación de API
- [ ] Documentar proceso de despliegue
- [ ] Crear runbooks para problemas comunes
- [ ] Documentar variables de entorno
- [ ] Comprobar funcionamiento de la exportación PDF
- [ ] Verificar carga de Example Queries en el home

## Variables de Entorno

### Requeridas

```env
URI_ONTOLOGIA=https://w3id.org/OntoExhibit/
VIRTUOSO_URL=http://your-virtuoso:8890/sparql
JWT_SECRET=your-secret-key-here
DEFAULT_GRAPH_URL=http://your-virtuoso:8890/DAV/home/dba/rdf_sink
```

### Opcionales

```env
DEPLOY_PATH=/api/v1
USER_SERVICE_URL=http://your-user-service
DATABASE_STARDOG=your-database
ENDPOINT_STARDOG=http://your-stardog:5820
USERNAME_STARDOG=admin
PASSWORD_STARDOG=admin
```

## Escalado

### Escalado Horizontal

```bash
# Docker Swarm
docker service scale complexhibit-api=5

# Kubernetes
kubectl scale deployment complexhibit-api --replicas=5
```

### Balanceo de Carga

#### Configuración Nginx

```nginx
upstream complexhibit_api {
    server api1:8000;
    server api2:8000;
    server api3:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://complexhibit_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Solución de Problemas

### Problemas Comunes

1. **Puerto ya en uso**
   ```bash
   # Encontrar proceso usando puerto 8000
   lsof -i :8000
   # Matar proceso
   kill -9 PID
   ```

2. **Variables de entorno no se cargan**
   - Verificar que el archivo `.env` existe
   - Verificar permisos del archivo
   - Buscar errores de sintaxis en `.env`

3. **Errores de conexión SPARQL**
   - Verificar que Virtuoso está ejecutándose
   - Verificar conectividad de red
   - Verificar URL del endpoint SPARQL

4. **Build de Docker falla**
   - Limpiar caché de Docker: `docker system prune -a`
   - Verificar sintaxis del Dockerfile
   - Verificar disponibilidad de imagen base

## Soporte

Para problemas de despliegue:
- Revisar [GitHub Issues](https://github.com/MartinM10/complexhibit/issues)
- Leer [CONTRIBUTING.md](CONTRIBUTING.md)
- Contactar a los mantenedores

---

**Última Actualización**: 2026-02-09
