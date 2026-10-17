# Day 5: Testing history with two snapshots

**Idea.** A test for a history table needs history. One snapshot proves very little. Write two
small snapshots, where the second changes one thing, and check the layers after each run.

Good history tests check four things: a new version closes the old one, only changed sections
are logged, running the same snapshot twice changes nothing, and the search sees only current text.

**In the code.** `tests/test_history.py`. The fixture is two hand-made lists of labels, and
`process()` runs the same code as the daily job.

**Try it.** Add a third snapshot where a section is removed. Which test would you write first?
