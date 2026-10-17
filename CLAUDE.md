# label-history

A student-sized project that teaches data engineering for AI on public FDA drug labels:
openFDA API -> bronze (daily snapshot) -> silver (history, committed state) -> gold -> search app.

## Commands

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # setup
.venv/bin/python -m pytest -q                                        # tests (no network)
.venv/bin/python -m pipeline.run                                     # fetch today and rebuild
.venv/bin/streamlit run app.py                                       # app
```

## Rules

- **Layers.** `data/bronze` is raw and disposable (gitignored). `data/silver` is the history and
  must never be rewritten: the earliest copy of each version wins. The app reads only `data/gold`.
- **Minimal code.** Target under 400 lines of Python. No new dependency or abstraction unless a
  lesson in `learn/` explains it. SQL in DuckDB before Python loops.
- **Python 3.9 compatible** (no `X | Y` type hints, no `match`).
- **Every pipeline change gets a test** in `tests/test_history.py`, written as a data quality check
  on two snapshots.
- **Deterministic output.** Tables are written with `ORDER BY ALL`, so unchanged data gives unchanged files.

## Cost guardrails (hard rules)

- Never add a paid API, API key, or paid service. Embeddings run locally with `fastembed`.
- Never enable extra usage / pay-per-token on the Claude account.
- When working with Claude: no subagents, quiet commands, do not re-read files just written.
  Check usage before each task; stop at 80% of the 5-hour window or 85% of the weekly limit,
  commit, tick the task in `docs/plan.md`, and set a one-time reminder for after the reset.
- Model choice: Sonnet for code, Haiku for lessons and README edits, Opus only for design changes.

## Adding a daily lesson

1. Pick the next unticked lesson in `docs/plan.md`.
2. Write `learn/day-NN-topic.md`: the idea in plain words, where it lives in the code, one
   "try it" exercise. Keep it under 200 words.
3. If the lesson needs code, add the smallest change that demonstrates it, with a test.

## Commits

- Author and committer are Abhijit Haridas only (repo-local git config, GitHub noreply email).
- About one commit in ten may carry a `Co-Authored-By: Claude` trailer; the rest carry none.
- No "Generated with" lines.

## Refine me

- A withdrawn label simply stops appearing; there is no "REMOVED" event yet. Add a `snapshot_date` check?
- Embeddings for old text are never pruned, so the file only grows (lesson 6).
- Only three sections are kept. Is `adverse_reactions` worth the size?
- The change log shows *which* section changed, not *how*. A word-level diff would help reviewers.
