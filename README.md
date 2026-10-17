# Label History

Keep every version of an FDA drug label, see exactly which section changed and when, and search
the current text by meaning. A small project for learning **data engineering for AI**, one idea a
day, on public life-sciences data.

> A learning project. Not medical advice.

## How it works

```
openFDA drug label API
  -> bronze   today's snapshot as JSON (disposable, not committed)
  -> silver   every version seen so far, one row per section (committed history)
  -> gold     current text, version timeline (SCD Type 2), change log, embeddings
  -> app      pick a label to see its history, or search by meaning
```

Everything runs in [DuckDB](https://duckdb.org). Embeddings are computed locally with
[fastembed](https://github.com/qdrant/fastembed). No API keys, no paid services.

## Run it

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run app.py
```

The repository ships with its history in `data/silver` and `data/gold`, so the app works straight
away. To fetch today's labels and update the history:

```bash
.venv/bin/python -m pipeline.run
```

Tests (no network needed):

```bash
.venv/bin/python -m pytest -q
```

## Learn

| Day | Lesson |
|---|---|
| 1 | [Why history needs state](learn/day-01-why-history-needs-state.md) |
| 2 | [Bronze is disposable, silver is the state](learn/day-02-bronze-disposable-silver-state.md) |
| 3 | [Detecting change with hashes and `lag()`](learn/day-03-detecting-change-with-hashes.md) |
| 4 | [Incremental embeddings keyed by content hash](learn/day-04-incremental-embeddings.md) |
| 5 | [Testing history with two snapshots](learn/day-05-testing-history-with-two-snapshots.md) |

More are planned in [docs/plan.md](docs/plan.md). A GitHub Action refreshes the history every day
and records it in [learn/LOG.md](learn/LOG.md).

## How it was built

Brainstorm -> [design](docs/design.md) -> [plan](docs/plan.md) -> implement one small task at a
time. Working rules for coding sessions are in [CLAUDE.md](CLAUDE.md).
