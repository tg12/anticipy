#
# License:          This module is released under the terms of the LICENSE file
#                   contained within this applications INSTALL directory

"""CLI entry point for running anticipy forecasts from CSV files."""

# -- Coding Conventions
#    http://www.python.org/dev/peps/pep-0008/   -   Use the Python style guide
# http://sphinx.pocoo.org/rest.html          -   Use Restructured Text for
# docstrings

from __future__ import annotations

import argparse
import logging
from pathlib import Path

import pandas as pd

from anticipy import configure_logging, forecast, forecast_plot

# Configuration
DEFAULT_FORECAST_YEARS = 2.0
DEFAULT_COL_NAME_Y = "y"
DEFAULT_COL_NAME_WEIGHT = "weight"
DEFAULT_COL_NAME_X = "x"
DEFAULT_COL_NAME_DATE = "date"
DEFAULT_COL_NAME_SOURCE = "source"
DEFAULT_OUTPUT_FORMAT = "png"

logger = logging.getLogger(__name__)


def run_forecast_app(
    path_in: Path | str,
    path_out: Path | str | None = None,
    forecast_years: float = DEFAULT_FORECAST_YEARS,
    col_name_y: str = DEFAULT_COL_NAME_Y,
    col_name_weight: str = DEFAULT_COL_NAME_WEIGHT,
    col_name_x: str = DEFAULT_COL_NAME_X,
    col_name_date: str = DEFAULT_COL_NAME_DATE,
    col_name_source: str = DEFAULT_COL_NAME_SOURCE,
    include_all_fits: bool = False,
    output_format: str = DEFAULT_OUTPUT_FORMAT,
) -> None:
    """
    Run the forecast workflow for a CSV file and persist the outputs.

    Parameters
    ----------
    path_in:
        Path to the input CSV file.
    path_out:
        Output directory for forecast data, metadata, and plots.
        Defaults to the input file directory.
    forecast_years:
        Number of years (or fraction) to extrapolate.
    col_name_y:
        Column name holding observed values.
    col_name_weight:
        Column name holding weights.
    col_name_x:
        Column name holding x-axis values.
    col_name_date:
        Column name holding dates.
    col_name_source:
        Column name holding time series identifiers.
    include_all_fits:
        Include non-optimal model fits in the output.
    output_format:
        Plot output format: png, html, or jupyter.
    """
    input_path = Path(path_in)
    if not input_path.exists() or not input_path.is_file():
        raise FileNotFoundError("path_in must point to an existing CSV file")

    output_dir: Path = Path(path_out) if path_out is not None else input_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    file_stem = input_path.stem
    path_data = output_dir / f"{file_stem}_fcast.csv"
    path_metadata = output_dir / f"{file_stem}_metadata.csv"
    path_plot = output_dir / f"{file_stem}_fcast"

    logger.info("Reading input CSV from %s", input_path)
    df_y = pd.read_csv(input_path)

    if col_name_date in df_y:
        df_y[col_name_date] = df_y[col_name_date].pipe(pd.to_datetime)

    df_y = forecast.normalize_df(
        df_y,
        col_name_y,
        col_name_weight,
        col_name_x,
        col_name_date,
        col_name_source,
    )

    dict_result = forecast.run_forecast(
        df_y,
        extrapolate_years=forecast_years,
        simplify_output=False,
        include_all_fits=include_all_fits,
    )

    df_result = dict_result["data"]
    df_metadata = dict_result["metadata"]

    logger.info("Writing forecast data to %s", path_data)
    df_result.to_csv(path_data, index=False)
    logger.info("Writing forecast metadata to %s", path_metadata)
    df_metadata.to_csv(path_metadata, index=False)

    try:
        forecast_plot.plot_forecast(
            df_result,
            output_format,
            path_plot,
            width=1920,
            height=1080,
        )
    except AssertionError:
        logger.info(
            "Plotting skipped: required plotting dependencies are not installed",
        )


def main(argv: list[str] | None = None) -> None:
    """
    Parse CLI arguments and run the forecasting workflow.

    Parameters
    ----------
    argv:
        Optional list of arguments to parse instead of sys.argv.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--path_in", help="Path of input .csv file", required=True)
    parser.add_argument(
        "--path_out",
        help="Path of output folder - defaults to folder of path_in",
        default=None,
    )
    parser.add_argument(
        "--forecast_years",
        help="Years in forecast interval",
        default=DEFAULT_FORECAST_YEARS,
        type=float,
    )
    parser.add_argument(
        "--col_name_y",
        help="Name of column for y",
        default=DEFAULT_COL_NAME_Y,
    )
    parser.add_argument(
        "--col_name_date",
        help="Name of column for date",
        default=DEFAULT_COL_NAME_DATE,
    )
    parser.add_argument(
        "--col_name_weight",
        help="Name of column for weight",
        default=DEFAULT_COL_NAME_WEIGHT,
    )
    parser.add_argument(
        "--col_name_source",
        help="Name of column for source identifier",
        default=DEFAULT_COL_NAME_SOURCE,
    )
    parser.add_argument(
        "--col_name_x",
        help="Name of column for x",
        default=DEFAULT_COL_NAME_X,
    )
    parser.add_argument(
        "--include_all_fits",
        help="If true, output includes non-optimal models",
        action="store_true",
    )
    parser.add_argument(
        "--output_format",
        help="png, html or jupyter",
        default=DEFAULT_OUTPUT_FORMAT,
    )

    args = parser.parse_args(argv)
    configure_logging()
    logger.info("Starting forecast for %s", args.path_in)

    run_forecast_app(
        args.path_in,
        args.path_out,
        args.forecast_years,
        args.col_name_y,
        args.col_name_weight,
        args.col_name_x,
        args.col_name_date,
        args.col_name_source,
        args.include_all_fits,
        args.output_format,
    )


if __name__ == "__main__":
    main()
