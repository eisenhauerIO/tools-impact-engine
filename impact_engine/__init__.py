from .run_impact_analysis import evaluate_impact
from .data_sources import DataSourceInterface, DataNotFoundError, DataSourceManager, TimeRange, CatalogSimulatorInterface
from .config import ConfigurationParser, ConfigurationError, parse_config_file
"""
Impact Engine - A tool for measuring causal impact of product interventions.
"""

__version__ = "0.1.0"
__author__ = "Impact Engine Team"



__all__ = [
    "evaluate_impact",
    "DataSourceInterface",
    "DataNotFoundError",
    "DataSourceManager",
    "TimeRange",
    "CatalogSimulatorInterface",
    "ConfigurationParser",
    "ConfigurationError",
    "parse_config_file",
]