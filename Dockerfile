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

COPY alembic.ini ./
COPY migrations ./migrations
COPY tests ./tests
COPY app ./app
COPY services ./services

ARG API_VERSION
RUN sed -i "3s/.*/version = \"${API_VERSION}\"/" pyproject.toml

CMD alembic upgrade head \
	&& uvicorn app.main:app --reload --proxy-headers --host 0.0.0.0 --port 8000
