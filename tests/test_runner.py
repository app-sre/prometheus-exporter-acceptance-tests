from pathlib import Path

import pytest
import responses
from pytest_mock import MockerFixture

from prometheus_exporter_acceptance_tests.runner import CheckResult, check_metrics, run


@pytest.fixture
def text_response() -> str:
    text_path = Path(__file__).parent.resolve() / "fixtures" / "text_response.txt"
    return text_path.read_text()


def test_check_metrics_ok(text_response: str) -> None:
    metrics_names = [
        "http_request_duration_seconds_bucket",
        "msdos_file_access_time_seconds",
        "metric_without_timestamp_and_labels",
    ]
    assert check_metrics(metrics_names, text_response) == CheckResult.OK


def test_check_metrics_none_matching(text_response: str) -> None:
    metrics_names = [
        "http_request",
        "file_access_time",
        "timestamp_and_labels",
        "defintely_not",
    ]
    assert check_metrics(metrics_names, text_response) == CheckResult.NOT_OK


def test_check_metrics_some_matching(text_response: str) -> None:
    metrics_names = ["http_request_duration_seconds_bucket", "defintely_not"]
    assert check_metrics(metrics_names, text_response) == CheckResult.NOT_OK


# test run
@pytest.fixture(autouse=True)
def patch_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EXPORTER_NAME", "test-exporter")
    monkeypatch.setenv("METRICS_URL", "http://a-certain-service:9100/metrics")
    monkeypatch.setenv("METRICS_NAMES", '["http_request_duration_seconds_bucket"]')
    monkeypatch.setenv("PUSHGATEWAY_USERNAME", "a_username")
    monkeypatch.setenv("PUSHGATEWAY_PASSWORD", "a_password")
    monkeypatch.setenv("PUSHGATEWAY_URL", "https://pushgateway.url")


@responses.activate
def test_run(mocker: MockerFixture, text_response: str) -> None:
    # mock the metrics scrape response
    responses.get("http://a-certain-service:9100/metrics", body=text_response)

    # mock the pushgateway response; we cannot use responses mock here since
    # prometheus_client does not use requests library to make HTTP calls.
    mock = mocker.patch(
        "prometheus_exporter_acceptance_tests.runner.basic_auth_handler", autospec=True
    )

    assert run() == CheckResult.OK
    mock.assert_called_once()
    # check main mock call args
    assert (
        mock.call_args.args[0]
        == "https://pushgateway.url/metrics/job/prometheus-exporter-acceptance-tests/exporter_name/test-exporter"
    )
    assert (
        "prometheus_exporter_acceptance_test_result" in mock.call_args.args[4].decode()
    )
    assert mock.call_args.args[5] == "a_username"
    assert mock.call_args.args[6] == "a_password"
