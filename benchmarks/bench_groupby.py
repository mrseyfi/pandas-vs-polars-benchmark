"""سناریو: GroupBy."""
import pandas as pd
import polars as pl
from config import FILE_KEYED, REPEATS
from benchmarks.utils import timed


def run():
    results = []
    pdf = pd.read_parquet(FILE_KEYED)
    pldf = pl.read_parquet(FILE_KEYED)

    def pd_gb_sum():
        return pdf.groupby("group_id", observed=True)["revenue"].sum()
    def pl_gb_sum():
        return pldf.group_by("group_id").agg(pl.col("revenue").sum())
    r = timed(pd_gb_sum, REPEATS)
    results.append(("GroupBy", "groupby sum (10K groups)", "pandas", r))
    r = timed(pl_gb_sum, REPEATS)
    results.append(("GroupBy", "groupby sum (10K groups)", "polars", r))

    def pd_gb_multi():
        return pdf.groupby("group_id", observed=True).agg(
            rev_sum=("revenue", "sum"),
            rev_mean=("revenue", "mean"),
            qty_sum=("qty", "sum"),
            qty_max=("qty", "max"),
        )
    def pl_gb_multi():
        return pldf.group_by("group_id").agg([
            pl.col("revenue").sum().alias("rev_sum"),
            pl.col("revenue").mean().alias("rev_mean"),
            pl.col("qty").sum().alias("qty_sum"),
            pl.col("qty").max().alias("qty_max"),
        ])
    r = timed(pd_gb_multi, REPEATS)
    results.append(("GroupBy", "groupby 4 aggregations", "pandas", r))
    r = timed(pl_gb_multi, REPEATS)
    results.append(("GroupBy", "groupby 4 aggregations", "polars", r))

    return results
