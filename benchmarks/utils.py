"""ابزارهای مشترک بنچمارک."""
import time
import statistics


def timed(fn, repeats=5, warmup=1):
    for _ in range(warmup):
        fn()
    times = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        fn()
        times.append(time.perf_counter() - t0)
    return {
        "median":  statistics.median(times),
        "min":     min(times),
        "max":     max(times),
        "stdev":   statistics.stdev(times) if len(times) > 1 else 0.0,
        "times":   times,
    }


def fmt_result(r):
    return f"{r['median']:.6f}s (min {r['min']:.6f}, max {r['max']:.6f})"
