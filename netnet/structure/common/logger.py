import logging
from typing import Dict

from netnet.structure.variables import ascii_colors as colors

FORMATTING: Dict[str, str] = {
    "DEBUG": "{filter}{background}{color}{level}{reset}".format(
        filter=colors.Bold,
        background="",
        color=colors.Magenta,
        level="DEBUG",
        reset=colors.ResetAll,
    ),
    "INFO": "{filter}{background}{color}{level}{reset}".format(
        filter=colors.Bold,
        background="",
        color=colors.Cyan,
        level="INFO",
        reset=colors.ResetAll,
    ),
    "WARNING": "{filter}{background}{color}{level}{reset}".format(
        filter=colors.Bold,
        background=colors.BackgroundLightGray,
        color=colors.Yellow,
        level="WARNING",
        reset=colors.ResetAll,
    ),
    "ERROR": "{filter}{background}{color}{level}{reset}".format(
        filter=colors.Bold,
        background="",
        color=colors.Red,
        level="ERROR",
        reset=colors.ResetAll,
    ),
    "CRITICAL": "{filter}{background}{color}{level}{reset}".format(
        filter=colors.Bold,
        background=colors.BackgroundRed,
        color=colors.Black,
        level="CRITICAL",
        reset=colors.ResetAll,
    ),
}

LOG_FORMAT: str = "%(name)s │ %(levelname)s - %(message)s"


class ColoredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        levelname: str = record.levelname
        name: str = record.name
        record.levelname = f"{str(FORMATTING[levelname])}"
        record.name = f"{colors.DarkGray}{name.split('.')[0]:10s}{colors.ResetAll}"
        return super().format(record)


def setup_logger(level: int = logging.DEBUG) -> logging.Logger:
    logger: logging.Logger = logging.getLogger()
    logger.setLevel(level)

    stream_handler: logging.StreamHandler = logging.StreamHandler()
    stream_handler.setLevel(level)

    formatter: ColoredFormatter = ColoredFormatter(LOG_FORMAT, datefmt="%d.%m %H:%M")
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)

    return logger