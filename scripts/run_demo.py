"""Same rows, 1 to 5,000 files. Prints a table and writes RESULTS.md from the real run."""
import os
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from smallfiles.bench import folder_stats, median_seconds  # noqa: E402
from smallfiles.gen import make_rows, new_connection, write_layout  # noqa: E402

N_ROWS = 2_000_000
LAYOUTS = (1, 10, 100, 1000, 5000)
WORK = ROOT / "work"


def main():
    con = new_connection()
    make_rows(con, N_ROWS)
    rows = []
    for n_files in LAYOUTS:
        folder = write_layout(con, N_ROWS, n_files, WORK / f"files_{n_files}")
        count, size = folder_stats(folder)
        total, total_med, _ = median_seconds(folder, "total")
        one, one_med, _ = median_seconds(folder, "one_user")
        flt, _, _ = median_seconds(folder, "float_total", runs=10, strict=False)
        rows.append((count, size, total, total_med, one, one_med, flt))
        print(f"{count:>5} files  {size / 1e6:7.1f} MB  total {total_med:.3f}s  one_user {one_med:.3f}s", flush=True)
    write_results(rows)


def write_results(rows):
    lines = [
        "# Results",
        "",
        f"Rows: {N_ROWS:,} in every layout. Query time is the median of 5 runs, each on a fresh DuckDB connection.",
        f"Machine: {platform.processor() or platform.machine()}, {os.cpu_count()} logical CPUs, Python {platform.python_version()}.",
        "The OS file cache was not cleared between runs, so these are warm-cache times.",
        "",
        "| files | total MB | total query (s) | one-user query (s) | decimal sum | float sum |",
        "|---|---|---|---|---|---|",
    ]
    for count, size, total, total_med, one, one_med, flt in rows:
        lines.append(
            f"| {count:,} | {size / 1e6:.1f} | {total_med:.3f} | {one_med:.3f} | {total[1]} | {sorted({v[0] for v in flt})} |"
        )
    lines += ["", f"Distinct float sums across layouts: {len({v for r in rows for v in r[6]})} (10 runs per layout). Distinct decimal sums: {len({r[2] for r in rows})}.", ""]
    (ROOT / "RESULTS.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
