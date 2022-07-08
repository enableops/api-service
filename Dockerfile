FROM golang:1.17 AS builder

WORKDIR /go/src/litestream

ARG LITESTREAM_VERSION=0.3.8

RUN git clone -b v${LITESTREAM_VERSION} https://github.com/benbjohnson/litestream . 

RUN --mount=type=cache,target=/root/.cache/go-build \
	--mount=type=cache,target=/go/pkg \
	go build -ldflags "-s -w -X 'main.Version=${LITESTREAM_VERSION}' -extldflags '-static'" -tags osusergo,netgo,sqlite_omit_load_extension -o /usr/local/bin/litestream ./cmd/litestream


FROM python:3.9-slim-bullseye

WORKDIR /usr/src/app

# Massive dependency installer to save layer space
COPY pyproject.toml poetry.lock ./
RUN apt-get update \
		# utility: for compiling https://python-poetry.org
		&& APT_UTILS="curl" \
		# utility: for compiling https://cryptography.io
		&& APT_UTILS="$APT_UTILS make gcc" \
		# Install apt-get deps collectet above
		&& apt-get install --yes --no-install-recommends $APT_DEPS $APT_UTILS \
	# Install poetry https://python-poetry.org
	&& curl -sSL \
		https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py \
		| python - \
	# Install python packages
	&& $HOME/.poetry/bin/poetry config virtualenvs.create false \
		&& $HOME/.poetry/bin/poetry install --no-dev --no-interaction --no-ansi \
	# Uninstall poetry https://python-poetry.org
	&& curl -sSL \
		https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py \
		| POETRY_UNINSTALL=1 python - \
		&& pip cache purge \
		&& rm -rf ~/.cache/pypoetry \
		&& rm -rf ~/.cache/pip \
	# Uninstall apt-get deps and clean package lists
	&& apt-get --yes --purge remove $APT_UTILS \
		&& apt-get --yes clean autoclean \
		&& apt-get --yes autoremove \
		&& rm -rf /var/lib/apt/lists/*

# https://litestream.io
COPY --from=builder /usr/local/bin/litestream /usr/local/bin/litestream

COPY litestream.yml /etc/
COPY alembic.ini ./
COPY migrations ./migrations
COPY tests ./tests
COPY app ./app
COPY services ./services

ARG API_VERSION
RUN sed -i "3s/.*/version = \"${API_VERSION}\"/" pyproject.toml

ARG LITESTREAM_BUCKET
RUN sed -i "6s/.*/        bucket: ${LITESTREAM_BUCKET}/" /etc/litestream.yml

ARG LITESTREAM_ENDPOINT
RUN sed -i "8s/.*/        endpoint: ${LITESTREAM_ENDPOINT}/" /etc/litestream.yml

CMD litestream restore -if-db-not-exists -if-replica-exists database.sqlite \
	&& alembic upgrade head \
	# 'litestream replicate' will run the app as configured in litestream.yml
	&& litestream replicate 
