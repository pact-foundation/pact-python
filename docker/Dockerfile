ARG PY
ARG ALPINE=3.17
FROM python:${PY}-alpine${ALPINE}

ENV PIP_ROOT_USER_ACTION=ignore

WORKDIR /home

COPY requirements_dev.txt .

RUN apk update \
    && apk upgrade \
    && apk add --no-cache --update gcc build-base linux-headers musl-locales \
    && pip install --progress-bar=off --upgrade pip \
    && pip install --progress-bar=off --upgrade psutil \
    && pip install --progress-bar=off --use-pep517 -r requirements_dev.txt

# We can't do ENV manipulation to remove the . for tox, so need another var
ARG TOXPY
ENV TOXPY="${TOXPY}"
CMD ["sh", "-c", "tox -e py${TOXPY}-{test,install}"]
