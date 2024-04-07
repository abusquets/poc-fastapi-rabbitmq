ARG PYTHON_VERSION=3.12.1

FROM python:${PYTHON_VERSION}-bookworm AS build-image

# Update and install dependencies
RUN apt-get -qq update && apt-get -qq install lsb-release && apt-get -qq install git

RUN mkdir -m 700 /root/.ssh; \
    touch -m 600 /root/.ssh/known_hosts; \
    ssh-keyscan github.com > /root/.ssh/known_hosts

# poetry
WORKDIR /srv
RUN pip install poetry==1.4.2
COPY poetry.lock pyproject.toml /srv/
ARG POETRY_DEV=false
RUN --mount=type=ssh,id=default --mount=type=cache,mode=0777,target=/root/.cache/pip \
    poetry export -f requirements.txt -o requirements.txt --without-hashes $(test "$POETRY_DEV" = "true" && echo "--with dev,test") \
    && python -m venv venv && . venv/bin/activate && pip install -r requirements.txt
# end poetry

# Optimized build
FROM python:${PYTHON_VERSION}-slim-bookworm
ARG WAIT_BIN=wait

# Add wait script
ADD "https://github.com/ufoscout/docker-compose-wait/releases/download/2.12.0/${WAIT_BIN}" /wait
RUN chmod +x /wait
# wait script

COPY --from=build-image /srv/venv/ /srv/venv/

ENV PATH="/srv/venv/bin:$PATH"

# Set working directory to function root directory
WORKDIR /app

# Copy the rest of the working directory contents into the container at /app
COPY src/ .
