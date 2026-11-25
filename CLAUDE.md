# Leviticus (v2)

27 units, https://lanehaden157.github.io/leviticus/ . All in Claude Code; Lane only answers calls (popups, recommended first, four each).

- `/unit N` or `/finish`; `fact-checker`, `builder` agents. Core's files (`biblecore/studio`); this file wins.
- Lens `lens.md`. Sources `resources.md`, read via `python tools/kit.py`. New source → `sources/marked/<key>.txt`, `python tools/split_sources.py`.
- Status `python tools/unit_status.py`. Other commands: `python -m biblecore`.

## Strong suggestions

- English verse numbers: Eng 6:1-7 = Heb 5:20-26, 6:8-30 = Heb 6:1-23. Milgrom, Sefaria, LXX use Hebrew.
- Decided terms (`translation-choices.md`) in prose too; names as translated (Moshe, Aharon).
- Promotions: book-wide bias, close call → Lane; `colour`; every occurrence needs `data-w`.
- After `port --dry`: check `opens` shape and `data-w` on split spans.

## Avoid

- Native Hebrew in chat or reader files: transliterate.
- Editing `biblecore/`, `.claude/`, core's `tools/*.py`, generated files. Look = `css/theme.css`.
- Inline Unicode in `bash -c`: use a `.py`. `git add -A`.

Corpus: morphhb 2.0.2 (`npm ci`), LXX (`biblecore fetch`). 859 verses, 11,955 words; drift → flag.

`session_index.md` first.
