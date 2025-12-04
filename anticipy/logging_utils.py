"""
Logging helpers for anticipy.
"""

from __future__ import annotations

import logging

# Configuration
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"


def configure_logging(level: int = DEFAULT_LOG_LEVEL, fmt: str = DEFAULT_LOG_FORMAT) -> None:
    """
    Configure root logging with a consistent formatter.

    Parameters
    ----------
    level:
        Logging level for the root logger.
    fmt:
        Format string applied to log records.
    """
    logging.basicConfig(level=level, format=fmt, force=False)
