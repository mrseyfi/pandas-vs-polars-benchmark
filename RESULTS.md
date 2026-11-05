# Pandas vs Polars — Benchmark Results

Generated on **2026-11-05 17:57**

pandas version: `3.1.0`  
polars version: `2.1.0`

> All times are **median of repeated runs**. Lower is better.

> Winner: ✅ = faster, 🏆 = faster significantly (>1.3×)


## IO

| Test | pandas | polars | Winner | Speedup |
|---|---|---|---|---|
| read_parquet (single col, 10M) | 224.40 ms | 65.57 ms | 🏆 polars | 3.42× |
| read_parquet (8 cols, 10M) | 727.64 ms | 252.90 ms | 🏆 polars | 2.88× |
| write_parquet (8 cols, 10M) | 4.74 s | 1.25 s | 🏆 polars | 3.80× |

## Aggregation

| Test | pandas | polars | Winner | Speedup |
|---|---|---|---|---|
| sum(revenue) on 10M | 8.30 ms | 4.92 ms | 🏆 polars | 1.69× |
| mean(price) on 10M | 26.11 ms | 7.20 ms | 🏆 polars | 3.62× |
| multi-agg (5 ops) on 10M | 255.99 ms | 22.02 ms | 🏆 polars | 11.63× |

## GroupBy

| Test | pandas | polars | Winner | Speedup |
|---|---|---|---|---|
| groupby sum (10K groups) | 508.06 ms | 365.13 ms | 🏆 polars | 1.39× |
| groupby 4 aggregations | 772.46 ms | 824.15 ms | ✅ pandas | 1.07× |

## Join

| Test | pandas | polars | Winner | Speedup |
|---|---|---|---|---|
| left join on 2 keys (10M x 30) | 836.24 ms | 477.13 ms | 🏆 polars | 1.75× |

## Filter

| Test | pandas | polars | Winner | Speedup |
|---|---|---|---|---|
| revenue>25M & region=EU | 433.87 ms | 68.08 ms | 🏆 polars | 6.37× |

## Sort

| Test | pandas | polars | Winner | Speedup |
|---|---|---|---|---|
| sort by revenue (10M) | 9.92 s | 2.56 s | 🏆 polars | 3.87× |

## Lazy pipeline

| Test | pandas | polars | Winner | Speedup |
|---|---|---|---|---|
| read+filter+groupby (10M) | 1.31 s | 128.29 ms | 🏆 polars | 10.19× |

---

## Summary

- **Total tests:** 12
- **Polars wins:** 11
- **Pandas wins:** 1
- **Biggest Polars win:** `multi-agg (5 ops) on 10M` — **11.63×** faster

---

### How to reproduce

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python generate_data.py
python run_all.py
python summarize.py
```
