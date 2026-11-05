"""سناریو: Aggregation."""
import pandas as pd
import polars as pl
from config import FILE_MULTI, REPEATS
from benchmarks.utils import timed


def run():
    results = []
    pdf = pd.read_parquet(FILE_MULTI)
    pldf = pl.read_parquet(FILE_MULTI)

    r = timed(lambda: pdf["revenue"].sum(), REPEATS)
    results.append(("Aggregation", "sum(revenue) on 10M", "pandas", r))
    r = timed(lambda: pldf.select(pl.col("revenue").sum()).item(), REPEATS)
    results.append(("Aggregation", "sum(revenue) on 10M", "polars", r))

    r = timed(lambda: pdf["price"].mean(), REPEATS)
    results.append(("Aggregation", "mean(price) on 10M", "pandas", r))
    r = timed(lambda: pldf.select(pl.col("price").mean()).item(), REPEATS)
    results.append(("Aggregation", "mean(price) on 10M", "polars", r))

    def pd_multi():
        return pdf[["revenue", "cost", "qty"]].agg(["sum", "mean", "std"])
    def pl_multi():
        return pldf.select([
            pl.col("revenue").sum().alias("revenue_sum"),
            pl.col("revenue").mean().alias("revenue_mean"),
            pl.col("revenue").std().alias("revenue_std"),
            pl.col("cost").sum().alias("cost_sum"),
            pl.col("qty").mean().alias("qty_mean"),
        ])
    r = timed(pd_multi, REPEATS)
    results.append(("Aggregation", "multi-agg (5 ops) on 10M", "pandas", r))
    r = timed(pl_multi, REPEATS)
    results.append(("Aggregation", "multi-agg (5 ops) on 10M", "polars", r))

    return results
