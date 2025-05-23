# syntax=docker/dockerfile:1.7.1

ARG PYTHON_VERSION=3.12.10

FROM python:${PYTHON_VERSION}-slim-bookworm as builder

ARG DEBIAN_FRONTEND=noninteractive

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get -qq update \
    && apt-get -qq install --no-install-recommends -y \
    build-essential \
    ca-certificates \
    curl \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# venv
ARG UV_PROJECT_ENVIRONMENT="/opt/venv"
ENV VENV="${UV_PROJECT_ENVIRONMENT}"
ENV PATH="$VENV/bin:$PATH"

# uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /src

COPY pyproject.toml .

# optimize startup time, don't use hardlinks, set cache for buildkit mount,
# set uv timeout
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_CACHE_DIR=/opt/uv-cache/
ENV UV_HTTP_TIMEOUT=90

RUN --mount=type=cache,target=/opt/uv-cache,sharing=locked \
    uv venv $UV_PROJECT_ENVIRONMENT \
    && uv pip install -r pyproject.toml

FROM python:${PYTHON_VERSION}-slim-bookworm as deps

ARG DEBIAN_FRONTEND=noninteractive

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get -qq update \
    && apt-get -qq install --no-install-recommends -y \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

FROM deps as runner

ARG WORKDIR="/src"
WORKDIR $WORKDIR

ARG USER_NAME=appuser
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USER_NAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USER_NAME \
    && mkdir -p $WORKDIR \
    && chown -R $USER_NAME:$USER_NAME $WORKDIR

ARG VENV="/opt/venv"
ENV PATH=$VENV/bin:$HOME/.local/bin:$PATH

COPY --from=builder \
    --chown=$USER_NAME:$USER_NAME "$VENV" "$VENV"

COPY --chown=$USER_NAME:$USER_NAME ./src/ ${WORKDIR}/

# standardise on locale, don't generate .pyc, enable tracebacks on seg faults
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1

USER $USER_NAME

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
