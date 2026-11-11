#!/usr/bin/env bash
# Backup de Complexhibit: Virtuoso (grafo RDF) + PostgreSQL (autenticación).
#
# Pensado para ejecutarse en el servidor de producción (cron semanal, p.ej. domingos a las 03:00:
#   0 3 * * 0 /ruta/deployment/backup.sh >> /var/log/complexhibit-backup.log 2>&1 ).
# Uso:  ./backup.sh            -> hace la copia y aplica la retención
#       ./backup.sh --dry-run  -> muestra lo que haría sin escribir nada
#
# No lee ningún .env: las credenciales se usan dentro de cada contenedor.
# Variables (todas opcionales, se definen en el entorno):
#   BACKUP_DIR          destino local               (/root/backups/complexhibit)
#   RETENTION_DAYS      días que se conservan       (28, ~4-5 copias semanales)
#   MIN_FREE_GB         espacio libre mínimo para empezar (10)
#   VIRTUOSO_CONTAINER  nombre del contenedor       (complexhibit-virtuoso)
#   POSTGRES_CONTAINER  nombre del contenedor       (complexhibit-postgres)
#   VIRTUOSO_VOLUME     volumen Docker de Virtuoso  (deployment_virtuoso-data)
#   RESULT_NT           ruta de result.nt a incluir si existe (vacío = omitir)
#   REMOTE_TARGET       destino rsync opcional, p.ej. usuario@host:/ruta/backups/
set -euo pipefail

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

# Nota: este script NO lee ni ejecuta ningún .env. Las credenciales se usan siempre
# dentro de los contenedores (variables propias de cada contenedor), de modo que
# nunca pasan por el script ni por la línea de comandos.

BACKUP_DIR="${BACKUP_DIR:-/root/backups/complexhibit}"
RETENTION_DAYS="${RETENTION_DAYS:-28}"   # backup semanal: se conserva el último mes (~4-5 copias)
MIN_FREE_GB="${MIN_FREE_GB:-10}"         # aborta si queda menos espacio libre que esto
VIRTUOSO_CONTAINER="${VIRTUOSO_CONTAINER:-complexhibit-virtuoso}"
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-complexhibit-postgres}"
VIRTUOSO_VOLUME="${VIRTUOSO_VOLUME:-deployment_virtuoso-data}"
RESULT_NT="${RESULT_NT:-}"
REMOTE_TARGET="${REMOTE_TARGET:-}"

STAMP="$(date +%Y%m%d_%H%M%S)"
DEST="$BACKUP_DIR/$STAMP"

log() { echo "[$(date '+%F %T')] $*"; }
run() { if $DRY_RUN; then echo "  (dry-run) $*"; else "$@"; fi; }

command -v docker >/dev/null || { log "ERROR: docker no encontrado"; exit 1; }
for c in "$VIRTUOSO_CONTAINER" "$POSTGRES_CONTAINER"; do
    docker inspect "$c" >/dev/null 2>&1 || { log "ERROR: contenedor $c no existe"; exit 1; }
done
PG_USER="$(docker exec "$POSTGRES_CONTAINER" printenv POSTGRES_USER)"
PG_DB="$(docker exec "$POSTGRES_CONTAINER" printenv POSTGRES_DB)"
VOLUME_PATH="$(docker volume inspect "$VIRTUOSO_VOLUME" --format '{{.Mountpoint}}')"
[[ -d "$VOLUME_PATH" ]] || { log "ERROR: volumen $VIRTUOSO_VOLUME no encontrado"; exit 1; }

# Protección de disco: no empezar si el espacio libre es bajo
mkdir -p "$BACKUP_DIR"
FREE_GB="$(df -BG --output=avail "$BACKUP_DIR" | tail -1 | tr -dc '0-9')"
if (( FREE_GB < MIN_FREE_GB )); then
    log "ERROR: solo hay ${FREE_GB} GB libres (mínimo ${MIN_FREE_GB} GB); se cancela el backup"
    exit 1
fi

log "Inicio de backup -> $DEST"
run mkdir -p "$DEST"

# 1) PostgreSQL: volcado lógico comprimido
log "PostgreSQL: pg_dump de $PG_DB"
if ! $DRY_RUN; then
    docker exec "$POSTGRES_CONTAINER" pg_dump -U "$PG_USER" "$PG_DB" | gzip > "$DEST/postgres_${PG_DB}.sql.gz"
    # gzip -t valida la integridad; el pipe con pipefail ya aborta si pg_dump falla
    gzip -t "$DEST/postgres_${PG_DB}.sql.gz"
fi

# 2) Virtuoso: checkpoint (vuelca el log de transacciones a virtuoso.db) y copia de la base
log "Virtuoso: checkpoint"
# La contraseña DBA se resuelve dentro del contenedor ($DBA_PASSWORD), sin pasar por este script
if docker exec "$VIRTUOSO_CONTAINER" sh -c '[ -n "$DBA_PASSWORD" ]'; then
    run docker exec "$VIRTUOSO_CONTAINER" sh -c 'isql 1111 dba "$DBA_PASSWORD" "exec=checkpoint;"' >/dev/null
else
    log "AVISO: el contenedor no define DBA_PASSWORD; se omite el checkpoint (la copia puede perder las últimas escrituras)"
fi
log "Virtuoso: copia de virtuoso.db"
if ! $DRY_RUN; then
    tar -C "$VOLUME_PATH" -czf "$DEST/virtuoso_db.tar.gz" virtuoso.db virtuoso.trx 2>/dev/null \
        || tar -C "$VOLUME_PATH" -czf "$DEST/virtuoso_db.tar.gz" virtuoso.db
    tar -tzf "$DEST/virtuoso_db.tar.gz" >/dev/null
fi

# 3) Opcional: volcado N-Triples fuente del grafo
if [[ -n "$RESULT_NT" && -s "$RESULT_NT" ]]; then
    log "Incluyendo $(basename "$RESULT_NT")"
    if ! $DRY_RUN; then gzip -c "$RESULT_NT" > "$DEST/result.nt.gz"; fi
fi

# 4) Sumas de verificación
if ! $DRY_RUN; then
    (cd "$DEST" && sha256sum ./* > SHA256SUMS)
    log "Tamaño de la copia: $(du -sh "$DEST" | cut -f1)"
fi

# 5) Copia remota opcional
if [[ -n "$REMOTE_TARGET" ]]; then
    log "Enviando a $REMOTE_TARGET"
    run rsync -a "$DEST" "$REMOTE_TARGET"
fi

# 6) Retención: borra solo carpetas con formato de fecha, más antiguas que RETENTION_DAYS
log "Retención: eliminando copias de más de $RETENTION_DAYS días"
if $DRY_RUN; then
    find "$BACKUP_DIR" -mindepth 1 -maxdepth 1 -type d -regextype posix-extended \
        -regex '.*/[0-9]{8}_[0-9]{6}' -mtime +"$RETENTION_DAYS" -print 2>/dev/null | sed 's/^/  (dry-run) borraría /'
else
    find "$BACKUP_DIR" -mindepth 1 -maxdepth 1 -type d -regextype posix-extended \
        -regex '.*/[0-9]{8}_[0-9]{6}' -mtime +"$RETENTION_DAYS" -exec rm -rf {} +
fi

log "Backup completado"
