#
# License:          This module is released under the terms of the LICENSE file
#                   contained within this applications INSTALL directory

"""
Unit tests for plotting functions.

Tests single and multiple time series plots in PNG and HTML formats,
including prediction intervals and faceted layouts.
"""

import logging
import os

import numpy as np
import pandas as pd

from anticipy import forecast_plot
from anticipy.utils_test import PandasTest

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

base_folder = os.path.join(os.path.dirname(__file__), "test_plots")
samples_folder = os.path.join(os.path.dirname(__file__), "data")
if not os.path.exists(base_folder):
    os.makedirs(base_folder)


def get_file_path(folder, name):
    """Return path to test output file."""
    return os.path.join(folder, name)


# Sample data: actuals and forecast without prediction intervals
df_forecast = pd.concat(
    [
        pd.DataFrame({
            "date": pd.date_range("2018-01-01", periods=6, freq="D"),
            "model": "actuals",
            "y": 1000 * np.arange(0.0, 6.0),
            "is_actuals": True,
        }),
        pd.DataFrame({
            "date": pd.date_range("2018-01-01", periods=10, freq="D"),
            "model": "forecast",
            "y": 1000 * np.full(10, 5.0),
            "is_actuals": False,
        }),
    ],
    sort=False,
    ignore_index=True,
)

# Multi-source data for faceted plots
_sources = ["ts1", "ts2", "ts3", "ts4", "ts5"]
df_forecast_facet = pd.concat(
    [df_forecast.assign(source=src) for src in _sources],
    sort=False,
    ignore_index=True,
)

# Data with prediction intervals (single source)
df_forecast_pi = pd.read_csv(get_file_path(samples_folder, "df_test_forecast.csv"))

# Data with prediction intervals and multiple sources
df_forecast_pi_facet = pd.read_csv(get_file_path(samples_folder, "df_test_forecast_mds.csv"))


class TestForecastPlotPNG(PandasTest):
    """Test matplotlib PNG plot generation."""

    def test_plot_single_series_png(self):
        """Test PNG output for single time series."""
        if not forecast_plot._matplotlib_imported:
            self.skipTest("Matplotlib not installed")

        path = get_file_path(base_folder, "test_mpl_single")
        result = forecast_plot.plot_forecast(
            df_forecast,
            "png",
            path,
            width=900,
            height=600,
            title="Single Series Forecast",
            show_legend=False,
        )
        self.assertEqual(result, 0)
        self.assertTrue(os.path.isfile(f"{path}.png"))

    def test_plot_facet_png(self):
        """Test PNG output with faceted layout for multiple sources."""
        if not forecast_plot._matplotlib_imported:
            self.skipTest("Matplotlib not installed")

        path = get_file_path(base_folder, "test_mpl_facet")
        result = forecast_plot.plot_forecast(
            df_forecast_facet,
            "png",
            path,
            width=1200,
            height=900,
            title="Multi-Source Forecast",
            show_legend=True,
        )
        self.assertEqual(result, 0)
        self.assertTrue(os.path.isfile(f"{path}.png"))

    def test_plot_with_intervals_png(self):
        """Test PNG output with prediction intervals."""
        if not forecast_plot._matplotlib_imported:
            self.skipTest("Matplotlib not installed")

        path = get_file_path(base_folder, "test_mpl_pi")
        result = forecast_plot.plot_forecast(
            df_forecast_pi,
            "png",
            path,
            width=900,
            height=600,
            title="Forecast with Prediction Intervals",
            show_legend=True,
            include_interval=True,
        )
        self.assertEqual(result, 0)
        self.assertTrue(os.path.isfile(f"{path}.png"))

    def test_plot_facet_with_intervals_png(self):
        """Test PNG output with faceted layout and prediction intervals."""
        if not forecast_plot._matplotlib_imported:
            self.skipTest("Matplotlib not installed")

        path = get_file_path(base_folder, "test_mpl_pi_facet")
        result = forecast_plot.plot_forecast(
            df_forecast_pi_facet,
            "png",
            path,
            width=1200,
            height=900,
            title="Multi-Source Forecast with Intervals",
            show_legend=True,
            include_interval=True,
        )
        self.assertEqual(result, 0)
        self.assertTrue(os.path.isfile(f"{path}.png"))

    def test_plot_png_missing_path(self):
        """Test PNG generation with missing path fails gracefully."""
        if not forecast_plot._matplotlib_imported:
            self.skipTest("Matplotlib not installed")

        result = forecast_plot.plot_forecast(
            df_forecast_pi,
            "png",
            path=None,
            title="Test",
        )
        self.assertEqual(result, 1)


class TestForecastPlotHTML(PandasTest):
    """Test plotly HTML plot generation."""

    def test_plot_single_series_html(self):
        """Test HTML output for single time series."""
        if not forecast_plot._plotly_imported:
            self.skipTest("Plotly not installed")

        path = get_file_path(base_folder, "test_plotly_single")
        result = forecast_plot.plot_forecast(
            df_forecast,
            "html",
            path,
            width=1000,
            height=600,
            title="Single Series Forecast",
            show_legend=False,
        )
        self.assertEqual(result, 0)
        self.assertTrue(os.path.isfile(f"{path}.html"))

    def test_plot_single_series_html_with_legend(self):
        """Test HTML output with legend enabled."""
        if not forecast_plot._plotly_imported:
            self.skipTest("Plotly not installed")

        path = get_file_path(base_folder, "test_plotly_legend")
        result = forecast_plot.plot_forecast(
            df_forecast,
            "html",
            path,
            width=1000,
            height=600,
            title="Forecast with Legend",
            show_legend=True,
        )
        self.assertEqual(result, 0)
        self.assertTrue(os.path.isfile(f"{path}.html"))

    def test_plot_facet_html(self):
        """Test HTML output with faceted layout."""
        if not forecast_plot._plotly_imported:
            self.skipTest("Plotly not installed")

        path = get_file_path(base_folder, "test_plotly_facet")
        result = forecast_plot.plot_forecast(
            df_forecast_facet,
            "html",
            path,
            width=1200,
            height=900,
            title="Multi-Source Forecast",
            show_legend=False,
        )
        self.assertEqual(result, 0)
        self.assertTrue(os.path.isfile(f"{path}.html"))

    def test_plot_with_intervals_html(self):
        """Test HTML output with prediction intervals."""
        if not forecast_plot._plotly_imported:
            self.skipTest("Plotly not installed")

        path = get_file_path(base_folder, "test_plotly_pi")
        result = forecast_plot.plot_forecast(
            df_forecast_pi,
            "html",
            path,
            width=1000,
            height=600,
            title="Forecast with Prediction Intervals",
            show_legend=False,
            include_interval=True,
        )
        self.assertEqual(result, 0)
        self.assertTrue(os.path.isfile(f"{path}.html"))

    def test_plot_facet_with_intervals_html(self):
        """Test HTML output with faceted layout and prediction intervals."""
        if not forecast_plot._plotly_imported:
            self.skipTest("Plotly not installed")

        path = get_file_path(base_folder, "test_plotly_pi_facet")
        result = forecast_plot.plot_forecast(
            df_forecast_pi_facet,
            "html",
            path,
            width=1200,
            height=900,
            title="Multi-Source Forecast with Intervals",
            show_legend=False,
            include_interval=True,
        )
        self.assertEqual(result, 0)
        self.assertTrue(os.path.isfile(f"{path}.html"))

    def test_plot_html_missing_path(self):
        """Test HTML generation with missing path fails gracefully."""
        if not forecast_plot._plotly_imported:
            self.skipTest("Plotly not installed")

        result = forecast_plot.plot_forecast(
            df_forecast_pi,
            "html",
            path=None,
            title="Test",
        )
        self.assertEqual(result, 1)

    def test_plot_html_invalid_format(self):
        """Test invalid output format returns error."""
        if not forecast_plot._plotly_imported:
            self.skipTest("Plotly not installed")

        path = get_file_path(base_folder, "test_invalid")
        result = forecast_plot.plot_forecast(
            df_forecast_pi,
            output="invalid_format",
            path=path,
        )
        self.assertEqual(result, 1)


class TestForecastPlotJupyter(PandasTest):
    """Test Jupyter notebook plot generation."""

    def test_plot_jupyter_output(self):
        """Test Jupyter output (validation is limited without notebook)."""
        if not (forecast_plot._plotly_imported and forecast_plot._ipython_imported):
            self.skipTest("Plotly or IPython not installed")

        # Jupyter output returns iplot result, not error code
        result = forecast_plot.plot_forecast(
            df_forecast_pi_facet,
            output="jupyter",
            width=1200,
            height=800,
            title="Jupyter Forecast",
            show_legend=False,
        )
        # Result is iplot object, not int
        self.assertIsNotNone(result)

