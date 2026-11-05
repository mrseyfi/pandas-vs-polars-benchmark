"""تولید دیتاست‌های تست."""
import numpy as np
import pandas as pd
import time
from config import (
    N_MEDIUM, FILE_SINGLE, FILE_MULTI, FILE_RIGHT, FILE_KEYED, SEED
)


def generate_single():
    print(f"[single] generating {N_MEDIUM:,} rows...")
    rng = np.random.default_rng(SEED)
    df = pd.DataFrame({
        "revenue": rng.integers(100_000, 50_000_000, size=N_MEDIUM, dtype=np.int64)
    })
    t0 = time.perf_counter()
    df.to_parquet(FILE_SINGLE, index=False, compression="snappy")
    print(f"[single] saved {FILE_SINGLE} in {time.perf_counter() - t0:.3f}s "
          f"({len(df):,} rows)")


def generate_multi():
    print(f"[multi] generating {N_MEDIUM:,} rows...")
    rng = np.random.default_rng(SEED + 1)

    n = N_MEDIUM
    df = pd.DataFrame({
        "id":       rng.integers(0, 10_000_000, size=n, dtype=np.int64),
        "revenue":  rng.integers(100_000, 50_000_000, size=n, dtype=np.int64),
        "cost":     rng.integers(10_000, 20_000_000, size=n, dtype=np.int64),
        "qty":      rng.integers(1, 100, size=n, dtype=np.int32),
        "price":    rng.random(n).astype(np.float64) * 1000,
        "region":   rng.choice(["EU", "US", "ASIA", "AFRICA", "LATAM"], size=n),
        "category": rng.choice(["A", "B", "C", "D", "E", "F"], size=n),
        "is_active": rng.integers(0, 2, size=n, dtype=np.int8),
    })
    t0 = time.perf_counter()
    df.to_parquet(FILE_MULTI, index=False, compression="snappy")
    print(f"[multi] saved {FILE_MULTI} in {time.perf_counter() - t0:.3f}s "
          f"({len(df):,} rows, {len(df.columns)} cols)")


def generate_right():
    print("[right] generating 100,000 key table...")
    rng = np.random.default_rng(SEED + 2)
    n = 100_000
    df = pd.DataFrame({
        "region":   rng.choice(["EU", "US", "ASIA", "AFRICA", "LATAM"], size=n),
        "category": rng.choice(["A", "B", "C", "D", "E", "F"], size=n),
        "discount": rng.random(n).astype(np.float64),
    })
    # unique keys
    df = df.drop_duplicates(subset=["region", "category"]).reset_index(drop=True)
    df.to_parquet(FILE_RIGHT, index=False, compression="snappy")
    print(f"[right] saved {FILE_RIGHT} ({len(df):,} rows)")


def generate_keyed():
    print(f"[keyed] generating {N_MEDIUM:,} rows for groupby...")
    rng = np.random.default_rng(SEED + 3)
    n = N_MEDIUM
    df = pd.DataFrame({
        "group_id": rng.integers(0, 10_000, size=n, dtype=np.int64),
        "revenue":  rng.integers(100_000, 50_000_000, size=n, dtype=np.int64),
        "qty":      rng.integers(1, 100, size=n, dtype=np.int32),
    })
    df.to_parquet(FILE_KEYED, index=False, compression="snappy")
    print(f"[keyed] saved {FILE_KEYED} ({len(df):,} rows)")


if __name__ == "__main__":
    generate_single()
    generate_multi()
    generate_right()
    generate_keyed()
    print("\nAll data generated.\n")