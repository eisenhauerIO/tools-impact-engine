"""
Data Abstraction Layer - Unified interface for business metrics retrieval.

This package provides a plugin-based architecture for retrieving business metrics
from various data sources (simulators, databases, APIs) with a consistent interface.

Main Components:
- DataSourceInterface: Abstract base class for all data sources
- DataSourceManager: Central coordinator for data source operations
- SimulatorDataSource: Built-in simulator data source implementation

External Data Source Registration:
Users can register their own data sources using the direct registration API:

    from impact_engine.data_sources import DataSourceManager
    from my_package.salesforce import SalesforceDataSource
    
    manager = DataSourceManager()
    manager.register_data_source("salesforce", SalesforceDataSource)
"""

# Import all public interfaces for backward compatibility
from .base import DataSourceInterface, DataNotFoundError, TimeRange
from .manager import DataSourceManager
from .simulator import SimulatorDataSource

# Export public API
__all__ = [
    # Core interfaces
    "DataSourceInterface",
    "DataNotFoundError", 
    "TimeRange",
    
    # Main manager
    "DataSourceManager",
    
    # Built-in data sources
    "SimulatorDataSource",
]