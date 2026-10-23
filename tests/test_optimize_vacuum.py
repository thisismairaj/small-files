import pytest
from deltalake import DeltaTable

from smallfiles.bench import run_files
from smallfiles.delta_demo import active_files, build_table, disk_stats

APPENDS, ROWS = 12, 500


def test_compact_keeps_rows_and_sum(tmp_path):
    t = build_table(tmp_path / "t", APPENDS, ROWS)
    before = run_files(active_files(t), "total")[0]
    n_before = len(active_files(t))
    t.optimize.compact()
    t = DeltaTable(str(tmp_path / "t"))
    assert run_files(active_files(t), "total")[0] == before
    assert len(active_files(t)) < n_before


def test_time_travel_survives_compact_but_not_vacuum(tmp_path):
    path = str(tmp_path / "t")
    t = build_table(path, APPENDS, ROWS)
    old_version = t.version()
    t.optimize.compact()
    old = DeltaTable(path, version=old_version)
    assert run_files(active_files(old), "total")[0][0] == APPENDS * ROWS
    t = DeltaTable(path)
    t.vacuum(retention_hours=0, dry_run=False, enforce_retention_duration=False)
    with pytest.raises(Exception):
        run_files(active_files(DeltaTable(path, version=old_version)), "total")
    assert disk_stats(path)[0] == len(active_files(DeltaTable(path)))
