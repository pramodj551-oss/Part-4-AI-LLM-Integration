"""
==========================================================
Incident Knowledge Assistant (RAG)

logger.py

Author : Pramod Prakash Jadhav
==========================================================

Centralized logging configuration.
"""

import logging
from pathlib import Path

from src.config import (
    LOGS_DIR,
    LOG_FILE,
)

# ==========================================================
# Create Logs Directory
# ==========================================================

Path(LOGS_DIR).mkdir(
    parents=True,
    exist_ok=True
)

# ==========================================================
# Logger Configuration
# ==========================================================

LOGGER_NAME = "IncidentKnowledgeAssistant"

logger = logging.getLogger(
    LOGGER_NAME
)

logger.setLevel(logging.INFO)

if not logger.handlers:

    formatter = logging.Formatter(

        fmt=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),

        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File Handler
    file_handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8"
    )

    file_handler.setFormatter(
        formatter
    )

    file_handler.setLevel(
        logging.INFO
    )

    # Console Handler
    console_handler = logging.StreamHandler()

    console_handler.setFormatter(
        formatter
    )

    console_handler.setLevel(
        logging.INFO
    )

    logger.addHandler(
        file_handler
    )

    logger.addHandler(
        console_handler
)
  # ==========================================================
# Get Logger
# ==========================================================

def get_logger():
    """
    Return the configured application logger.

    Returns
    -------
    logging.Logger
        Configured logger instance.
    """

    return logger


# ==========================================================
# Set Log Level
# ==========================================================

def set_log_level(
    level=logging.INFO
):
    """
    Update logger level.

    Parameters
    ----------
    level : int
        Python logging level.
    """

    logger.setLevel(level)

    for handler in logger.handlers:

        handler.setLevel(level)

    logger.info(
        f"Logger level changed to: "
        f"{logging.getLevelName(level)}"
    )


# ==========================================================
# Execution Check
# ==========================================================

if __name__ == "__main__":

    app_logger = get_logger()

    app_logger.info("=" * 60)
    app_logger.info("Logger Demonstration")
    app_logger.info("=" * 60)

    app_logger.debug(
        "Debug message"
    )

    app_logger.info(
        "Info message"
    )

    app_logger.warning(
        "Warning message"
    )

    app_logger.error(
        "Error message"
    )

    app_logger.info("=" * 60)
    app_logger.info(
        "logger.py executed successfully."
    )
    app_logger.info("=" * 60)
