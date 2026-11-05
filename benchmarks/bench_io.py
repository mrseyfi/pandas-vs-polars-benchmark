"""سناریو: I/O — خواندن و نوشتن parquet."""
import pandas as pd
import polars as pl
from config import FILE_MULTI, FILE_SINGLE, REPEATS
from benchmarks.utils import timed


def run():
    results = []

    r = timed(lambda: pd.read_parquet(FILE_SINGLE), REPEATS)
    results.append(("IO", "read_parquet (single col, 10M)", "pandas", r))
    r = timed(lambda: pl.read_parquet(FILE_SINGLE), REPEATS)
    results.append(("IO", "read_parquet (single col, 10M)", "polars", r))

    r = timed(lambda: pd.read_parquet(FILE_MULTI), REPEATS)
    results.append(("IO", "read_parquet (8 cols, 10M)", "pandas", r))
    r = timed(lambda: pl.read_parquet(FILE_MULTI), REPEATS)
    results.append(("IO", "read_parquet (8 cols, 10M)", "polars", r))

    pdf = pd.read_parquet(FILE_MULTI)
    pldf = pl.read_parquet(FILE_MULTI)

    r = timed(lambda: pdf.to_parquet("_tmp_pd.parquet", index=False, compression="snappy"), REPEATS)
    results.append(("IO", "write_parquet (8 cols, 10M)", "pandas", r))
    r = timed(lambda: pldf.write_parquet("_tmp_pl.parquet", compression="snappy"), REPEATS)
    results.append(("IO", "write_parquet (8 cols, 10M)", "polars", r))

    return results
