# Heavily inspired by: https://github.com/astral-sh/uv-docker-example/blob/main/multistage.Dockerfile

# Build arguments for flexibility in base image selection
ARG PYTHON_VERSION=3.13
ARG DEBIAN_VERSION=bookworm

# Builder stage - uses uv for faster, more reliable dependency installation
FROM ghcr.io/astral-sh/uv:python${PYTHON_VERSION}-${DEBIAN_VERSION}-slim AS builder

RUN set -ex && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Install dependencies first (better layer caching)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Copy application code
ADD . /app

# Install project in production mode
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


# Final stage - minimal runtime image
FROM python:${PYTHON_VERSION}-slim-${DEBIAN_VERSION} AS runtime

RUN set -ex && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy application from builder stage
COPY --from=builder /app /app

# Create non-root user for security
RUN groupadd -r app && \
    useradd -r -g app app && \
    chown -R app:app /app

# Configure runtime environment
ARG PORT=3000
ENV PATH="/app/.venv/bin:$PATH" \
    PORT=${PORT} \
    PYTHONUNBUFFERED=1

# Expose the application port
EXPOSE ${PORT}

# Switch to non-root user
USER app
SHELL ["/bin/bash", "-c"]

ARG GIT_COMMIT_SHA \
    APP_VERSION
ENV GIT_COMMIT_SHA=${GIT_COMMIT_SHA} \
    APP_VERSION=${APP_VERSION}

CMD python /app/src/python_service_template/app.py
