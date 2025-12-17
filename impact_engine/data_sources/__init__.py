"""
Data Abstraction Layer - Unified interface for business metrics retrieval.
"""

from .base import DataSourceInterface, DataNotFoundError, TimeRange
from .manager import DataSourceManager
from .interface_catalog_simulator import CatalogSimulatorInterface

__all__ = [
    "DataSourceInterface",
    "DataNotFoundError", 
    "TimeRange",
    "DataSourceManager",
    "CatalogSimulatorInterface",
]