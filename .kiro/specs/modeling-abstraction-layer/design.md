# Design Document: Modeling Abstraction Layer

## Overview

The modeling abstraction layer provides a unified interface for statistical impact measurement approaches, starting with interrupted time series analysis using statsmodels. This layer integrates with the existing data abstraction layer to provide end-to-end impact analysis capabilities.

The design focuses on standardizing the interface and output format, not the impact measurements themselves. Each statistical model produces its own specific measurements, but these are returned through a consistent interface structure.

The design follows the same plugin-based architecture pattern as the data abstraction layer, allowing for future extension with additional modeling approaches while maintaining a consistent interface.

## Architecture

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│ evaluate_impact     │───▶│ ModelingEngine       │───▶│ ModelInterface      │
│ (existing)          │    │                      │    │                     │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
           │                          │                           ▲
           ▼                          ▼                           │
┌─────────────────────┐    ┌──────────────────────┐              │
│ DataSourceManager   │    │ Model Configuration  │              │
│ (existing)          │    │ Parser               │              │
└─────────────────────┘    └──────────────────────┘              │
                                                                  │
                           ┌─────────────────┬─────────────────┼─────────────────┐
                           ▼                 ▼                 ▼                 ▼
                   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
                   │ Interrupted  │  │ Causal       │  │ Regression   │  │ Custom       │
                   │ Time Series  │  │ Impact       │  │ Discontinuity│  │ Model        │
                   └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
```

The modeling layer sits between the existing impact analysis function and provides statistical modeling capabilities. It receives preprocessed data from the data abstraction layer and returns standardized impact estimates.

## Components and Interfaces

### ModelInterface (Abstract Base Class)

```python
class ModelInterface(ABC):
    @abstractmethod
    def fit(self, data: pd.DataFrame, intervention_date: str, output_path: str, **kwargs) -> str
    
    @abstractmethod
    def validate_data(self, data: pd.DataFrame) -> bool
    
    @abstractmethod
    def get_required_columns(self) -> List[str]
```

### ModelingEngine (Manager Class)

The `ModelingEngine` class serves as the central coordinator, similar to `DataSourceManager`:

- Manages model registration and selection
- Handles configuration parsing and validation
- Coordinates data preprocessing and model fitting
- Returns file paths to saved results

### InterruptedTimeSeriesModel (Concrete Implementation)

The initial implementation focuses on interrupted time series analysis using statsmodels:

- Uses `statsmodels.tsa.statespace.sarimax.SARIMAX` for time series modeling
- Implements intervention effects through dummy variables
- Saves impact estimates and model outputs directly to disk (CSV/JSON format)
- Returns the path to the saved results file

## Data Models

### Input Data Schema

The modeling layer expects data from the data abstraction layer with the following required columns:
- `date`: datetime column for time series analysis
- `revenue` or `sales_volume`: dependent variable for impact measurement
- Additional columns may be used as covariates

### Configuration Schema

```json
{
  "model": {
    "type": "interrupted_time_series",
    "parameters": {
      "dependent_variable": "revenue",
      "intervention_date": "2024-11-15"
    }
  }
}
```

### Output File Format

Each model saves its results to disk in JSON format. The structure varies by model type but follows a consistent pattern:

```json
{
  "model_type": "interrupted_time_series",
  "impact_estimates": {
    "intervention_effect": 1250.75,
    "pre_intervention_mean": 5000.0,
    "post_intervention_mean": 6250.75
  },
  "model_summary": {
    "n_observations": 60,
    "pre_period_length": 30,
    "post_period_length": 30
  }
}
```

Additional files may be saved (e.g., fitted_values.csv, residuals.csv) depending on the model type.
## Correc
tness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

After reviewing the acceptance criteria, I identified several redundant properties. Properties 1.3 and 2.2 both test output schema consistency, so they can be combined into a single comprehensive property.

**Property 1: Model fitting completeness**
*For any* valid time series dataset with sufficient observations and any intervention date within the data range, the Modeling_Engine should successfully fit a model and return a file path to saved results
**Validates: Requirements 1.1**

**Property 2: Output file consistency**
*For any* successfully fitted model, the saved results file should exist at the returned path and contain valid JSON with model_type and impact_estimates fields
**Validates: Requirements 1.2, 1.3, 2.2**

**Property 3: Interface consistency**
*For any* registered model type, the fit method should accept the same parameter signature (data: pd.DataFrame, intervention_date: str, output_path: str, **kwargs) and return a string path
**Validates: Requirements 2.1**

**Property 4: Data format compatibility**
*For any* DataFrame produced by the data abstraction layer with the standard schema, the Modeling_Engine should accept it as valid input
**Validates: Requirements 2.3**



## Testing Strategy

### Unit Testing Approach

Unit tests will focus on:
- Individual model implementations (InterruptedTimeSeriesModel)
- Data validation functions
- Configuration parsing
- Result formatting and serialization

### Property-Based Testing Approach

The testing strategy uses **Hypothesis** as the property-based testing library for Python. Each correctness property will be implemented as a property-based test that:
- Generates random time series data with varying characteristics
- Tests the universal properties across many different inputs
- Runs a minimum of 100 iterations per property test
- Uses smart generators that create realistic business metrics data

Property-based tests will be tagged with comments referencing the design document properties using this format: `**Feature: modeling-abstraction-layer, Property {number}: {property_text}**`

Each correctness property will be implemented by a single property-based test that validates the specified behavior across all valid inputs.

### Integration Testing

Integration tests will verify:
- End-to-end workflow from data retrieval through model fitting
- Compatibility with existing data abstraction layer
- Configuration-driven model selection

The dual testing approach ensures comprehensive coverage: unit tests catch specific implementation bugs, while property tests verify that the universal correctness properties hold across all possible inputs.