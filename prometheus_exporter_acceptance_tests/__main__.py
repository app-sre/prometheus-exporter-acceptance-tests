from rich import print as rich_print

from prometheus_exporter_acceptance_tests.triathlon import race


def main() -> None:
    rich_print(race())


if __name__ == "__main__":  # pragma: no cover
    main()
