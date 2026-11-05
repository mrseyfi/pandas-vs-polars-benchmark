"""سناریو: Join."""
import pandas as pd
import polars as pl
from config import FILE_MULTI, FILE_RIGHT, REPEATS
from benchmarks.utils import timed


def run():
    results = []
    pdf = pd.read_parquet(FILE_MULTI)
    pldf = pl.read_parquet(FILE_MULTI)
    pright = pd.read_parquet(FILE_RIGHT)
    plright = pl.read_parquet(FILE_RIGHT)

    def pd_join():
        return pdf.merge(pright, on=["region", "category"], how="left")
    def pl_join():
        return pldf.join(plright, on=["region", "category"], how="left")

    r = timed(pd_join, REPEATS)
    results.append(("Join", "left join on 2 keys (10M x 30)", "pandas", r))
    r = timed(pl_join, REPEATS)
    results.append(("Join", "left join on 2 keys (10M x 30)", "polars", r))

    return results
