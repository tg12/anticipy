# Plot Architecture: Non-Obvious Design Issues

## The Version Nobody Talks About

### Date Handling Problem
**Obvious fix**: Changed `tickformat=".0f"` to `tickformat="%Y-%m-%d"`
**Real issue**: Plotly receives datetime objects but the format string was treating them as floats.

**What most miss**: 
- The dataframe `date` column type matters more than the format string
- If dates come in as Unix timestamps or strings, format strings won't help
- No validation exists that `date` column is actually datetime64

**Better approach**:
```python
# Ensure date column is proper datetime before plotting
if not pd.api.types.is_datetime64_any_dtype(df_fcast['date']):
    df_fcast['date'] = pd.to_datetime(df_fcast['date'])
```

### Matplotlib Date Axis Reality
Current code:
```python
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
```

**Hidden assumption**: DatetimeIndex already set via `df_fcast.set_index("date")`
**Failure mode**: If dates aren't proper datetime64, matplotlib silently plots garbage
**No validation**: Code assumes input is clean

## Expert vs Beginner View

### Beginner sees:
- "Just format the x-axis dates"
- "Change tickformat and it works"

### Expert sees:
1. **Data type pipeline**:
   - CSV read → string dates
   - pd.concat → may coerce types inconsistently
   - DataFrame operations → datetime preservation not guaranteed

2. **Performance issue**:
   - Every trace queries `df_fcast.loc[source_filt & condition]` repeatedly
   - For 5 sources × 2 traces × 4 PI bands = 50+ dataframe queries
   - Should pre-filter and cache per source

3. **Memory pattern**:
   - Multiple copies created during filtering
   - No view optimization
   - Prediction intervals create 4 traces per series (wasteful)

## What You Didn't Ask About

### 1. Subplot Grid Calculation
```python
nrows = int(np.ceil(np.sqrt(num_plots)))
ncols = int(np.ceil(1.0 * num_plots / nrows))
```

**Problem**: Square grid assumption
- 7 plots → 3×3 grid with 2 empty slots (22% waste)
- 5 plots → 3×2 grid (16% waste)

**Better**: Aspect-ratio aware grid:
```python
# Target 16:9 aspect ratio
aspect = 1.6
nrows = int(np.ceil(np.sqrt(num_plots / aspect)))
ncols = int(np.ceil(num_plots / nrows))
```

### 2. Legend Visibility Logic
```python
is_first_source = True
# ...
showlegend=is_first_source
```

**Issue**: Only first source gets legend labels
**Result**: Multi-source plots have incomplete legends
**Real intent**: Avoid duplicate "Actuals"/"Forecast" labels across subplots
**Problem**: Lost context in complex plots

### 3. Prediction Interval Inefficiency
Creates 4 separate traces per interval:
- q_low (invisible line)
- q_hi (filled area)
- Repeated for each quantile pair

**Better**: Single trace with error bars or ribbon fill
**Why not fixed**: Plotly API limitation for asymmetric fills
**Workaround**: Custom shape annotations (faster)

### 4. Color Hardcoding
```python
line=dict(color="rgb(17, 157, 165)", width=2)
```

**Issue**: No color palette abstraction
**Result**: Can't theme plots or support colorblind modes
**Missing**: Color scheme configuration

### 5. Date Locator Intelligence
```python
ax.xaxis.set_major_locator(mdates.AutoDateLocator())
```

**Hidden cost**: AutoDateLocator iterates multiple times to find optimal spacing
**For sparse data**: Overkill (daily data doesn't need auto)
**For dense data**: May skip important dates

**Better**: Detect frequency and use appropriate locator:
```python
freq = pd.infer_freq(df_fcast['date'])
if freq == 'D':
    locator = mdates.DayLocator(interval=max(1, len(dates)//10))
elif freq == 'M':
    locator = mdates.MonthLocator()
```

## Determinism Concerns

### Current Issues:
1. **Grid calculation**: Inconsistent for edge cases (7 vs 8 plots)
2. **Auto locator**: Non-deterministic spacing based on date range
3. **Color cycling**: Implicit for multiple sources (not in current code, but common)

### Should Be Deterministic:
- Exact subplot placement
- Date tick positions
- Legend ordering
- Trace stacking order

## Performance Bottlenecks

### DataFrame Filtering
```python
df_fcast.loc[source_filt & df_fcast["is_actuals"]]
```
Executed ~10-50 times per plot. Should be:
```python
# Pre-filter once per source
source_data = df_fcast[df_fcast["source"] == src].copy()
actuals = source_data[source_data["is_actuals"]]
forecasts = source_data[~source_data["is_actuals"]]
```

### Type Conversion
DatetimeIndex set/unset multiple times through pipeline.
Should validate and convert once at function entry.

## Security/Robustness Gaps

1. **No validation** that `y` column is numeric
2. **No check** for NaN/inf in plot data (crashes matplotlib)
3. **No bounds checking** on width/height (can OOM with huge values)
4. **Path traversal**: User-supplied `path` not validated
5. **Column existence**: Assumes `date`, `model`, `y`, `is_actuals` exist

## What Should Be Added

### Input Validation
```python
def _validate_forecast_df(df):
    required = ['date', 'model', 'y', 'is_actuals']
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        raise TypeError("'date' column must be datetime64")
    
    if not pd.api.types.is_numeric_dtype(df['y']):
        raise TypeError("'y' column must be numeric")
    
    if df['y'].isna().any():
        raise ValueError("'y' column contains NaN values")
```

### Configuration Object
```python
@dataclass
class PlotConfig:
    width: int = 1000
    height: int = 600
    dpi: int = 100
    color_actuals: str = "rgb(17, 157, 165)"
    color_forecast: str = "rgb(220, 100, 80)"
    font_family: str = "Segoe UI, sans-serif"
    font_size_title: int = 14
    font_size_axis: int = 8
    # ...
```

### Frequency-Aware Formatting
```python
def _get_date_formatter(dates):
    freq = pd.infer_freq(dates)
    span = (dates.max() - dates.min()).days
    
    if span < 7:
        return "%m-%d %H:%M"  # Hour precision
    elif span < 60:
        return "%Y-%m-%d"     # Daily
    elif span < 730:
        return "%Y-%m"        # Monthly
    else:
        return "%Y"           # Yearly
```

## The Real Question You Should Ask

**"Why are we creating plots in application code at all?"**

Modern approach:
1. Service returns **data** (JSON)
2. Frontend renders plots (D3.js, Vega, Observable)
3. Backend focuses on forecasting quality
4. Separation of concerns: computation vs visualization

This module exists because of historical "export report to HTML/PNG" requirements.

For production 2025 systems:
- API returns forecast data
- Client-side JS handles visualization
- Backend pre-computes but doesn't render
- Avoids server-side matplotlib/plotly overhead

## Bottom Line

The obvious fixes (date format, font sizes) are surface-level.
Real issues: validation, performance, architecture, determinism.

Code works but isn't production-hardened.
Tests pass but don't cover edge cases.
Design is functional but not scalable.
