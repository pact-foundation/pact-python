#!/bin/bash
set -o pipefail

uvicorn src.provider:app --host 0.0.0.0 --port 8080 & &>/dev/null
FASTAPI_PID=$!

function teardown {
  echo "Tearing down FastAPI server: ${FASTAPI_PID}"
  kill -9 $FLASK_PID
}
trap teardown EXIT

sleep 1

pytest