# Prometheus exporter acceptance tests

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

Welcome to Prometheus exporter acceptance tests! :rocket:

## Features

Runs a job that checks that all metrics provided in the options are present in the Prometheus metrics gathered from the provided exporter url. It returns true if and only if all the metrics are present.

Once finished checking, it creates `prometheus_exporter_acceptance_test_result` metric in the configured pushgateway, being `0` success or `1` failure.

## Deployment

See `openshift` templates.

## Usage

An example of usage:

```bash
export METRICS_URL=http://exporter.url:9102/metrics
export METRICS_NAMES='["http_request_duration_seconds_bucket"]'
export EXPORTER_NAME=test-exporter
export PUSHGATEWAY_USERNAME="a_username"
export PUSHGATEWAY_PASSWORD="a_password"
export PUSHGATEWAY_URL="https://pushgateway.url"

prometheus-exporter-acceptance-tests
```

## Development

Create and maintain a development virtual environment via:

```bash
make dev-env
```

Activate the virtual environment in the current shell via:

```bash
source .venv/bin/activate
```

Run the tests suite via:

```bash
make tests
```

## License

This project is licensed under the terms of the [Apache 2.0 license](/LICENSE).

[pypi-link]:      <https://pypi.org/project/prometheus-exporter-acceptance-tests/>
[pypi-platforms]: <https://img.shields.io/pypi/pyversions/prometheus-exporter-acceptance-tests>
