FROM python:3.14.6-alpine3.24

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apk add --no-cache --virtual .build-deps \
        git \
        build-base \
        postgresql-dev \
        musl-dev \
        libffi-dev \
    && git clone https://github.com/gestionentubolsillo/gestionentubolsillo.git . \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps \
    && apk add --no-cache libpq

WORKDIR /app/gestionatubolsillo

RUN python ./manage.py collectstatic --noinput