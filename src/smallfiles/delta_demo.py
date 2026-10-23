"""Build a Delta table out of many small appends, then compact and vacuum it."""
import shutil
from pathlib import Path

import duckdb
from deltalake import DeltaTable, write_deltalake


def build_table(path, n_appends, rows_per):
    """One commit per append, like a streaming job writing every few seconds."""
    p = Path(path)
    if p.exists():
        shutil.rmtree(p)
    con = duckdb.connect()
    for k in range(n_appends):
        lo = k * rows_per
        batch = con.sql(
            f"""
            SELECT i AS id, (i * 7919) % 10000 AS user_id,
                   (((i * 31) % 50000)::DECIMAL(12,2) / 100)::DECIMAL(12,2) AS amount
            FROM range({lo}, {lo + rows_per}) t(i)
            """
        ).to_arrow_table()
        write_deltalake(str(p), batch, mode="append")
    return DeltaTable(str(p))


def active_files(table):
    return table.file_uris()


def disk_stats(path):
    """(count, bytes) of every parquet data file on disk, active or not."""
    files = [f for f in Path(path).rglob("*.parquet") if "_delta_log" not in f.parts]
    return len(files), sum(f.stat().st_size for f in files)


def active_stats(table):
    files = [Path(f) for f in active_files(table)]
    return len(files), sum(f.stat().st_size for f in files)
