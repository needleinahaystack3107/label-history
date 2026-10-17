"""Data quality checks on two hand-made daily snapshots (no network, no model)."""
from datetime import date

from pipeline.run import process
from pipeline.search import search


class FakeEmbedder:
    """Records every text it was asked to embed, so tests can count the work done."""

    def __init__(self):
        self.texts = []

    def __call__(self, texts):
        self.texts += texts
        return [[float(len(t)), 1.0] + [0.0] * 382 for t in texts]


def label(set_id, version, effective, boxed="", warnings="", indications="Hypertension."):
    return {"set_id": set_id, "version": version, "effective_time": effective,
            "openfda": {"brand_name": ["Brand " + set_id], "generic_name": ["drug " + set_id],
                        "manufacturer_name": ["Maker"]},
            "boxed_warning": [boxed] if boxed else [],
            "warnings_and_cautions": [warnings] if warnings else [],
            "indications_and_usage": [indications]}


DAY1 = [label("A", 5, "20240101", boxed="Lactic acidosis risk.", warnings="Watch B12."),
        label("B", 1, "20230101", indications="Diabetes.")]
DAY2 = [label("A", 6, "20250101", boxed="Lactic acidosis and kidney warning.", warnings="Watch B12."),
        label("B", 1, "20230101", indications="Diabetes.")]


def run_both_days(tmp_path, embed):
    process(tmp_path, DAY1, date(2024, 1, 2), embed=embed)
    return process(tmp_path, DAY2, date(2025, 1, 2), embed=embed)


def test_first_snapshot_has_one_open_version(tmp_path):
    con = process(tmp_path, DAY1, date(2024, 1, 2), embed=FakeEmbedder())
    assert con.execute("SELECT count(*) FROM fact_label_version WHERE set_id = 'A'").fetchone()[0] == 1
    assert con.execute("SELECT is_current FROM fact_label_version WHERE set_id = 'A'").fetchone()[0]


def test_new_version_closes_the_old_one(tmp_path):
    con = run_both_days(tmp_path, FakeEmbedder())
    rows = con.execute("""SELECT version, valid_from, valid_to, is_current FROM fact_label_version
                          WHERE set_id = 'A' ORDER BY version""").fetchall()
    assert rows == [(5, date(2024, 1, 1), date(2025, 1, 1), False),
                    (6, date(2025, 1, 1), None, True)]


def test_only_changed_sections_are_logged(tmp_path):
    con = run_both_days(tmp_path, FakeEmbedder())
    changed = con.execute("""SELECT section FROM fact_section_change
                             WHERE set_id = 'A' AND version = 6 AND change_type = 'CHANGED'""").fetchall()
    assert changed == [("boxed_warning",)]  # warnings and indications did not change


def test_rerunning_a_snapshot_changes_nothing(tmp_path):
    embed = FakeEmbedder()
    con = run_both_days(tmp_path, embed)
    before = con.execute("SELECT count(*) FROM silver_label_section").fetchone()[0]
    con = process(tmp_path, DAY2, date(2025, 1, 3), embed=embed)
    assert con.execute("SELECT count(*) FROM silver_label_section").fetchone()[0] == before
    seen = con.execute("""SELECT min(snapshot_date) FROM silver_label_section
                          WHERE set_id = 'A' AND version = 6""").fetchone()[0]
    assert seen == date(2025, 1, 2)  # the first copy of a version is kept


def test_only_new_text_is_embedded(tmp_path):
    embed = FakeEmbedder()
    run_both_days(tmp_path, embed)
    # Day 1 has three non-empty sections (A) plus one (B). Day 2 adds one new boxed warning.
    assert len(embed.texts) == 4 + 1


def test_search_returns_current_versions_only(tmp_path):
    embed = FakeEmbedder()
    con = run_both_days(tmp_path, embed)
    result = search(con, embed(["query"])[0])
    assert set(zip(result.set_id, result.version)) == {("A", 6), ("B", 1)}


def test_change_after_the_stored_text_is_still_detected(tmp_path):
    long = "x" * 2000  # longer than the 1500 characters we store
    process(tmp_path, [label("A", 1, "20240101", warnings=long + " old")], date(2024, 1, 2), embed=FakeEmbedder())
    con = process(tmp_path, [label("A", 2, "20250101", warnings=long + " new")], date(2025, 1, 2),
                  embed=FakeEmbedder())
    changed = con.execute("SELECT section FROM fact_section_change WHERE version = 2 AND change_type = 'CHANGED'")
    assert changed.fetchall() == [("warnings",)]


def test_old_style_warnings_are_kept(tmp_path):
    old = label("C", 1, "20200101")
    old["warnings"] = ["Old format warning."]
    con = process(tmp_path, [old], date(2024, 1, 2), embed=FakeEmbedder())
    text = con.execute("SELECT text FROM label_section_current WHERE set_id = 'C' AND section = 'warnings'")
    assert text.fetchone()[0] == "Old format warning."


def test_unchanged_data_does_not_rewrite_files(tmp_path):
    run_both_days(tmp_path, FakeEmbedder())
    files = sorted(tmp_path.rglob("*.parquet"))
    before = [f.stat().st_mtime_ns for f in files]
    process(tmp_path, DAY2, date(2025, 1, 3), embed=FakeEmbedder())
    assert [f.stat().st_mtime_ns for f in files] == before


def test_search_shows_shared_text_once(tmp_path):
    same = [label("A", 1, "20240101", indications="Same text."), label("B", 1, "20240101", indications="Same text.")]
    embed = FakeEmbedder()
    con = process(tmp_path, same, date(2024, 1, 2), embed=embed)
    result = search(con, embed(["query"])[0])
    assert len(result) == 1 and result.labels_sharing[0] == 2
