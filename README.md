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

- Cold-cache and object-storage (S3, ADLS) timings. Each file is a separate request there, so the gap is likely larger. NOT MEASURED.
- Fixing the problem with OPTIMIZE or compaction. That is the next piece.

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
