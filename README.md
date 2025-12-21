# Impact Engine

Evaluate causal impact of product interventions using business metrics and statistical modeling.

## Installation

```bash
pip install impact-engine
```

## Quick Start

```python
from impact_engine import evaluate_impact
import pandas as pd

products = pd.DataFrame({
    'product_id': ['prod1', 'prod2'],
    'name': ['Product 1', 'Product 2']
})

result_path = evaluate_impact(
    config_path='config.json',
    products=products,
    storage_url='./results'
)
```

## Documentation

- [User Guide](documentation/user-guide.md)
- [Configuration](documentation/configuration.md)
- [Design](documentation/design.md)

## License

MIT
