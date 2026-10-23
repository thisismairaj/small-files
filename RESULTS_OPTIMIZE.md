# Results: OPTIMIZE and VACUUM

500 appends of 4,000 rows = 2,000,000 rows. Query time is the median of 5 runs, warm cache.
Machine: 8 logical CPUs, Python 3.14.7, delta-rs (deltalake) in this venv.

| step | active files | active MB | files on disk | disk MB | total query (s) | rows |
|---|---|---|---|---|---|---|
| after 500 small appends | 500 | 33.9 | 500 | 33.9 | 0.093 | 2,000,000 |
| after OPTIMIZE (compact) | 1 | 8.9 | 501 | 42.8 | 0.015 | 2,000,000 |

Compact metrics: files removed 500, files added 1.
Time travel to version 499 (before OPTIMIZE) after OPTIMIZE: 2,000,000 rows, 500 files read.
VACUUM with the default retention, dry run: 0 files would be deleted.
VACUUM with retention 0 and the safety check off, dry run: 500 files would be deleted.

| step | active files | active MB | files on disk | disk MB | total query (s) | rows |
|---|---|---|---|---|---|---|
| after VACUUM (retention 0) | 1 | 8.9 | 1 | 8.9 | 0.022 | 2,000,000 |

Time travel to version 499 after VACUUM: failed with IOException.

Compaction size by writer codec (same 500 small files each time):

| compaction codec | files after | MB after |
|---|---|---|
| delta-rs default | 1 | 8.9 |
| Snappy forced | 1 | 16.6 |
| ZSTD forced | 1 | 9.0 |
