"""Time a query over a folder of parquet files."""
import statistics
import time
from pathlib import Path

import duckdb

QUERIES = {
    "total": "SELECT count(*), sum(amount) FROM read_parquet('{glob}')",
    "float_total": "SELECT sum(amount_float) FROM read_parquet('{glob}')",
    "one_user": "SELECT count(*), sum(amount) FROM read_parquet('{glob}') WHERE user_id = 42",
}


def folder_stats(folder):
    files = sorted(Path(folder).glob("*.parquet"))
    return len(files), sum(f.stat().st_size for f in files)


def run_query(folder, name):
    """Run one query on a fresh connection, return (answer, seconds)."""
    glob = (Path(folder) / "*.parquet").as_posix()
    con = duckdb.connect()
    start = time.perf_counter()
    answer = con.execute(QUERIES[name].format(glob=glob)).fetchone()
    seconds = time.perf_counter() - start
    con.close()
    return answer, seconds


def median_seconds(folder, name, runs=5, strict=True):
    answers, times = set(), []
    for _ in range(runs):
        answer, seconds = run_query(folder, name)
        answers.add(answer)
        times.append(seconds)
    if not strict:  # float sums can differ between runs: report every value seen
        return answers, statistics.median(times), min(times)
    assert len(answers) == 1, "answers changed between runs"
    return answers.pop(), statistics.median(times), min(times)
