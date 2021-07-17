FROM python:3.7.9-alpine3.11

WORKDIR /home

COPY requirements_dev.txt .

RUN apk update
RUN apk upgrade

RUN apk add gcc py-pip python-dev libffi-dev openssl-dev gcc libc-dev bash cmake make
ENV MUSL_LOCALE_DEPS musl-dev gettext-dev libintl

RUN apk add --no-cache \
    $MUSL_LOCALE_DEPS \
    && wget https://gitlab.com/rilian-la-te/musl-locales/-/archive/master/musl-locales-master.zip \
    && unzip musl-locales-master.zip \
      && cd musl-locales-master \
      && cmake -DLOCALE_PROFILE=OFF -D CMAKE_INSTALL_PREFIX:PATH=/usr . && make && make install \
      && cd .. && rm -r musl-locales-master

RUN python -m pip install psutil
RUN pip install -r requirements_dev.txt

CMD tox -e py37
