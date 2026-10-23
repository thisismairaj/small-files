# Results

Rows: 2,000,000 in every layout. Query time is the median of 5 runs, each on a fresh DuckDB connection.
Machine: Intel64 Family 6 Model 142 Stepping 12, GenuineIntel, 8 logical CPUs, Python 3.14.7.
The OS file cache was not cleared between runs, so these are warm-cache times.

| files | total MB | total query (s) | one-user query (s) | decimal sum | float sum |
|---|---|---|---|---|---|
| 1 | 30.3 | 0.012 | 0.015 | 499990000.00 | [499989999.99999994, 499990000.0, 499990000.00000006] |
| 10 | 30.4 | 0.012 | 0.015 | 499990000.00 | [499989999.9999999, 499989999.99999994, 499990000.0, 499990000.00000006] |
| 100 | 33.9 | 0.017 | 0.023 | 499990000.00 | [499989999.99999994, 499990000.0] |
| 1,000 | 34.6 | 0.077 | 0.086 | 499990000.00 | [499990000.0] |
| 5,000 | 37.9 | 0.618 | 0.700 | 499990000.00 | [499989999.99999994, 499990000.0] |

Distinct float sums across layouts: 4 (10 runs per layout). Distinct decimal sums: 1.
