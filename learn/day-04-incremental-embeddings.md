# Day 4: Incremental embeddings keyed by content hash

**Idea.** Embedding is the slow, expensive step. Most of the text does not change from one day to
the next, so re-embedding everything wastes time. Key each vector by the hash of its text. Before
embedding, check which hashes already have a vector. Embed only the rest.

This is the same idea as an idempotent job, applied to the AI step.

**In the code.** `_embed_new()` in `pipeline/gold.py` reads yesterday's `section_embedding` and
embeds only the hashes that are missing.

**Why it matters for AI.** Cost and speed scale with *change*, not with the size of the corpus.
That is what makes a daily refresh affordable on a laptop.

**Try it.** Count how many texts `embed` receives on the second snapshot in
`tests/test_history.py`. Why is the number so small?
