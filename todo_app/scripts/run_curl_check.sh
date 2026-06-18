#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
rm -f todo_app.db

uv run uvicorn entrypoints.run:app --host 127.0.0.1 --port 8000 > server.out.log 2> server.err.log &
SERVER_PID=$!

cleanup() {
  kill "$SERVER_PID" >/dev/null 2>&1 || true
  wait "$SERVER_PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT

for _ in {1..30}; do
  if curl -fsS http://127.0.0.1:8000/docs >/dev/null 2>&1; then
    bash scripts/curl_demo.sh
    exit 0
  fi
  sleep 1
done

echo "Server did not start. stderr:"
cat server.err.log
exit 1
