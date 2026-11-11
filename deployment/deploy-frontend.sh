#!/usr/bin/env bash
#
# Rebuild and redeploy the Complexhibit frontend container.
#
# Why a script: docker-compose v1 on this host crashes with
# `KeyError: 'ContainerConfig'` when recreating a container built by BuildKit
# (`up -d --build` / `up -d` over an existing container). This works around it
# by building first, then removing the old container, then `up -d`.
#
# Requires working HTTPS egress (through your HTTP proxy if your network needs one) because the
# build downloads npm dependencies (e.g. the knowledge-graph explorer).
#
# Usage:  ./deploy-frontend.sh
set -euo pipefail

# Run from the directory this script lives in (deployment/).
cd "$(dirname "$0")"

COMPOSE="docker-compose -f docker-compose.prod.yml"
SVC="frontend"
CONTAINER="complexhibit-frontend"

echo "==> 1/4 Building $SVC image (downloads npm deps via proxy)…"
$COMPOSE build "$SVC"

echo "==> 2/4 Removing old container (and any stale renamed one)…"
docker stop "$CONTAINER" 2>/dev/null || true
docker rm   "$CONTAINER" 2>/dev/null || true
# compose v1 leaves the previous container renamed as <hash>_<name> after a failed recreate
STALE=$(docker ps -a --filter "name=$CONTAINER" -q)
[ -n "$STALE" ] && docker rm $STALE || true

echo "==> 3/4 Starting fresh container…"
$COMPOSE up -d "$SVC"

echo "==> 4/4 Verifying…"
sleep 6
docker ps --filter "name=$CONTAINER" --format "    {{.Names}}  {{.Status}}"
code_home=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/ || echo "ERR")
code_graph=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/graph || echo "ERR")
echo "    http://localhost:3000/       -> $code_home"
echo "    http://localhost:3000/graph  -> $code_graph  (graph explorer)"

if [ "$code_home" = "200" ] && [ "$code_graph" = "200" ]; then
  echo "==> Frontend deployed OK. Hard-refresh https://complexhibit.uma.es (Ctrl+F5)."
else
  echo "==> WARNING: unexpected status codes. Check: docker logs $CONTAINER"
  exit 1
fi
