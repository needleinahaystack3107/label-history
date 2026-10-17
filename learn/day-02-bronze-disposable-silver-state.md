# Day 2: Bronze is disposable, silver is the state

**Idea.** Layers have different jobs. *Bronze* is the raw copy from the source: cheap to lose,
because you can fetch it again. *Silver* is the history you cannot rebuild from the source,
because the source has moved on. So silver is the state the pipeline carries from one run to the next.

**In the code.** `data/bronze/` is gitignored. `data/silver/label_section.parquet` is committed.
`history.run()` reads yesterday's silver and merges today's snapshot into it.

**Why it matters for AI.** When a model's answer goes wrong, you need to know what the data was
*at that time*. Keeping the state, not just the latest output, makes that possible.

**Try it.** Delete `data/bronze/` and run `pipeline.run`. The history still grows from silver.
