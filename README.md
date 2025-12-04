# anticipy-sawyer

> **Fork Notice**: This is an independently maintained fork of the original [Anticipy](https://github.com/sky-uk/anticipy) project by Sky UK Ltd. This fork is provided "as-is" without warranty of any kind. The maintainer of this fork assumes no legal responsibility for its use. See the original project for the authoritative source. Licensed under BSD 3-Clause (see [LICENSE.md](LICENSE.md)).

Maintained fork of the original Anticipy forecasting toolkit. This fork keeps the API compatible while refreshing dependencies, tooling, and packaging for modern Python versions.

- Install from PyPI: `pip install anticipy-sawyer`
- Imports remain `anticipy`, and the CLI entry point is `anticipy-forecast`.
- Original documentation remains useful at [anticipy.readthedocs.io](https://anticipy.readthedocs.io/en/latest/).

## Features

- Simple interface: single-call forecasting on a pandas DataFrame.
- Model selection: compare multiple candidate models (linear, sigmoidal, exponential, and more).
- Trend and seasonality: weekly and monthly seasonality support.
- Calendar events: incorporate holiday/event calendars to improve fit.
- Data cleaning: outlier detection and step-change handling.

## Quickstart

```python
import numpy as np
import pandas as pd
from anticipy import forecast

df = pd.DataFrame({'y': np.arange(0.0, 5)}, index=pd.date_range('2018-01-01', periods=5, freq='D'))
df_forecast = forecast.run_forecast(df, extrapolate_years=1)
print(df_forecast.head(12))
```

Example output:

```
   .        date   model             y  is_actuals
   0  2018-01-01       y  0.000000e+00        True
   1  2018-01-02       y  1.000000e+00        True
   2  2018-01-03       y  2.000000e+00        True
   3  2018-01-04       y  3.000000e+00        True
   4  2018-01-05       y  4.000000e+00        True
   5  2018-01-01  linear  5.551115e-17       False
   6  2018-01-02  linear  1.000000e+00       False
   7  2018-01-03  linear  2.000000e+00       False
   8  2018-01-04  linear  3.000000e+00       False
   9  2018-01-05  linear  4.000000e+00       False
   10 2018-01-06  linear  5.000000e+00       False
   11 2018-01-07  linear  6.000000e+00       False
```

## Fork highlights

- Updated runtime stack (numpy 2.x, pandas 2.2+, SciPy 1.14+, Plotly 5.22+).
- Added Ruff configuration and dev extras (`pip install -e .[dev,extras]`) for linting and notebooks.
- Cleaned unused imports and variables flagged by Ruff and Vulture.
- Fixed console entry point to target `anticipy.app:main`.

## Development

1. Create an environment targeting Python 3.10+: `python -m venv .venv && source .venv/bin/activate`
2. Install with dev and notebook extras: `pip install -e .[dev,extras]`
3. Run checks: `ruff check .`, `vulture anticipy tests`, then `pytest`.
