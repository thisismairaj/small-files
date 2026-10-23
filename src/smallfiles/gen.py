"""Make the same rows and write them as 1 file or many small files."""
import shutil
from pathlib import Path

import duckdb


def make_rows(con, n_rows):
    # Deterministic rows: no random numbers, so every run sees the same data.
    con.execute(
        f"""
        CREATE OR REPLACE TABLE src AS
        SELECT i AS id,
               (i * 7919) % 10000 AS user_id,
               (((i * 31) % 50000)::DECIMAL(12,2) / 100)::DECIMAL(12,2) AS amount,
               ((i * 31) % 50000) / 100.0 AS amount_float
        FROM range({n_rows}) t(i)
        """
    )


def write_layout(con, n_rows, n_files, out_dir):
    """Write all rows into exactly n_files parquet files under out_dir."""
    out = Path(out_dir)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    per_file = -(-n_rows // n_files)  # ceiling division
    for k in range(n_files):
        lo, hi = k * per_file, min((k + 1) * per_file, n_rows)
        path = (out / f"part-{k:05d}.parquet").as_posix()
        con.execute(
            f"COPY (SELECT * FROM src WHERE id >= {lo} AND id < {hi}) "
            f"TO '{path}' (FORMAT PARQUET)"
        )
    return out


def new_connection():
    return duckdb.connect()
