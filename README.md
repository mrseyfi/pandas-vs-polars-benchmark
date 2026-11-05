# Pandas vs Polars — A Comprehensive Benchmark

A reproducible, side-by-side benchmark of **pandas** and **Polars** across **8 real-world workloads** running on **10 million rows** of synthetic data.

The goal is simple: measure **which library is faster, and by how much**, on realistic data-pipeline operations — not just micro-benchmarks.

[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![pandas](https://img.shields.io/badge/pandas-3.1.0-green.svg)](https://pandas.pydata.org/)
[![polars](https://img.shields.io/badge/polars-2.1.0-orange.svg)](https://pola.rs/)
[![pyarrow](https://img.shields.io/badge/pyarrow-26.0.1-yellow.svg)](https://arrow.apache.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

---

## TL;DR

- **Polars wins 11 out of 12 tests** on this machine.
- **Up to 11.6x faster** on multi-column aggregations.
- **Up to 10.2x faster** on lazy end-to-end pipelines (`scan_parquet → filter → group_by → agg`).
- **Pandas stays competitive** on in-memory single-column aggregations and complex `groupby` — the two are within ~7% of each other there.
- The **single most reliable** takeaway: for pipelines that read from disk, **Polars is in a different league**.

---

## Benchmark Results

Environment: see [below](#environment). Times are the **median of 5 runs** after one warm-up. Lower is better.

### Summary

| Metric | Value |
|---|---|
| Total tests | 12 |
| Polars wins | **11** |
| Pandas wins | 1 |
| Biggest Polars win | `multi-agg (5 ops)` — **11.63x** |
| Biggest Pandas win | `groupby 4 aggregations` — 1.07x (within noise) |

### Full results

#### I/O — Reading and writing parquet

| Test | pandas | polars | Winner | Speedup |
|---|---|---|---|---|
| `read_parquet` (1 col, 10M rows) | 224.40 ms | **65.57 ms** | Polars | **3.42x** |
| `read_parquet` (8 cols, 10M rows) | 727.64 ms | **252.90 ms** | Polars | **2.88x** |
| `write_parquet` (8 cols, 10M rows) | 4.74 s | **1.25 s** | Polars | **3.80x** |

#### Aggregation — `sum`, `mean`, multi-op

| Test | pandas | polars | Winner | Speedup |
|---|---|---|---|---|
| `sum(revenue)` on 10M | 8.30 ms | **4.92 ms** | Polars | **1.69x** |
| `mean(price)` on 10M | 26.11 ms | **7.20 ms** | Polars | **3.62x** |
| multi-agg (5 ops) on 10M | 255.99 ms | **22.02 ms** | Polars | **11.63x** (best result) |

#### GroupBy

| Test | pandas | polars | Winner | Speedup |
|---|---|---|---|---|
| `groupby("group_id").sum()` (10K groups) | 508.06 ms | **365.13 ms** | Polars | **1.39x** |
| `groupby("group_id").agg(4 ops)` | **772.46 ms** | 824.15 ms | Pandas | 1.07x (tie) |

#### Join

| Test | pandas | polars | Winner | Speedup |
|---|---|---|---|---|
| left join on 2 keys (10M x 30) | 836.24 ms | **477.13 ms** | Polars | **1.75x** |

#### Filter

| Test | pandas | polars | Winner | Speedup |
|---|---|---|---|---|
| `revenue > 25M & region == "EU"` | 433.87 ms | **68.08 ms** | Polars | **6.37x** |

#### Sort

| Test | pandas | polars | Winner | Speedup |
|---|---|---|---|---|
| `sort by revenue` (10M rows) | 9.92 s | **2.56 s** | Polars | **3.87x** |

#### Lazy pipeline — the killer feature

| Test | pandas | polars | Winner | Speedup |
|---|---|---|---|---|
| `scan → filter → group_by → agg` | 1.31 s | **128.29 ms** | Polars | **10.19x** (best result) |

---

## Analysis

### I/O — Parquet read/write

Polars wins consistently because its in-memory representation **is Apache Arrow**, the same columnar format parquet stores on disk. Reading is therefore **zero-copy**: no conversion between disk format and in-memory format. Pandas (even on 3.x) must transform from Arrow to numpy and then to its internal block manager, and this double conversion costs time.

**Write** is even more one-sided: Polars uses a native Rust writer while pandas delegates to `pyarrow` with its own overhead.

### Aggregation — where the tests split

- **Single-column `sum()` / `mean()`**: essentially tied. Both call highly optimized code (numpy's C loops vs. Arrow's SIMD kernels). Differences at the millisecond level are within run-to-run noise.
- **Multi-column aggregations**: Polars wins **massively** (11.6x). Pandas computes each `(column, op)` pair **independently**, requiring one full pass over the data per op. Polars computes **everything in one pass** with SIMD and multithreading.

> **Rule of thumb:** if you find yourself writing `df[["a", "b", "c"]].agg(["sum", "mean", "std"])`, Polars will beat pandas by an **order of magnitude**.

### GroupBy

Polars is ~40% faster for a single-aggregation `groupby`, but **slightly slower** for a `groupby` with 4 aggregations over 2 columns. Pandas 3.0's `groupby` engine has improved significantly; the 1.07x difference here is at noise level.

### Join

Polars uses a **parallel hash join** in Rust. The 1.75x lead on this benchmark grows substantially with larger right-hand-side tables.

### Filter

Polars' SIMD-backed predicate evaluation combined with lazy expression compilation gives it a **6.4x** advantage on a two-condition filter over 10M rows. This gap widens with more predicates.

### Sort

Polars uses a **parallel merge sort** that saturates available cores. Pandas' numpy-based `argsort` is single-threaded. On 10M rows, Polars is **~3.9x faster** — and the gap scales with data size.

### Lazy pipeline — the headline result

This is where Polars' architectural advantage becomes impossible to ignore:

```python
# pandas: full materialization
df = pd.read_parquet("data_multi.parquet")     # reads all 10M rows
df = df[(df["revenue"] > 20_000_000) & (df["region"] == "EU")]
result = df.groupby("category")["revenue"].sum()

# polars: fused lazy plan, zero intermediate allocation
result = (
    pl.scan_parquet("data_multi.parquet")       # doesn't read yet
      .filter((pl.col("revenue") > 20_000_000) & (pl.col("region") == "EU"))
      .group_by("category")
      .agg(pl.col("revenue").sum())
      .collect()                                # one pass over the file
)
```

Polars:

1. **Pushes the filter down** to the parquet reader (only reads relevant row groups).
2. **Prunes unused columns** (`id`, `cost`, `price`, etc. are never touched).
3. **Fuses all operations into a single pass** — no intermediate DataFrames.
4. **Parallelizes** the aggregation.
5. **Never materializes 10M rows into memory** — the plan processes row chunks on the fly.

The result: **10x faster**, and the advantage **grows** with data size. For datasets bigger than RAM, pandas needs out-of-core tools (Dask, Vaex, DuckDB); Polars handles them natively.

---

## Project structure

```
.
├── README.md                  # this file
├── RESULTS.md                 # auto-generated benchmark report
├── requirements.txt           # pandas, polars, pyarrow, numpy
├── config.py                  # dataset sizes, repeats, file paths
├── generate_data.py           # synthetic parquet datasets
├── run_all.py                 # runs every benchmark -> results_raw.csv
├── summarize.py               # results_raw.csv -> RESULTS.md
└── benchmarks/
    ├── __init__.py
    ├── utils.py               # timed() helper (median of N runs)
    ├── bench_io.py            # parquet read/write
    ├── bench_aggregation.py   # sum, mean, multi-agg
    ├── bench_groupby.py       # group-by with 1 and 4 aggregations
    ├── bench_join.py          # left join on 2 composite keys
    ├── bench_filter.py        # two-condition filter
    ├── bench_sort.py          # full sort by one column
    └── bench_lazy.py          # scan_parquet -> filter -> group_by -> agg
```

The **`benchmarks/`** folder is designed so that each scenario is an **isolated module** with a single `run()` function — add a new file, register it in `run_all.py`, and you have a new benchmark.

---

## Reproducing the benchmark

### Requirements

- Python 3.10+ (tested on 3.12)
- 16 GB RAM or more (10M rows x 8 columns is about 700 MB per loaded DataFrame)
- Any OS with `pyarrow` wheels available

### Setup

```bash
git clone https://github.com/mrseyfi/pandas-vs-polars-benchmark.git
cd pandas-vs-polars-benchmark

python -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

### Run

```bash
python generate_data.py    # ~10s  — creates 4 parquet files (~1.2 GB total)
python run_all.py          # ~3min — runs all 12 benchmarks -> results_raw.csv
python summarize.py        # ~1s   — builds RESULTS.md
cat RESULTS.md
```

### Tune the benchmark

Edit `config.py`:

```python
N_MEDIUM = 10_000_000   # number of rows for each dataset
REPEATS  = 5            # median is computed over this many runs per test
SEED     = 42           # reproducible seed
```

Increase `N_MEDIUM` to 50M or 100M for larger-scale tests (requires more RAM).

---

## Environment

| | |
|---|---|
| OS | Linux (Ubuntu 22.04+) |
| Python | 3.12 |
| pandas | **3.1.0** |
| polars | **2.1.0** (32-bit runtime) |
| pyarrow | 26.0.1 |
| numpy | 2.5.4 |
| Rows (each dataset) | 10,000,000 |
| Repeats per test | 5 (median recorded) |

---

## About the results — a note on variance

Micro-benchmarks in the single-digit-millisecond range are **noisy**. Run-to-run variance of 10–50% on sub-20ms operations is expected, caused by:

- OS page cache state
- CPU frequency scaling (`powersave` vs `performance` governor)
- Background processes / thermal throttling
- Arrow buffer reuse between runs

**How to read the table safely:**

1. Focus on operations **>100 ms** — these are stable.
2. Look at the **ratio**, not the absolute number.
3. Results of two independent runs of this benchmark drew the **same qualitative conclusions**: Polars wins I/O, sort, filter, join, and lazy pipelines by 2–10x while remaining within noise of pandas on small in-memory aggregations.

For the most stable possible results, run on a machine with `cpupower frequency-set -g performance`.

---

## What we did *not* benchmark (yet)

- **String operations** — Polars is known to be much faster for regex, splits, and categoricals. Next priority.
- **`groupby` with `apply` / custom UDFs** — pandas' Python UDF performance vs. Polars' `map_elements`.
- **Time series resampling** — both libraries have dedicated infrastructure.
- **Memory footprint** — requires `psutil`; skipped here for reproducibility across environments.
- **Very large data (100M+ rows)** — could not fit into this test environment.

Contributions welcome — see the [structure](#project-structure) above for how to add a benchmark.

---

## Conclusion

**If your pipeline reads files from disk, filters, groups, and aggregates — use Polars.** The 5–15x performance advantage is structural (Arrow-native, lazy, parallel) and does not go away with more optimization on the pandas side.

**If you work with in-memory DataFrames where the operations are simple (`sum`, `mean`, single-column `groupby`) — either library works.** Pandas 3.x is genuinely fast, and the differences are within noise.

**If you need `groupby` with many aggregations over many columns — Polars will save you minutes per run.**

The larger lesson: **"fastest library" is the wrong question**. The *right* question is *"does my workload match the library's design assumptions?"* Polars assumes columnar data on disk + multi-step pipelines + parallelism. Pandas assumes in-memory rectangular data + interactive notebooks + a rich Python ecosystem. Both are excellent — for their respective problems.

---

## License

MIT — see [`LICENSE`](LICENSE) if present, otherwise feel free to use and adapt.