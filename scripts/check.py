#!/usr/bin/env python3
"""Sanity checks for the progress-tracking files and routine prompts.

Usage (from the repo root):
    python3 scripts/check.py                      # everything
    python3 scripts/check.py data                 # LEVEL.md, HISTORY.md, RATINGS.md
    python3 scripts/check.py routines/daily.md    # one prompt file

Prints every failed check and exits 1, or prints OK.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors = []


def need(cond, msg):
    if not cond:
        errors.append(msg)


def read(rel):
    path = ROOT / rel
    if not path.exists():
        errors.append(f"missing file: {rel}")
        return ""
    return path.read_text(encoding="utf-8")


def block(text, name):
    m = re.search(rf"<!-- {name}:BEGIN -->\n(.*?)<!-- {name}:END -->", text, re.S)
    return None if m is None else [l for l in m[1].splitlines() if l.strip()]


LEVEL_KEYS = ("am", "pm", "am_words", "pm_words", "am_l5_since", "pm_l5_since",
              "am_c1_unlocked", "pm_c1_unlocked", "last_weekly_review", "last_monthly_review")
LEVEL_SECTIONS = ("## Cari vəziyyət", "## Pilləkən", "## Hədd rəqəmləri", "## Maraq", "## Tarixçə")


def check_level():
    s = read("LEVEL.md")
    for h in LEVEL_SECTIONS:
        need(h in s, f"LEVEL.md: section '{h}' missing")
    for key in LEVEL_KEYS:
        need(re.search(rf"^- {key}: \S", s, re.M), f"LEVEL.md: key '{key}' missing")
    for slot in ("am", "pm"):
        need(re.search(rf"^- {slot}: L[1-6]$", s, re.M), f"LEVEL.md: '{slot}' must be L1..L6")
        need(re.search(rf"^- {slot}_c1_unlocked: (yes|no)$", s, re.M),
             f"LEVEL.md: '{slot}_c1_unlocked' must be yes or no")
        m = re.search(rf"^- {slot}_words: (\d+)-(\d+)$", s, re.M)
        need(m and 60 <= int(m[1]) and int(m[2]) <= 300 and int(m[2]) - int(m[1]) == 20,
             f"LEVEL.md: '{slot}_words' must be N-(N+20) within 60-300")
    for n in range(1, 7):
        need(re.search(rf"^\| L{n} \|", s, re.M), f"LEVEL.md: ladder row L{n} missing")
    for name in ("Sevimli", "Seyrək"):
        need(re.search(rf"^- {name}: \S", s, re.M), f"LEVEL.md: '{name}' line missing")


HISTORY_RE = re.compile(
    r"^(\d{4}-\d{2}-\d{2}) \| (am|pm) \| (PRACTICAL|KNOWLEDGE) \| \d+ [^|]+ \| [^|]+ \| [^|]+?"
    r"(?: \| L[1-6] \| \d+w)?$")
LEVELED_FROM = "2026-09-28"  # lines from this date on must carry | Ln | Nw


def check_history():
    lines = block(read("HISTORY.md"), "RUNS")
    need(lines is not None, "HISTORY.md: RUNS markers missing")
    for line in lines or []:
        m = HISTORY_RE.match(line)
        need(m, f"HISTORY.md: bad line: {line}")
        if m and m[1] >= LEVELED_FROM:
            need(re.search(r" \| L[1-6] \| \d+w$", line), f"HISTORY.md: level/word columns missing: {line}")


RATING_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2} \| (am|pm) \| \d+ [^|]+ \| L[1-6] \| \d+w \| ([^|]+) \| \d{4}-\d{2}-\d{2} \d{2}:\d{2}$")
FIELDS_RE = {
    "am": re.compile(r"^cet=([1-5]|-) isl=([1-5]|-) fay=([1-5]|-) uzn=[+0-]$"),
    "pm": re.compile(r"^cet=([1-5]|-) bil=[bqy-] anl=([1-5]|-) mar=([1-5]|-) uzn=[+0-]$"),
}


def check_ratings():
    lines = block(read("RATINGS.md"), "RATINGS")
    need(lines is not None, "RATINGS.md: RATINGS markers missing")
    seen = set()
    for line in lines or []:
        m = RATING_RE.match(line)
        need(m, f"RATINGS.md: bad line: {line}")
        if not m:
            continue
        need(FIELDS_RE[m[1]].match(m[2].strip()), f"RATINGS.md: bad {m[1]} fields: {line}")
        key = " | ".join(line.split(" | ")[:3])
        need(key not in seen, f"RATINGS.md: duplicate rating: {key}")
        seen.add(key)


GIT_RULES = ["git checkout -B main origin/main", "git push origin HEAD:main", "git pull --rebase origin main"]
PROMPT_RULES = {
    "routines/daily.md": GIT_RULES + [
        "cat LEVEL.md", "Sevimli", "Seyrək", "## Pilləkən", "wc -w", "| Ln | Nw",
        "## Qiymət kodu", "Nümunə: 2 4 5 +", "Nümunə: 3 q 4 5 -",
        "the fields follow the text's slot", "ask him once", "use `L2`",
        "replace it instead of adding a second one", "<!-- RATINGS:BEGIN -->",
        'git commit -m "Rate reading text: <English title>"',
    ],
    "routines/weekly.md": GIT_RULES + [
        "TZ=Asia/Baku date '+%G-W%V'", "last_weekly_review", "python3", "down wins",
        "c1_unlocked", "Səhv sözlər:", "Never write the answers", "exclude every quiz word",
        "### Nəticə: cavablanmayıb",
        'git commit -m "Weekly review: <label>"', 'git commit -m "Grade word quiz: <label>"',
        'git commit -m "Revert level change: <label>"', "geri qaytar",
    ],
    "routines/monthly.md": GIT_RULES + [
        "last_monthly_review", "Sevimli", "Seyrək", "at least 90 days", "next free index",
        "c1_unlocked", 'git commit -m "Monthly review: <label>"',
        'git commit -m "Revert monthly change: <label>"',
    ],
}
FORBIDDEN = {"routines/daily.md": ["5–6 sentence", "A2–B1"]}


def check_prompt(rel):
    s = read(rel)
    if not s:
        return
    for phrase in PROMPT_RULES[rel]:
        need(phrase in s, f"{rel}: missing rule text: {phrase}")
    for phrase in FORBIDDEN.get(rel, []):
        need(phrase not in s, f"{rel}: outdated text still present: {phrase}")


def main(args):
    for target in args or ["data", *PROMPT_RULES]:
        if target == "data":
            check_level()
            check_history()
            check_ratings()
        elif target in PROMPT_RULES:
            check_prompt(target)
        else:
            errors.append(f"unknown target: {target}")
    if errors:
        print("\n".join(errors))
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
