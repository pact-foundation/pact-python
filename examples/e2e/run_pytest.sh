#!/bin/bash
set -o pipefail

FLASK_APP=pact_provider.py python -m flask run -p 5001 & &>/dev/null

FLASK_PID=$!

teardown() {
  echo "Tearing down Flask server ${FLASK_PID}";
  kill -9 $FLASK_PID;
};
trap teardown EXIT

sleep 3

pytest --publish-pact 1

teardown

