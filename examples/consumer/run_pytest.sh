#!/bin/bash
set -o pipefail

pytest tests --run-broker True --publish-pact 1