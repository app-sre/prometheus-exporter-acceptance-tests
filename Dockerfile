#
# Base image with defaults for all stages
FROM registry.access.redhat.com/ubi9/python-312@sha256:c9a967a1cf947f2374f45d8817f5328f4893be6b0d5749d2287f1db8ed429675 AS base

# Keep this version tag in sync with pyproject.toml or feel free to remove it
LABEL konflux.additional-tags="0.1.0"
COPY LICENSE /licenses/


#
# Builder image
#
FROM base AS builder
COPY --from=ghcr.io/astral-sh/uv:0.8.0@sha256:5778d479c0fd7995fedd44614570f38a9d849256851f2786c451c220d7bd8ccd /uv /bin/uv

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
