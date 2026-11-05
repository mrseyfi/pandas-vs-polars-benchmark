"""سناریو: Lazy pipeline — خواندن + فیلتر + groupby در یک پاس."""
import pandas as pd
import polars as pl
from config import FILE_MULTI, REPEATS
from benchmarks.utils import timed


def run():
    results = []

    def pd_e2e():
        df = pd.read_parquet(FILE_MULTI)
        df = df[(df["revenue"] > 20_000_000) & (df["region"] == "EU")]
        return df.groupby("category", observed=True)["revenue"].sum()

    def pl_e2e():
        return (
            pl.scan_parquet(FILE_MULTI)
              .filter((pl.col("revenue") > 20_000_000) & (pl.col("region") == "EU"))
              .group_by("category")
              .agg(pl.col("revenue").sum())
              .collect()
        )

    r = timed(pd_e2e, REPEATS)
    results.append(("Lazy pipeline", "read+filter+groupby (10M)", "pandas", r))
    r = timed(pl_e2e, REPEATS)
    results.append(("Lazy pipeline", "read+filter+groupby (10M)", "polars", r))

    return results
