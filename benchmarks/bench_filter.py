"""سناریو: Filter."""
import pandas as pd
import polars as pl
from config import FILE_MULTI, REPEATS
from benchmarks.utils import timed


def run():
    results = []
    pdf = pd.read_parquet(FILE_MULTI)
    pldf = pl.read_parquet(FILE_MULTI)

    def pd_filter():
        return pdf[(pdf["revenue"] > 25_000_000) & (pdf["region"] == "EU")]
    def pl_filter():
        return pldf.filter((pl.col("revenue") > 25_000_000) & (pl.col("region") == "EU"))

    r = timed(pd_filter, REPEATS)
    results.append(("Filter", "revenue>25M & region=EU", "pandas", r))
    r = timed(pl_filter, REPEATS)
    results.append(("Filter", "revenue>25M & region=EU", "polars", r))

    return results
