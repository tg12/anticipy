"""
Public package metadata and helpers.
"""

from __future__ import annotations

from importlib import metadata

from anticipy.logging_utils import configure_logging

# Configuration
PACKAGE_NAME = "anticipy-sawyer"
FALLBACK_VERSION = "0.2.2"

try:
    __version__ = metadata.version(PACKAGE_NAME)
except metadata.PackageNotFoundError:
    __version__ = FALLBACK_VERSION
