#!/bin/bash
set -o pipefail

# Run the FastAPI server, using the pact_provider.py as the app to be able to
# inject the provider_states endpoint
uvicorn tests.pact_provider:app & &>/dev/null
FASTAPI_PID=$!

# Make sure the FastAPI server is stopped when finished to avoid blocking the port
function teardown {
  echo "Tearing down FastAPI server ${FASTAPI_PID}"
  kill -9 $FASTAPI_PID
}
trap teardown EXIT

# Wait a little in case FastAPI isn't quite ready
sleep 1

VERSION=$1
if [ -x $VERSION ];
then
  echo "Validating provider locally"

  pact-verifier --provider-base-url=http://localhost:8000 \
    --provider-states-setup-url=http://localhost:8000/_pact/provider_states \
    ../pacts/userserviceclient-userservice.json
else
  echo "Validating against Pact Broker"

  pact-verifier --provider-base-url=http://localhost:8000 \
    --provider-app-version $VERSION \
    --pact-url="http://127.0.0.1/pacts/provider/UserService/consumer/UserServiceClient/latest" \
    --pact-broker-username pactbroker \
    --pact-broker-password pactbroker \
    --publish-verification-results \
    --provider-states-setup-url=http://localhost:8000/_pact/provider_states
fi