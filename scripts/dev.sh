#!/usr/bin/env bash
# Arranca backend Flask y frontend Next.js en desarrollo.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

cleanup() {
  echo ""
  echo "Deteniendo servicios..."
  kill "$API_PID" "$FRONT_PID" 2>/dev/null || true
  exit 0
}
trap cleanup INT TERM

echo "=== Buscador INAPI — modo desarrollo ==="

# Backend
source .venv/bin/activate
python api.py &
API_PID=$!
echo "API Flask PID: $API_PID (http://127.0.0.1:5001)"

sleep 3

# Frontend
cd frontend
bun dev &
FRONT_PID=$!
echo "Next.js PID: $FRONT_PID (http://localhost:3000)"

echo ""
echo "Presiona Ctrl+C para detener ambos servicios."
wait
