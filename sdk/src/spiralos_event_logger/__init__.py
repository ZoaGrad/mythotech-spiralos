"""Lightweight event logging utilities for SpiraLOS.

This package provides the :class:`EventLogger` along with a JSON-backed
storage adapter and a small CLI helper. It is intentionally standalone and
relies only on the Python standard library so it can be embedded within the
existing monorepo layout without additional packaging metadata.
"""

from .event_logger import EventLogger
from .storage import JSONStorage

__all__ = ["EventLogger", "JSONStorage"]
