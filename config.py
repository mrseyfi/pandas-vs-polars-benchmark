"""تنظیمات مرکزی بنچمارک."""

# اندازه‌ی رکوردها برای هر سناریو
N_SMALL = 1_000_000
N_MEDIUM = 10_000_000
N_LARGE = 50_000_000

# تعداد تکرار هر تست
REPEATS = 5

# فایل‌های داده
FILE_SINGLE = "data_single.parquet"    # یک ستون revenue
FILE_MULTI  = "data_multi.parquet"     # چند ستون عددی + categorical
FILE_RIGHT  = "data_right.parquet"     # برای join
FILE_KEYED  = "data_keyed.parquet"     # برای groupby

# مسیر خروجی نتایج
RESULTS_CSV = "results_raw.csv"
RESULTS_MD  = "RESULTS.md"

# seed
SEED = 42
