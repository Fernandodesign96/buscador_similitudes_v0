#!/usr/bin/env bash
# Reinicia el backend si el healthcheck falla repetidamente.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MAX_INTENTOS=3
API_URL="${API_URL:-http://127.0.0.1:5001}"

fallos=0
for _ in $(seq 1 "$MAX_INTENTOS"); do
  if bash "$ROOT/monitoring/healthcheck.sh"; then
    exit 0
  fi
  fallos=$((fallos + 1))
  sleep 2
done

echo "WARN: ${fallos} fallos consecutivos. Reiniciando API..."
pkill -f "python api.py" 2>/dev/null || true
sleep 1
cd "$ROOT"
source .venv/bin/activate
nohup python api.py > /tmp/buscador-api.log 2>&1 &
echo "API reiniciada. Log: /tmp/buscador-api.log"
