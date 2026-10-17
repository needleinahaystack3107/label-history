# Design

**Goal.** Keep a history of FDA drug labels, so you can ask "what changed, and when?", and
search the current text by meaning. One learning idea per day, same as trial-lens.

**Source.** openFDA drug label API (public, no key). About 100 labels: 10 common generic drugs,
up to 10 labels each.

## Why history needs state

openFDA only returns the *current* version of each label. A daily job that overwrites its
output forgets yesterday's text. So the project keeps a **silver history table** that is
committed to the repo and only ever grows. Bronze (raw daily JSON) is disposable.

## Flow

```
openFDA -> ingest.py -> data/bronze/<day>.json     raw, gitignored, one file per day
        -> history.py -> data/silver/label_section.parquet   every version seen so far (committed state)
        -> gold.py    -> data/gold/*.parquet        current text, SCD2 versions, change log, embeddings
app.py: pick a label -> its version timeline and changed sections; or search by meaning
```

## Data model (gold)

| Table | Grain | Columns |
|---|---|---|
| `dim_label` | one label | set_id, brand_name, generic_name, manufacturer |
| `label_section_current` | one section of the current version | set_id, version, section, text, text_hash |
| `fact_label_version` | one version (SCD Type 2) | set_id, version, valid_from, valid_to, is_current |
| `fact_section_change` | one changed section in one version | set_id, version, section, change_type, prev_hash, text_hash |
| `section_embedding` | one distinct text | text_hash, embedding FLOAT[384] |

Silver (`silver_label_section`) holds one row per set_id x version x section, with the earliest
snapshot date kept.

## Choices

- **Sections as text hashes.** Change detection is a comparison of hashes with `lag()`, not a text diff.
  Cheap, and it works in SQL.
- **Embeddings keyed by text hash.** An unchanged section keeps its vector; only new text is embedded.
- **Commit silver and gold, not bronze.** Silver is the history, so it must live in git. Bronze would be too large.
- **Three sections only** (boxed warning, warnings and cautions, indications), capped at 1500 characters.

## Out of scope

Full-text diffs, all label sections, drug-to-drug comparisons, medical advice.
