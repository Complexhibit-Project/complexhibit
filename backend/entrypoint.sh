#!/bin/bash
set -e

# Esperar a que la base de datos esté lista
# (Podríamos usar pg_isready si el cliente de postgres estuviera instalado,
# pero para mantener la imagen ligera, usamos un script de python simple o reintentos)
echo "Waiting for database..."
sleep 5  # Simple wait, or implement a better check logic

# Inicializar admin
echo "Initializing admin user..."
python -m app.scripts.init_admin

# Ejecutar comando principal
echo "Starting application..."
exec "$@"
