# Results: the same layouts read from Azure Blob Storage

Read over the internet from a laptop (see README for the machine) to a US East storage account.
Python 3.14.7. Median of 5 runs, each on a fresh DuckDB connection (it lists and reads the blobs every time).
Latency depends on this connection and location; treat the shape as the result, not the exact seconds.

| files | total query (s) | fastest run (s) | rows |
|---|---|---|---|
| 1 | 3.72 | 3.28 | 2,000,000 |
| 10 | 4.52 | 3.82 | 2,000,000 |
| 100 | 10.32 | 8.96 | 2,000,000 |
| 1,000 | 9.53 | 7.71 | 2,000,000 |
| 5,000 | 35.17 | 31.50 | 2,000,000 |
