FROM python:3.7.7-alpine3.11

WORKDIR /home

COPY requirements_dev.txt .

RUN apk add gcc py-pip python-dev libffi-dev openssl-dev gcc libc-dev make

RUN python -m pip install psutil subprocess32
RUN pip install -r requirements_dev.txt

CMD tox -e py37
