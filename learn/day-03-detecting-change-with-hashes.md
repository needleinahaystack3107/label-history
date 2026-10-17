# Day 3: Detecting change with hashes and `lag()`

**Idea.** To know whether a section changed, you do not need to compare full texts. Store a short
hash of each section's text. Two versions with different hashes have different text.

Then `lag()` reads the previous version's hash for the same label and section, in the same SQL
query. A row is logged only when the hash differs.

**In the code.** `fact_section_change` in `pipeline/gold.py`. The `hashes` CTE builds one row per
version and section. `ordered` adds `prev_hash`. The final `WHERE` keeps only the changes.

**A trap.** The first version of a label has no previous hash, so every section looks new. We log
those as `INITIAL`, not `CHANGED`, so the change log stays honest.

**Try it.** Edit one boxed warning in a test fixture by a single word. Does the change log
notice? Does a change in whitespace matter?
