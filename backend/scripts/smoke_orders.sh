#!/usr/bin/env bash
# Quick Order CRUD + activity smoke test (PR2).
#
# Default: spins an ephemeral server on :8010 with a temp DB, then tears it down.
# Against your own server:
#   BASE=http://127.0.0.1:8000 ./backend/scripts/smoke_orders.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

STARTED_SERVER=0
PID=""

cleanup() {
  if [[ "$STARTED_SERVER" -eq 1 && -n "${PID}" ]]; then
    kill "$PID" 2>/dev/null || true
    wait "$PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

if [[ -n "${BASE:-}" ]]; then
  echo "Using existing server at $BASE"
  DB_PATH="${DB_PATH:-}"
else
  PORT="${PORT:-8010}"
  DB_PATH="${DB_PATH:-/tmp/data-extracting-smoke.db}"
  BASE="http://127.0.0.1:${PORT}"
  echo "Starting ephemeral API at $BASE (db=$DB_PATH)"
  rm -f "$DB_PATH"
  # Absolute SQLite URL needs four slashes: sqlite:////tmp/file.db
  DATABASE_URL="sqlite:////${DB_PATH#/}" uv run uvicorn data_extracting_backend.main:app \
    --host 127.0.0.1 --port "$PORT" >/tmp/data-extracting-smoke-uvicorn.log 2>&1 &
  PID=$!
  STARTED_SERVER=1
  for _ in $(seq 1 50); do
    if curl -sf "$BASE/health" >/dev/null 2>&1; then
      break
    fi
    sleep 0.1
  done
  curl -sf "$BASE/health" >/dev/null || {
    echo "Server failed to start. Log:"
    cat /tmp/data-extracting-smoke-uvicorn.log || true
    exit 1
  }
fi

echo "== health =="
curl -sf "$BASE/health"
echo

# Optional: API_KEY=... ./smoke_orders.sh when the server has API_KEY set.
AUTH_HDR=()
if [[ -n "${API_KEY:-}" ]]; then
  AUTH_HDR=(-H "X-API-Key: ${API_KEY}")
fi

echo "== list (expect Buffy seed) =="
curl -sf "$BASE/api/v1/orders" | tee /tmp/smoke-list.json | python3 -m json.tool
echo

echo "== create Willow =="
CREATE=$(curl -sf -X POST "$BASE/api/v1/orders" \
  "${AUTH_HDR[@]}" \
  -H 'Content-Type: application/json' \
  -d '{"first_name":"Willow","last_name":"Rosenberg","date_of_birth":"1981-05-01","source_filename":"willow-chart.pdf"}')
echo "$CREATE" | tee /tmp/smoke-create.json | python3 -m json.tool
OID=$(python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<<"$CREATE")
echo "OID=$OID"

echo "== get =="
curl -sf "$BASE/api/v1/orders/$OID" | python3 -m json.tool
echo

echo "== patch =="
curl -sf -X PATCH "$BASE/api/v1/orders/$OID" \
  "${AUTH_HDR[@]}" \
  -H 'Content-Type: application/json' \
  -d '{"first_name":"Willow Mia"}' | python3 -m json.tool
echo

echo "== reject path filename (expect 422) =="
CODE=$(curl -s -o /tmp/smoke-bad-filename.json -w '%{http_code}' -X POST "$BASE/api/v1/orders" \
  "${AUTH_HDR[@]}" \
  -H 'Content-Type: application/json' \
  -d '{"first_name":"Xander","last_name":"Harris","date_of_birth":"1981-01-01","source_filename":"../evil.pdf"}')
echo "HTTP $CODE"
python3 -m json.tool </tmp/smoke-bad-filename.json
[[ "$CODE" == "422" ]] || { echo "FAIL: expected 422 for bad filename"; exit 1; }

echo "== reject missing fields (expect 422) =="
CODE=$(curl -s -o /tmp/smoke-missing.json -w '%{http_code}' -X POST "$BASE/api/v1/orders" \
  "${AUTH_HDR[@]}" \
  -H 'Content-Type: application/json' \
  -d '{"first_name":"Cordelia"}')
echo "HTTP $CODE"
python3 -m json.tool </tmp/smoke-missing.json
[[ "$CODE" == "422" ]] || { echo "FAIL: expected 422 for missing fields"; exit 1; }

echo "== delete =="
CODE=$(curl -s -o /dev/null -w '%{http_code}' -X DELETE "$BASE/api/v1/orders/$OID" "${AUTH_HDR[@]}")
echo "HTTP $CODE"
[[ "$CODE" == "204" ]] || { echo "FAIL: expected 204 on delete"; exit 1; }

if [[ -n "${DB_PATH}" && -f "$DB_PATH" ]]; then
  echo "== activity_logs =="
  python3 - <<PY
import sqlite3
c = sqlite3.connect("$DB_PATH")
rows = c.execute(
    "select action, method, path, detail from activity_logs order by id"
).fetchall()
for r in rows:
    print(r)
assert rows, "expected activity rows"
actions = {r[0] for r in rows}
for needed in ("list", "create", "get", "update", "delete"):
    assert needed in actions, f"missing activity action: {needed}"
print("activity OK:", sorted(actions))
PY
else
  echo "(skip activity DB assert — external server; check DB manually if needed)"
fi

echo
echo "SMOKE OK"
echo "OpenAPI: $BASE/docs"
