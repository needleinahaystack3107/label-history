# Day 1: Why history needs state

**Idea.** Most data sources only tell you the *current* state. A label today says what it says
today. If your job overwrites its output each day, yesterday's text is gone, and you can never
answer "when did this warning appear?"

The usual fix is a **slowly changing dimension, Type 2**: keep one row per version, with a
`valid_from` and `valid_to`. The current version has no end date.

**In the code.** `fact_label_version` in `pipeline/gold.py`. `lead()` finds the next version's
start date, which becomes this version's end.

**Why it matters for AI.** A model that answers "what does the label say?" should be able to say
*which* version it read, and when that version was in force.

**Try it.** Open `fact_label_version` after two snapshots. Which version has `is_current = true`?
