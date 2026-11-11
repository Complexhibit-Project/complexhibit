# Build multi-stage para imagen más pequeña
# Proxy handling updated for strict protocol requirements
FROM node:20-alpine AS base

# Instalar dependencias solo cuando sea necesario
FROM base AS deps

ARG HTTP_PROXY
ARG HTTPS_PROXY

ENV HTTP_PROXY=$HTTP_PROXY
ENV HTTPS_PROXY=$HTTPS_PROXY
ENV http_proxy=$HTTP_PROXY
ENV https_proxy=$HTTPS_PROXY

# Ver https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine para entender por qué podría necesitarse libc6-compat.
RUN set -e; \
    normalize_proxy() { \
        if [ -n "$1" ]; then \
            echo "$1" | sed -E 's|^([^:/]+:[0-9]+)$|http://\1|'; \
        fi \
    }; \
    FIXED_HTTP=$(normalize_proxy "$HTTP_PROXY"); \
    FIXED_HTTPS=$(normalize_proxy "$HTTPS_PROXY"); \
    if [ -n "$FIXED_HTTP" ]; then \
        export http_proxy="$FIXED_HTTP"; \
        export https_proxy="$FIXED_HTTPS"; \
        export HTTP_PROXY="$FIXED_HTTP"; \
        export HTTPS_PROXY="$FIXED_HTTPS"; \
    fi; \
    echo Skipping apk add

WORKDIR /app

# Instalar dependencias basándose en el gestor de paquetes preferido
COPY package.json package-lock.json* ./

# Configurar Proxy de forma robusta (asegurando http://)
RUN set -e; \
    # Función para normalizar URL del proxy
    normalize_proxy() { \
        if [ -n "$1" ]; then \
            echo "$1" | sed -E 's|^([^:/]+:[0-9]+)$|http://\1|'; \
        fi \
    }; \
    FIXED_HTTP=$(normalize_proxy "$HTTP_PROXY"); \
    FIXED_HTTPS=$(normalize_proxy "$HTTPS_PROXY"); \
    echo "--- Proxy Configuration ---"; \
    echo "Original: $HTTP_PROXY"; \
    echo "Fixed:    $FIXED_HTTP"; \
    if [ -n "$FIXED_HTTP" ]; then \
        npm config set proxy "$FIXED_HTTP"; \
        npm config set https-proxy "$FIXED_HTTPS"; \
        npm config set strict-ssl false; \
    fi; \
    npm ci

# Reconstruir el código fuente solo cuando sea necesario
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Next.js recopila datos telemetría completamente anónimos sobre el uso general.
# Más información aquí: https://nextjs.org/telemetry
# Descomentar la siguiente línea en caso de querer deshabilitar telemetría durante el build.
# ENV NEXT_TELEMETRY_DISABLED 1

ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

RUN npm run build

# Imagen de producción, copiar todos los archivos y ejecutar next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
# Descomentar la siguiente línea en caso de querer deshabilitar telemetría durante runtime.
# ENV NEXT_TELEMETRY_DISABLED 1

# No ejecutar como root
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Establecer los permisos correctos para caché de prerender
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Aprovechar automáticamente output traces para reducir tamaño de imagen
# https://nextjs.org/docs/advanced-features/output-file-tracing
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
# Establecer hostname a localhost
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
