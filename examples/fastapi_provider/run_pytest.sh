#!/bin/bash
set -o pipefail

# Unlike in the Flask example, here the FastAPI service is started up as a pytest fixture. This is then including the
# main and pact routes via fastapi_provider.py to run the tests against
if [ "$RUN_BROKER" = '0' ]; then
    pytest tests --publish-pact 1
else
    pytest tests --run-broker True --publish-pact 1
fi