#!/bin/bash
set -o pipefail

# Run the Flask server, using the pact_provider.py as the app to be able to
# inject the provider_states endpoint
FLASK_APP=tests/pact_provider.py python -m flask run -p 5001 &
FLASK_PID=$!

# Make sure the Flask server is stopped when finished to avoid blocking the port
function teardown {
  echo "Tearing down Flask server: ${FLASK_PID}"
  kill -9 $FLASK_PID
}
trap teardown EXIT

# Wait a little in case Flask isn't quite ready
sleep 1

# Now run the tests
pytest tests --run-broker True --publish-pact 1