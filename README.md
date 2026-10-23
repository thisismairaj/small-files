# small-files

The small file problem, measured. The same 2,000,000 rows saved as 1, 10, 100, 1,000 and 5,000 Parquet files, then queried with DuckDB.

Think of a library where the same books sit in one box versus 5,000 envelopes. The books are identical. Fetching them is not.

## Run it

```
uv venv .venv
uv pip install --python .venv/Scripts/python.exe -e ".[dev]"
.venv/Scripts/python.exe scripts/run_demo.py
.venv/Scripts/python.exe -m pytest
```

It takes under a minute, runs locally and costs nothing. `RESULTS.md` is written from your own run.

## What it shows (from `RESULTS.md`, on one laptop, warm cache)

- **Time:** the total query went from 0.012 s on 1 file to 0.618 s on 5,000 files. Same rows, same answer.
- **Size:** the same rows took 30.3 MB as 1 file and 37.9 MB as 5,000 files.
- **A silent trap:** summing a float column returned different totals between runs, even on one file (parallel addition order). The decimal column returned the same total every time. Keep money in decimals.

## Not covered

- Cold-cache local timings, and other object stores (S3, GCS). Azure Blob is Part 3.

## Layout

- `src/smallfiles/gen.py` makes the rows and writes the files.
- `src/smallfiles/bench.py` times the queries.
- `scripts/run_demo.py` runs every layout and writes `RESULTS.md`.
- `tests/` checks every layout holds the same rows and gives the same decimal sums.

## Part 2: OPTIMIZE and VACUUM

`scripts/run_optimize_vacuum.py` builds a Delta table from 500 small appends (2,000,000 rows), compacts it, checks time travel, then runs VACUUM. Results are in `RESULTS_OPTIMIZE.md`. It uses the open-source `deltalake` (delta-rs) library, not Databricks, and it takes about a minute.

- **Speed:** the total query went from 0.093 s on 500 files to 0.015 s on 1 file.
- **OPTIMIZE does not free space:** the old files stay on disk for time travel. Disk use went from 33.9 MB to 42.8 MB after compaction.
- **VACUUM is what frees it, and it ends time travel:** the default retention is 7 days (Databricks docs) or one week (delta-rs docs), so a fresh table deletes nothing. The demo sets retention to 0 and turns the safety check off, which you should not do on a real table. After that, the disk was back to 8.9 MB and reading the pre-compaction version failed.
- **The size drop is two effects:** merging alone took 33.9 MB to 16.6 MB. delta-rs compaction also switched the codec to ZSTD (the appends used Snappy), which took it to 8.9 MB.
- **Other formats:** `OPTIMIZE` and `VACUUM` are Delta Lake names. Iceberg does the same jobs with `rewrite_data_files` and `expire_snapshots`. NOT TESTED here.

## Part 3: the same layouts on Azure Blob Storage

`scripts/run_azure.py` reads the same five layouts from an Azure Blob Storage account (US East) with DuckDB, from a laptop in Pakistan over a home connection. Results are in `RESULTS_AZURE.md`. The storage account was created for the test and deleted afterwards. The connection string is fetched from `az` at run time and never written to a file.

- **Reading:** 1 file took 3.72 s, 100 files 10.32 s and 5,000 files 35.17 s (median of 5 runs). Same rows, same answer.
- **The ratio is smaller, the cost is bigger:** 5,000 files were about 9.5 times slower than 1 file, against about 50 times locally. Part of that is the 1-file case now paying to download 30 MB. But the extra time went from about 0.6 s locally to about 31 s.
- **Writing is slow too:** uploading with the Azure CLI took 44 s for the 1-file layout (30 MB), 4 min 12 s for 1,000 files and 20 min for 5,000.
- **Noisy:** 100 files (10.32 s) came out slower than 1,000 files (9.53 s). That is the internet connection, not a real effect. Treat the shape as the result.
- **Not measured:** cost. It was expected to be a few cents, and the actual figure is NOT MEASURED. Azure's cost data lags by about a day.
- **Not tested:** S3 or GCS, a nearer region, and storage that is in the same region as the reader.
