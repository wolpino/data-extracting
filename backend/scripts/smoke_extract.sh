#!/usr/bin/env bash
# Extract + confirm smoke (PR4). Requires GEMINI_API_KEY in backend/.env or env.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO="$(cd "$ROOT/.." && pwd)"
cd "$ROOT"

PDF="${PDF:-$REPO/docs/testdata/DME Patient Demo Document CPAP.fax.pdf}"
PORT="${PORT:-8011}"
BASE="http://127.0.0.1:${PORT}"
DB_PATH=/tmp/data-extracting-extract-smoke.db
PID=""

cleanup() {
  if [[ -n "${PID}" ]]; then
    kill "$PID" 2>/dev/null || true
    wait "$PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$DB_PATH"
DATABASE_URL="sqlite:////${DB_PATH#/}" uv run uvicorn data_extracting_backend.main:app \
  --host 127.0.0.1 --port "$PORT" >/tmp/data-extracting-extract-uvicorn.log 2>&1 &
PID=$!
for _ in $(seq 1 50); do
  curl -sf "$BASE/health" >/dev/null 2>&1 && break
  sleep 0.1
done
curl -sf "$BASE/health" >/dev/null

# Optional: API_KEY=... when the server requires X-API-Key.
AUTH_HDR=()
if [[ -n "${API_KEY:-}" ]]; then
  AUTH_HDR=(-H "X-API-Key: ${API_KEY}")
fi

echo "== reject non-PDF =="
CODE=$(curl -s -o /tmp/extract-bad.json -w '%{http_code}' \
  "${AUTH_HDR[@]}" \
  -F "file=@$ROOT/README.md;type=text/plain" "$BASE/api/v1/extract")
echo "HTTP $CODE"
cat /tmp/extract-bad.json; echo
[[ "$CODE" == "415" || "$CODE" == "400" ]] || { echo "FAIL: expected 415/400"; exit 1; }

ORDERS_BEFORE=$(curl -sf "$BASE/api/v1/orders" | python3 -c 'import sys,json; print(len(json.load(sys.stdin)))')

echo "== extract sample PDF =="
DRAFT=$(curl -sf "${AUTH_HDR[@]}" -F "file=@${PDF};type=application/pdf" "$BASE/api/v1/extract")
echo "$DRAFT" | python3 -m json.tool
ORDERS_AFTER=$(curl -sf "$BASE/api/v1/orders" | python3 -c 'import sys,json; print(len(json.load(sys.stdin)))')
[[ "$ORDERS_BEFORE" == "$ORDERS_AFTER" ]] || { echo "FAIL: extract persisted an Order"; exit 1; }

echo "== confirm draft =="
CONFIRM=$(python3 - <<PY
import json
draft=json.loads('''$DRAFT''')
draft['source_filename']='DME Patient Demo Document CPAP.fax.pdf'
print(json.dumps(draft))
PY
)
curl -sf -X POST "$BASE/api/v1/orders/confirm" "${AUTH_HDR[@]}" -H 'Content-Type: application/json' \
  -d "$CONFIRM" | python3 -m json.tool

echo
echo "EXTRACT SMOKE OK"
