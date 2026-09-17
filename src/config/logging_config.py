import logging
from pathlib import Path


LOG_DIR = Path("logs")

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


LOG_FILE = LOG_DIR / "application.log"


def setup_logging():

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
        handlers=[
            logging.FileHandler(
                LOG_FILE,
                encoding="utf-8",
            ),
            logging.StreamHandler(),
        ],
        force=True,
    )


def get_logger(name):

    return logging.getLogger(name)