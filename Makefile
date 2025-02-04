.DEFAULT_GOAL := test

CONTAINER_ENGINE ?= $(shell which podman >/dev/null 2>&1 && echo podman || echo docker)

.PHONY: format
format:
	uv run ruff check
	uv run ruff format

.PHONY: test
test:
	uv run ruff check --no-fix
	uv run ruff format --check
	uv run mypy
	uv run pytest -vv --cov=prometheus_exporter_acceptance_tests --cov-report=term-missing --cov-report xml

.PHONY: build
build:
	$(CONTAINER_ENGINE) build -t prometheus-exporter-acceptance-tests:test --target test .

.PHONY: dev-env
dev-env:
	uv sync
