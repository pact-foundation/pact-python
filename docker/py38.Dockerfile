FROM python:3.8-alpine3.11

WORKDIR /home

COPY requirements_dev.txt .

RUN apk update
RUN apk upgrade

RUN apk add gcc py-pip python-dev libffi-dev openssl-dev gcc libc-dev bash make

RUN python -m pip install psutil
RUN pip install -r requirements_dev.txt

CMD tox -e py38
