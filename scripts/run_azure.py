"""Query the same layouts from Azure Blob Storage. Usage: run_azure.py ACCOUNT RESOURCE_GROUP [layouts...]

The connection string is fetched from `az` at run time and kept only in this process.
Writes RESULTS_AZURE.md from the real run.
"""
import os
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from smallfiles.azure_bench import run_layout  # noqa: E402


def main():
    account, group = sys.argv[1], sys.argv[2]
    layouts = [int(x) for x in sys.argv[3:]] or [1, 10, 100, 1000, 5000]
    cs = subprocess.run(
        ["az", "storage", "account", "show-connection-string", "-n", account, "-g", group,
         "--query", "connectionString", "-o", "tsv"],
        capture_output=True, text=True, check=True, shell=(os.name == "nt"),
    ).stdout.strip()
    os.environ["AZURE_STORAGE_CONNECTION_STRING"] = cs
    lines = [
        "# Results: the same layouts read from Azure Blob Storage",
        "",
        "Read over the internet from a laptop (see README for the machine) to a US East storage account.",
        f"Python {platform.python_version()}. Median of 5 runs, each on a fresh DuckDB connection (it lists and reads the blobs every time).",
        "Latency depends on this connection and location; treat the shape as the result, not the exact seconds.",
        "",
        "| files | total query (s) | fastest run (s) | rows |",
        "|---|---|---|---|",
    ]
    for n in layouts:
        answer, med, fastest = run_layout(n)
        lines.append(f"| {n:,} | {med:.2f} | {fastest:.2f} | {answer[0]:,} |")
        print(lines[-1], flush=True)
    (ROOT / "RESULTS_AZURE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
