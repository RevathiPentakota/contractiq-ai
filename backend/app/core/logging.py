"""Loguru-based logging configuration."""

import sys

from loguru import logger

from app.core.config import get_settings


def configure_logging() -> None:
    """Set up structured application logging.

    Removes the default Loguru sink and adds a formatted console handler
    whose level is driven by the ``LOG_LEVEL`` environment variable.
    """
    settings = get_settings()

    logger.remove()  # remove default stderr sink

    logger.add(
        sys.stdout,
        level=settings.log_level.upper(),
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> — "
            "<level>{message}</level>"
        ),
        colorize=True,
        backtrace=True,
        diagnose=not get_settings().is_production,
    )


# Re-export `logger` so the rest of the application imports from one place.
__all__ = ["logger", "configure_logging"]
