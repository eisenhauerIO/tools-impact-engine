# Test Coverage Analysis Report

## Executive Summary

The Impact Engine codebase has a solid foundation of 77 test methods across 5 test files, achieving an estimated **~70% code coverage**. However, several significant gaps exist that should be addressed to improve reliability and maintainability.

**Test-to-Source Ratio:** ~1.4:1 (good)
**Critical Gap Identified:** `ConfigurationParser` class has no direct unit tests

---

## Current Test Coverage Overview

| Component | Test File | Test Count | Coverage | Status |
|-----------|-----------|------------|----------|--------|
| `evaluate_impact()` | test_evaluate_impact.py | 4 | ~60% | Needs improvement |
| `MetricsManager` | test_metrics_manager.py | 17 | ~85% | Good |
| `CatalogSimulatorAdapter` | test_metrics_catalog_simulator.py | 19 | ~75% | Good |
| `ModelsManager` | test_models_manager.py | 16 | ~80% | Good |
| `InterruptedTimeSeriesAdapter` | test_models_interrupted_time_series.py | 21 | ~75% | Good |
| `ConfigurationParser` | **NONE** | 0 | **0%** | Critical gap |

---

## Priority 1: Critical Gaps (Must Fix)

### 1.1 ConfigurationParser Has No Direct Tests

**Location:** `science/impact_engine/config.py`
**Risk Level:** HIGH

The `ConfigurationParser` class (114 lines) has zero direct unit tests. It is only tested indirectly through `MetricsManager` and `ModelsManager`, leaving many code paths untested.

**Untested functionality:**
- `parse_config()` method directly
- YAML file parsing (all indirect tests use JSON)
- Fallback parsing logic (lines 34-39) when file extension is unrecognized
- `_validate_config()` validation of MEASUREMENT section
- `ConfigurationError` exception class
- Convenience function `parse_config_file()`

**Recommended tests to add:**

```python
# test_config.py (NEW FILE)

class TestConfigurationParser:
    """Tests for ConfigurationParser class."""

    def test_parse_json_config_success(self):
        """Test parsing a valid JSON configuration file."""

    def test_parse_yaml_config_success(self):
        """Test parsing a valid YAML configuration file."""

    def test_parse_yml_extension_config_success(self):
        """Test parsing .yml extension files."""

    def test_parse_unknown_extension_tries_json_first(self):
        """Test fallback parsing for unknown extensions."""

    def test_parse_config_file_not_found(self):
        """Test FileNotFoundError for missing config files."""

    def test_validate_config_not_dict(self):
        """Test ConfigurationError when config is not a dictionary."""

    def test_validate_missing_data_section(self):
        """Test ConfigurationError for missing DATA section."""

    def test_validate_missing_measurement_section(self):
        """Test ConfigurationError for missing MEASUREMENT section."""

    def test_validate_missing_data_type(self):
        """Test ConfigurationError for missing TYPE in DATA."""

    def test_validate_missing_data_start_date(self):
        """Test ConfigurationError for missing START_DATE in DATA."""

    def test_validate_missing_data_end_date(self):
        """Test ConfigurationError for missing END_DATE in DATA."""

    def test_validate_data_invalid_date_format(self):
        """Test ConfigurationError for invalid date format in DATA."""

    def test_validate_data_date_ordering(self):
        """Test ConfigurationError when DATA START_DATE > END_DATE."""

    def test_validate_missing_measurement_model(self):
        """Test ConfigurationError for missing MODEL in MEASUREMENT."""

    def test_validate_missing_measurement_params(self):
        """Test ConfigurationError for missing PARAMS in MEASUREMENT."""

    def test_validate_missing_params_start_date(self):
        """Test ConfigurationError for missing START_DATE in PARAMS."""

    def test_validate_missing_params_end_date(self):
        """Test ConfigurationError for missing END_DATE in PARAMS."""

    def test_validate_params_invalid_date_format(self):
        """Test ConfigurationError for invalid date format in PARAMS."""

    def test_validate_params_date_ordering(self):
        """Test ConfigurationError when PARAMS START_DATE > END_DATE."""

    def test_convenience_function_parse_config_file(self):
        """Test the parse_config_file convenience function."""
```

---

### 1.2 evaluate_impact() Missing Test Cases

**Location:** `science/impact_engine/engine.py`
**Risk Level:** MEDIUM-HIGH

**Untested scenarios:**
- `products=None` parameter handling
- Invalid `storage_url` paths
- Error propagation from MetricsManager
- Error propagation from ModelsManager
- Different storage backends (S3-style URLs)

**Recommended tests to add:**

```python
class TestEvaluateImpactEdgeCases:
    def test_evaluate_impact_with_none_products(self):
        """Test behavior when products parameter is None."""

    def test_evaluate_impact_invalid_storage_url(self):
        """Test behavior with invalid storage URL."""

    def test_evaluate_impact_metrics_error_propagation(self):
        """Test that metrics layer errors propagate correctly."""

    def test_evaluate_impact_model_error_propagation(self):
        """Test that model fitting errors propagate correctly."""
```

---

## Priority 2: Important Gaps (Should Fix)

### 2.1 CatalogSimulatorAdapter Edge Cases

**Location:** `science/impact_engine/metrics/adapter_catalog_simulator.py`

**Untested edge cases in `transform_outbound()`:**
- Products with no ID column at all (uses index)
- Products with 'sku' or 'code' as ID column
- Products with 'asin' column already present
- Empty columns in product DataFrame

**Untested edge cases in `transform_inbound()`:**
- DataFrame without 'asin' column
- DataFrame with 'quantity' instead of 'ordered_units'
- Handling of NaN values in numeric columns
- Empty DataFrame edge case behavior

**Recommended tests to add:**

```python
class TestCatalogSimulatorAdapterTransforms:
    def test_transform_outbound_uses_index_when_no_id_column(self):
        """Test that index is used when no ID column found."""

    def test_transform_outbound_with_sku_column(self):
        """Test transform with 'sku' as ID column."""

    def test_transform_outbound_with_existing_asin(self):
        """Test transform when 'asin' column already exists."""

    def test_transform_inbound_with_quantity_column(self):
        """Test mapping 'quantity' to 'sales_volume'."""

    def test_transform_inbound_handles_nan_values(self):
        """Test NaN handling in numeric columns."""

    def test_transform_inbound_calculates_customer_engagement(self):
        """Test customer_engagement calculation from sales."""
```

---

### 2.2 InterruptedTimeSeriesAdapter Edge Cases

**Location:** `science/impact_engine/models/adapter_interrupted_time_series.py`

**Untested scenarios:**
- `_calculate_impact_estimates()` with pre_mean = 0 (division by zero handling)
- Model fitting with all observations in pre or post period
- `transform_outbound()` with missing dependent variable
- Invalid intervention date format
- Intervention date outside data range

**Recommended tests to add:**

```python
class TestInterruptedTimeSeriesEdgeCases:
    def test_impact_estimates_handles_zero_pre_mean(self):
        """Test percent_change when pre_intervention_mean is zero."""

    def test_fit_with_intervention_before_all_data(self):
        """Test fitting when all data is post-intervention."""

    def test_fit_with_intervention_after_all_data(self):
        """Test fitting when all data is pre-intervention."""

    def test_transform_outbound_missing_dependent_variable(self):
        """Test error when dependent variable column missing."""

    def test_fit_minimum_observations_boundary(self):
        """Test fitting with exactly 3 observations (minimum)."""
```

---

## Priority 3: Nice-to-Have Improvements

### 3.1 Integration Test Improvements

**Current state:** Only 4 integration tests exist in `test_evaluate_impact.py`

**Recommended additions:**
- End-to-end test with YAML configuration
- Test with larger datasets (performance regression test)
- Test with different model types (when more are added)
- Cross-layer error scenario tests

### 3.2 Error Message Quality Tests

Verify that error messages are user-friendly and actionable:

```python
class TestErrorMessages:
    def test_config_error_messages_are_descriptive(self):
        """Verify error messages include relevant context."""

    def test_validation_errors_suggest_corrections(self):
        """Verify validation errors help users fix issues."""
```

### 3.3 Abstract Base Class Interface Compliance

Add tests to ensure adapters properly implement interfaces:

```python
class TestInterfaceCompliance:
    def test_catalog_simulator_implements_all_interface_methods(self):
        """Verify CatalogSimulatorAdapter implements MetricsInterface."""

    def test_its_adapter_implements_all_model_methods(self):
        """Verify InterruptedTimeSeriesAdapter implements Model."""
```

---

## Test Infrastructure Recommendations

### 3.4 Add pytest-cov Configuration

Add coverage configuration to `pyproject.toml`:

```toml
[tool.pytest.ini_options]
addopts = "--cov=impact_engine --cov-report=term-missing --cov-report=html"
testpaths = ["science/impact_engine/tests"]

[tool.coverage.run]
branch = true
source = ["science/impact_engine"]
omit = ["*/tests/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
]
```

### 3.5 Add Test Fixtures File

Create `conftest.py` for shared fixtures:

```python
# science/impact_engine/tests/conftest.py

import pytest
import pandas as pd
import tempfile
import json

@pytest.fixture
def sample_products():
    """Fixture for sample products DataFrame."""
    return pd.DataFrame({
        'product_id': ['prod_001', 'prod_002'],
        'name': ['Product A', 'Product B'],
        'category': ['Electronics', 'Home'],
        'price': [99.99, 49.99]
    })

@pytest.fixture
def valid_config():
    """Fixture for valid configuration dictionary."""
    return {
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
                "DEPENDENT_VARIABLE": "revenue",
                "INTERVENTION_DATE": "2024-01-15",
                "START_DATE": "2024-01-01",
                "END_DATE": "2024-01-31"
            }
        }
    }

@pytest.fixture
def temp_config_file(valid_config):
    """Fixture that creates a temporary config file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(valid_config, f)
        yield f.name
    Path(f.name).unlink()
```

---

## Implementation Priority Order

1. **Week 1:** Create `test_config.py` with comprehensive ConfigurationParser tests
2. **Week 2:** Add edge case tests for CatalogSimulatorAdapter transforms
3. **Week 3:** Add edge case tests for InterruptedTimeSeriesAdapter
4. **Week 4:** Add missing evaluate_impact() tests and create conftest.py fixtures
5. **Ongoing:** Add pytest-cov and track coverage metrics in CI

---

## Metrics & Goals

| Metric | Current | Target |
|--------|---------|--------|
| Test Count | 77 | 110+ |
| Estimated Coverage | ~70% | 90%+ |
| ConfigurationParser Coverage | 0% | 95%+ |
| Integration Tests | 4 | 10+ |

---

## Summary

The most critical action item is creating direct unit tests for `ConfigurationParser` in a new `test_config.py` file. This class handles all configuration parsing and validation but has zero direct tests, creating a significant blind spot in the test suite.

Secondary priorities include adding edge case tests for the adapter classes and expanding the integration test suite to cover more realistic scenarios.
