"""خواندن results_raw.csv و ساخت RESULTS.md برای GitHub."""
import pandas as pd
import polars as pl
from config import RESULTS_CSV, RESULTS_MD


def humanize(sec: float) -> str:
    if sec < 1e-3:
        return f"{sec * 1e6:.1f} µs"
    if sec < 1:
        return f"{sec * 1000:.2f} ms"
    return f"{sec:.2f} s"


def main():
    df = pd.read_csv(RESULTS_CSV)

    lines = []
    lines.append("# Pandas vs Polars — Benchmark Results\n")
    lines.append(f"Generated on **{pd.Timestamp.now():%Y-%m-%d %H:%M}**\n")
    lines.append(f"pandas version: `{pd.__version__}`  ")
    lines.append(f"polars version: `{pl.__version__}`\n")
    lines.append("> All times are **median of repeated runs**. Lower is better.\n")
    lines.append("> Winner: ✅ = faster, 🏆 = faster significantly (>1.3×)\n")

    # خلاصهٔ بردها
    wins_pd, wins_pl, total_tests = 0, 0, 0
    summary_rows = []

    for cat in df["category"].unique():
        sub = df[df["category"] == cat]
        lines.append(f"\n## {cat}\n")
        lines.append("| Test | pandas | polars | Winner | Speedup |")
        lines.append("|---|---|---|---|---|")

        for test in sub["test"].unique():
            row = sub[sub["test"] == test]
            pd_row = row[row["lib"] == "pandas"]
            pl_row = row[row["lib"] == "polars"]

            if pd_row.empty or pl_row.empty:
                print(f"  ⚠️ skip incomplete test: {cat} / {test}")
                continue

            pd_s = pd_row["median_s"].iloc[0]
            pl_s = pl_row["median_s"].iloc[0]

            if pl_s < pd_s:
                ratio = pd_s / max(pl_s, 1e-9)
                winner = "🏆 polars" if ratio > 1.3 else "✅ polars"
                wins_pl += 1
            else:
                ratio = pl_s / max(pd_s, 1e-9)
                winner = "🏆 pandas" if ratio > 1.3 else "✅ pandas"
                wins_pd += 1
            total_tests += 1

            lines.append(
                f"| {test} | {humanize(pd_s)} | {humanize(pl_s)} | {winner} | {ratio:.2f}× |"
            )
            summary_rows.append((test, pd_s, pl_s, ratio, winner))

    # خلاصهٔ کلی
    lines.append("\n---\n")
    lines.append("## Summary\n")
    lines.append(f"- **Total tests:** {total_tests}")
    lines.append(f"- **Polars wins:** {wins_pl}")
    lines.append(f"- **Pandas wins:** {wins_pd}")

    if summary_rows:
        max_row = max(summary_rows, key=lambda x: x[3] if "polars" in x[4] else 0)
        lines.append(f"- **Biggest Polars win:** `{max_row[0]}` — **{max_row[3]:.2f}×** faster")

    # دستور اجرا
    lines.append("\n---\n")
    lines.append("### How to reproduce\n")
    lines.append("```bash")
    lines.append("python -m venv venv && source venv/bin/activate")
    lines.append("pip install -r requirements.txt")
    lines.append("python generate_data.py")
    lines.append("python run_all.py")
    lines.append("python summarize.py")
    lines.append("```\n")

    with open(RESULTS_MD, "w") as f:
        f.write("\n".join(lines))

    print(f"Wrote {RESULTS_MD}")
    print(f"  Total: {total_tests} tests | Polars wins: {wins_pl} | Pandas wins: {wins_pd}")


if __name__ == "__main__":
    main()
