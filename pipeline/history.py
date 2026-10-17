"""Silver layer: every version of every label we have ever seen, one row per section."""
import hashlib

import pandas as pd

# Section name -> openFDA fields to try in order. Newer labels use `warnings_and_cautions`,
# older ones (and most over-the-counter labels) use `warnings`.
SECTIONS = {
    "boxed_warning": ["boxed_warning"],
    "warnings": ["warnings_and_cautions", "warnings"],
    "indications": ["indications_and_usage"],
}
MAX_CHARS = 1500  # stored and embedded; the hash covers the full text


def flatten(record, snapshot):
    """Three rows per label version. Empty sections keep a row, so a removed warning shows up."""
    openfda = record.get("openfda", {})
    rows = []
    for section, fields in SECTIONS.items():
        full = " ".join(next((record[f] for f in fields if record.get(f)), [])).strip()
        rows.append({
            "set_id": record["set_id"],
            "version": int(record["version"]),
            "effective_date": pd.to_datetime(record["effective_time"], format="%Y%m%d").date(),
            "snapshot_date": snapshot,
            "brand_name": (openfda.get("brand_name") or ["Unknown"])[0],
            "generic_name": (openfda.get("generic_name") or ["Unknown"])[0],
            "manufacturer": (openfda.get("manufacturer_name") or ["Unknown"])[0],
            "section": section,
            "text": full[:MAX_CHARS],
            # Hash the full text: a change after the first 1500 characters is still a change.
            "text_hash": hashlib.sha1(full.encode()).hexdigest()[:16],
        })
    return rows


def run(con, records, snapshot, prior=None):
    """Merge a snapshot into history. Keep the earliest copy of each version, so history is never rewritten."""
    con.register("new_rows", pd.DataFrame([row for r in records for row in flatten(r, snapshot)]))
    if prior is not None:
        con.execute(f"CREATE OR REPLACE TABLE old_rows AS SELECT * FROM read_parquet('{prior}')")
    else:
        con.execute("CREATE OR REPLACE TABLE old_rows AS SELECT * FROM new_rows LIMIT 0")
    con.execute("""
        CREATE OR REPLACE TABLE silver_label_section AS
        SELECT * FROM (SELECT * FROM old_rows UNION ALL BY NAME SELECT * FROM new_rows)
        QUALIFY row_number() OVER (PARTITION BY set_id, version, section ORDER BY snapshot_date) = 1
    """)
