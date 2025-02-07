import logging
import re
from collections.abc import Callable
from enum import IntEnum

import requests
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from prometheus_client.exposition import basic_auth_handler
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class CheckResult(IntEnum):
    OK = 0
    NOT_OK = 1


class Settings(BaseSettings):
    exporter_name: str
    metrics_url: str
    metrics_names: list[str]
    metrics_timeout: int = 30
    pushgateway_username: str
    pushgateway_password: str
    pushgateway_url: str


def check_metrics(metrics_names: list[str], text: str) -> CheckResult:
    metrics_regexps = set()

    for m in metrics_names:
        regex = re.compile("^" + m + r"(\s|{).+")
        metrics_regexps.add(regex)

    for line in text.split("\n"):
        if not line or line.startswith("#"):
            continue

        matching = set()
        for r in metrics_regexps:
            if r.match(line):
                matching.add(r)

        metrics_regexps -= matching

        if not metrics_regexps:
            break

    if metrics_regexps:
        logger.error("some metrics not found: %s", metrics_regexps)
        return CheckResult.NOT_OK

    return CheckResult.OK


def auth_handler(
    url: str,
    method: str,
    timeout: float | None,
    headers: list[tuple[str, str]],
    data: bytes,
) -> Callable[[], None]:
    settings = Settings()  # type: ignore[call-arg]
    return basic_auth_handler(
        url,
        method,
        timeout,
        headers,
        data,
        settings.pushgateway_username,
        settings.pushgateway_password,
    )


def push_metric(url: str, exporter_name: str, check_result: CheckResult) -> None:
    registry = CollectorRegistry()
    result = Gauge(
        name="prometheus_exporter_acceptance_test_result",
        documentation="Prometheus exporter acceptance test result",
        labelnames=["exporter_name"],
        registry=registry,
    )
    result.labels(exporter_name=exporter_name).set(check_result)
    grouping_key = {"exporter_name": exporter_name}

    push_to_gateway(
        gateway=url,
        job="prometheus-exporter-acceptance-tests",
        registry=registry,
        handler=auth_handler,
        grouping_key=grouping_key,
    )


def run() -> CheckResult:
    settings = Settings()  # type: ignore[call-arg]

    logger.info("getting metrics from %s", settings.metrics_url)
    response = requests.get(settings.metrics_url, timeout=settings.metrics_timeout)
    response.raise_for_status()

    logger.info("checking all metrics requested are found in the response")
    check_result = check_metrics(settings.metrics_names, response.text)

    logger.info("Pushing result %d to %s", check_result, settings.pushgateway_url)
    push_metric(settings.pushgateway_url, settings.exporter_name, check_result)

    return check_result
