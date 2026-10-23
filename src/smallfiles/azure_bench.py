"""Time the same query over the same layouts, read from Azure Blob Storage with DuckDB."""
import os
import statistics
import time

import duckdb

CONTAINER = "layouts"
QUERIES = {
    "total": "SELECT count(*), sum(amount) FROM read_parquet('az://{container}/files_{n}/*.parquet')",
}


def connect():
    """Fresh connection. The connection string comes from the environment, never from a file."""
    con = duckdb.connect()
    con.execute("INSTALL azure; LOAD azure;")
    con.execute("SET azure_transport_option_type = 'curl'")
    con.execute(
        "CREATE SECRET az_demo (TYPE azure, CONNECTION_STRING ?)",
        [os.environ["AZURE_STORAGE_CONNECTION_STRING"]],
    )
    return con


def run_layout(n_files, name="total", runs=5):
    """Median seconds over `runs` fresh connections (each re-lists and re-reads the blobs)."""
    sql = QUERIES[name].format(container=CONTAINER, n=n_files)
    answers, times = set(), []
    for _ in range(runs):
        con = connect()
        start = time.perf_counter()
        answers.add(con.execute(sql).fetchone())
        times.append(time.perf_counter() - start)
        con.close()
    assert len(answers) == 1, "answers changed between runs"
    return answers.pop(), statistics.median(times), min(times)
