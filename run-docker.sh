#!/bin/bash

for arch in arm64 amd64; do
    # for version in 3.6; do 
    for version in 3.7 3.8 3.9 3.10 3.11; do
        docker build -t python-$arch-$version --build-arg PYTHON_VERSION=$version --platform=linux/$arch .
        docker run -it --rm python-$arch-$version
    done
done
