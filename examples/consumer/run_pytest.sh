#!/bin/bash
set -o pipefail

if [ "$RUN_BROKER" = '0' ]; then
    pytest tests --publish-pact 1 -rP
else
    pytest tests --run-broker True --publish-pact 1
fi