"""Retrieval: nearest label sections to a query vector, current versions only."""
from pathlib import Path

import duckdb


def load(gold_dir="data/gold"):
    con = duckdb.connect()
    for f in sorted(Path(gold_dir).glob("*.parquet")):
        con.execute(f"CREATE TABLE {f.stem} AS SELECT * FROM '{f}'")
    return con


def search(con, query_vector, k=10):
    return con.execute("""
        SELECT l.set_id, l.brand_name, l.generic_name, l.version, l.section, l.text,
               array_cosine_similarity(e.embedding::FLOAT[384], ?::FLOAT[384]) AS score
        FROM label_section_current l
        JOIN section_embedding e USING (text_hash)
        ORDER BY score DESC LIMIT ?""", [query_vector, int(k)]).df()
