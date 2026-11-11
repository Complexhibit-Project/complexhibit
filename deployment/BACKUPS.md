# Copias de seguridad

Script: [`backup.sh`](backup.sh). Hace una copia de:

| Componente | Contenido | Formato |
|---|---|---|
| Virtuoso | grafo RDF (`virtuoso.db`, tras un `checkpoint`) | `virtuoso_db.tar.gz` |
| PostgreSQL | base de usuarios y autenticación | `postgres_<db>.sql.gz` |

Cada copia incluye `SHA256SUMS` y se guarda en `$BACKUP_DIR/<AAAAMMDD_HHMMSS>/`
(por defecto `/root/backups/complexhibit/`). Tamaño medido: ~156 MB por copia.

## Programación

Copia semanal (domingos 03:00), conservando las de los últimos 28 días (~5 copias, < 1 GB):

```cron
0 3 * * 0 /ruta/al/repo/deployment/backup.sh >> /var/log/complexhibit-backup.log 2>&1
```

- Si queda menos de `MIN_FREE_GB` (10 GB) de espacio libre, el script aborta sin escribir nada.
- Solo borra carpetas con nombre de fecha más antiguas que `RETENTION_DAYS`.
- `./backup.sh --dry-run` muestra lo que haría sin escribir nada.
- No lee ningún `.env`: el `checkpoint` de Virtuoso usa la contraseña del propio contenedor.

Variables opcionales: `BACKUP_DIR`, `RETENTION_DAYS`, `MIN_FREE_GB`, `VIRTUOSO_CONTAINER`,
`POSTGRES_CONTAINER`, `VIRTUOSO_VOLUME`, `RESULT_NT`, `REMOTE_TARGET`.

## Copias en otra máquina

Por defecto las copias residen en el mismo servidor, así que protegen frente a errores y a
corrupción de datos, pero no frente a la pérdida del servidor. Para replicarlas:

**Desde la máquina de destino** (recomendado), con acceso SSH al servidor:

```bash
rsync -av -e "ssh -p <puerto>" <usuario>@<servidor>:/root/backups/complexhibit/ /ruta/local/backups/
```

**Desde el servidor**, tras cada copia, definiendo `REMOTE_TARGET` en el entorno del cron:

```cron
0 3 * * 0 REMOTE_TARGET=<usuario>@<destino>:/ruta/backups/ /ruta/al/repo/deployment/backup.sh >> /var/log/complexhibit-backup.log 2>&1
```

> La copia de PostgreSQL contiene datos personales de usuarios (correos y hashes de contraseña).
> Guárdala siempre en almacenamiento privado y **nunca** en un repositorio Git.

## Restauración

```bash
# PostgreSQL
gunzip -c postgres_<db>.sql.gz | docker exec -i complexhibit-postgres psql -U <usuario> <db>

# Virtuoso (con el contenedor parado)
docker stop complexhibit-virtuoso
tar -xzf virtuoso_db.tar.gz -C <ruta del volumen deployment_virtuoso-data>
docker start complexhibit-virtuoso
```

Comprobar la integridad antes de restaurar: `sha256sum -c SHA256SUMS`.

El grafo también puede regenerarse desde los datos de origen con el pipeline ETL
(`etl-pipeline/`, ver `etl-pipeline/docs/CORRECCION_DATOS.md`).
