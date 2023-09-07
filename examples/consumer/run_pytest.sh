#!/bin/bash
set -o pipefail

# PODMAN:- Log verbosely when failing tests to work out whats going on!
pytest tests --run-broker True --publish-pact 1 -rP
