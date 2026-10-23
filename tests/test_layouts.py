from smallfiles.bench import folder_stats, run_query
from smallfiles.gen import make_rows, new_connection, write_layout

N = 10_000


def test_same_answer_in_every_layout(tmp_path):
    con = new_connection()
    make_rows(con, N)
    answers = {}
    for n_files in (1, 7, 100):
        folder = write_layout(con, N, n_files, tmp_path / f"f{n_files}")
        answers[n_files] = {
            q: run_query(folder, q)[0] for q in ("total", "one_user")
        }
    assert answers[1] == answers[7] == answers[100]
    assert answers[1]["total"][0] == N


def test_file_counts_are_exact(tmp_path):
    con = new_connection()
    make_rows(con, N)
    for n_files in (1, 10, 250):
        folder = write_layout(con, N, n_files, tmp_path / f"c{n_files}")
        assert folder_stats(folder)[0] == n_files
