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

VERSION=$1
if [ -z "$VERSION" ];
then
  echo "Validating provider locally"

  pact-verifier \
    --provider-base-url=http://localhost:5001 \
    --provider-states-setup-url=http://localhost:5001/_pact/provider_states \
    ../pacts/userserviceclient-userservice.json
else
  echo "Validating against Pact Broker"

  pact-verifier \
    --provider-base-url=http://localhost:5001 \
    --provider-app-version $VERSION \
    --pact-url="http://127.0.0.1/pacts/provider/UserService/consumer/UserServiceClient/latest" \
    --pact-broker-username pactbroker \
    --pact-broker-password pactbroker \
    --publish-verification-results \
    --provider-states-setup-url=http://localhost:5001/_pact/provider_states
fi
