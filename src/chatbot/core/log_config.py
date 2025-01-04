import logging
import os
import typing

LogLevel = typing.Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LOG_FORMAT = "%(levelname) -8s %(asctime)s %(name) -50s ln:%(lineno) -5d %(funcName) -35s %(message)s"


def setup_logging(log_location: str, log_level: LogLevel) -> None:
    log_dir = os.path.dirname(log_location)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    file_handler = logging.FileHandler(log_location)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    logging.basicConfig(
        level=log_level,
        format=LOG_FORMAT,
        handlers=[file_handler],
    )
