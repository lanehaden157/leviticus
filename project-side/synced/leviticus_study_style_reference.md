# Leviticus Study — Style Reference

Leviticus's differences from `fragment-contract.md` (shared, read first). This
file wins. ✎ marks what the book decides. A book may instead keep a full
contract here.

## Components ✎

*Tentative draft.* On: echo, list, digest (`book.json` `"components"`; markup in
`components-reference.md`).

- **echo**: intertexts in both directions: Exodus 25-40 pattern, Genesis 1-3
  and Eden, Deuteronomy's reuse of the law, the prophets, the New Testament.
- **list**: ordered rites and enumerations (animals, unions, festivals, blessings
  and curses), in the text's own order.
- **digest**: condensed and digest units per `card-condensed.md`.
- Handoff box kinds: none beyond the shared ones yet; add as units need them.

## Hebrew in English ✎

**Transliteration** follows core's Hebrew adapter (`biblecore/lang/hebrew.py`):
diacritic only where the plain letter is already claimed (`ḥ ṭ ś`, `ʾ`/`ʿ`);
no vowel length; no spirantization; dagesh forte doubles; divine name `YHWH`,
rendered **Yahweh**.

**Translation.** Fresh, wooden-but-readable rendering from the Hebrew, not a
polish of an existing English version. Creative, intentional glosses
encouraged.

**Ids.** One root often spans several Strong's numbers, and one number can
bundle senses worth splitting. Bare id (`2416`) claims every lexeme under the
number; suffixed id (`2416e`) claims exactly one.

## Judgment ✎

- Structure markers: Masoretic paragraph breaks (`candidate-boundaries.md`).
- Names are joined by hand: place-name wordplay is real, Strong's etymology
  unreliable.
- *Tentative.* Genre cautions: `lens.md` has the lens. Plus:
  - Ritual steps keep the text's order and actor; no reconstruction of what a rite "means" in the verse text.
  - Law cases: translate the condition and the consequence as the Hebrew states them; mark inference.
  - Cite English verse numbers (Eng 6:1-7 = Heb 5:20-26; Eng 6:8-30 = Heb 6:1-23).
  - Fixed terms (kipper, ḥaṭṭaʾt, ʾasham, ʿolah, qorban, ṭameʾ/ṭahor, tsaraʿat, karet, qadash, goʾel): rendering per `translation-choices.md`, all decided.
  - Priestly speech is plural "you" (y'all) when addressed to Israel.

## Unit map ✎

From the project side as `leviticus-literary-unit-map.md`.
`python -m biblecore units-from-map` loads its **Overview** table; keep this
shape:

    | # | Passage | Working title |
    |---|---|---|
    | | **PART ONE — Label (1:1–25:18)** | |
    | | *I. Label (1:1–10:10)* | |
    | 01 | 1:1–54 | Title |
    | 17 | 16:36–17:13 [Heb 17:1–28] | Title |

Bold row opens an outer grouping, italic an inner one; both optional. Passages
in English numbering, Hebrew difference in `[Heb ...]`.
Renumbering after units ship means editing `threads.json` opens/payoffs, every
`retro` entry and every fragment's meta block: confirm the map before unit 1.
