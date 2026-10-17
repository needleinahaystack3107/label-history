# Plan

Workflow: brainstorm -> design (`design.md`) -> this plan -> implement one task at a time
(test, code, lesson, commit) -> verify.

## Build

- [x] 1. Design, plan and CLAUDE.md
- [x] 2. Bronze: daily snapshot from openFDA — `pipeline/ingest.py`
- [x] 3. Silver: history merged, earliest copy kept — `pipeline/history.py`
- [x] 4. Gold: current text, SCD2 versions, change log — `pipeline/gold.py`
- [x] 5. Incremental embeddings keyed by text hash — `pipeline/gold.py`
- [x] 6. Tests on two snapshots — `tests/test_history.py`
- [x] 7. Runner and search — `pipeline/run.py`, `pipeline/search.py`, `app.py`
- [x] 8. Daily refresh workflow — `.github/workflows/daily.yml`
- [x] 9. Push to GitHub and confirm the workflow is green

## Lessons

- [x] Day 1: why history needs state (SCD Type 2)
- [x] Day 2: bronze is disposable, silver is the state
- [x] Day 3: detecting change with hashes and `lag()`
- [x] Day 4: incremental embeddings keyed by content hash
- [x] Day 5: testing history with two snapshots
- [ ] Day 6: pruning embeddings for text that is no longer current
- [ ] Day 7: when a label is withdrawn (missing from a snapshot)
