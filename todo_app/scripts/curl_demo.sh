#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"

echo "POST /users/"
USER_JSON=$(curl -sS -X POST "$BASE_URL/users/" \
  -H "Content-Type: application/json" \
  -d '{"email":"bob@example.com","name":"Bob"}')
echo "$USER_JSON"
USER_ID=$(python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<< "$USER_JSON")

echo
echo "GET /users/$USER_ID"
curl -sS "$BASE_URL/users/$USER_ID"

echo
echo
echo "POST /todos/"
TODO_JSON=$(curl -sS -X POST "$BASE_URL/todos/" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Prepare BASIC-2\",\"user_id\":$USER_ID}")
echo "$TODO_JSON"
TODO_ID=$(python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<< "$TODO_JSON")

echo
echo "GET /todos/?user_id=$USER_ID"
curl -sS "$BASE_URL/todos/?user_id=$USER_ID"

echo
echo
echo "PATCH /todos/$TODO_ID/complete"
curl -sS -X PATCH "$BASE_URL/todos/$TODO_ID/complete"
echo
