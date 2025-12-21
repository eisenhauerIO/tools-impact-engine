# User Guide

This guide covers installation, getting started, and common usage patterns for Impact Engine.

## Installation

### Basic Installation

```bash
pip install impact-engine
```

### Development Installation

```bash
git clone https://github.com/eisenhauerio/impact-engine.git
cd impact-engine
pip install -e ".[dev]"
```

## Getting Started

### Basic Usage

```python
from impact_engine import evaluate_impact
import pandas as pd

# Define products to analyze
products = pd.DataFrame({
    'product_id': ['prod1', 'prod2'],
    'name': ['Product 1', 'Product 2']
})

# Run impact analysis
result_path = evaluate_impact(
    config_path='config.json',
    products=products,
    storage_url='results/'
)

print(f"Results saved to: {result_path}")
```

### Configuration File

Create a `config.json` file:

```json
{
  "DATA": {
    "TYPE": "simulator",
    "MODE": "rule",
    "SEED": 42,
    "START_DATE": "2024-01-01",
    "END_DATE": "2024-01-31"
  },
  "MEASUREMENT": {
    "MODEL": "interrupted_time_series",
    "PARAMS": {
      "INTERVENTION_DATE": "2024-01-15",
      "DEPENDENT_VARIABLE": "revenue"
    }
  }
}
```

For complete configuration options, see the [Configuration Reference](configuration.md).

## Who Should Use This

### Data Analysts

Measure the causal impact of product interventions on business metrics to provide evidence-based recommendations to stakeholders.

**User Journey:**
1. Create configuration file specifying data source and model parameters
2. Define products to analyze in a DataFrame
3. Run `evaluate_impact()` with configuration and products
4. Review results in standardized JSON format
5. Share findings with stakeholders

### Data Engineers

Integrate custom data sources with Impact Engine so that analysts can access company-specific metrics without modifying core code.

**User Journey:**
1. Implement `MetricsInterface` for company data source
2. Handle connection logic and data transformations
3. Register adapter with `MetricsManager`
4. Test with existing analysis workflows
5. Deploy for analyst use

### Research Scientists

Implement custom statistical models to apply cutting-edge causal inference techniques to business problems.

**User Journey:**
1. Implement `Model` interface for new statistical approach
2. Handle data validation and transformation logic
3. Ensure output matches standardized format
4. Register model with `ModelsManager`
5. Test with existing data pipelines

### Product Managers

Quickly assess the impact of feature launches to make data-driven decisions about product development.

**User Journey:**
1. Request analysis from data team with intervention details
2. Review impact estimates and confidence intervals
3. Compare results across different products or features
4. Use findings to inform future product decisions

## Understanding Output

### Standardized Results Format

All models produce a consistent JSON output:

```json
{
  "model_type": "interrupted_time_series",
  "intervention_date": "2024-01-15",
  "dependent_variable": "revenue",
  "impact_estimates": {
    "intervention_effect": 1250.75,
    "pre_intervention_mean": 5000.0,
    "post_intervention_mean": 6250.75,
    "absolute_change": 1250.75,
    "percent_change": 25.015
  },
  "model_summary": {
    "n_observations": 365,
    "pre_period_length": 180,
    "post_period_length": 185,
    "aic": 4521.2,
    "bic": 4535.8
  }
}
```

### Metrics Data Schema

All metrics adapters return standardized data:

| Column | Type | Description |
|--------|------|-------------|
| `product_id` | str | Unique product identifier |
| `name` | str | Product name |
| `category` | str | Product category |
| `price` | float | Product price |
| `date` | datetime | Observation date |
| `sales_volume` | int | Number of units sold |
| `revenue` | float | Total revenue |
| `inventory_level` | int | Current inventory |
| `customer_engagement` | float | Engagement metric |
| `metrics_source` | str | Source identifier |
| `retrieval_timestamp` | datetime | When data was retrieved |

## Advanced Usage

### Direct Manager Access

For more control, use the managers directly:

```python
from impact_engine.models import ModelsManager
from impact_engine.metrics import MetricsManager

# Initialize managers
metrics_manager = MetricsManager.from_config_file('config.json')
models_manager = ModelsManager.from_config_file('config.json')

# Retrieve metrics
business_metrics = metrics_manager.retrieve_metrics(products)

# Fit model
result_path = models_manager.fit_model(
    data=business_metrics,
    output_path='results/'
)
```

### Custom Metrics Adapter

```python
from impact_engine.metrics import MetricsManager, MetricsInterface

class SalesforceAdapter(MetricsInterface):
    def connect(self, config):
        # Initialize connection
        return True

    def transform_outbound(self, products, start_date, end_date):
        # Transform to Salesforce query format
        return query_params

    def transform_inbound(self, external_data):
        # Transform to standard schema
        return standardized_df

# Register and use
manager = MetricsManager(config)
manager.register_metrics("salesforce", SalesforceAdapter)
```

### Custom Model Registration

```python
from impact_engine.models import ModelsManager, Model

class CausalImpactModel(Model):
    def connect(self, config):
        # Initialize model
        return True

    def transform_outbound(self, data, intervention_date, **kwargs):
        # Transform to model format
        return transformed_data

    def transform_inbound(self, model_results):
        # Transform to standard format
        return standardized_results

    def fit(self, data, intervention_date, output_path, **kwargs):
        # Fit model and save results
        return result_path

# Register and use
manager = ModelsManager(config)
manager.register_model("causal_impact", CausalImpactModel)
```

## Troubleshooting

### Common Issues

**Connection Errors**: Verify data source credentials and network connectivity. Check `validate_connection()` output for diagnostics.

**Data Not Found**: Ensure products exist in the data source for the specified date range. The system returns empty DataFrames with correct schema when no data is found.

**Invalid Configuration**: Configuration is validated at startup. Check error messages for specific parameter guidance.

**Model Fitting Errors**: Verify data meets model requirements using `validate_data()`. Check that the date range includes both pre and post intervention periods.
