FROM golang:1.17 AS builder

WORKDIR /go/src/litestream

ARG LITESTREAM_VERSION=0.3.8

RUN git clone -b v${LITESTREAM_VERSION} https://github.com/benbjohnson/litestream . 

RUN --mount=type=cache,target=/root/.cache/go-build \
	--mount=type=cache,target=/go/pkg \
	go build -ldflags "-s -w -X 'main.Version=${LITESTREAM_VERSION}' -extldflags '-static'" -tags osusergo,netgo,sqlite_omit_load_extension -o /usr/local/bin/litestream ./cmd/litestream




FROM python:3.10-bullseye as venv

ENV LANG=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV POETRY_VERSION=1.1.14
RUN curl -sSL https://install.python-poetry.org | python -
ENV PATH /root/.poetry/bin:$PATH

WORKDIR /usr/src/app
COPY pyproject.toml poetry.lock ./

RUN python -m venv --copies /usr/src/app/venv
RUN . /usr/src/app/venv/bin/activate && poetry install --no-dev




FROM python:3.10-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /usr/src/app

# https://litestream.io
COPY --from=builder /usr/local/bin/litestream /usr/local/bin/litestream
COPY litestream.yml /etc/
ARG LITESTREAM_BUCKET
RUN sed -i "6s/.*/        bucket: ${LITESTREAM_BUCKET}/" /etc/litestream.yml
ARG LITESTREAM_ENDPOINT
RUN sed -i "8s/.*/        endpoint: ${LITESTREAM_ENDPOINT}/" /etc/litestream.yml

# python dependencies
COPY --from=venv /usr/src/app/venv /usr/src/app/venv
ENV PATH="/usr/src/app/venv/bin:$PATH"

COPY pyproject.toml ./

COPY alembic.ini ./
COPY migrations ./migrations

COPY tests ./tests

COPY app ./app
COPY services ./services

ARG API_VERSION
RUN sed -i "3s/.*/version = \"${API_VERSION}\"/" pyproject.toml

CMD litestream restore -if-db-not-exists -if-replica-exists database.sqlite \
	&& alembic upgrade head \
	# 'litestream replicate' will run the app as configured in litestream.yml
	&& litestream replicate 
