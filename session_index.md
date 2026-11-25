# Session Index

Read this first. Standing state, then the last three sessions, one line each. Older lines → `history/session_index_archive.md`.

## Standing state
- v2 (this folder, from 2026-11-25): studio flow on core 0.38.1: `/unit N`, `/finish`, `fact-checker` and `builder` agents (Sonnet); sources in `sources/` (gitignored), indexed by verse, read through `tools/kit.py`. Claude.ai project, cards, field and sync retired; old folder `../Leviticus` frozen.
- Unit 1 shipped on the new flow; waiting on Lane's review before `/finish`.

## Recent
- 2026-11-13: core 0.37.1 vendored; words.tsv regenerated (eng_ref); box kinds + components (story added) in book.json, style ref and field; Lane's Lev 1 wording calls in translation-choices; unit-pack 1 written (8 rulings tied).
- 2026-11-13: unit 1 ported (7 threads promoted, aec kept as aside.echo); source artifact needed hand fixes (opens shape, data-w on split spans); not committed.
- 2026-11-25: unit 1 (Lev 1:1-17) rebuilt on the new flow, full tier, no promotions; pushed.
- 2026-11-25: v2 setup (Opus planning, Sonnet sessions): 20 sources converted and indexed (Milgrom x3, Morales x2, Constable, 8 Sefaria commentators, K&D, Ellicott, Pulpit, Henry, JPS, Tyndale; no free Origen); prompts rewritten; unit 1 piloted.
- 2026-11-25: core 0.38.2 vendored: lessons loop (`tools/lessons.py`, `lessons.jsonl`: fact-checker and builder log mistake kinds, `/finish` reports recurring ones); pilot fixes to unit-pack, checks, agents.
