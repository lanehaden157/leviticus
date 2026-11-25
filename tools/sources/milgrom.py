#!/usr/bin/env python
"""Convert the three Milgrom Leviticus (Anchor Bible) text files into marked files.

Reads  sources/milgrom-1/milgrom-lev1-16.txt, milgrom-2/milgrom-lev17-22.txt,
       milgrom-3/milgrom-lev23-27.txt
Writes sources/marked/milgrom-1.txt, milgrom-2.txt, milgrom-3.txt

Usage: python tools/sources/milgrom.py [milgrom-1 milgrom-2 milgrom-3]

The input files are fixed conversions, so vols 2 and 3 use line-number anchors
(checked against the line text, see CHECK) where the OCR dropped the headings.
Vol 1 finds its units by regex. Text is left as is (transliteration OCR damage
is documented in research/milgrom-transliteration-key.md).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "sources"
OUT = SRC / "marked"

LABEL_TAIL = ("Private copy: paraphrase, never quote at length; transliteration OCR-damaged, "
              "check against research/milgrom-transliteration-key.md")

# ---------------------------------------------------------------- helpers

def read_lines(path):
    return path.read_text(encoding="utf-8").split("\n")


def clean(lines):
    """Drop blank-page notices and obvious running heads; collapse blank runs."""
    out = []
    for ln in lines:
        s = ln.strip()
        if s == "[blank page]":
            continue
        if re.fullmatch(r"LEVITICUS \d+\s*[-–—]\s*\d+", s):
            continue
        out.append(ln.rstrip())
    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text).strip("\n")
    # a body line must never start a section
    text = re.sub(r"(?m)^@@ ", " @@ ", text)
    return text


class Out:
    def __init__(self, key, label, numbering=None):
        self.key = key
        self.head = ["#source: " + key, "#label: " + label]
        if numbering:
            self.head.append("#numbering: " + numbering)
        self.sections = []

    def add(self, rng, title, lines):
        body = clean(lines)
        if not body.strip():
            return
        title = re.sub(r"\s+", " ", title).strip()
        self.sections.append((rng, title, body))

    def write(self):
        OUT.mkdir(parents=True, exist_ok=True)
        parts = ["\n".join(self.head)]
        for rng, title, body in self.sections:
            parts.append("@@ %s | %s\n%s" % (rng, title, body))
        (OUT / (self.key + ".txt")).write_text("\n".join(parts) + "\n", encoding="utf-8", newline="\n")
        return len(self.sections)


def find(lines, pat, start=0, end=None, flags=0):
    rx = re.compile(pat, flags)
    end = len(lines) if end is None else end
    for i in range(start, end):
        if rx.search(lines[i].strip()):
            return i
    return None


def lettered(lines, start, end):
    """Sequential lettered headings 'A. TITLE' in lines[start:end]: A first,
    then each next letter within +3 (OCR drops some); never go back."""
    out = []
    last = None
    for i in range(start, end):
        s = lines[i].strip()
        m = re.match(r"^([A-Z])\.\s+(\S.*)$", s)
        if not m or len(s) > 90:
            continue
        letter, title = m.groups()
        if s.endswith((".", ",", ";")) or len(title) < 3 or len(title.split()) > 14:
            continue
        if last is None:
            if letter not in "ABC":
                continue
        elif not (last < letter <= chr(ord(last) + 3)) or i - out[-1][0] < 12:
            continue
        out.append((i, letter, title))
        last = letter
    return out


def caps_continuation(lines, i, maxn=4):
    """Title of an all-caps block starting at line i (joined)."""
    t = [lines[i].strip()]
    j = i + 1
    while j < len(lines) and len(t) < maxn:
        s = lines[j].strip()
        if s and re.fullmatch(r"[A-Z][A-Z ,:;'’()\-—0-9]*", s) and len(s) < 60:
            t.append(s)
            j += 1
        else:
            break
    return " ".join(t)


def comment_sections(o, lines, a, b, rng, chapters, title0):
    """Split a COMMENT block lines[a:b] (a = heading line) at lettered headings."""
    heads = lettered(lines, a + 1, b)
    # drop heads that open a tiny section: outline-list lines, not real headings
    while True:
        small = None
        for k, (i, _l, _t) in enumerate(heads):
            nxt = heads[k + 1][0] if k + 1 < len(heads) else b
            if sum(len(x) for x in lines[i + 1:nxt]) < 250 and k + 1 < len(heads):
                small = k
                break
        if small is None:
            break
        del heads[small]
    first = heads[0][0] if heads else b
    o.add(rng, "COMMENT: " + title0 if title0 else "COMMENT", lines[a + 1:first])
    for k, (i, letter, title) in enumerate(heads):
        nxt = heads[k + 1][0] if k + 1 < len(heads) else b
        r = rng
        m = re.search(r"(\d+):(\d+)[a-z]*\s*[-–—]\s*(?:(\d+):)?(\d+)", title)
        if m:
            c1, v1, c2, v2 = m.groups()
            if int(c1) in chapters and (c2 is None or int(c2) in chapters):
                r = "%s:%s-%s%s" % (c1, v1, (c2 + ":") if c2 else "", v2)
        o.add(r, "COMMENT %s: %s" % (letter, title), lines[i + 1:nxt])


def note_sections(o, lines, a, b, chapters, mode, unit_rng, unit_title):
    """Split NOTES lines[a:b] (a is the 'NOTES' line) into per-verse notes."""
    if mode == "cv":     # vol 1: '1: 1. lemma', '2:1.' for a chapter's first note, then bare '5. lemma'
        rx = re.compile(r"^(?:(\d+):\s?)?(\d+)[a-z]{0,2}(?:\s?[-–—]\s?(?:(\d+):\s?)?(\d+))?[a-z]{0,2}\.\s+(\S.*)$")
    else:                # vols 2,3: '17. lemma' / '3-4. lemma'
        rx = re.compile(r"^()(\d+)[a-z]{0,2}(?:\s?[-–—]\s?()(\d+))?[a-z]{0,2}\.\s+(\S.*)$")
    starts = []
    prev = 0
    chap = chapters[0]
    first_v = int(re.match(r"\d+:(\d+)", unit_rng).group(1))
    for i in range(a + 1, b):
        s = lines[i].strip()
        m = rx.match(s)
        if not m:
            continue
        c, v1, c2, v2, rest = m.groups()
        v1 = int(v1)
        if mode == "cv":
            if c:
                if int(c) not in chapters:
                    continue
                if starts and chap != int(c):
                    prev = 0
                chap = int(c)
            elif not starts:
                continue
        v2n = int(v2) if v2 else None
        if v1 < prev or (starts and v1 - prev > 8) or v1 > CH_MAX[chap] or (v2n and (v2n > CH_MAX[chap] or v2n < v1)):
            continue
        if not starts and v1 > first_v + 5:
            continue
        starts.append((i, chap, v1, int(v2) if v2 else None, rest))
        prev = v1
    if not starts:
        o.add(unit_rng, "NOTES: " + unit_title, lines[a + 1:b])
        return 0
    o.add(unit_rng, "NOTES intro: " + unit_title, lines[a + 1:starts[0][0]])
    for k, (i, chap, v1, v2, rest) in enumerate(starts):
        nxt = starts[k + 1][0] if k + 1 < len(starts) else b
        rng = "%d:%d" % (chap, v1)
        lab = rng
        if v2 and v2 > v1:
            rng = "%d:%d-%d" % (chap, v1, v2)
            lab = rng
        lemma = re.split(r"[.:]\s", rest, maxsplit=1)[0][:50]
        o.add(rng, "NOTE %s%s" % (lab, " - " + lemma if lemma else ""), lines[i:nxt])
    return len(starts)


# ---------------------------------------------------------------- units

# last verse of each chapter, Masoretic numbering (6 has 23 verses; 5 has 26)
CH_MAX = {1: 17, 2: 16, 3: 17, 4: 35, 5: 26, 6: 23, 7: 38, 8: 36, 9: 24, 10: 20, 11: 47, 12: 8, 13: 59,
          14: 57, 15: 33, 16: 34, 17: 16, 18: 30, 19: 37, 20: 27, 21: 24, 22: 33, 23: 44, 24: 23,
          25: 55, 26: 46, 27: 34}

# (range as Milgrom prints it, chapters set, title). Vol 1 + outline in vol 2.
UNITS_1 = [
    ("1:1-17", {1}, "The Burnt Offering"),
    ("2:1-16", {2}, "The Cereal Offering"),
    ("3:1-17", {3}, "The Well-Being Offering"),
    ("4:1-35", {4}, "The Purification Offering"),
    ("5:1-13", {5}, "The Graduated Purification Offering"),
    ("5:14-26", {5}, "The Reparation Offering"),
    ("6:1-7:38", {6, 7}, "Sacrifices: The Administrative Order"),
    ("8:1-36", {8}, "The Consecration of the Priests"),
    ("9:1-24", {9}, "The Inaugural Service"),
    ("10:1-20", {10}, "The Tragic Aftermath of the Inaugural Service"),
    ("11:1-47", {11}, "Diet Laws"),
    ("12:1-8", {12}, "Childbirth"),
    ("13:1-59", {13}, "Scale Disease"),
    ("14:1-57", {14}, "Purification after Scale Disease"),
    ("15:1-33", {15}, "Genital Discharges"),
    ("16:1-34", {16}, "The Day of Purgation (Yom Kippur)"),
]


# OCR dropped the COMMENT line; absolute 1-based line of the first lettered comment head
COMMENT_START_1 = {"5:14-26": 10864, "15:1-33": 35658}


def vol1():
    lines = read_lines(SRC / "milgrom-1" / "milgrom-lev1-16.txt")
    o = Out("milgrom-1", "Milgrom, Leviticus 1-16, Anchor Bible 3 (1991). Biblical numbering is Masoretic "
            "(5:20-26 = Eng 6:1-7; 6:1-23 = Eng 6:8-30). " + LABEL_TAIL, numbering="hebrew")
    # ---- introduction
    end_intro = find(lines, r"^Translation, Notes$")
    end_intro = end_intro - 1 if end_intro else find(lines, r"^Leviticus 1-16$")
    heads = [
        (0, "Introduction A: Name, Scope, Text, and Methodology"),
        (find(lines, r"^B\. The Antiquity of P"), "Introduction B: The Antiquity of P"),
        (find(lines, r"^C\. On the Parameters"), "Introduction C: On the Parameters, Date, and Provenience of P"),
        (find(lines, r"^D\. On Vocabulary"), "Introduction D: On Vocabulary, Style, and Structure"),
        (find(lines, r"^E\. The Priestly Theology"), "Introduction E: The Priestly Theology"),
        (find(lines, r"^F\. The Priest$"), "Introduction F: The Priest"),
        (find(lines, r"^G\. Anthropomorphism"), "Introduction G: Anthropomorphism and Revelation"),
        (find(lines, r"^H\. The Composition of Lev"), "Introduction H: The Composition of Lev 1-16"),
        (find(lines, r"^I\. The Commentators"), "Introduction I: The Commentators (and postscript)"),
    ]
    for k, (i, t) in enumerate(heads):
        j = heads[k + 1][0] if k + 1 < len(heads) else end_intro
        o.add("intro", t, lines[i + 1 if i else 0:j] if i else lines[3:j])
    # ---- units: anchored on the 16 'NOTES' lines, heading found before each
    nlines = [i for i in range(end_intro, len(lines)) if lines[i].strip() == "NOTES"]
    if len(nlines) != len(UNITS_1):
        sys.exit("milgrom-1: expected %d NOTES lines, found %d" % (len(UNITS_1), len(nlines)))
    starts = []
    prev_n = end_intro
    for (rng, chs, title), n in zip(UNITS_1, nlines):
        m = re.match(r"(\d+):(\d+)-(?:(\d+):)?(\d+)", rng)
        c1, v1, c2, v2 = m.groups()
        pat = r"^[A-Za-z][A-Za-z ,:;'’()\-—]*\(%s: ?%s ?[-–—] ?%s\)$" % (
            c1, v1, ((c2 + ":") if c2 else "") + v2)
        i = None
        for j in range(prev_n + 1, n):
            s_ = lines[j].strip()
            if re.match(pat, s_) and len(re.findall(r"[a-z]", s_)) <= 3:
                i = j
                break
        if i is None:   # OCR dropped the heading (ch 11): translation starts at the last 'Introduction' label
            for j in range(n - 1, prev_n, -1):
                if lines[j].strip() == "Introduction":
                    i = j
                    break
        if i is None:
            sys.exit("milgrom-1: heading not found for " + rng)
        starts.append(i)
        prev_n = n
    starts.append(len(lines))
    part_rx = re.compile(r"^PART [IVX]+\s*$")
    for (rng, chs, title), a, b in zip(UNITS_1, starts, starts[1:]):
        # trim trailing short title lines that belong to the next unit
        b2 = b
        for k in range(b - 1, max(a, b - 8), -1):
            s = lines[k].strip()
            if s == "" or re.match(r"^\[p\. \d+\]$", s):
                continue
            if len(s) < 75 and not s.endswith("."):
                b2 = k
            else:
                break
        pk = None
        for k in range(a + 5, b2):
            if part_rx.match(lines[k].strip()):
                pk = k
                break
        if pk:
            b2 = pk
        notes = find(lines, r"^NOTES$", a, b2)
        comm = None
        if notes is not None:
            for k in range(notes + 1, b2):
                s = lines[k].strip()
                if re.match(r"^COMMENTS?\s*:?(\s+[A-Z ,:;'’\-—]*)?$", s):
                    comm = k
                    break
        if comm is None and rng in COMMENT_START_1:
            comm = COMMENT_START_1[rng] - 2   # heading-less comment: begins at the first lettered head
        trans_end = notes if notes is not None else b2
        # introduction to chapters 1-7 sits at the end of the translation of ch 1
        ii = find(lines, r"^INTRODUCTION TO CHAPTERS", a, trans_end)
        if ii:
            o.add(rng, "Translation: " + title, lines[a + 1:ii])
            o.add("1-7", "Introduction to chapters 1-7", lines[ii + 1:trans_end])
        else:
            o.add(rng, "Translation: " + title, lines[a + 1:trans_end])
        if notes is not None:
            nend = comm if comm else b2
            note_sections(o, lines, notes, nend, sorted(chs), "cv", rng, title)
        if comm:
            ctitle = caps_continuation(lines, comm).replace("COMMENTS:", "").replace("COMMENT:", "")
            ctitle = re.sub(r"^COMMENTS?\s*", "", ctitle).strip(" :")
            comment_sections(o, lines, comm, b2, rng, chs, ctitle)
    return o


# Vol 2 / 3 anchors: (range, chapters, title, start, notes, comments, end)
# 1-based line numbers into the cleaned input; None = no such block.
UNITS_2 = [
    ("17:1-16", {17}, "The Slaughter and Consumption of Meat", 6774, 6866, 8438, 9363),
    ("18:1-30", {18}, "Illicit Sexual Practices", 9363, 9426, 12146, 12507),
    ("19:1-37", {19}, "Ritual and Moral Holiness", 12507, 13055, 17422, 17970),
    ("20:1-27", {20}, "Penalties for Molek Worship, Necromancy, and Sexual Offenses", 17970, 18041, 19575, 20515),
    ("21:1-24", {21}, "Instructions for the Priests", 20515, 20574, 22204, 22750),
    ("22:1-33", {22}, "Instructions for the Priests and Lay Persons", 22750, 22824, 24561, None),
]
UNITS_3 = [
    ("23:1-44", {23}, "The Holiday Calendar", 2827, 2990, 7700, 9036),
    ("24:1-23", {24}, "Tabernacle Oil and Bread; The Case of Blasphemy", 9036, 9109, 11106, 11985),
    ("25:1-55", {25}, "Jubilee, the Priestly Solution for Economic Injustice", 11985, 12147, 17083, 18604),
    ("26:1-46", {26}, "Blessings, Curses, and the Recall of the Covenant", 18604, 18805, 22369, 23640),
    ("27:1-34", {27}, "Consecrations and Their Redemption", 23640, 23769, 25425, None),
]


def run_units(o, lines, units, end_of_file, extra_end=None):
    for rng, chs, title, a, n, c, e in units:
        a -= 1
        n = n - 1 if n else None
        c = c - 1 if c else None
        e = (e - 1) if e else end_of_file
        # translation ends at the "Comment(s)" cross-reference list when present, else at intro start
        tend = n
        xref = find(lines, r"^Comments?$", a, n)
        intro_a = None
        if xref is not None:
            intro_a = xref
        o.add(rng, "Translation: " + title, lines[a + 1:(xref if xref else tend) + (3 if xref else 0)])
        if xref is not None:
            # lines after the xref list up to NOTES = structural/composition introduction
            body = lines[xref + 3:n]
            o.add(rng, "Introduction to chapter %d" % min(chs), body)
        elif n and n > a:
            pass
        if n is None:
            continue
        nend = c if c else e
        if c is None and rng == "23:1-44":
            # chapter 23 comments are not marked in the OCR; find first lettered comment
            pass
        note_sections(o, lines, n, nend, sorted(chs), "v", rng, title)
        if c:
            ctitle = ""
            if re.fullmatch(r"COMMENTS?", lines[c].strip()):
                nxt = lines[c + 1].strip() if c + 1 < len(lines) else ""
                ctitle = ""
            else:
                ctitle = lines[c].strip()
            comment_sections(o, lines, c, e, rng, chs, ctitle)


def vol2():
    lines = read_lines(SRC / "milgrom-2" / "milgrom-lev17-22.txt")
    o = Out("milgrom-2", "Milgrom, Leviticus 17-22, Anchor Bible 3A (2000). Printed refs for chaps. 5-6 "
            "are Masoretic. " + LABEL_TAIL, numbering="hebrew")
    # ---- full-book translation (units 1-16 only; 17-22 repeat below)
    t0 = 55
    pos = t0
    starts = []
    for n in range(1, 17):
        rx = re.compile(r"^%d\. [A-Z]" % n)
        i = None
        for j in range(pos, 1990):
            if rx.match(lines[j].strip()):
                i = j
                break
        if i is None:
            sys.exit("milgrom-2: full translation unit %d not found" % n)
        starts.append(i)
        pos = i + 1
    i17 = find(lines, r"^17\. The Slaughter", pos)
    starts.append(i17)
    for (rng, chs, title), a, b in zip(UNITS_1, starts, starts[1:]):
        body = [l for l in lines[a + 1:b] if not re.match(r"^PART [IVX]+\.", l.strip())]
        o.add(rng, "Full-book translation: " + title, body)
    # ---- introduction to H (printed pp. 1319-1443)
    ia = find(lines, r"^Lev 17-27 is conventionally called the Holiness Code")
    ib = 6773 - 0
    # drop the page-number-only separator lines at the very start
    split = 4085   # 'B. RATIONALES ARE THEOLOGY': the lettering restarts here (part 2)
    parts = [(i, l, t, 1) for i, l, t in lettered(lines, ia, split - 1)]
    parts += [(i, l, t, 2) for i, l, t in lettered(lines, split - 1, ib)]
    o.add("intro", "Introduction to H: opening", lines[ia:parts[0][0]])
    for k, (i, l, t, part) in enumerate(parts):
        j = parts[k + 1][0] if k + 1 < len(parts) else ib
        pname = "Introduction to H" if part == 1 else "Introduction to H, part 2"
        o.add("intro", "%s %s: %s" % (pname, l, t), lines[i + 1:j])
    run_units(o, lines, UNITS_2, len(lines))
    return o


def vol3():
    lines = read_lines(SRC / "milgrom-3" / "milgrom-lev23-27.txt")
    o = Out("milgrom-3", "Milgrom, Leviticus 23-27, Anchor Bible 3B (2001). " + LABEL_TAIL)
    run_units(o, lines, UNITS_3, 26901)   # ch 27 comments end where the responses begin
    # appendices after the commentary: responses, addenda, corrigenda
    ra = 26901
    marks = [
        (find(lines, r"^RESPONSE$", ra - 1, ra + 5), "Responses to reviewers: preface"),
        (find(lines, r"^B\. RESPONSE$", ra), "Response B: to Baruch Levine"),
        (find(lines, r"^C\. Rejoinder to Israel Knohl", ra), "Response C: Rejoinder to Israel Knohl"),
        (find(lines, r"^D\. Response to Adrian Schenker", ra), "Response D: to Adrian Schenker"),
        (find(lines, r"^E\. RESPONSE$", ra), "Response E: to Victor Hurowitz"),
        (find(lines, r"^F\. ON THE SAVAGE IN JUDAISM", ra), "Response F: On The Savage in Judaism (Eilberg-Schwartz)"),
        (find(lines, r"^RESPONSE$", find(lines, r"^F\. ON THE SAVAGE", ra) + 2), "Response G: to Hyam Maccoby"),
        (find(lines, r"^ADDENDA$", ra), "Addenda"),
        (find(lines, r"^CORRIGENDA$", ra), "Corrigenda"),
    ]
    marks = [(i, t) for i, t in marks if i is not None]
    marks.sort()
    for k, (i, t) in enumerate(marks):
        j = marks[k + 1][0] if k + 1 < len(marks) else len(lines)
        o.add("intro", t, lines[i + 1:j])
    return o


def main():
    which = sys.argv[1:] or ["milgrom-1", "milgrom-2", "milgrom-3"]
    for k in which:
        o = {"milgrom-1": vol1, "milgrom-2": vol2, "milgrom-3": vol3}[k]()
        n = o.write()
        print("%s: %d sections" % (k, n))


if __name__ == "__main__":
    main()
