"""
Data Source Manager for coordinating data source operations.
"""

import pandas as pd
from typing import Dict, List, Any, Optional

from .base import DataSourceInterface, TimeRange
from .simulator import SimulatorDataSource
from ..config import ConfigurationParser


class DataSourceManager:
    """Central coordinator for data source management."""
    
    def __init__(self):
        """Initialize the DataSourceManager."""
        self.config_parser = ConfigurationParser()
        self.data_source_registry: Dict[str, type] = {}
        self.current_config: Optional[Dict[str, Any]] = None
        self._register_builtin_data_sources()
    
    def _register_builtin_data_sources(self) -> None:
        """Register built-in data source implementations."""
        self.register_data_source("simulator", SimulatorDataSource)
    
    def register_data_source(self, source_type: str, source_class: type) -> None:
        """Register a new data source implementation."""
        if not issubclass(source_class, DataSourceInterface):
            raise ValueError(f"Data source class {source_class.__name__} must implement DataSourceInterface")
        self.data_source_registry[source_type] = source_class
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load and validate configuration from file."""
        self.current_config = self.config_parser.parse_config(config_path)
        return self.current_config
    
    def get_data_source(self, source_type: Optional[str] = None) -> DataSourceInterface:
        """Get data source implementation based on configuration or specified type."""
        if source_type is None:
            if self.current_config is None:
                raise ValueError("No configuration loaded. Call load_config() first or provide source_type.")
            source_type = self.current_config["DATA"]["TYPE"]
        
        if source_type not in self.data_source_registry:
            raise ValueError(f"Unknown data source type '{source_type}'. Available: {list(self.data_source_registry.keys())}")
        
        data_source = self.data_source_registry[source_type]()
        
        if self.current_config is not None:
            # Build connection config from DATA section
            data_config = self.current_config["DATA"]
            connection_config = {
                "mode": data_config.get("MODE", "rule"),
                "seed": data_config.get("SEED", 42)
            }
            if not data_source.connect(connection_config):
                raise ConnectionError(f"Failed to connect to {source_type} data source")
        
        return data_source
    
    def retrieve_metrics(self, products: List[str]) -> pd.DataFrame:
        """Retrieve business metrics for specified products using DATA section date range."""
        # Get date range from DATA section
        data_config = self.current_config["DATA"]
        start_date = data_config["START_DATE"]
        end_date = data_config["END_DATE"]
        
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
    
    def get_current_config(self) -> Optional[Dict[str, Any]]:
        """Get the currently loaded configuration."""
        return self.current_config