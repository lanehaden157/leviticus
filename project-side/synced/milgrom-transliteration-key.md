# Milgrom text files: transliteration decode key

The Milgrom text came from old OCR of the Anchor Bible volumes. The OCR drops or garbles the diacritics on transliterated Hebrew/Akkadian. This key says what was auto-fixed and what is left for you to read through. Page numbers are printed page numbers (`[p. N]` markers). Real examples are quoted from the clean files.

Rule of thumb: the Hebrew words are for ideas and search, so match by the consonant skeleton, not the exact vowels/dots.

## Auto-fixed in the clean files (unambiguous)

| Raw pattern | Fixed to | Meaning | Example (page) |
|---|---|---|---|
| `^`, `*`, `}` between letters (vol. 1-16) | `ʾ` | aleph | `se^et` -> seʾet, scale-disease term (p. 774); `we*im` (p. 14) |
| `hatta^t`, `hattd^t`, `hattd%`, `hattd\` | `ḥaṭṭāʾt` | the purification (sin) offering | `the hatta^t pericope` (p. 18); `hattd%` (p. 232) |
| `$` between letters | `ṣ` | tsade | `lir$i5nekem` -> lirṣônekem (vol. 17-22, p. 1331); `ra$6n` (p. 1324) |
| `l;` between letters | `ḥ` | het | `zana 'al;are` -> 'aḥare (p. 1342); `mispal;a` (p. 1402) |
| `l}` between letters | `ḥ` | het | `l}erem` -> ḥerem, "ban" (p. 1848) |
| `/J` between letters | `ḥ` | het | `a/Juzza`, `na/Jala` -> 'aḥuzza, naḥala (p. 1326) |
| `fm` ending a word | `îm` | plural -îm (the `f` is the OCR of `î`) | `panfm` -> pānîm (p. 1471); `gillulfm` -> gillulîm "fetishes" (p. 1513) |

## Left as-is: read with this key

| Pattern | Usually means | Example (page) |
|---|---|---|
| `~` inside a word | ḥ, ṣ or ʿ (ambiguous) | `Dise~sc` is plain "Disease" (p. 1267); `a~fka` is probably 'aḥîka |
| `/:z` or `I;` | ḥ (capital Ḥ for `I;`) | `mimma/:zorat hassabbat` -> mimmoḥŏrat (p. 1322) |
| `c` before a vowel in a Hebrew word (vol. 1-16 only) | ʿ ayin | `mele*ket caboda` -> mĕleʾket ʿăbōdâ (p. 20) |
| `'` or `‘` | ʾ aleph or ʿ ayin | |
| `f` in a Hebrew word | î | `panfm` etc. (only the `-fm` ending is auto-fixed) |
| `d`, `a` after a consonant, in vol. 1-16 | ā (the macron is lost) | `hattd%` -> ḥaṭṭāʾt |
| `$` or `§` at a word start | ṣ or š | `qéde§` -> qodeš "holy" (vol. 23-27, p. 1993) |
| `é`, `ó`, `ü` etc. (vol. 23-27) | ĕ, ô/ō, û (accents replace the dots/macrons) | `kappéret` -> kapporet (p. 1921); `Yém Kippür` -> Yôm Kippur (p. 1895) |
| plain `h`, `t`, `s` in Hebrew words | often ḥ, ṭ, ś/š/ṣ (dots lost) | `hatta't` = ḥaṭṭāʾt |
| `>` or `<` in vol. 1-16 | ʾ aleph in Ugaritic/Akkadian words | `>asam` = ʾāšām, reparation offering |
| `{`, `}` around words | usually round brackets `(`, `)` | `{Tgs. Ps.-J., Yer.}` |
| Gibberish lines of `UG UG`, `O O`, `3 3` | a diagram or table the OCR could not read | see the `[figure]` / `[table]` marker on that page |

Vol. 1-16 uses a Hebrew-letter OCR of the Hebrew itself in a few places (lines such as `HHYWT WRYT M TW`); treat these as garbled.

## Which volume looks like what
- Lev 1-16 (printed pp. 1-1084): `^ * }` for aleph, `c` for ayin, `¬` for soft hyphens (removed).
- Lev 17-22 (pp. 1267-1892): `$ ~ l; /J l}` for dotted letters, `f` for î.
- Lev 23-27 (pp. 1895-2468): mostly accented letters (é ó ü), the cleanest transliteration.
