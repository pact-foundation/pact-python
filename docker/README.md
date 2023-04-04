# Introduction

This is for contributors who want to make changes and test for all different
versions of python currently supported. If you don't want to set up and install
all the different python versions locally (and there are some difficulties with
that) you can just run them in docker using containers.

# Setup

To build a container say for Python 3.11, change to the root directory of the
project and run:

```bash
(export PY=3.11 && docker build --build-arg PY="$PY" --build-arg TOXPY="$(sed 's/\.//' <<< "$PY")" -t pactfoundation:python${PY} -f docker/Dockerfile .)
```

This uses an Alpine based image (currently 3.17), which is available as of
2023-04 for Python versions 3.7 - 3.11.

Note: To run tox, the Python version without the '.' is required, i.e. '311'
instead of '3.11', so some manipulation with `sed` is used to remove the '.'

To build for Python versions which require a different Alpine image, such as if
trying to build against Python 3.6, an extra `ALPINE` arg can be provided:

```bash
(export PY=3.6 && docker build --build-arg PY="$PY" --build-arg TOXPY="$(sed 's/\.//' <<< "$PY")" --build-arg ALPINE=3.15 -t pactfoundation:python${PY} -f docker/Dockerfile .)
```

To then run the tests and exit:

```bash
docker run -it --rm -v "$(pwd)":/home pactfoundation:python3.11
```

If you need to debug you can change the command to:

```bash
docker run -it --rm -v "$(pwd)":/home pactfoundation:python3.11 sh
```

This will open a container with a prompt. From the `/home` location in the
container you can run the same tests manually:

```bash
tox -e py311-{test,install}
```

In all the above if you need to run a different version change
`py311`/`python3.11` where appropriate.  Or you can run the convenience script
to build:

```bash
docker/build.sh 3.11
```

where `3.11` is the python environment version.
