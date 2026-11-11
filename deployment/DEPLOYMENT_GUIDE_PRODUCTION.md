# Guía de despliegue a producción - Complexhibit

Despliegue con `docker-compose.prod.yml`: backend, frontend, Virtuoso y PostgreSQL con
**`network_mode: host`**, y **Nginx en modo bridge** que sale al host vía `host.docker.internal`.
La guía asume `docker-compose` v1 (ver el bug conocido en §2). Sustituye los marcadores
`<...>` por los valores de tu entorno.

> Los comandos de despliegue se ejecutan desde `deployment/` apuntando a `docker-compose.prod.yml`.

## 1. Configuración

### 1.1. Certificados SSL
`docker-compose.prod.yml` monta los certificados desde el directorio indicado en la variable **`CERTS_DIR`** de `deployment/.env`:
- `fullchain.cer` (certificado público + cadena intermedia)
- la clave privada correspondiente

Para renovar, actualiza ese directorio (`CERTS_DIR`) y recarga nginx: `docker exec complexhibit-nginx nginx -s reload`.

### 1.2. Variables de entorno (`deployment/.env`)
El backend lee `deployment/.env` (`env_file: .env`). Parte de `.env.template` (raíz del repo) y **no lo subas nunca a git**. Variables clave:

```env
# URLs (red host: localhost, NO nombres de servicio)
NEXT_PUBLIC_API_URL=https://<tu-dominio>/api/v1   # se hornea en el build del frontend
API_URL=http://127.0.0.1:8000/api/v1
FRONTEND_URL=https://<tu-dominio>

# Base de datos / Virtuoso (localhost por red host)
VIRTUOSO_URL=http://localhost:8890/sparql

# Certificados TLS (obligatoria): directorio con fullchain.cer y la clave privada
CERTS_DIR=<ruta-certificados>

# Seguridad (CAMBIAR todos en producción; usa valores largos y aleatorios)
# POSTGRES_PASSWORD es obligatoria: el compose no arranca sin ella
JWT_SECRET=<clave_larga_y_aleatoria>
VIRTUOSO_DBA_PASSWORD=<segura>
POSTGRES_PASSWORD=<segura>
ADMIN_PASSWORD=<segura>

# Admins auto-sembrados al arranque: "email:pass,email:pass" (split por el PRIMER ':')
ADMIN_USERS=<admin1@dominio>:<pass>,<admin2@dominio>:<pass>
# Opcional: contraseña del usuario interno system_admin (si no, aleatoria)
# SYSTEM_ADMIN_PASSWORD=<opcional>

# CORS (lista separada por comas)
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,https://<tu-dominio>

# Recuperación de contraseña
PASSWORD_RESET_EXPIRE_MINUTES=60

# SMTP (SSL 465 — ver §6)
SMTP_HOST=<servidor-smtp>
SMTP_PORT=465
SMTP_USER=<usuario-smtp>
SMTP_PASSWORD=<contraseña_de_aplicación>
SMTP_FROM=<remitente>
ADMIN_EMAIL=<correo-del-administrador>
```

> **IMPORTANTE**: `NEXT_PUBLIC_API_URL` se hornea en el build del frontend. Si cambia,
> **hay que reconstruir** el contenedor del frontend.

### 1.3. Virtuoso
`backend/virtuoso.ini` contiene el ajuste de producción (memoria y estimación de costes).
`backend/virtuoso.prod.ini` es una copia de referencia; no hace falta copiarla salvo que partas de cero.

## 2. Despliegue

```bash
cd <ruta-del-repo>/deployment
docker-compose -f docker-compose.prod.yml up -d
```

### Bug conocido de compose v1 al reconstruir/recrear
`docker-compose` v1 + imágenes BuildKit lanza `KeyError: 'ContainerConfig'` al recrear un
contenedor (`up -d --build` o `up -d` sobre uno existente). **Patrón de trabajo:**

```bash
# 1) construir la imagen
docker-compose -f docker-compose.prod.yml build <servicio>
# 2) eliminar el contenedor viejo (queda renombrado <hash>_<nombre>, bórralo también)
docker stop complexhibit-<servicio>; docker rm complexhibit-<servicio>
docker ps -a --filter "name=complexhibit-<servicio>" -q | xargs -r docker rm
# 3) levantarlo de nuevo
docker-compose -f docker-compose.prod.yml up -d <servicio>
```
(`deploy-frontend.sh` automatiza este patrón para el frontend.)

### Qué necesita rebuild vs restart
- **Backend**: `backend/app` va montado por volumen → un `docker restart complexhibit-api`
  recoge cambios de código. Solo necesita rebuild si cambia `requirements.txt`.
- **Frontend**: el código se hornea en la imagen → **siempre requiere rebuild** para cambios
  de UI o de `NEXT_PUBLIC_API_URL`. Reconstruirlo descarga dependencias npm (requiere salida HTTPS).

## 3. Verificación

```bash
docker-compose -f docker-compose.prod.yml ps          # nginx, backend, frontend, virtuoso, postgres "Up"
docker-compose -f docker-compose.prod.yml logs -f backend
```
- `https://<tu-dominio>` → frontend.
- `https://<tu-dominio>/api/v1/docs` → documentación de la API.
- Comprobación rápida en el host: `curl -sk -o /dev/null -w '%{http_code}\n' https://localhost/api/v1/`

## 4. Gestión de contenedores
```bash
docker ps                                   # estado
docker logs -f complexhibit-api             # logs
docker restart complexhibit-api             # reinicio (recoge código backend montado)
docker exec -it complexhibit-postgres psql -U <usuario> -d <base>   # consola DB
```

## 5. Seguridad
Con `network_mode: host` los servicios escuchan directamente en el host, así que **conviene
restringir lo que no deba ser público**:
- Mantén **PostgreSQL** atado a `127.0.0.1` (`command: postgres -c listen_addresses=127.0.0.1`
  en el compose) y con una contraseña fuerte.
- Expón al exterior solo Nginx (80/443). Cierra o ata a loopback los puertos internos
  (backend, frontend, Virtuoso) con reglas de firewall (`nft`/`ufw`) o un firewall de perímetro.
- La cuenta SPARQL anónima de Virtuoso **no** debe tener el rol `SPARQL_UPDATE`; la escritura exige la cuenta DBA.
- Genera `JWT_SECRET`, `VIRTUOSO_DBA_PASSWORD` y las contraseñas de `ADMIN_USERS` con valores fuertes
  y mantén `.env` fuera de git (`.gitignore`).

## 6. Solución de problemas

### 6.1. Salida a Internet a través de un proxy
Si tu red exige un proxy HTTP(S), configúralo en el entorno del usuario y en el daemon Docker
(`/etc/systemd/system/docker.service.d/proxy.conf`). El build del frontend lo usa vía
build-args (`HTTP_PROXY`/`HTTPS_PROXY` en `docker-compose.prod.yml`). Si un `docker build` falla
descargando paquetes, comprueba que el proxy permite `CONNECT` al puerto 443.

### 6.2. Envío de emails (SMTP)
Algunos proxies bloquean `CONNECT` en puertos distintos de 443 (p. ej. 587/STARTTLS). Solución:
`smtplib.SMTP_SSL` directo al puerto 465, que con `network_mode: host` no requiere proxy.
Con Gmail, `SMTP_PASSWORD` debe ser la «contraseña de aplicación» de 16 caracteres sin espacios.

### 6.3. "Failed to fetch" / contadores en `-` en el navegador
El frontend se hornea con `NEXT_PUBLIC_API_URL`. Si apunta a `localhost`, el navegador bloquea las
peticiones en producción. Reconstruye el frontend con la URL pública correcta (ver §2).
