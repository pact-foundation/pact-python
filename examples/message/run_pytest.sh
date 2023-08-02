#!/bin/bash
set -o pipefail

if [ "$RUN_BROKER" = '0' ]; then
    pytest tests --publish-pact 2
else
    pytest tests --run-broker True --publish-pact 2
fi

# publish to broker assuming broker is active
# pytest tests/consumer/test_message_consumer.py::test_publish_to_broker --publish-pact 2
