#!/bin/bash
set -o pipefail

pytest

# publish to broker assuming broker is active
# pytest tests/consumer/test_message_consumer.py::test_publish_to_broker --publish-pact 2
