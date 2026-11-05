"""سناریو: Sort."""
import pandas as pd
import polars as pl
from config import FILE_MULTI, REPEATS
from benchmarks.utils import timed


def run():
    results = []
    pdf = pd.read_parquet(FILE_MULTI)
    pldf = pl.read_parquet(FILE_MULTI)

    r = timed(lambda: pdf.sort_values("revenue"), REPEATS)
    results.append(("Sort", "sort by revenue (10M)", "pandas", r))
    r = timed(lambda: pldf.sort("revenue"), REPEATS)
    results.append(("Sort", "sort by revenue (10M)", "polars", r))

    return results
