"""Gold layer: what the app reads. Current text, version history (SCD Type 2), change log, embeddings."""
from pathlib import Path

MODEL = "BAAI/bge-small-en-v1.5"  # 384 dimensions, runs on a laptop CPU

SQL = """
CREATE OR REPLACE TABLE label_section_current AS
SELECT set_id, version, brand_name, generic_name, manufacturer, section, text, text_hash
FROM silver_label_section
QUALIFY version = max(version) OVER (PARTITION BY set_id);

CREATE OR REPLACE TABLE dim_label AS
SELECT DISTINCT set_id, brand_name, generic_name, manufacturer FROM label_section_current;

CREATE OR REPLACE TABLE fact_label_version AS
SELECT set_id, version, effective_date AS valid_from,
       lead(effective_date) OVER w AS valid_to,
       lead(effective_date) OVER w IS NULL AS is_current
FROM (SELECT DISTINCT set_id, version, effective_date FROM silver_label_section)
WINDOW w AS (PARTITION BY set_id ORDER BY version);

CREATE OR REPLACE TABLE fact_section_change AS
WITH hashes AS (
    SELECT DISTINCT set_id, version, section, text_hash FROM silver_label_section),
ordered AS (
    SELECT *, lag(text_hash) OVER (PARTITION BY set_id, section ORDER BY version) AS prev_hash
    FROM hashes)
SELECT set_id, version, section,
       CASE WHEN prev_hash IS NULL THEN 'INITIAL' ELSE 'CHANGED' END AS change_type,
       prev_hash, text_hash
FROM ordered
WHERE prev_hash IS NULL OR prev_hash <> text_hash;
"""


def embed_texts(texts):
    from fastembed import TextEmbedding

    return [v.round(4).tolist() for v in TextEmbedding(MODEL).embed(texts)]


def _embed_new(con, prior, embed):
    """Embed only text whose hash we have not seen before. Unchanged sections cost nothing."""
    con.execute("CREATE OR REPLACE TABLE section_embedding (text_hash VARCHAR, embedding FLOAT[384])")
    if Path(prior).exists():
        con.execute(f"""INSERT INTO section_embedding
                        SELECT text_hash, CAST(embedding AS FLOAT[384])
                        FROM read_parquet('{prior}')""")
    todo = con.execute("""
        SELECT DISTINCT text_hash, text FROM label_section_current
        WHERE text <> '' AND text_hash NOT IN (SELECT text_hash FROM section_embedding)
        ORDER BY text_hash""").fetchall()
    if todo:
        vectors = embed([text for _, text in todo])
        con.executemany("INSERT INTO section_embedding VALUES (?, ?)",
                        [(h, v) for (h, _), v in zip(todo, vectors)])


def build(con, prior, embed=embed_texts):
    con.execute(SQL)
    _embed_new(con, Path(prior), embed)
