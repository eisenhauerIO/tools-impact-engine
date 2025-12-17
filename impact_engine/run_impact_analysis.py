"""
Impact analysis function for the impact_engine package.
"""
import pandas as pd
from typing import Union, List
from pathlib import Path
from .data_sources import DataSourceManager
from .modeling import ModelingEngine


def evaluate_impact(
    config_path: str, 
    products: Union[List[str], None] = None,
    output_path: str = "impact_analysis_result.csv"
) -> str:
    """
    Evaluate impact using business metrics retrieved through the data abstraction layer
    and modeling layer for statistical analysis.
    
    This function integrates the data abstraction layer with the modeling layer to:
    1. Retrieve business metrics for specified products
    2. Fit statistical models to measure causal impact
    3. Return results from the modeling analysis
    
    Args:
        config_path: Path to configuration file containing data source and model settings
        products: List of product IDs to analyze (optional)
        output_path: Directory path where model results should be saved
    
    Returns:
        str: Path to the saved model results file
    """
    
    # Initialize components with their respective config blocks
    manager = DataSourceManager.from_config_file(config_path)
    modeling_engine = ModelingEngine.from_config_file(config_path)
    
    # Retrieve business metrics using data abstraction layer
    business_metrics = manager.retrieve_metrics(products)
    
    # Fit model using modeling engine (parameters come from config)
    model_results_path = modeling_engine.fit_model(
        data=business_metrics,
        output_path=output_path
    )
    
    return model_results_path
