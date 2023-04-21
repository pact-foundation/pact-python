ARG PYTHON_VERSION=3.6
FROM python:$PYTHON_VERSION-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update --yes && apt install --yes gcc make

WORKDIR /app
COPY . /app

RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements_dev.txt
RUN python -m flake8
RUN python -m pydocstyle pact
RUN python -m tox -e test

CMD ["sh","-c","python -m tox -e test"]