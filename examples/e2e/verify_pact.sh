#!/bin/bash
set -o pipefail

python pact_provider.py & &>/dev/null
FLASK_PID=$!
VERSION=$1

function teardown {
  echo "Tearing down Flask server ${FLASK_PID}"
  CHILD=`pgrep -P $FLASK_PID`
  echo "Kill provider app with pid $CHILD"

  kill -9 $CHILD
}
trap teardown EXIT

if [ -x $VERSION ];
then
  echo "Validating provider locally"

  pact-verifier --provider-base-url=http://localhost:5001 \
    --provider-states-setup-url=http://localhost:5001/_pact/provider_states \
    ./pythonclient-pythonservice.json
else

  pact-verifier --provider-base-url=http://localhost:5001 \
    --provider-app-version $VERSION \
    --pact-url="http://127.0.0.1/pacts/provider/UserService/consumer/UserServiceClient/latest" \
    --pact-broker-username pactbroker \
    --pact-broker-password pactbroker \
    --publish-verification-results \
    --provider-states-setup-url=http://localhost:5001/_pact/provider_states
fi
