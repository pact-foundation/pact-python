#!/bin/bash
set -o pipefail



FLASK_APP=pact_provider.py python -m flask run -p 1235 & &>/dev/null

# python pact_provider.py & &>/dev/null
FLASK_PID=$!

function teardown {
  echo "Tearing down Flask server ${FLASK_PID}"

  kill -9 $FLASK_PID
}
trap teardown EXIT

sleep 3

pytest

teardown()