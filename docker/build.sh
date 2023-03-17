#!/bin/sh

set -eo pipefail

if [ $# -ne 1 ]; then
    echo "$0: usage: build.sh 37|38|39|310|311"
    exit 1
fi
DOCKER_ENV=$1
echo "Building env ${DOCKER_ENV}"

DOCKER_IMAGE="pactfoundation:python${DOCKER_ENV}"
DOCKER_FILE="docker/py${DOCKER_ENV}.Dockerfile"

docker build -t "$DOCKER_IMAGE" -f "$DOCKER_FILE" .
