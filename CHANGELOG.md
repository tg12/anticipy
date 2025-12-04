# Changelog

## Unreleased
### Packaging and dependencies
- Retagged the fork as `anticipy-sawyer` with Python >=3.10 support and added PEP 517 `pyproject.toml`.
- Bumped core runtime stack to numpy 2.x, pandas 2.2+, SciPy 1.14+, and Plotly 5.22+; refreshed dev extras (Ruff, Vulture) and Sphinx toolchain.
- Updated `README.md`, `PKG-INFO`, and `CONTRIBUTING.md` to reflect the fork, install targets, and dev workflow.

### Tooling and observability
- Added `anticipy/logging_utils.py` and wired package init to expose `configure_logging`.
- Introduced `.ruff.toml` for linting and enforced fixes across library modules.

### Forecasting logic
- Made forecasting code numpy 2.x safe by replacing deprecated APIs and cleaning `np.NaN` usage.
- Hardened outlier detection to short-circuit on empty change groups and avoid duplicate columns.
- Normalized resampling and aggregation to avoid pandas deprecations; added safer PI grouping and metadata fill logic.

### Plotting
- Refined Plotly imports and matplotlib window handling for better backend compatibility.
- Prepared Plotly helpers for consolidated HTML output (dashboard work pending).

### Testing
- Updated tests for numpy 2.x compatibility and fixed chained-assignment in fixtures.
- Added guidance to run `pip install -e .[dev,extras]` before executing the suite.
