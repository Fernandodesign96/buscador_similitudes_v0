#!/usr/bin/env bash
# Verifica que la API Flask responda correctamente.
set -euo pipefail

API_URL="${API_URL:-http://127.0.0.1:5001}"

curl -sf "${API_URL}/api/health" | grep -q '"status":"ok"'
echo "OK: API saludable en ${API_URL}"
