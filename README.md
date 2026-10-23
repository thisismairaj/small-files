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
