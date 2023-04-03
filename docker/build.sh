#!/bin/sh

set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: $0 PYTHON_VERSION [ALPINE_VERSION]"
    echo
    echo "Example:"
    echo "$0 3.11       Build using Python 3.11, default Alpine"
    echo "$0 3.6 3.16   Build using Python 3.6, Alpine 3.15"
    exit 1
fi

PY=$1
ALPINE=${2:-3.17}
echo "Building env for Python: ${PY}, Alpine: ${ALPINE}"

DOCKER_IMAGE="pactfoundation:python${PY}"
DOCKER_FILE="docker/Dockerfile"

docker build \
    --build-arg PY="$PY" \
    --build-arg TOXPY="$(sed 's/\.//' <<< "$PY")" \
    --build-arg ALPINE="${ALPINE}" \
    -t "$DOCKER_IMAGE" -f "$DOCKER_FILE" .

echo
echo "Image successfully built and tagged as: ${DOCKER_IMAGE}"
