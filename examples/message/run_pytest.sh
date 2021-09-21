#!/bin/bash
set -o pipefail

pytest --run-broker True --publish-pact 2

# publish to broker assuming broker is active
# pytest tests/consumer/test_message_consumer.py::test_publish_to_broker --publish-pact 2
