FROM python:2.7.17-alpine3.11

WORKDIR /home

COPY requirements_dev.txt .

RUN apk add gcc py-pip python-dev libffi-dev openssl-dev gcc libc-dev make

RUN python -m pip install psutil subprocess32
RUN pip install -r requirements_dev.txt
RUN apk --no-cache add ca-certificates wget && \
  wget -q -O /etc/apk/keys/sgerrand.rsa.pub  https://alpine-pkgs.sgerrand.com/sgerrand.rsa.pub && \
  wget https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.25-r0/glibc-2.25-r0.apk && \
  wget https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.25-r0/glibc-bin-2.25-r0.apk && \
  wget https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.25-r0/glibc-i18n-2.25-r0.apk && \
  apk add glibc-bin-2.25-r0.apk glibc-i18n-2.25-r0.apk glibc-2.25-r0.apk


RUN ln -sf /usr/glibc-compat/bin/locale /usr/local/bin/locale

CMD tox -e py27