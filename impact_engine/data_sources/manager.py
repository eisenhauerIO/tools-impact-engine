"""
Data Source Manager for coordinating data source operations.
"""

import pandas as pd
from typing import Dict, List, Any, Optional

from .base import DataSourceInterface, TimeRange
from .interface_catalog_simulator import CatalogSimulatorInterface
from ..config import ConfigurationParser


class DataSourceManager:
    """Central coordinator for data source management."""
    
    def __init__(self, data_config: Dict[str, Any]):
        """Initialize the DataSourceManager with DATA configuration block."""
        self.data_source_registry: Dict[str, type] = {}
        self.data_config = data_config
        self._register_builtin_data_sources()
        
        # Validate the data config
        self._validate_data_config(data_config)
    
    @classmethod
    def from_config_file(cls, config_path: str) -> 'DataSourceManager':
        """Create DataSourceManager from config file, extracting DATA block."""
        config_parser = ConfigurationParser()
        full_config = config_parser.parse_config(config_path)
        return cls(full_config["DATA"])
    
    def _register_builtin_data_sources(self) -> None:
        """Register built-in data source implementations."""
        self.register_data_source("simulator", CatalogSimulatorInterface)
    
    def register_data_source(self, source_type: str, source_class: type) -> None:
        """Register a new data source implementation."""
        if not issubclass(source_class, DataSourceInterface):
            raise ValueError(f"Data source class {source_class.__name__} must implement DataSourceInterface")
        self.data_source_registry[source_type] = source_class
    
    def _validate_data_config(self, data_config: Dict[str, Any]) -> None:
        """Validate DATA configuration block."""
        required_fields = ["TYPE", "START_DATE", "END_DATE"]
        for field in required_fields:
            if field not in data_config:
                raise ValueError(f"Missing required field '{field}' in DATA configuration")
        
        # Validate date format
        from datetime import datetime
        try:
            start_date = datetime.strptime(data_config["START_DATE"], "%Y-%m-%d")
            end_date = datetime.strptime(data_config["END_DATE"], "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(f"Invalid date format in DATA configuration. Expected YYYY-MM-DD: {e}")
        
        # Validate date consistency
        if start_date > end_date:
            raise ValueError(f"START_DATE must be before or equal to END_DATE in DATA configuration")
    
    def get_data_source(self, source_type: Optional[str] = None) -> DataSourceInterface:
        """Get data source implementation based on configuration or specified type."""
        if source_type is None:
            source_type = self.data_config["TYPE"]
        
        if source_type not in self.data_source_registry:
            raise ValueError(f"Unknown data source type '{source_type}'. Available: {list(self.data_source_registry.keys())}")
        
        data_source = self.data_source_registry[source_type]()
        
        # Build connection config from DATA configuration
        connection_config = {
            "mode": self.data_config.get("MODE", "rule"),
            "seed": self.data_config.get("SEED", 42)
        }
        if not data_source.connect(connection_config):
            raise ConnectionError(f"Failed to connect to {source_type} data source")
        
        return data_source
    
    def retrieve_metrics(self, products: List[str]) -> pd.DataFrame:
        """Retrieve business metrics for specified products using DATA configuration date range."""
        if not products:
            raise ValueError("Products list cannot be empty")
        
        # Get date range from DATA configuration
        start_date = self.data_config["START_DATE"]
        end_date = self.data_config["END_DATE"]
        
        # Get data source
        data_source = self.get_data_source()
        
        return data_source.retrieve_business_metrics(
            products=products,
            start_date=start_date,
            end_date=end_date
        )
    
    def get_available_data_sources(self) -> List[str]:
        """Get list of available data source types."""
        return list(self.data_source_registry.keys())
    
    def get_available_data_sources(self) -> List[str]:
        """Get list of available data source types."""
        return list(self.data_source_registry.keys())
    
    def get_current_config(self) -> Optional[Dict[str, Any]]:
        """Get the currently loaded configuration."""
        return self.current_config