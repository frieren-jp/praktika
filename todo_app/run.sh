#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo "Starting BASIC-2 ToDo API..."
echo "URL: http://127.0.0.1:8000/docs"
echo

uv sync
uv run uvicorn entrypoints.run:app --host 127.0.0.1 --port 8000
