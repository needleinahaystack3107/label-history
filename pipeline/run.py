"""Run every stage: fetch today's labels, merge into history, build gold, embed what is new."""
import json
from datetime import date
from pathlib import Path

import duckdb

from pipeline import gold, history, ingest

SILVER = "label_section.parquet"
GOLD = ["dim_label", "label_section_current", "fact_label_version", "fact_section_change",
        "section_embedding"]


def process(data_dir, records, snapshot, embed=gold.embed_texts):
    """Everything after the network call, so tests can run it on fake records."""
    data = Path(data_dir)
    silver, out = data / "silver" / SILVER, data / "gold"
    silver.parent.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    history.run(con, records, snapshot, prior=silver if silver.exists() else None)
    con.execute(f"COPY (SELECT * FROM silver_label_section ORDER BY ALL) TO '{silver}' (FORMAT parquet)")
    gold.build(con, prior=out / "section_embedding.parquet", embed=embed)
    for table in GOLD:  # sorted, so unchanged data gives unchanged files
        con.execute(f"COPY (SELECT * FROM {table} ORDER BY ALL) TO '{out / table}.parquet' (FORMAT parquet)")
    return con


def main(data_dir="data"):
    path = ingest.run(Path(data_dir) / "bronze")
    con = process(data_dir, json.loads(path.read_text()), date.fromisoformat(path.stem))
    labels, versions, changes = con.execute("""
        SELECT (SELECT count(*) FROM dim_label), (SELECT count(*) FROM fact_label_version),
               (SELECT count(*) FROM fact_section_change WHERE change_type = 'CHANGED')""").fetchone()
    print(f"{labels} labels, {versions} versions, {changes} changed sections")


if __name__ == "__main__":
    main()
