#!/bin/bash
set -o pipefail

FLASK_APP=pact_provider.py python -m flask run -p 5001 &
FLASK_PID=$!

function teardown {
  echo "Tearing down Flask server: ${FLASK_PID}"
  kill -9 $FLASK_PID
}
trap teardown EXIT

sleep 1

pytest tests --run-broker True --publish-pact 1