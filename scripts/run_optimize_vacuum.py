"""Many small appends, then OPTIMIZE (compact), time travel, and VACUUM. Writes RESULTS_OPTIMIZE.md."""
import os
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from deltalake import DeltaTable, WriterProperties  # noqa: E402

from smallfiles.bench import median_files, run_files  # noqa: E402
from smallfiles.delta_demo import active_files, active_stats, build_table, disk_stats  # noqa: E402

APPENDS, ROWS = 500, 4000
PATH = str(ROOT / "work" / "delta_table")
out = []


def log(line=""):
    print(line, flush=True)
    out.append(line)


def snapshot(label, table):
    n, size = active_stats(table)
    d_n, d_size = disk_stats(PATH)
    answer, secs = median_files(active_files(table), "total")
    log(f"| {label} | {n} | {size / 1e6:.1f} | {d_n} | {d_size / 1e6:.1f} | {secs:.3f} | {answer[0]:,} |")
    return answer


def codec_check():
    """Same 500 small files compacted three ways, to split merging from the codec change."""
    log("")
    log("Compaction size by writer codec (same 500 small files each time):")
    log("")
    log("| compaction codec | files after | MB after |")
    log("|---|---|---|")
    for label, wp in (("delta-rs default", None), ("Snappy forced", WriterProperties(compression="SNAPPY")), ("ZSTD forced", WriterProperties(compression="ZSTD"))):
        t = build_table(PATH + "_codec", APPENDS, ROWS)
        t.optimize.compact(writer_properties=wp)
        n, size = active_stats(DeltaTable(PATH + "_codec"))
        log(f"| {label} | {n} | {size / 1e6:.1f} |")


def main():
    log("# Results: OPTIMIZE and VACUUM")
    log("")
    log(f"{APPENDS} appends of {ROWS:,} rows = {APPENDS * ROWS:,} rows. Query time is the median of 5 runs, warm cache.")
    log(f"Machine: {os.cpu_count()} logical CPUs, Python {platform.python_version()}, delta-rs (deltalake) in this venv.")
    log("")
    log("| step | active files | active MB | files on disk | disk MB | total query (s) | rows |")
    log("|---|---|---|---|---|---|---|")
    table = build_table(PATH, APPENDS, ROWS)
    before_version = table.version()
    base = snapshot("after 500 small appends", table)
    metrics = table.optimize.compact()
    table = DeltaTable(PATH)
    assert snapshot("after OPTIMIZE (compact)", table) == base, "answer changed"
    log("")
    log(f"Compact metrics: files removed {metrics.get('numFilesRemoved')}, files added {metrics.get('numFilesAdded')}.")
    old = DeltaTable(PATH, version=before_version)
    old_rows = run_files(active_files(old), "total")[0][0]
    log(f"Time travel to version {before_version} (before OPTIMIZE) after OPTIMIZE: {old_rows:,} rows, {len(active_files(old))} files read.")
    default_list = table.vacuum(dry_run=True)
    log(f"VACUUM with the default retention, dry run: {len(default_list)} files would be deleted.")
    risky = table.vacuum(retention_hours=0, dry_run=True, enforce_retention_duration=False)
    log(f"VACUUM with retention 0 and the safety check off, dry run: {len(risky)} files would be deleted.")
    table.vacuum(retention_hours=0, dry_run=False, enforce_retention_duration=False)
    table = DeltaTable(PATH)
    log("")
    log("| step | active files | active MB | files on disk | disk MB | total query (s) | rows |")
    log("|---|---|---|---|---|---|---|")
    assert snapshot("after VACUUM (retention 0)", table) == base, "answer changed"
    log("")
    try:
        run_files(active_files(DeltaTable(PATH, version=before_version)), "total")
        log(f"Time travel to version {before_version} after VACUUM: still worked.")
    except Exception as exc:  # the point of the demo: record what actually happens
        log(f"Time travel to version {before_version} after VACUUM: failed with {type(exc).__name__}.")
    codec_check()
    (ROOT / "RESULTS_OPTIMIZE.md").write_text("\n".join(out) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
