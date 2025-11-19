# Heavily inspired by: https://github.com/astral-sh/uv-docker-example/blob/main/multistage.Dockerfile

# Build arguments for flexibility in base image selection
ARG PYTHON_VERSION=3.13
ARG DEBIAN_VERSION=bookworm
ARG UV_VERSION=0.5.11

# Builder stage - uses uv for faster, more reliable dependency installation
FROM ghcr.io/astral-sh/uv:${UV_VERSION}-python${PYTHON_VERSION}-${DEBIAN_VERSION}-slim AS builder

# Security: Run with minimal privileges and optimized system packages
RUN set -ex && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/* /tmp/* /var/tmp/*

# UV configuration for optimal build performance
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    UV_NO_PROGRESS=1

WORKDIR /app

# Install dependencies first (maximizes layer caching)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Copy only necessary application files
COPY --link src /app/src
COPY --link pyproject.toml README.md /app/

# Install project in production mode
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


# Final stage - minimal runtime image
FROM python:${PYTHON_VERSION}-slim-${DEBIAN_VERSION} AS runtime

# Image metadata
LABEL org.opencontainers.image.title="python-service-template" \
      org.opencontainers.image.description="Production-ready FastAPI service template" \
      org.opencontainers.image.vendor="ntphiep" \
      org.opencontainers.image.source="https://github.com/ntphiep/fastapi-uv-servive-template"

# Security and optimization: Minimal system packages
RUN set -ex && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/* /tmp/* /var/tmp/* /root/.cache

# Create non-root user first (better layer ordering)
RUN groupadd -r app --gid=1000 && \
    useradd -r -g app --uid=1000 --home-dir=/app --shell=/bin/bash app

WORKDIR /app

# Copy virtual environment and application from builder
COPY --from=builder --chown=app:app --link /app/.venv /app/.venv
COPY --from=builder --chown=app:app --link /app/src /app/src
COPY --from=builder --chown=app:app --link /app/pyproject.toml /app/README.md /app/

# Build arguments with defaults
ARG PORT=3000
ARG GIT_COMMIT_SHA=dev
ARG APP_VERSION=0.1.0

# Runtime environment configuration
ENV PATH="/app/.venv/bin:$PATH" \
    PORT=${PORT} \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    GIT_COMMIT_SHA=${GIT_COMMIT_SHA} \
    APP_VERSION=${APP_VERSION}

# Security: Switch to non-root user
USER app

# Expose the application port
EXPOSE ${PORT}

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/').read()" || exit 1

# Use exec form for proper signal handling
CMD ["python", "/app/src/python_service_template/app.py"]
