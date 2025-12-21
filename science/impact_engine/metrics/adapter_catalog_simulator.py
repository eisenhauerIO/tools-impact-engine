"""
Catalog Simulator Adapter - adapts online_retail_simulator package to MetricsInterface.
"""

import pandas as pd
from typing import Dict, List, Any
from datetime import datetime

from .base import MetricsInterface


class CatalogSimulatorAdapter(MetricsInterface):
    """Adapter for catalog simulator that implements MetricsInterface."""
    
    def __init__(self):
        """Initialize the CatalogSimulatorAdapter."""
        self.is_connected = False
        self.config = None
        self.available_metrics = ['sales_volume', 'revenue', 'inventory_level', 'customer_engagement']
    
    def connect(self, config: Dict[str, Any]) -> bool:
        """Establish connection to the catalog simulator."""
        # Validate mode
        mode = config.get('mode', 'rule')
        if mode not in ['rule', 'ml']:
            raise ValueError(f"Invalid simulator mode '{mode}'. Must be 'rule' or 'ml'")
        
        # Validate seed
        seed = config.get('seed', 42)
        if not isinstance(seed, int) or seed < 0:
            raise ValueError("Simulator seed must be a non-negative integer")
        
        self.config = {'mode': mode, 'seed': seed}
        self.is_connected = True
        return True
    
    def retrieve_business_metrics(self, products: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
        """Retrieve business metrics for specified products using catalog simulator."""
        if not self.is_connected:
            raise ConnectionError("Not connected to simulator. Call connect() first.")

        if products is None or len(products) == 0:
            raise ValueError("Products DataFrame cannot be empty")

        try:
            from online_retail_simulator.core import RuleBackend

            # Transform input to simulator format
            transformed_input = self.transform_outbound(products, start_date, end_date)

            # Create RuleBackend with config
            backend = RuleBackend(transformed_input["rule_config"])

            # Generate metrics using the backend
            raw_metrics = backend.simulate_metrics(transformed_input["product_characteristics"])

            # Transform response to impact engine format
            return self.transform_inbound(raw_metrics)

        except ImportError as e:
            raise ConnectionError(f"online_retail_simulator package not available: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve metrics: {e}")
    

    
    def validate_connection(self) -> bool:
        """Validate that the catalog simulator connection is active and functional."""
        if not self.is_connected:
            return False

        try:
            from online_retail_simulator.core import RuleBackend
            return True
        except ImportError:
            return False
    
    def transform_outbound(self, products: pd.DataFrame, start_date: str, end_date: str) -> Dict[str, Any]:
        """Transform impact engine format to catalog simulator format."""
        # Prepare products DataFrame for simulator
        product_characteristics = products.copy()

        # Handle product_id → asin mapping (RuleBackend expects 'asin')
        if 'product_id' in product_characteristics.columns:
            product_characteristics['asin'] = product_characteristics['product_id']
        elif 'asin' not in product_characteristics.columns:
            # Try to find a suitable ID column
            id_columns = [col for col in product_characteristics.columns
                        if 'id' in col.lower() or col.lower() in ['product', 'sku', 'code']]
            if id_columns:
                product_characteristics['asin'] = product_characteristics[id_columns[0]]
            else:
                # If no ID column found, create one from the index
                product_characteristics['asin'] = product_characteristics.index.astype(str)

        # Add default values for missing required columns
        if 'name' not in product_characteristics.columns:
            product_characteristics['name'] = product_characteristics['asin'].apply(lambda x: f'Product {x}')
        if 'category' not in product_characteristics.columns:
            product_characteristics['category'] = 'Electronics'  # Default category
        if 'price' not in product_characteristics.columns:
            product_characteristics['price'] = 100.0  # Default price

        # Build RuleBackend config structure
        rule_config = {
            "CHARACTERISTICS": {
                "FUNCTION": "simulate_characteristics_rule_based",
                "PARAMS": {"num_products": len(product_characteristics)}
            },
            "METRICS": {
                "FUNCTION": "simulate_metrics_rule_based",
                "PARAMS": {
                    "date_start": start_date,
                    "date_end": end_date,
                    "sale_prob": 0.7,
                    "seed": self.config['seed'],
                    "granularity": "daily",
                    "impression_to_visit_rate": 0.15,
                    "visit_to_cart_rate": 0.25,
                    "cart_to_order_rate": 0.80
                }
            }
        }

        return {
            "product_characteristics": product_characteristics,
            "rule_config": rule_config
        }
    
    def transform_inbound(self, external_data: Any) -> pd.DataFrame:
        """Transform catalog simulator response to impact engine format."""
        if not isinstance(external_data, pd.DataFrame):
            raise ValueError("Expected pandas DataFrame from catalog simulator")

        raw_metrics = external_data

        if raw_metrics.empty:
            return pd.DataFrame(columns=[
                'product_id', 'name', 'category', 'price', 'date',
                'sales_volume', 'revenue', 'inventory_level', 'customer_engagement',
                'metrics_source', 'retrieval_timestamp'
            ])

        standardized = raw_metrics.copy()

        # Map asin → product_id (RuleBackend uses 'asin')
        if 'asin' in standardized.columns:
            standardized['product_id'] = standardized['asin']
            standardized.drop('asin', axis=1, inplace=True)

        # Ensure date column is datetime
        if 'date' in standardized.columns:
            standardized['date'] = pd.to_datetime(standardized['date'])

        # Map 'ordered_units' to 'sales_volume' (RuleBackend output)
        if 'ordered_units' in standardized.columns:
            standardized['sales_volume'] = standardized['ordered_units']
            standardized.drop('ordered_units', axis=1, inplace=True)
        # Also handle legacy 'quantity' column
        elif 'quantity' in standardized.columns:
            standardized['sales_volume'] = standardized['quantity']
            standardized.drop('quantity', axis=1, inplace=True)

        # Add missing standardized fields
        if 'inventory_level' not in standardized.columns:
            max_inventory = 1000
            standardized['inventory_level'] = (max_inventory - (standardized.get('sales_volume', 0) * 10)).clip(lower=0).astype(int)

        if 'customer_engagement' not in standardized.columns:
            # Customer engagement based on sales activity
            sales_col = standardized.get('sales_volume', pd.Series([0] * len(standardized)))
            max_sales = sales_col.max() if len(sales_col) > 0 else 1
            if max_sales > 0:
                standardized['customer_engagement'] = (sales_col / max_sales).clip(upper=1.0)
            else:
                standardized['customer_engagement'] = 0.0
            standardized['customer_engagement'] = standardized['customer_engagement'].fillna(0.0)

        # Add metadata fields
        standardized['metrics_source'] = 'catalog_simulator'
        standardized['retrieval_timestamp'] = datetime.now()

        # Ensure proper data types
        if 'price' in standardized.columns:
            standardized['price'] = pd.to_numeric(standardized['price'], errors='coerce')
        if 'revenue' in standardized.columns:
            standardized['revenue'] = pd.to_numeric(standardized['revenue'], errors='coerce')
        if 'sales_volume' in standardized.columns:
            standardized['sales_volume'] = pd.to_numeric(standardized['sales_volume'], errors='coerce').fillna(0).astype(int)

        # Reorder columns to match standard schema
        column_order = [
            'product_id', 'name', 'category', 'price', 'date',
            'sales_volume', 'revenue', 'inventory_level', 'customer_engagement',
            'metrics_source', 'retrieval_timestamp'
        ]
        available_columns = [col for col in column_order if col in standardized.columns]
        return standardized[available_columns]
    
