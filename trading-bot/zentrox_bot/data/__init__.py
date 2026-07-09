"""Data ingestion layer (ingesta de datos)."""

from .base import DataFeed
from .synthetic import SyntheticFeed
from .csv_feed import CSVFeed

__all__ = ["DataFeed", "SyntheticFeed", "CSVFeed"]
