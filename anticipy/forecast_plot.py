#
# License:          This module is released under the terms of the LICENSE file
#                   contained within this applications INSTALL directory

"""
Functions to plot forecast outputs
"""

# -- Coding Conventions
#    http://www.python.org/dev/peps/pep-0008/   -   Use the Python style guide
# http://sphinx.pocoo.org/rest.html          -   Use Restructured Text for
# docstrings

# -- Public Imports
import importlib.util
import logging
import os
import webbrowser

import numpy as np
import pandas as pd

# -- Globals
logger = logging.getLogger(__name__)

try:
    import matplotlib.pyplot as plt

    _matplotlib_imported = True
except ImportError:
    logger.info("Matplotlib not available, skipping importing library...")
    _matplotlib_imported = False

try:
    import plotly as py
    import plotly.graph_objs as go
    from plotly import subplots

    _plotly_imported = True
except ImportError:
    logger.info("Plotly not available, skipping importing library...")
    _plotly_imported = False

_ipython_imported = importlib.util.find_spec("IPython") is not None
if not _ipython_imported:
    logger.info("IPython not available, skipping importing library...")


# ---- Plotting functions
def _matplotlib_forecast_create(
    df_fcast,
    subplots,
    sources,
    nrows,
    ncols,
    width=None,
    height=None,
    title=None,
    dpi=100,
    show_legend=True,
    include_interval=False,
):
    """
    Generate matplotlib figure from forecast data.

    :param df_fcast: Forecast DataFrame with columns: date, model, y, is_actuals
    :param subplots: Create facet grid for multiple sources
    :param sources: Data sources to plot
    :param nrows: Subplot rows
    :param ncols: Subplot columns
    :param title: Plot title
    :param width: Plot width in pixels
    :param height: Plot height in pixels
    :param dpi: Rendering resolution
    :param show_legend: Display legend
    :param include_interval: Display prediction intervals
    :return: Matplotlib figure
    """
    assert _matplotlib_imported, "matplotlib required for PNG output"

    # Colors and styling
    act_col = "#119da5"  # Teal actuals
    for_col = "#dc6450"  # Warm red forecast
    plt.style.use("default")
    figsize = (width / dpi, height / dpi)

    # Filter out weight rows
    df_fcast = df_fcast.loc[df_fcast.model != "weight"].copy()
    df_fcast = df_fcast.set_index("date")

    fig, axes = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=figsize,
        dpi=dpi,
        squeeze=False,
        facecolor="#ffffff",
    )
    fig.suptitle(title, fontsize=12, fontweight="normal", color="#1f1f1f", y=0.98)

    x = 0
    y = 0
    for src in sources:
        ax = axes[x, y]
        source_filt = True if not subplots else (df_fcast["source"] == src)

        # Plot actuals
        ax.plot(
            df_fcast.loc[source_filt & df_fcast["is_actuals"], :].index,
            df_fcast.loc[source_filt & df_fcast["is_actuals"], "y"],
            color=act_col,
            marker="o",
            markersize=4,
            linestyle="solid",
            linewidth=1.5,
            label="Actuals",
            alpha=0.85,
        )

        # Plot forecast
        ax.plot(
            df_fcast.loc[source_filt & ~df_fcast["is_actuals"], :].index,
            df_fcast.loc[source_filt & ~df_fcast["is_actuals"], "y"],
            color=for_col,
            marker="o",
            markersize=3,
            linestyle="solid",
            linewidth=1.5,
            label="Forecast",
            alpha=0.80,
        )

        # Prediction interval fills
        if include_interval and "q5" in df_fcast.columns and "q95" in df_fcast.columns:
            where_fill = (
                source_filt
                & (~df_fcast["is_actuals"])
                & (df_fcast["q5"].notna())
                & (df_fcast["q95"].notna())
            )
            ax.fill_between(
                df_fcast[where_fill].index,
                df_fcast.loc[where_fill, "q5"],
                df_fcast.loc[where_fill, "q95"],
                facecolor=for_col,
                alpha=0.12,
                label="95% PI",
            )

        if include_interval and "q20" in df_fcast.columns and "q80" in df_fcast.columns:
            where_fill = (
                source_filt
                & (~df_fcast["is_actuals"])
                & (df_fcast["q20"].notna())
                & (df_fcast["q80"].notna())
            )
            ax.fill_between(
                df_fcast[where_fill].index,
                df_fcast.loc[where_fill, "q20"],
                df_fcast.loc[where_fill, "q80"],
                facecolor=for_col,
                alpha=0.08,
                label="80% PI",
            )

        # Grid and styling
        ax.grid(True, alpha=0.35, linestyle="-", linewidth=0.4, color="#eeeeee")
        ax.set_facecolor("#fafafa")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#d0d0d0")
        ax.spines["bottom"].set_color("#d0d0d0")
        ax.spines["left"].set_linewidth(0.7)
        ax.spines["bottom"].set_linewidth(0.7)
        ax.tick_params(labelsize=8, colors="#666666", length=3, width=0.7)
        
        # X-axis date formatting
        import matplotlib.dates as mdates
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        ax.xaxis.set_tick_params(rotation=45, which="major")
        for label in ax.get_xticklabels():
            label.set_fontsize(8)
            label.set_color("#666666")

        if subplots:
            ax.set_title(src, fontsize=10, fontweight="normal", color="#1f1f1f", pad=8)

        if show_legend:
            ax.legend(loc="best", fontsize=8, framealpha=0.95, edgecolor="#e0e0e0", fancybox=True)

        y += 1
        if y >= ncols:
            y = 0
            x += 1

    # Hide unused subplots
    while x < nrows:
        while y < ncols:
            axes[x, y].set_visible(False)
            y += 1
        y = 0
        x += 1

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    return fig


def _plotly_forecast_create(
    df_fcast,
    use_subplots,
    sources,
    nrows,
    ncols,
    width=None,
    height=None,
    title=None,
    show_legend=False,
    add_rangeslider=False,
    include_interval=False,
    pi_q1=5,
    pi_q2=20,
):
    """
    Generate Plotly figure from forecast data.

    :param df_fcast: Forecast DataFrame with columns: date, model, y, is_actuals
    :param use_subplots: Create facet grid for multiple sources
    :param sources: Data sources to plot
    :param nrows: Subplot rows
    :param ncols: Subplot columns
    :param title: Plot title
    :param width: Plot width in pixels
    :param height: Plot height in pixels
    :param show_legend: Display legend
    :param add_rangeslider: Add range slider
    :param include_interval: Display prediction intervals
    :param pi_q1: Outer percentile for PI (5%-95%)
    :param pi_q2: Inner percentile for PI (20%-80%)
    :return: Plotly figure
    """
    assert _plotly_imported, "plotly required for HTML output"

    vertical_spacing = 50.0 / height if height is not None else 0.1

    if use_subplots:
        titles = list(map(str, sources))
        fig = subplots.make_subplots(
            rows=nrows,
            cols=ncols,
            subplot_titles=titles,
            print_grid=False,
            horizontal_spacing=0.10,
            vertical_spacing=vertical_spacing,
        )
        margin_top = 50
    else:
        fig = subplots.make_subplots(rows=nrows, cols=ncols, print_grid=False)
        margin_top = 30

    x = 1
    y = 1
    is_first_source = True

    for src in sources:
        source_filt = True if not use_subplots else (df_fcast["source"] == src)
        actuals_name = "Actuals"
        forecasts_name = "Forecast"

        # Actuals line
        actuals = go.Scatter(
            x=df_fcast.loc[source_filt & df_fcast["is_actuals"]].date,
            y=df_fcast.loc[source_filt & df_fcast["is_actuals"]].y,
            name=actuals_name,
            line=dict(color="rgb(17, 157, 165)", width=2),
            marker=dict(color="rgb(17, 157, 165)", size=4),
            mode="lines+markers",
            opacity=0.85,
            legendgroup="actuals",
            showlegend=is_first_source,
            hovertemplate="%{x|%Y-%m-%d}<br>%{y:.4g}<extra></extra>",
        )
        fig.add_trace(actuals, x, y)

        # Forecast line
        forecast = go.Scatter(
            x=df_fcast.loc[source_filt & ~df_fcast["is_actuals"]].date,
            y=df_fcast.loc[source_filt & ~df_fcast["is_actuals"]].y,
            name=forecasts_name,
            line=dict(color="rgb(220, 100, 80)", width=2),
            marker=dict(color="rgb(220, 100, 80)", size=4),
            mode="lines+markers",
            legendgroup="forecast",
            showlegend=is_first_source,
            hovertemplate="%{x|%Y-%m-%d}<br>%{y:.4g}<extra></extra>",
        )
        fig.add_trace(forecast, x, y)

        # Prediction intervals
        if include_interval:
            for pi_q in [pi_q1, pi_q2]:
                str_q_low = f"q{pi_q}"
                str_q_hi = f"q{100 - pi_q}"
                if str_q_low in df_fcast.columns and str_q_hi in df_fcast.columns:
                    q_low = go.Scatter(
                        x=df_fcast.loc[source_filt & ~df_fcast["is_actuals"]].date,
                        y=df_fcast.loc[source_filt & ~df_fcast["is_actuals"]][str_q_low],
                        line=dict(color="rgba(0,0,0,0)"),
                        mode="lines",
                        showlegend=False,
                        hoverinfo="skip",
                    )
                    fig.add_trace(q_low, x, y)

                    q_hi = go.Scatter(
                        x=df_fcast.loc[source_filt & ~df_fcast["is_actuals"]].date,
                        y=df_fcast.loc[source_filt & ~df_fcast["is_actuals"]][str_q_hi],
                        fill="tonexty",
                        fillcolor=f"rgba(220, 100, 80, {0.12 if pi_q == pi_q1 else 0.08})",
                        line=dict(color="rgba(0,0,0,0)"),
                        mode="lines",
                        showlegend=False,
                        hoverinfo="skip",
                    )
                    fig.add_trace(q_hi, x, y)

        y += 1
        if y > ncols:
            y = 1
            x += 1
        is_first_source = False

    # Layout and theme configuration
    fig["layout"].update(
        autosize=False,
        width=width,
        height=height,
        title=dict(text=title, font=dict(size=14, family="Segoe UI, sans-serif", color="#1f1f1f"), pad=dict(b=15)),
        showlegend=show_legend,
        legend=dict(
            traceorder="normal",
            font=dict(family="Segoe UI, sans-serif", size=9, color="#333333"),
            bordercolor="#e0e0e0",
            borderwidth=0.5,
            orientation="h",
            x=0.0,
            y=1.08,
        ),
        margin={"l": 55, "r": 40, "t": margin_top, "b": 50},
        paper_bgcolor="#ffffff",
        plot_bgcolor="#fafafa",
        hovermode="x unified",
        font=dict(family="Segoe UI, sans-serif", size=9, color="#1f1f1f"),
    )

    # Configure axes: optimized grid and typography
    for key in fig["layout"]:
        if key.startswith("xaxis"):
            fig["layout"][key].update(
                automargin=True,
                tickfont=dict(size=8, family="Segoe UI, sans-serif", color="#666666"),
                tickangle=-45,
                tickformat="%Y-%m-%d",
                gridcolor="#f5f5f5",
                showgrid=False,
                zeroline=False,
                linewidth=1,
                linecolor="#d0d0d0",
                ticklen=4,
            )
        elif key.startswith("yaxis"):
            fig["layout"][key].update(
                automargin=True,
                tickfont=dict(size=8, family="Segoe UI, sans-serif", color="#666666"),
                gridcolor="#eeeeee",
                showgrid=True,
                gridwidth=0.5,
                zeroline=False,
                linewidth=1,
                linecolor="#d0d0d0",
                ticklen=4,
            )

    if not use_subplots and add_rangeslider:
        fig["layout"].update(
            xaxis=dict(rangeslider=dict(visible=True, thickness=0.05), type="date")
        )

    return fig


def plot_forecast(
    df_fcast,
    output="html",
    path=None,
    width=None,
    height=None,
    title=None,
    dpi=100,
    show_legend=True,
    auto_open=False,
    include_interval=False,
    pi_q1=5,
    pi_q2=20,
):
    """
    Generate and save forecast plot as PNG or HTML.

    :param df_fcast: Forecast DataFrame with columns: date, model, y, is_actuals
    :param output: Output format: "html", "png", or "jupyter"
    :param path: Output file path (required for html/png)
    :param width: Width in pixels (default 1000)
    :param height: Height in pixels (default 600)
    :param title: Plot title
    :param dpi: Rendering DPI (default 100)
    :param show_legend: Display legend
    :param auto_open: Open output file after creation
    :param include_interval: Display prediction intervals
    :param pi_q1: Outer percentile for PI (5%-95%)
    :param pi_q2: Inner percentile for PI (20%-80%)
    :return: 0 on success, 1 on failure
    """
    assert isinstance(df_fcast, pd.DataFrame)

    # Validate and coerce date column to datetime
    if "date" not in df_fcast.columns:
        logger.error("DataFrame missing required 'date' column")
        return 1
    
    if not pd.api.types.is_datetime64_any_dtype(df_fcast["date"]):
        try:
            df_fcast = df_fcast.copy()
            df_fcast["date"] = pd.to_datetime(df_fcast["date"])
        except Exception as e:
            logger.error("Failed to convert 'date' column to datetime: %s", e)
            return 1

    # Set sensible defaults for dimensions if not provided
    if width is None:
        width = 1000
    if height is None:
        height = 600

    add_rangeslider = False  # Currently disabled

    if not path and (output == "html" or output == "png"):
        logger.error("No export path provided.")
        return 1

    # Determine if we need subplots based on multiple sources
    if "source" in df_fcast.columns and df_fcast.source.nunique() > 1:
        subplots = True
        sources = df_fcast.loc[df_fcast["is_actuals"], "source"].unique()
        num_plots = len(sources)
        nrows = int(np.ceil(np.sqrt(num_plots)))
        ncols = int(np.ceil(1.0 * num_plots / nrows))
    else:
        subplots = False
        sources = ["y"]
        nrows = 1
        ncols = 1

    if output == "png":
        if _matplotlib_imported:
            fig = _matplotlib_forecast_create(
                df_fcast,
                subplots,
                sources,
                nrows,
                ncols,
                width,
                height,
                title,
                dpi,
                show_legend,
                include_interval,
            )

            path = f"{path}.png"
            dirname, _ = os.path.split(path)
            if dirname and not os.path.exists(dirname):
                logger.info("Creating output directory %s", dirname)
                os.makedirs(dirname, exist_ok=True)
            plt.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="#ffffff")
            plt.close(fig)

            if auto_open:
                fileurl = f"file://{path}"
                webbrowser.open(fileurl, new=2, autoraise=True)
        else:
            logger.error("matplotlib not installed; PNG export unavailable")
            return 1

    elif output == "html":
        if _plotly_imported:
            fig = _plotly_forecast_create(
                df_fcast,
                use_subplots=subplots,
                sources=sources,
                nrows=nrows,
                ncols=ncols,
                width=width,
                height=height,
                title=title,
                show_legend=show_legend,
                add_rangeslider=add_rangeslider,
                include_interval=include_interval,
                pi_q1=pi_q1,
                pi_q2=pi_q2,
            )
            path = f"{path}.html"
            dirname, _ = os.path.split(path)
            if dirname and not os.path.exists(dirname):
                logger.info("Creating output directory %s", dirname)
                os.makedirs(dirname, exist_ok=True)
            py.offline.plot(
                fig, filename=path, show_link=False, auto_open=auto_open, include_plotlyjs="cdn"
            )
        else:
            logger.error("plotly not installed; HTML export unavailable")
            return 1

    elif output == "jupyter":
        if _plotly_imported and _ipython_imported:
            py.offline.init_notebook_mode(connected=True)
            fig = _plotly_forecast_create(
                df_fcast,
                use_subplots=subplots,
                sources=sources,
                nrows=nrows,
                ncols=ncols,
                width=width,
                height=height,
                title=title,
                show_legend=show_legend,
                add_rangeslider=add_rangeslider,
                include_interval=include_interval,
                pi_q1=pi_q1,
                pi_q2=pi_q2,
            )
            return py.offline.iplot(fig, show_link=False)
        else:
            logger.error("plotly and ipython required for Jupyter output")
            return 1

    else:
        logger.error(
            "Invalid output format '%s'. Supported formats: 'png', 'html', 'jupyter'.",
            output,
        )
        return 1

    return 0
