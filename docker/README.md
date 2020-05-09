# Introduction

This is for contributors who want to make changes and test for all different versions of python currently supported. If you don't want to set up and install all the different python versions locally (and there are some difficulties with that) you can just run them in docker using containers.

# Setup

To build a container say for python 3.6 change to the root directory of the project and run

```bash
docker build -t pactfoundation:python36 -f docker/py36.Dockerfile .
```

And then to run you will need:

```bash
docker run  -it -v `pwd`:/home pactfoundation:python36
```

If you need to debug you can change the command to:

```bash
docker run  -it -v `pwd`:/home pactfoundation:python36 sh
```

This will open a container with a prompt. From the /home location in the container you can run

```bash
tox -e py36
```

In all the above if you need to run a different version change py36/python36 where appropriate. Or you can run the convenience script to build:

```bash
docker/build.sh 38
```

where 38 is the python environment version (3.8 in this case)