import logging
import sys

from prometheus_exporter_acceptance_tests.runner import run


def main() -> None:
    log_format = "%(asctime)s %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(format=log_format, level=logging.INFO)
    sys.exit(run())


if __name__ == "__main__":  # pragma: no cover
    main()
