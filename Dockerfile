#
# Base image with defaults for all stages
FROM registry.access.redhat.com/ubi9/python-312@sha256:7b8f2ee184b40eb160e2c90c240a16fd9ec93279cc1553c0b8b872e2274a139b AS base

# Keep this version tag in sync with pyproject.toml or feel free to remove it
LABEL konflux.additional-tags="0.1.0"
COPY LICENSE /licenses/


#
# Builder image
#
FROM base AS builder
COPY --from=ghcr.io/astral-sh/uv:0.9.7@sha256:ba4857bf2a068e9bc0e64eed8563b065908a4cd6bfb66b531a9c424c8e25e142 /uv /bin/uv

ENV \
    # use venv from ubi image
    UV_PROJECT_ENVIRONMENT=$APP_ROOT \
    # compile bytecode for faster startup
    UV_COMPILE_BYTECODE="true" \
    # disable uv cache. it doesn't make sense in a container
    UV_NO_CACHE=true

COPY pyproject.toml uv.lock ./
# Test lock file is up to date
RUN uv lock --check
# Install the project dependencies
RUN uv sync --frozen --no-install-project --no-group dev

COPY README.md ./
COPY prometheus_exporter_acceptance_tests ./prometheus_exporter_acceptance_tests
RUN uv sync --frozen --no-group dev


#
# Test image
#
FROM builder AS test

COPY Makefile ./
RUN uv sync --frozen

COPY tests ./tests
RUN make test
#
# Production image
#
FROM base AS prod
COPY --from=builder /opt/app-root /opt/app-root
ENTRYPOINT [ "prometheus-exporter-acceptance-tests" ]
