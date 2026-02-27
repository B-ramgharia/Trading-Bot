"""
logging_config.py
-----------------
Configures structured logging for the trading bot.
Logs are written to both the console (INFO+) and a rotating log file (DEBUG+).
"""

import logging
import logging.handlers
import os
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_FILE = LOG_DIR / "trading_bot.log"

_configured = False


def setup_logging(log_level: str = "DEBUG") -> logging.Logger:
    """
    Set up root logger with console + rotating file handler.

    Parameters
    ----------
    log_level : str
        Minimum log level for the file handler (default: DEBUG).

    Returns
    -------
    logging.Logger
        Configured root logger.
    """
    global _configured
    if _configured:
        return logging.getLogger("trading_bot")

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger("trading_bot")
    root_logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ── Console handler (INFO and above) ──────────────────────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(fmt)

    # ── Rotating file handler (DEBUG and above, max 5 MB × 3 backups) ────────
    file_handler = logging.handlers.RotatingFileHandler(
        filename=LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(getattr(logging, log_level.upper(), logging.DEBUG))
    file_handler.setFormatter(fmt)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    _configured = True
    root_logger.info("Logging initialised → %s", LOG_FILE)
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Return a child logger of the 'trading_bot' root logger."""
    return logging.getLogger(f"trading_bot.{name}")
