"""اجرای همهٔ بنچمارک‌ها و ذخیرهٔ نتایج در CSV."""
import csv
import time
import sys
import pandas as pd
import polars as pl
from config import RESULTS_CSV, REPEATS

from benchmarks import (
    bench_io, bench_aggregation, bench_groupby,
    bench_join, bench_filter, bench_sort, bench_lazy,
)

ALL = [
    ("IO",          bench_io.run),
    ("Aggregation", bench_aggregation.run),
    ("GroupBy",     bench_groupby.run),
    ("Join",        bench_join.run),
    ("Filter",      bench_filter.run),
    ("Sort",        bench_sort.run),
    ("Lazy",        bench_lazy.run),
]


def main():
    print(f"pandas {pd.__version__} | polars {pl.__version__}")
    print(f"repeats = {REPEATS}\n")

    rows = []
    for name, fn in ALL:
        print(f"Running {name}...", flush=True)
        t0 = time.perf_counter()
        try:
            r = fn()
            rows.extend(r)
            print(f"  done in {time.perf_counter() - t0:.2f}s ({len(r)} measurements)")
        except Exception as e:
            print(f"  FAILED: {e}", file=sys.stderr)

    with open(RESULTS_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["category", "test", "lib", "median_s", "min_s", "max_s", "stdev_s"])
        for cat, test, lib, r in rows:
            w.writerow([cat, test, lib,
                        f"{r['median']:.6f}",
                        f"{r['min']:.6f}",
                        f"{r['max']:.6f}",
                        f"{r['stdev']:.6f}"])

    print(f"\nSaved {len(rows)} measurements -> {RESULTS_CSV}")


if __name__ == "__main__":
    main()
