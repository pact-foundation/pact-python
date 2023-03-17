FROM python:3.7-alpine3.17

ENV PIP_ROOT_USER_ACTION=ignore

WORKDIR /home

COPY requirements_dev.txt .

RUN apk update \
    && apk upgrade \
    && apk add --no-cache --update gcc build-base linux-headers musl-locales \
    && pip install --progress-bar=off --upgrade pip \
    && pip install --progress-bar=off --upgrade psutil \
    && pip install --progress-bar=off --use-pep517 -r requirements_dev.txt

CMD ["tox", "-e", "py37-{test,install}"]
