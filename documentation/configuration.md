# Configuration Reference

This document describes all configuration options for Impact Engine.

## Configuration File Structure

Impact Engine uses JSON configuration files with two main sections:

```json
{
  "DATA": {
    // Data source configuration
  },
  "MEASUREMENT": {
    // Model configuration
  }
}
```

## DATA Section

Configures where metrics data comes from.

### Common Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `TYPE` | string | Yes | Data source type: `"simulator"`, `"database"`, `"api"` |
| `PATH` | string | Yes | Path to products CSV file |
| `START_DATE` | string | Yes | Analysis start date (YYYY-MM-DD) |
| `END_DATE` | string | Yes | Analysis end date (YYYY-MM-DD) |

### Simulator Configuration

Use the built-in catalog simulator for testing and development.

```json
{
  "DATA": {
    "TYPE": "simulator",
    "PATH": "data/products.csv",
    "MODE": "rule",
    "SEED": 42,
    "START_DATE": "2024-01-01",
    "END_DATE": "2024-01-31"
  }
}
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `MODE` | string | `"rule"` | Simulation mode: `"rule"` (deterministic) or `"ml"` (ML-based) |
| `SEED` | int | `42` | Random seed for reproducibility |

### Database Configuration

Connect to a SQL database.

```json
{
  "DATA": {
    "TYPE": "database",
    "PATH": "data/products.csv",
    "CONNECTION_STRING": "${DATABASE_URL}",
    "TABLE": "product_metrics",
    "START_DATE": "2024-01-01",
    "END_DATE": "2024-01-31"
  }
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `CONNECTION_STRING` | string | Yes | Database connection string (supports env vars) |
| `TABLE` | string | Yes | Table name containing metrics |

### API Configuration

Connect to an external API.

```json
{
  "DATA": {
    "TYPE": "api",
    "PATH": "data/products.csv",
    "BASE_URL": "https://api.example.com",
    "AUTH_TOKEN": "${API_TOKEN}",
    "START_DATE": "2024-01-01",
    "END_DATE": "2024-01-31"
  }
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `BASE_URL` | string | Yes | API base URL |
| `AUTH_TOKEN` | string | No | Authentication token (supports env vars) |

## MEASUREMENT Section

Configures the statistical model for impact analysis.

### Common Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `MODEL` | string | Yes | Model type: `"interrupted_time_series"` |
| `PARAMS` | object | Yes | Model-specific parameters |

### Interrupted Time Series Model

```json
{
  "MEASUREMENT": {
    "MODEL": "interrupted_time_series",
    "PARAMS": {
      "INTERVENTION_DATE": "2024-01-15",
      "DEPENDENT_VARIABLE": "revenue",
      "order": [1, 0, 0],
      "seasonal_order": [0, 0, 0, 0]
    }
  }
}
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `INTERVENTION_DATE` | string | Yes | - | Date when intervention occurred (YYYY-MM-DD) |
| `DEPENDENT_VARIABLE` | string | No | `"revenue"` | Column name to analyze |
| `order` | array | No | `[1, 0, 0]` | ARIMA order (p, d, q) |
| `seasonal_order` | array | No | `[0, 0, 0, 0]` | Seasonal ARIMA order (P, D, Q, s) |

## Environment Variables

Configuration values can reference environment variables:

```json
{
  "DATA": {
    "CONNECTION_STRING": "${DATABASE_URL}",
    "AUTH_TOKEN": "${API_TOKEN}"
  }
}
```

Values like `${VAR_NAME}` are replaced with the corresponding environment variable at runtime.

## Complete Example

```json
{
  "DATA": {
    "TYPE": "simulator",
    "PATH": "data/products.csv",
    "MODE": "rule",
    "SEED": 42,
    "START_DATE": "2024-01-01",
    "END_DATE": "2024-03-31"
  },
  "MEASUREMENT": {
    "MODEL": "interrupted_time_series",
    "PARAMS": {
      "INTERVENTION_DATE": "2024-02-01",
      "DEPENDENT_VARIABLE": "revenue",
      "order": [1, 0, 0],
      "seasonal_order": [0, 0, 0, 7]
    }
  }
}
```

## YAML Configuration

YAML format is also supported:

```yaml
DATA:
  TYPE: simulator
  PATH: data/products.csv
  MODE: rule
  SEED: 42
  START_DATE: "2024-01-01"
  END_DATE: "2024-03-31"

MEASUREMENT:
  MODEL: interrupted_time_series
  PARAMS:
    INTERVENTION_DATE: "2024-02-01"
    DEPENDENT_VARIABLE: revenue
    order: [1, 0, 0]
    seasonal_order: [0, 0, 0, 7]
```

## Configuration Validation

Impact Engine validates configuration at startup:

- Required parameters are checked
- Date formats are validated
- Model-specific parameters are verified
- Environment variable references are resolved

Invalid configuration produces clear error messages with remediation guidance.
