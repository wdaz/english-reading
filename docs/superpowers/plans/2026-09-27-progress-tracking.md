# Progress Tracking Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ruslan rates every reading text in its session; weekly and monthly routines turn those ratings into level, length and topic changes that the daily routine applies.

**Architecture:** The repository is the shared memory. The daily routine reads `LEVEL.md` to decide level and length, and writes ratings to `RATINGS.md`. A new weekly routine reads `RATINGS.md` and rewrites `LEVEL.md`. A new monthly routine updates interest lists, `TOPICS.md` and C1. Routine prompts are versioned in `routines/*.md` and deployed with the RemoteTrigger tool. `scripts/check.py` pins file formats and prompt rules.

**Tech Stack:** Markdown files · Claude Code cloud routines (RemoteTrigger API) · git · Python 3 stdlib (check script only).

**Spec:** `docs/superpowers/specs/2026-09-27-progress-tracking-design.md`

## Global Constraints

- Work in the clone `/Users/ruslan/.claude/jobs/2fca03af/tmp/engilish-reading` (remote `https://github.com/wdaz/english-reading.git`, branch `main`); this repo is pushed straight to `main`.
- Before each task: `git fetch -q origin && git checkout -q main && git reset -q --hard origin/main` — routines push to `main` twice a day.
- Every commit made while executing this plan ends with:
  `Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>` and
  `Claude-Session: https://claude.ai/code/session_01J1dMVideq8JXAMr7R6iTs5`.
- Routine git, verbatim: `git fetch origin main` + `git checkout -B main origin/main`; push only with `git push origin HEAD:main`; on rejection `git pull --rebase origin main` once, then push again.
- Routine config: environment `env_01G4m8Pj3jLp3gg2FmJUafTA`, model `claude-sonnet-5`, tools `Bash, Read, Write, Edit, Glob, Grep`, source `https://github.com/wdaz/english-reading`.
- Cron (UTC): daily `0 6,15 * * *` (10:00/19:00 Baku), weekly `0 17 * * 0` (Sunday 21:00 Baku), monthly `30 17 1 * *` (1st, 21:30 Baku).
- Start values: `am: L3`, `pm: L2`, `am_words: 100-120`, `pm_words: 100-120`.
- Length: step 20 words, bounds 60–300, measurement tolerance 10%. Length changes only via weekly `+`/`-` votes (net ≥ 2 / ≤ −2); no direct command.
- Rating codes: am `<çətinlik> <işlədə bilərəm> <faydalı> [+|-]` (example `2 4 5 +`), pm `<çətinlik> <bilirdim b|q|y> <anlama> <maraq> [+|-]` (example `3 q 4 5 -`); stored `uzn` ∈ {`+`, `0`, `-`}; a missing field is `-`.
- Everything Ruslan reads is Azerbaijani with correct orthography (ə, ı, ö, ü, ç, ş, ğ); routine prompts are English.

## Review Focus

1. Rating an older text whose `HISTORY.md` line has no `| Ln | Nw` columns → level `L2`, word count from the file; must not fail or invent a level. (Task 2 prompt rule + check.)
2. Rating the same text twice → the second rating replaces the first; `RATINGS.md` never holds two lines with the same date | slot | category. (Task 1 duplicate check + Task 2 prompt rule.)
3. Rating yesterday's `pm` text from this morning's `am` session, or giving 4 values to an `am` text → fields follow the rated text's slot; a mismatched count is asked about once. (Task 2 prompt rules + check.)
4. A week with zero ratings and HISTORY lines without word counts → review is still written, levels unchanged, word counts taken from files. (Task 6 live W39 run.)
5. Quiz answers leaking before grading → the review file and message hold only questions until Ruslan answers. (Task 3 prompt rule + check; Task 6 inspection.)

---

### Task 1: Data files and the check script

**Files:**
- Create: `scripts/check.py`
- Create: `LEVEL.md`
- Create: `RATINGS.md`
- Modify: `HISTORY.md` (header format line only)
- Modify: `README.md` (full rewrite, content below)

**Interfaces:**
- Produces: `python3 scripts/check.py [data|routines/daily.md|routines/weekly.md|routines/monthly.md]` → prints `OK` / exit 0, or one line per failure / exit 1. `LEVEL.md` keys `am`, `pm`, `am_words`, `pm_words`, `am_l5_since`, `pm_l5_since`, `am_c1_unlocked`, `pm_c1_unlocked`, `last_weekly_review`, `last_monthly_review`; sections `## Cari vəziyyət`, `## Pilləkən`, `## Hədd rəqəmləri`, `## Maraq` (lines `- Sevimli:` / `- Seyrək:`), `## Tarixçə`. `RATINGS.md` block `<!-- RATINGS:BEGIN -->` / `<!-- RATINGS:END -->`.

- [ ] **Step 1: Write the check script (the test)**

Create `scripts/check.py`:

```python
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
        "c1_unlocked", "Səhv sözlər:", "Never write the answers", "### Nəticə: cavablanmayıb",
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
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python3 scripts/check.py data`
Expected: exit 1, output contains `missing file: LEVEL.md`, `missing file: RATINGS.md`, `RATINGS.md: RATINGS markers missing`. No `HISTORY.md: bad line` lines (existing history must already pass).

- [ ] **Step 3: Create `LEVEL.md`**

```markdown
# Səviyyə

Routine-lər bu faylı oxuyur və yeniləyir: gündəlik routine mətni buradakı pillə və
uzunluğa görə yazır, həftəlik və aylıq review-lar dəyərləri dəyişir.
Rəqəmləri əl ilə də dəyişmək olar — formatı saxla.

## Cari vəziyyət

- am: L3
- pm: L2
- am_words: 100-120
- pm_words: 100-120
- am_l5_since: -
- pm_l5_since: -
- am_c1_unlocked: no
- pm_c1_unlocked: no
- last_weekly_review: -
- last_monthly_review: -

## Pilləkən

Qrammatika yığılır: hər pillə cədvəldə özündən yuxarıdakı sətirlərin qrammatikasını da
daxil edir. Uzunluq pillədən asılı deyil — onu `am_words` / `pm_words` idarə edir.

| Pillə | CEFR | Yeni söz | Qrammatika | Səhər məzmunu | Axşam məzmunu |
|---|---|---|---|---|---|
| L1 | A2 | 4–5 | present/past simple, can, going to | sadə xahiş | bir fakt və ya hadisə |
| L2 | A2+ | 5–6 | + present perfect, comparatives, because/so | + problem, şikayət | + səbəb |
| L3 | B1 | 6–7 | + passive, first conditional, relative clauses | + izah etmək, danışıq | + nəticə, müqayisə |
| L4 | B1+ | 7–8 | + second conditional, reported speech, phrasal verbs | + rəsmi dil, telefon, e-mail | + fərqli baxışlar |
| L5 | B2 | 8 | mixed tenses, idiomlar, bağlayıcılar | + nəzakət, yumşaltma | + nüans, mübahisəli tərəf |
| L6 | C1 | 8–10 | inversion, cleft sentences, mixed conditionals | + inandırma, diplomatik dil | + abstrakt arqument, gizli məna |

## Hədd rəqəmləri

- min_ratings: 3
- am_up: cet <= 2.5 and isl >= 4.0
- am_down: cet >= 4.2 or isl <= 2.0
- pm_up: anl >= 4.3 and cet <= 2.5 (bil=b olan qiymətlər sayılmır)
- pm_down: anl <= 2.5 or cet >= 4.2
- c1_after_days: 90
- length_step: 20
- length_min: 60
- length_max: 300
- length_vote: (+) − (−) >= 2 → +step; <= −2 → −step
- length_tolerance: 10%
- favorite: avg >= 4.5, min 2 ratings, repeat after 10 days
- rare: avg <= 2.0, min 2 ratings, skip for 45 days
- max_new_categories_per_month: 3

## Maraq

- Sevimli: -
- Seyrək: -

## Tarixçə

- 2026-09-27: başlanğıc — am L3 100-120 söz, pm L2 100-120 söz
```

- [ ] **Step 4: Create `RATINGS.md`**

```markdown
# Qiymətlər

Hər sətir bir mətnin qiymətidir. Gündəlik routine yazır (Step 7). Format:

`mətn tarixi | slot | index kateqoriya | pillə | söz sayı | qiymət | qiymət vaxtı (Bakı)`

- Səhər: `cet=<1-5> isl=<1-5> fay=<1-5> uzn=<+|0|->`
- Axşam: `cet=<1-5> bil=<b|q|y> anl=<1-5> mar=<1-5> uzn=<+|0|->`
- `-` = sahə verilməyib. `uzn`: `+` daha uzun, `0` uyğun, `-` daha qısa.
- Eyni mətn yenidən qiymətləndirilsə sətir əvəz olunur.

<!-- RATINGS:BEGIN -->
<!-- RATINGS:END -->
```

- [ ] **Step 5: Update the `HISTORY.md` header**

Replace exactly this line:

```
`YYYY-MM-DD | am|pm | LIST | index kateqoriya | keyword | English title`
```

with:

```
`YYYY-MM-DD | am|pm | LIST | index kateqoriya | keyword | English title | L<n> | <n>w`

Son iki sütun: mətnin pilləsi (`LEVEL.md`) və passage-ın həqiqi söz sayı.
2026-09-28-dən əvvəlki sətirlərdə bu sütunlar yoxdur — onlar üçün pillə L2 sayılır.
```

Do not touch anything inside the `RUNS` markers.

- [ ] **Step 6: Rewrite `README.md`**

Replace the whole file with:

```markdown
# English Reading

Gündəlik ingilis dili oxu mətnləri, Azərbaycan dilində izahlarla. Səviyyə A2-dən
C1-ə qədər dəyişir və sənin qiymətlərinə görə uyğunlaşır.
Claude Code routine-ləri avtomatik işləyir: mətnlər hər gün 10:00 və 19:00 (Bakı),
həftəlik review bazar 21:00, aylıq review ayın 1-i 21:30.

## Struktur

| Fayl | Nə üçün |
|---|---|
| `TOPICS.md` | Kateqoriya siyahıları (PRACTICAL / KNOWLEDGE). Prompt-u dəyişmədən redaktə et. |
| `HISTORY.md` | İşlənmiş mövzular: təkrarın qarşısını alır, pillə və söz sayını saxlayır. |
| `LEVEL.md` | Cari pillə, mətn uzunluğu, qaydaların rəqəmləri, maraq siyahıları, tarixçə. |
| `RATINGS.md` | Verdiyin qiymətlər, hər mətnə bir sətir. |
| `texts/` | Mətnlərin özü, `YYYY-MM-DD-{am,pm}.md` formatında. |
| `reviews/` | Həftəlik (`2026-W40.md`) və aylıq (`2026-10.md`) review-lar. |
| `routines/` | Routine prompt-larının mənbəyi. |
| `scripts/check.py` | Faylların formatını yoxlayır: `python3 scripts/check.py`. |

## Mətni necə oxumalı

1. Əvvəlcə ingiliscə mətni lüğətsiz oxu.
2. "Yeni sözlər"-ə bax, tələffüzü ucadan təkrarla.
3. Mətni ikinci dəfə oxu.
4. "Suallar"-a öz sözlərinlə cavab ver, sonra "Tərcümə"-yə bax.
5. Mətnin gəldiyi sessiyada qiymət kodunu yaz.

## Qiymət vermək

Hər mətnin sonunda `Qiymət kodu` bloku gəlir. Kodu həmin sessiyada yaz.

Səhər (praktik mətn):

    Qiymət: <çətinlik> <işlədə bilərəm> <faydalı> [uzunluq]
    Nümunə: 2 4 5 +

Axşam (bilik mətni):

    Qiymət: <çətinlik> <bilirdim> <anlama> <maraq> [uzunluq]
    Nümunə: 3 q 4 5 -

| Sahə | 1 | 3 | 5 |
|---|---|---|---|
| Çətinlik | hər şey tanış idi | bir neçə cümlə çətin idi | lüğətsiz alınmadı |
| İşlədə bilərəm | bu situasiyada özüm danışa bilməzdim | yarımçıq danışardım | rahat danışardım |
| Faydalı | belə situasiya həyatımda olmur | bəzən olur | tez-tez rast gəlirəm |
| Anlama (tərcüməsiz) | ≈ 20% | ≈ 60% | ≈ 100% |
| Maraq | darıxdırıcı | normal | belə mətnlərdən daha çox istəyirəm |

- **Anlama:** 1 ≈ 20% · 2 ≈ 40% · 3 ≈ 60% · 4 ≈ 80% · 5 ≈ 100%
- **Bilirdim:** `b` bəli · `q` qismən · `y` yox
- **Uzunluq** (istəyə bağlı): `+` daha uzun olsun · `-` daha qısa olsun · yazmasan = uyğun
- Təbii dillə də yazmaq olar: "asan idi, bilmirdim, çox maraqlı".
- Başqa günün mətni: `dünənki axşam: 2 b 5 3` və ya `2026-09-25 pm: 2 b 5 3`.
- Yenidən qiymət versən, köhnəsi əvəz olunur.

## Səviyyə və uzunluq

- Səhər və axşamın ayrıca pilləsi var: L1 (A2) → L6 (C1). Pilləkən `LEVEL.md`-dədir.
- Həftəlik review hər slotu qiymətlərə görə ən çox bir pillə qaldırır və ya endirir.
- L5-də (B2) 90 gün qalandan sonra aylıq review C1-i (L6) açır.
- Uzunluq pillədən asılı deyil. Həftə ərzində `+` işarələri `-`-lərdən ən azı 2 çox olsa,
  mətnlər 20 söz uzanır; `-` işarələri ən azı 2 çox olsa, 20 söz qısalır.

## Review-lar

- **Həftəlik** (bazar 21:00): ortalamalar, pillə və uzunluq qərarı, 5 suallıq söz testi.
  Testə həmin sessiyada cavab ver. Qərarı bəyənməsən, "geri qaytar" yaz.
- **Aylıq** (ayın 1-i 21:30): trend, maraq siyahıları (sevimli mövzular tez-tez gəlir,
  darıxdırıcılar seyrək), sevimli mövzulara yeni kateqoriyalar, C1 yoxlaması.

## Anlaşılmayan söz olanda

Mətn gələn sessiyada birbaşa sözü yaz — izah orada verilir, sonra avtomatik
həmin günün mətn faylındakı `## Yeni sözlər` siyahısının sonuna əlavə edilib
push olunur. Beləliklə hər mətn öz çətin sözləri ilə birlikdə bir yerdə qalır.
```

- [ ] **Step 7: Run the check to verify it passes**

Run: `python3 scripts/check.py data`
Expected: `OK`, exit 0.

- [ ] **Step 8: Prove the check catches bad data (in a throwaway copy)**

```bash
tmp=$(mktemp -d) && cp -R . "$tmp/r" && cd "$tmp/r" && python3 - <<'PY'
p = "RATINGS.md"
s = open(p, encoding="utf-8").read()
bad = ("2026-09-27 | pm | 1 space and planets | L2 | 130w | cet=3 bil=q anl=4 mar=5 uzn=0 | 2026-09-27 21:10\n"
       "2026-09-27 | pm | 1 space and planets | L2 | 130w | cet=3 bil=q anl=4 mar=5 uzn=0 | 2026-09-27 21:20\n"
       "2026-09-28 | am | 5 hotels and accommodation | L3 | 108w | cet=2 bil=q anl=4 mar=5 uzn=0 | 2026-09-28 10:42\n")
open(p, "w", encoding="utf-8").write(s.replace("<!-- RATINGS:END -->", bad + "<!-- RATINGS:END -->"))
PY
python3 scripts/check.py data; echo "exit=$?"; cd - >/dev/null; rm -rf "$tmp"
```

Expected: `RATINGS.md: duplicate rating: 2026-09-27 | pm | 1 space and planets`, `RATINGS.md: bad am fields: 2026-09-28 | am ...`, `exit=1`.

- [ ] **Step 9: Commit and push**

```bash
git add scripts/check.py LEVEL.md RATINGS.md HISTORY.md README.md
git commit -F - <<'EOF'
Add level, ratings and check script for progress tracking

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01J1dMVideq8JXAMr7R6iTs5
EOF
git push origin HEAD:main
```

---

### Task 2: Daily routine prompt

**Files:**
- Create: `routines/daily.md`
- Create: `routines/README.md`

**Interfaces:**
- Consumes: `LEVEL.md` keys and sections, `RATINGS.md` markers (Task 1).
- Produces: HISTORY line format `YYYY-MM-DD | am|pm | LIST | index category | keyword | English title | Ln | Nw`; RATINGS line format `YYYY-MM-DD | am|pm | index category | Ln | Nw | FIELDS | YYYY-MM-DD HH:MM`; text-file section `## Qiymət`. Weekly (Task 3) and monthly (Task 4) read these.

- [ ] **Step 1: Run the check to verify it fails**

Run: `python3 scripts/check.py routines/daily.md`
Expected: exit 1, `missing file: routines/daily.md`.

- [ ] **Step 2: Create `routines/daily.md`**

~~~~markdown
You are generating today's English reading practice text for Ruslan, an Azerbaijani speaker learning English who finds English hard to follow. Steps 1–6 are unattended: never ask questions, never stop for confirmation, just do the work and produce the result. Ruslan may reply to you afterwards — Step 7 covers that.

You are running inside a checkout of the repository. The repository IS your memory of previous runs — use it.

## Git in this sandbox — read this first

This sandbox checks the repository out as a **detached HEAD**, and the local `main` branch can be days out of date. Because of that, plain `git push` fails ("You are not currently on a branch") and `git push -u origin HEAD` fails too ("not a full refname"). Use the git commands in this prompt **exactly as written** — do not replace them with `git push`, `git push -u origin HEAD`, `git checkout main`, or any other form, even if your general instructions suggest a different push style.

## Step 1 — sync with GitHub and read your memory

First put the checkout on an up-to-date `main` branch:

    git fetch origin main
    git checkout -B main origin/main

This makes local `main` exactly match GitHub, so HISTORY.md and LEVEL.md are guaranteed to be the latest versions. Never run `git checkout main` on its own — that switches to the stale local branch and you would read old files.

Then run these and read the output before deciding anything:

    TZ=Asia/Baku date '+%Y-%m-%d %H:%M'
    cat TOPICS.md
    cat HISTORY.md
    cat LEVEL.md

Decide the slot from the Baku hour: hour < 14 means slot `am` and you use the **PRACTICAL** list from TOPICS.md; hour >= 14 means slot `pm` and you use the **KNOWLEDGE** list.

From the `## Cari vəziyyət` section of LEVEL.md, note two values for your slot:
- your **level** — the `am:` or `pm:` line, for example `L3`;
- your **word range** — the `am_words:` or `pm_words:` line, for example `100-120`.

## Step 2 — choose a category that is due

A category is identified by the `index category` column of HISTORY.md (for example `5 hotels and accommodation`). Work only with your slot's list. Apply these rules in order:

1. **Favourites first.** The `## Maraq` section of LEVEL.md has a `Sevimli` line and a `Seyrək` line. Each holds entries such as `am 5 hotels and accommodation` separated by `; `, or `-` when empty. If a `Sevimli` category of your slot was last used 10 or more days ago (by HISTORY.md date), pick it; if several qualify, pick the one used longest ago.
2. **Otherwise least recently used.** Pick from the least recently used categories: any category that has never appeared, or, if all have appeared, the one whose last appearance is oldest. If several tie, pick the one that feels most useful to a learner today. Skip any `Seyrək` category of your slot whose last use was fewer than 45 days ago.
3. Never repeat a category used in the last 7 days unless the list gives you no other option.

## Step 3 — choose a narrow subject

Pick ONE specific, narrow subject inside that category — never a general overview.
- Good: "how octopuses change colour", "what to say when your hotel room is not ready".
- Bad: "wild animals", "hotels".

Hard rule: the subject must not repeat anything in HISTORY.md — compare against both the keyword column and the title column, and treat close variations as repeats.
- For KNOWLEDGE categories, deliberately avoid the most famous, obvious example; prefer something less well known but genuinely true and interesting.
- For PRACTICAL categories, write about a realistic everyday situation or concrete useful advice, and use the words and phrases a person would actually need in that situation.

## Step 4 — write the text at your level and length

Find your level's row in the `## Pilləkən` table of LEVEL.md and follow it:
- **CEFR** column — the overall level of the language.
- **Qrammatika** column — use the grammar of your row and of every row above it in the table; avoid grammar that first appears in the rows below it.
- **Yeni söz** column — how many items the `Yeni sözlər` list gets.
- **Content column** — `Səhər məzmunu` for slot `am`, `Axşam məzmunu` for slot `pm`. It tells you how deep the passage goes; a `+` means "in addition to everything in the rows above".

Length: the passage must have between the two numbers of your word range (for `100-120`: 100 to 120 words). Length is independent of level — never make the passage longer or shorter because of the level. The number of sentences follows from the length and the level; do not aim for a fixed number of sentences.

Use clear, natural sentences. Everything must be factually accurate — if you are not sure a detail is true, leave it out.

The finished text must follow this Markdown structure **exactly** — same headings, same heading level, same order, nothing added before the title and nothing extra between the sections:

    # English Title

    ### *Azərbaycanca başlıq*

    <the passage, one single paragraph>

    ## Yeni sözlər

    - **word** /IPA/ [AZ-TƏLƏFFÜZ] — azərbaycanca tərcümə; qısa qeyd.
    - **word** /IPA/ [AZ-TƏLƏFFÜZ] — azərbaycanca tərcümə; qısa qeyd.

    ## Tərcümə

    <full Azerbaijani translation of the passage, one single paragraph>

    ## Suallar

    1. <short comprehension question in English>
    2. <short comprehension question in English>

Formatting rules, follow them strictly:
- The `#` title line holds the English title ONLY. Never put the Azerbaijani title in brackets after it.
- The Azerbaijani title is the subtitle. It goes on the line right below the `#` title, as an `###` heading with the text in italics: `### *Azərbaycanca başlıq*`. Keep both the `###` level and the italics exactly as shown.
- The three section headings — `## Yeni sözlər`, `## Tərcümə`, `## Suallar` — are always `##`, never bold text instead of a heading. `###` is used for the subtitle and nowhere else.
- **`Yeni sözlər` is a Markdown bullet list.** Every entry is its own list item and MUST begin with `- `. This is not optional: plain lines without a list marker collapse into one paragraph when the file is rendered, which makes the section unreadable.
- The list has as many items as the `Yeni söz` column of your level says, as consecutive lines with no blank line between them.
- After the `- `, each entry is exactly: the English word in bold, the IPA in slashes, the Azerbaijani-letter pronunciation in square brackets with the stressed syllable in CAPITALS, an em dash, the Azerbaijani translation, a semicolon, a short note.
  Real example: `- **ancient** /ˈeɪn.ʃənt/ [EYN-şınt] — qədim; çox köhnə dövrlərə aid.`
- `Suallar` holds exactly 2 numbered questions, written in English, with no answers. At L4 and above, make the second question a "why" or "what would happen if" question.
- Everything outside the English passage and the English questions is in Azerbaijani, with correct orthography (ə, ı, ö, ü, ç, ş, ğ).

## Step 5 — save, measure, record

Write that text, exactly as structured above, to `texts/YYYY-MM-DD-SLOT.md`, using the Baku date and the slot `am` or `pm`. If that file already exists, append `-2` before `.md`. Remember this file path — you will need it in Step 7.

Measure the passage — the lines between the `###` subtitle and the first `##` heading — with exactly this command (use your file path):

    awk '/^### /{p=1;next} /^## /{p=0} p' texts/YYYY-MM-DD-SLOT.md | wc -w

The count is acceptable if it is at least 90% of the lower number and at most 110% of the upper number of your word range (for `100-120`: 90 to 132). If it is outside, rewrite the passage and its translation to fit, keep everything else, and measure again. Do at most 2 rewrites; after that keep the text as it is. Remember the final count N.

Then add exactly one line inside the `<!-- RUNS:BEGIN -->` / `<!-- RUNS:END -->` block in HISTORY.md, at the end of the block, in this format:

    YYYY-MM-DD | am|pm | LIST | index category | keyword | English title | Ln | Nw

where `keyword` is the one-word main keyword of your subject, `Ln` is your level (for example `L3`) and `Nw` is the final count followed by `w` (for example `112w`). The title column holds the English title only.

Then commit and push with exactly these commands:

    git add -A
    git commit -m "Add reading text: <English title>"
    git push origin HEAD:main

`HEAD:main` pushes the commit you are on to the `main` branch on GitHub, and it works whether or not you are on a branch. If the push is rejected because GitHub has newer commits, run `git pull --rebase origin main` once and then `git push origin HEAD:main` again. If it still fails, do not give up on the run — report the failure in one line at the end of your message and continue.

## Step 6 — deliver

Send the complete text (title, Azerbaijani subtitle, passage, Yeni sözlər, Tərcümə, Suallar) as your final message to the user, so it appears in full in the notification. Keep the same structure as the file: English title, italic Azerbaijani subtitle under it, and the `Yeni sözlər` bullet list. Do not summarise it, do not just link to the file, and do not add any commentary before the title.

After `Suallar`, end the message with the rating guide for your slot, copied exactly. It goes in the message only — never into the file. The example numbers are fixed; never replace them with a real rating.

For slot `am`:

    ## Qiymət kodu

    ```
    Qiymət: <çətinlik> <işlədə bilərəm> <faydalı> [uzunluq]
    Nümunə: 2 4 5 +

    çətinlik, işlədə bilərəm, faydalı: 1–5
    uzunluq: + uzun olsun · - qısa olsun · boş = uyğun
    ```

For slot `pm`:

    ## Qiymət kodu

    ```
    Qiymət: <çətinlik> <bilirdim> <anlama> <maraq> [uzunluq]
    Nümunə: 3 q 4 5 -

    çətinlik, anlama, maraq: 1–5
    bilirdim: b bəli · q qismən · y yox
    uzunluq: + uzun olsun · - qısa olsun · boş = uyğun
    ```

## Step 7 — answer follow-ups in this session

After you deliver the text, Ruslan may reply in this same session. A reply can be a word question (7a), a rating (7b), or both in one message — handle every part. Hours may have passed and GitHub may have newer commits, so before changing any file run `git pull --rebase origin main`.

### 7a — a word or sentence he did not understand

He writes in Azerbaijani, and he may just paste the bare word with no explanation; treat that as "explain this".

1. Answer him in Azerbaijani, in the chat, right away. Explain the word simply: what it means, how it is pronounced, and one short example sentence in English that uses it in a different context. If he asks about a whole sentence, break the sentence into parts and explain the grammar in plain Azerbaijani. Keep it short — he is a learner, not a linguist.
2. Add the word to the **`Yeni sözlər` list of the file you wrote in Step 5** — that same day's text file. Do not create a new section and do not put the word anywhere else in the file. Append it as one more list item at the end of the existing list, starting with `- `, in exactly the same format as the items already there, with no blank line between items:

       - **word** /IPA/ [AZ-TƏLƏFFÜZ] — azərbaycanca tərcümə; qısa qeyd.

   If the word is already in that list, just improve its note instead of adding a duplicate item.
3. Commit and push with exactly these commands:

       git add -A
       git commit -m "Add '<word>' to vocabulary list"
       git push origin HEAD:main

   If the push is rejected, run `git pull --rebase origin main` once and `git push origin HEAD:main` again.
4. Tell him in one short Azerbaijani line that the word was added, naming the file path.

### 7b — a rating

A rating is a short code in the format of the `Qiymət kodu` guide, or the same information in words (for example "asan idi, bilmirdim, çox maraqlı, bir az qısa olsun"). Fields:

- `am` text: `<çətinlik 1–5> <işlədə bilərəm 1–5> <faydalı 1–5> [+|-]`
- `pm` text: `<çətinlik 1–5> <bilirdim b|q|y> <anlama 1–5> <maraq 1–5> [+|-]`
- The last mark is optional: `+` means "make texts longer", `-` means "make them shorter", no mark means the length was fine (stored as `0`).

Which text it is about: by default the file you wrote in Step 5. If he names another text ("dünənki axşam", "səhərki", "2026-09-25 pm"), use `texts/<date>-<slot>.md` for that Baku date and slot; if a `-2` file also exists for it, use the `-2` one unless he says otherwise. Take the slot from that file's name — the fields follow the text's slot, not this session's slot.

If the number of values does not fit the text's slot (for example 4 values for an `am` text), or you cannot understand the rating at all, ask him once, in one short Azerbaijani line, and wait for his answer. A field he leaves out, or that you cannot read, becomes `-`.

Then:

1. Find the text's line in HISTORY.md (same date, same slot, same English title as the file's `#` heading). Take its level `Ln` and word count `Nw` from the last two columns. If the line has no such columns (older texts), use `L2` as the level and count the words with the `awk ... | wc -w` command from Step 5.
2. Put a `## Qiymət` section at the very end of the text file, after `## Suallar`. If the file already has a `## Qiymət` section, replace that whole section. Use exactly these lines (values are examples):

   `am` text:

       ## Qiymət

       - Çətinlik: 2/5
       - İşlədə bilərəm: 4/5
       - Faydalı: 5/5
       - Uzunluq: daha uzun olsun (108 söz)

   `pm` text:

       ## Qiymət

       - Çətinlik: 3/5
       - Mövzunu bilirdim: qismən
       - Anlama: 4/5
       - Maraq: 5/5
       - Uzunluq: uyğun (130 söz)

   `bilirdim` is written `bəli` / `qismən` / `yox`; length is written `daha uzun olsun` / `uyğun` / `daha qısa olsun` with the word count in brackets; a missing field is written `-`.
3. Get the time with `TZ=Asia/Baku date '+%Y-%m-%d %H:%M'`. Then add one line at the end of the `<!-- RATINGS:BEGIN -->` / `<!-- RATINGS:END -->` block in RATINGS.md:

       YYYY-MM-DD | am|pm | index category | Ln | Nw | FIELDS | YYYY-MM-DD HH:MM

   The first three columns are the text's date, slot and `index category` from its HISTORY.md line; `Ln` and `Nw` are from step 1; the last column is the time you just got. FIELDS is:
   - `am` text: `cet=2 isl=4 fay=5 uzn=+`
   - `pm` text: `cet=3 bil=q anl=4 mar=5 uzn=0`

   Use `-` for a missing field and `uzn=0` when there is no length mark. If a line with the same first three columns already exists, replace it instead of adding a second one — a new rating of the same text always overwrites the old one.
4. Commit and push with exactly these commands:

       git add -A
       git commit -m "Rate reading text: <English title>"
       git push origin HEAD:main

   If the push is rejected, run `git pull --rebase origin main` once and `git push origin HEAD:main` again.
5. Confirm in one short Azerbaijani line, repeating what you recorded, for example: `Qeyd etdim: çətinlik 3, qismən bilirdin, anlama 4, maraq 5, uzunluq uyğun (130 söz).`

Keep doing this for every follow-up he sends in this session — several words, one at a time, or several at once, and any number of ratings. Never refuse and never tell him to open a new session. If he asks for something unrelated to the text, just help him with it normally.
~~~~

- [ ] **Step 3: Create `routines/README.md`**

```markdown
# Routine prompt-ları

Bu fayllar claude.ai-dakı cloud routine-lərin prompt-larıdır — mənbə buradır.
Routine işləyəndə prompt-u trigger-dən oxuyur, bu fayldan yox: faylı dəyişəndən sonra
trigger-i də yeniləmək lazımdır (RemoteTrigger `update`).

| Fayl | Routine | Vaxt (Bakı) | Cron (UTC) |
|---|---|---|---|
| `daily.md` | Daily English Reading (AZ) — `trig_017Pt3sNTiukVCgvymhiu1JK` | hər gün 10:00, 19:00 | `0 6,15 * * *` |
| `weekly.md` | Weekly English Progress Review (AZ) | bazar 21:00 | `0 17 * * 0` |
| `monthly.md` | Monthly English Progress Review (AZ) | ayın 1-i 21:30 | `30 17 1 * *` |
```

- [ ] **Step 4: Run the check to verify it passes**

Run: `python3 scripts/check.py routines/daily.md`
Expected: `OK`.

- [ ] **Step 5: Confirm the untouched parts match the live prompt**

Run RemoteTrigger `get` on `trig_017Pt3sNTiukVCgvymhiu1JK`, save `derived_state.prompt` to `$CLAUDE_JOB_DIR/tmp/daily-live.md`, then `diff $CLAUDE_JOB_DIR/tmp/daily-live.md routines/daily.md`.
Expected: differences only in Step 1 (LEVEL.md), Step 2, Step 4, Step 5, Step 6 (rating guide) and Step 7 (7a/7b split); the git section, Step 3 and the 7a word flow are unchanged.

- [ ] **Step 6: Commit and push**

```bash
git add routines/daily.md routines/README.md
git commit -F - <<'EOF'
Add daily routine prompt with level, length and ratings

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01J1dMVideq8JXAMr7R6iTs5
EOF
git push origin HEAD:main
```

---

### Task 3: Weekly routine prompt

**Files:**
- Create: `routines/weekly.md`

**Interfaces:**
- Consumes: RATINGS line format and HISTORY `| Ln | Nw` columns (Task 2); `LEVEL.md` keys (Task 1); commit subjects `Add '<word>' to vocabulary list` (existing).
- Produces: `reviews/<YYYY-Www>.md` with sections `## Xülasə`, `## Qərar`, `## Söz testi` (+ `### Nəticə: ...`, `Səhv sözlər: ...`), `## Həftənin sözləri`; `LEVEL.md` `## Tarixçə` lines `- <date> (<label>): ...`. Monthly (Task 4) reads these.

- [ ] **Step 1: Run the check to verify it fails**

Run: `python3 scripts/check.py routines/weekly.md`
Expected: exit 1, `missing file: routines/weekly.md`.

- [ ] **Step 2: Create `routines/weekly.md`**

~~~~markdown
You are running the weekly progress review of Ruslan's English reading practice. Ruslan is an Azerbaijani speaker learning English. A daily routine sends him two texts a day — slot `am` (PRACTICAL topics) and slot `pm` (KNOWLEDGE topics) — and he rates them. Your job: summarise the week, adjust each slot's level and text length by the fixed rules below, give him a 5-question word quiz, and save everything in the repository. Steps 1–6 are unattended: never ask questions, never stop for confirmation. Ruslan may reply afterwards — Step 7 covers that.

Everything you write for Ruslan is in Azerbaijani with correct orthography (ə, ı, ö, ü, ç, ş, ğ); English words stay English.

## Git in this sandbox — read this first

This sandbox checks the repository out as a **detached HEAD**, and the local `main` branch can be days out of date. Because of that, plain `git push` fails ("You are not currently on a branch") and `git push -u origin HEAD` fails too ("not a full refname"). Use the git commands in this prompt **exactly as written** — do not replace them with `git push`, `git push -u origin HEAD`, `git checkout main`, or any other form.

## Step 1 — sync and read

    git fetch origin main
    git checkout -B main origin/main

Never run `git checkout main` on its own — that switches to a stale local branch. Then run:

    TZ=Asia/Baku date '+%Y-%m-%d %H:%M'
    TZ=Asia/Baku date '+%G-W%V'
    TZ=Asia/Baku python3 -c "import datetime as d; t=d.date.today(); m=t-d.timedelta(days=t.weekday()); print(m, m+d.timedelta(days=6))"
    cat LEVEL.md
    cat RATINGS.md
    cat HISTORY.md
    ls reviews/ 2>/dev/null

The second command gives the week **label** (for example `2026-W40`); the third gives the week's Monday and Sunday. Write down the current values of the `## Cari vəziyyət` section of LEVEL.md — you need them for the decisions and, if Ruslan asks, to undo them.

## Step 2 — collect the week's data

For each slot (`am`, `pm`) separately:

- **Texts of the week:** HISTORY.md lines whose date is between Monday and Sunday inclusive. Count them. The word count of each is its `Nw` column; if a line has no such column, count its file with `awk '/^### /{p=1;next} /^## /{p=0} p' texts/<file> | wc -w`. Compute the average word count.
- **Ratings in the window:** RATINGS.md lines whose last column (the rating time) is later than `last_weekly_review` in LEVEL.md. If `last_weekly_review` is `-`, every line is in the window. The window follows rating time, not text date, so a late rating of last week's text counts now and is never lost.
- **Words he asked about:** run

      git log --since="<Monday> 00:00 +0400" --format='@@ %s' --name-only -- texts/

  Every commit subject of the form `Add '<word>' to vocabulary list` or `Add '<w1>' and '<w2>' to vocabulary list` holds asked words; the file name listed under it (`...-am.md` or `...-pm.md`, possibly with `-2`) gives the slot. Count them per slot and keep the list.

Do all averages with python3, not in your head, and round them to one decimal. A field whose value is `-` is left out of that field's average.

## Step 3 — decide level and length

The default thresholds are below. If the `## Hədd rəqəmləri` section of LEVEL.md has different numbers, LEVEL.md wins.

**Level, slot `am`** (fields `cet`, `isl`):
- fewer than 3 ratings in the window → keep the level (reason: məlumat azdır);
- average `cet` ≤ 2.5 **and** average `isl` ≥ 4.0 → up one level;
- average `cet` ≥ 4.2 **or** average `isl` ≤ 2.0 → down one level;
- otherwise keep.

**Level, slot `pm`** (fields `cet`, `bil`, `anl`):
- For going **up**, use only ratings whose `bil` is not `b` — a topic he already knew is easy to understand and says nothing about his English. Up needs at least 3 such ratings with average `anl` ≥ 4.3 **and** average `cet` ≤ 2.5.
- For going **down**, use all pm ratings in the window. Down needs at least 3 ratings with average `anl` ≤ 2.5 **or** average `cet` ≥ 4.2.
- If both up and down hold, down wins. Otherwise keep.

**Level limits, both slots:**
- at most one step per week; never below L1 or above L6;
- moving from L5 to L6 is allowed only when `<slot>_c1_unlocked: yes`; otherwise keep L5 and say that C1 opens through the monthly review after 90 days at L5;
- when the new level is L5 and the old one was not, set `<slot>_l5_since` to today's Baku date (`YYYY-MM-DD`); when the old level was L5 and the new one is not, set `<slot>_l5_since: -`.

**Length, each slot** (field `uzn` of the slot's ratings in the window): net = number of `uzn=+` minus number of `uzn=-`.
- net ≥ 2 → add 20 to both numbers of `<slot>_words` (for example `100-120` → `120-140`);
- net ≤ −2 → subtract 20 from both;
- otherwise keep.
- The range must stay within 60–300 (lower number ≥ 60, upper number ≤ 300). If a step would cross that, keep the range and say so.
- Length and level are independent: decide them separately.

## Step 4 — prepare the word quiz

Make exactly 5 questions.

Word pool: the `## Yeni sözlər` items of this week's text files (both slots). Choose the words in this order:
1. up to 2 words from the `Səhv sözlər:` line of the previous weekly review — the newest `reviews/*-W*.md` file other than this week's — if that line lists any;
2. the words he asked about this week;
3. the rest from the pool, mixing am and pm words.

Question types — use each type at least once:
- EN → AZ: `**emerge** sözünün mənası nədir?`
- AZ → EN: `"yırtıcı" ingiliscə necədir?`
- fill the gap: an English sentence in a new context with `____` in place of the word, for example `The cicadas ____ from the ground after 17 years.` — no hint letters.

Never write the answers anywhere — not in the file, not in your message — until you grade his reply in Step 7.

## Step 5 — write the review and update LEVEL.md

Write `reviews/<label>.md` (for example `reviews/2026-W40.md`; if it exists, append `-2` before `.md`) with exactly this structure:

    # Həftə <week number> (<Monday> – <Sunday>)

    ## Xülasə

    |                         | Səhər | Axşam |
    |-------------------------|-------|-------|
    | Mətn / qiymətləndirilən | 7 / 6 | 7 / 5 |
    | Çətinlik (ort.)         | 2.3   | 3.4   |
    | İşlədə bilərəm (ort.)   | 4.2   | —     |
    | Faydalı (ort.)          | 3.8   | —     |
    | Anlama (ort.)           | —     | 3.6   |
    | Maraq (ort.)            | —     | 4.4   |
    | Soruşulan söz           | 3     | 9     |
    | Söz sayı (ort.)         | 108   | 115   |
    | Uzunluq siqnalı (+/−)   | 2 / 0 | 0 / 1 |

    ## Qərar

    - Səhər səviyyəsi: L3 → L4. Səbəb: çətinlik 2.3, işlədə bilərəm 4.2.
    - Axşam səviyyəsi: L2 saxlanır. Səbəb: anlama 3.6 (≥ 4.3 lazımdır).
    - Səhər uzunluğu: 100–120 → 120–140. Səbəb: `+` 2, `-` 0.
    - Axşam uzunluğu: 100–120 saxlanır.

    ## Söz testi

    1. <question>
    2. <question>
    3. <question>
    4. <question>
    5. <question>

    ### Nəticə: cavablanmayıb

    ## Həftənin sözləri

    <the words he asked about this week, comma-separated, or —>

The numbers above are only an example; write the real ones. Use `—` for a value with no data. Write dates like `28 sentyabr – 4 oktyabr` with Azerbaijani month names in lower case: yanvar, fevral, mart, aprel, may, iyun, iyul, avqust, sentyabr, oktyabr, noyabr, dekabr.

If there are no ratings at all in the window, add this line right below the table: `Bu həftə qiymət yoxdur — qiymət kodu hər mətnin sonunda var.` Every decision is then "saxlanır — məlumat azdır".

Then update LEVEL.md:
- in `## Cari vəziyyət`: the new `am`, `pm`, `am_words`, `pm_words`, `am_l5_since`, `pm_l5_since` values, and `last_weekly_review:` set to the Baku date and time from Step 1 (`YYYY-MM-DD HH:MM`);
- in `## Tarixçə`: one line at the end, `- <today> (<label>): ` followed by the changes (for example `am L3 → L4; am_words 100-120 → 120-140`) or `dəyişiklik yoxdur`.

Change nothing else in LEVEL.md. Then commit and push with exactly these commands:

    git add -A
    git commit -m "Weekly review: <label>"
    git push origin HEAD:main

If the push is rejected, run `git pull --rebase origin main` once and `git push origin HEAD:main` again. If it still fails, report it in one line at the end of your message.

## Step 6 — deliver

Send the whole review file as your final message. End it with:
- `Testə belə cavab ver: 1 ... 2 ... 3 ... 4 ... 5 ...`
- only if a level or length changed: `Dəyişikliyi bəyənməsən, "geri qaytar" yaz.`

## Step 7 — follow-ups in this session

Before changing any file, run `git pull --rebase origin main`.

**Quiz answers.** When he replies with answers (numbered, in any format):
1. Grade each one: accept small spelling mistakes and any correct synonym or translation; a wrong or missing answer is wrong.
2. In `reviews/<label>.md`, replace the line `### Nəticə: cavablanmayıb` with:

       ### Nəticə: 4/5

       1. <question> — sənin cavabın: <his answer> — düzgün: <correct answer> ✓
       2. <question> — sənin cavabın: <his answer> — düzgün: <correct answer> ✗

       Səhv sözlər: <the English words he got wrong, comma-separated, or ->

   If he answers again later, replace this same block instead of adding a second one.
3. Commit and push with exactly these commands:

       git add -A
       git commit -m "Grade word quiz: <label>"
       git push origin HEAD:main

   If the push is rejected, run `git pull --rebase origin main` once and push again.
4. Reply in Azerbaijani: the score, and for each wrong word a one-line explanation with a short English example sentence.

**"geri qaytar".** When he asks to undo this review's changes:
1. In LEVEL.md `## Cari vəziyyət`, set `am`, `pm`, `am_words`, `pm_words`, `am_l5_since`, `pm_l5_since` back to the values you wrote down in Step 1. Leave `last_weekly_review` as it is.
2. Add one line at the end of `## Tarixçə`: `- <today> (<label>): geri qaytarıldı — am <level> <words>, pm <level> <words>`.
3. Commit and push with exactly these commands:

       git add -A
       git commit -m "Revert level change: <label>"
       git push origin HEAD:main

   If the push is rejected, run `git pull --rebase origin main` once and push again.
4. Confirm in one Azerbaijani line.

Anything else: answer him normally, in Azerbaijani.
~~~~

- [ ] **Step 3: Run the check to verify it passes**

Run: `python3 scripts/check.py routines/weekly.md`
Expected: `OK`.

- [ ] **Step 4: Commit and push**

```bash
git add routines/weekly.md
git commit -F - <<'EOF'
Add weekly progress review routine prompt

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01J1dMVideq8JXAMr7R6iTs5
EOF
git push origin HEAD:main
```

---

### Task 4: Monthly routine prompt

**Files:**
- Create: `routines/monthly.md`

**Interfaces:**
- Consumes: weekly review files and Tarixçə lines (Task 3); RATINGS format (Task 2); `LEVEL.md` `## Maraq` line format `- Sevimli: <slot> <index> <category>; ...` read by the daily Step 2 (Task 2).
- Produces: `reviews/<YYYY-MM>.md`; rewritten `## Maraq` lines; appended `TOPICS.md` categories; C1 fields.

- [ ] **Step 1: Run the check to verify it fails**

Run: `python3 scripts/check.py routines/monthly.md`
Expected: exit 1, `missing file: routines/monthly.md`.

- [ ] **Step 2: Create `routines/monthly.md`**

~~~~markdown
You are running the monthly progress review of Ruslan's English reading practice. Ruslan is an Azerbaijani speaker learning English. A daily routine sends him two texts a day — slot `am` (PRACTICAL topics) and slot `pm` (KNOWLEDGE topics) — he rates them, and a weekly review adjusts level and length. Your job: show the month's trend, update the interest lists that steer topic choice, add new related categories for his favourite topics, and open C1 when he has stayed at L5 long enough. Steps 1–6 are unattended: never ask questions, never stop for confirmation. Ruslan may reply afterwards — Step 7 covers that.

Everything you write for Ruslan is in Azerbaijani with correct orthography (ə, ı, ö, ü, ç, ş, ğ); English words stay English.

## Git in this sandbox — read this first

This sandbox checks the repository out as a **detached HEAD**, and the local `main` branch can be days out of date. Because of that, plain `git push` fails ("You are not currently on a branch") and `git push -u origin HEAD` fails too ("not a full refname"). Use the git commands in this prompt **exactly as written** — do not replace them with `git push`, `git push -u origin HEAD`, `git checkout main`, or any other form.

## Step 1 — sync and read

    git fetch origin main
    git checkout -B main origin/main

Never run `git checkout main` on its own. Then run:

    TZ=Asia/Baku date '+%Y-%m-%d %H:%M'
    TZ=Asia/Baku python3 -c "import datetime as d; f=d.date.today().replace(day=1); l=f-d.timedelta(days=1); print(l.strftime('%Y-%m'), l.replace(day=1), l)"
    cat LEVEL.md
    cat RATINGS.md
    cat HISTORY.md
    cat TOPICS.md
    ls reviews/ 2>/dev/null

The python line prints the month **label** (the previous calendar month, for example `2026-09`) and its first and last day. Write down the current `## Cari vəziyyət` and `## Maraq` values of LEVEL.md — you need them for the decisions and, if Ruslan asks, to undo them.

Then read every weekly review `reviews/*-W*.md` whose Sunday falls inside the month (its `#` title line shows the dates).

## Step 2 — trend

Build a table with one row per weekly review of the month:

    | Həftə | Səhər pillə | Axşam pillə | Səhər çət / işl / fay | Axşam çət / anl / mar | Söz sayı (səhər / axşam) | Soruşulan söz | Söz testi |

Take the values from each weekly review's `Xülasə`, `Qərar` (the level after the decision) and `### Nəticə` line. If there are no weekly reviews for the month, write `Bu ay həftəlik review yoxdur.` instead of the table.

Then the month totals, per slot where it applies:
- texts: HISTORY.md lines dated inside the month;
- ratings: RATINGS.md lines whose rating time (last column) is inside the month;
- asked words: count the words in the `Add '...' to vocabulary list` subjects of

      git log --since="<first day> 00:00 +0400" --until="<last day> 23:59 +0400" --format='%s' -- texts/

- average word count: the `Nw` column of the month's HISTORY.md lines; for a line without it, count the file with `awk '/^### /{p=1;next} /^## /{p=0} p' texts/<file> | wc -w`.

Do all arithmetic with python3, not in your head.

## Step 3 — interest lists

Use the whole of RATINGS.md — all months, not only this one. For every category with at least 2 ratings whose interest field is a number, compute that field's average with python3: `mar` for `pm` lines, `fay` for `am` lines; ignore `-`. A category is identified by slot + `index category`, for example `am 5 hotels and accommodation`.

- average ≥ 4.5 → **Sevimli**
- average ≤ 2.0 → **Seyrək**
- anything else, or fewer than 2 ratings → neither list

Rewrite the two lines in the `## Maraq` section of LEVEL.md from scratch, entries separated by `; `, `-` when a list is empty:

    - Sevimli: am 5 hotels and accommodation; pm 1 space and planets
    - Seyrək: -

The daily routine picks a Sevimli category again after 10 days and skips a Seyrək category for 45 days.

## Step 4 — new categories for new favourites

A **new favourite** is a Sevimli entry that was not in the Sevimli line you wrote down in Step 1. For each new favourite — at most 3 per month; if there are more, take those with the highest average:
- invent ONE new category related to it for the same list in TOPICS.md (PRACTICAL for `am`, KNOWLEDGE for `pm`) — broad enough to hold many narrow subjects, and not a copy or near-copy of any category already in that list;
- append it at the end of that list with the next free index. Never renumber, reorder or edit existing lines.

Example: new favourite `pm 1 space and planets` → new KNOWLEDGE category `rockets and space missions`.

## Step 5 — C1 check

For each slot: if its level is `L5`, its `<slot>_l5_since` is a date, its `<slot>_c1_unlocked` is `no`, and at least 90 days have passed since that date (compute with python3), then set the level to `L6`, `<slot>_c1_unlocked: yes` and `<slot>_l5_since: -`. From then on the weekly review moves that slot between L5 and L6 with its normal rules.

## Step 6 — write, save, deliver

Write `reviews/<label>.md` (if it exists, append `-2` before `.md`) with exactly this structure:

    # Ay: <month name> <year>

    ## Trend

    <the table from Step 2, or the no-weekly-review line>

    ## Ay üzrə

    - Mətn: səhər <n>, axşam <n>
    - Qiymət: səhər <n>, axşam <n>
    - Soruşulan söz: <n>
    - Orta söz sayı: səhər <n>, axşam <n>

    ## Maraq

    - Sevimli: <list or ->
    - Seyrək: <list or ->
    - Dəyişiklik: <what entered or left the lists, or yoxdur>

    ## Yeni kateqoriyalar

    - <PRACTICAL|KNOWLEDGE> <index> <category> — <the favourite it came from>

    ## C1

    - Səhər: <L5-də N gündür | C1 açıldı | L5-də deyil>
    - Axşam: <L5-də N gündür | C1 açıldı | L5-də deyil>

Write `yoxdur` under `## Yeni kateqoriyalar` if you added none. The month name is Azerbaijani, lower case (yanvar, fevral, mart, aprel, may, iyun, iyul, avqust, sentyabr, oktyabr, noyabr, dekabr).

Then update LEVEL.md: the `## Maraq` lines (Step 3), the C1 values (Step 5), `last_monthly_review:` set to the Baku date and time from Step 1, and one line at the end of `## Tarixçə`: `- <today> (<label> aylıq): ` followed by the changes or `dəyişiklik yoxdur`. Change nothing else. Then commit and push with exactly these commands:

    git add -A
    git commit -m "Monthly review: <label>"
    git push origin HEAD:main

If the push is rejected, run `git pull --rebase origin main` once and `git push origin HEAD:main` again. If it still fails, report it in one line at the end of your message.

Send the whole review file as your final message.

## Step 7 — follow-ups in this session

Before changing any file, run `git pull --rebase origin main`.

If he asks to undo something from this review — a new category, an interest list, the C1 step — restore it from the values you wrote down in Step 1 (for TOPICS.md, remove only the line you added), add one line at the end of `## Tarixçə`: `- <today> (<label> aylıq): geri qaytarıldı — <what>`, then commit and push with exactly these commands:

    git add -A
    git commit -m "Revert monthly change: <label>"
    git push origin HEAD:main

If the push is rejected, run `git pull --rebase origin main` once and push again. Confirm in one Azerbaijani line.

Anything else: answer him normally, in Azerbaijani.
~~~~

- [ ] **Step 3: Run the full check to verify everything passes**

Run: `python3 scripts/check.py`
Expected: `OK`.

- [ ] **Step 4: Commit and push**

```bash
git add routines/monthly.md
git commit -F - <<'EOF'
Add monthly progress review routine prompt

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01J1dMVideq8JXAMr7R6iTs5
EOF
git push origin HEAD:main
```

---

### Task 5: Deploy the daily prompt

**Files:** none in the repo (remote trigger `trig_017Pt3sNTiukVCgvymhiu1JK`).

**Interfaces:**
- Consumes: `routines/daily.md` (Task 2).

- [ ] **Step 1: Generate a fresh event UUID**

Run: `python3 -c "import uuid; print(uuid.uuid4())"`

- [ ] **Step 2: Update the trigger**

RemoteTrigger `update`, `trigger_id: trig_017Pt3sNTiukVCgvymhiu1JK`, body (content = the full text of `routines/daily.md`, byte for byte):

```json
{
  "job_config": {
    "ccr": {
      "environment_id": "env_01G4m8Pj3jLp3gg2FmJUafTA",
      "session_context": {
        "allowed_tools": ["Bash", "Read", "Write", "Edit", "Glob", "Grep"],
        "model": "claude-sonnet-5",
        "sources": [{"git_repository": {"url": "https://github.com/wdaz/english-reading"}}],
        "outcomes": [{"git_repository": {"git_info": {"branches": ["claude/gracious-lovelace"], "repo": "wdaz/english-reading"}}}]
      },
      "events": [{
        "data": {
          "message": {"content": "<full text of routines/daily.md>", "role": "user"},
          "parent_tool_use_id": null,
          "session_id": "",
          "type": "user",
          "uuid": "<uuid from Step 1>"
        }
      }]
    }
  }
}
```

Expected: HTTP 200; cron still `0 6,15 * * *`; `next_run_at` = `2026-09-28T06:10…Z`.

- [ ] **Step 3: Verify the live prompt equals the file**

RemoteTrigger `get`; save `derived_state.prompt` to `$CLAUDE_JOB_DIR/tmp/daily-live.md`; run `diff $CLAUDE_JOB_DIR/tmp/daily-live.md routines/daily.md`.
Expected: no output (a trailing-newline difference only is acceptable).

---

### Task 6: Create the weekly routine and run it once for W39

**Files:**
- Modify: `routines/README.md` (weekly trigger id)

**Interfaces:**
- Consumes: `routines/weekly.md` (Task 3), deployed data files (Task 1).
- Produces: trigger id `trig_…` for the weekly routine; `reviews/2026-W39.md`.

- [ ] **Step 1: Create the trigger**

Generate a UUID as in Task 5 Step 1. RemoteTrigger `create`, body:

```json
{
  "name": "Weekly English Progress Review (AZ)",
  "cron_expression": "0 17 * * 0",
  "enabled": true,
  "job_config": {
    "ccr": {
      "environment_id": "env_01G4m8Pj3jLp3gg2FmJUafTA",
      "session_context": {
        "allowed_tools": ["Bash", "Read", "Write", "Edit", "Glob", "Grep"],
        "model": "claude-sonnet-5",
        "sources": [{"git_repository": {"url": "https://github.com/wdaz/english-reading"}}]
      },
      "events": [{
        "data": {
          "message": {"content": "<full text of routines/weekly.md>", "role": "user"},
          "parent_tool_use_id": null,
          "session_id": "",
          "type": "user",
          "uuid": "<new uuid>"
        }
      }]
    }
  }
}
```

Expected: HTTP 200; `next_run_at` = `2026-10-04T17:00…Z`. Then `get` it: if `notifications.channel.push` is not `true`, `update` with `{"notifications": {"channel": {"push": true, "email": false, "slack": false}}}`.

- [ ] **Step 2: Run it now**

RemoteTrigger `run` with the new trigger id. Wait for the run to finish (poll `list_runs` every few minutes), then `get_run_log` for its session.
Expected in the log: no failed `git push`; final message is the review with 5 quiz questions and no answers.

- [ ] **Step 3: Verify the output in the repo**

```bash
git fetch -q origin && git reset -q --hard origin/main
cat reviews/2026-W39.md
grep -n "last_weekly_review\|^- am: \|^- pm: \|W39" LEVEL.md
python3 scripts/check.py data
```

Expected:
- `reviews/2026-W39.md` starts with `# Həftə 39 (21 sentyabr – 27 sentyabr)`, has the Xülasə table with `Mətn / qiymətləndirilən` `7 / 0` for both slots (plus any `-2` texts), the line `Bu həftə qiymət yoxdur — qiymət kodu hər mətnin sonunda var.`, word-count averages ≈ 108 (am) / ≈ 116 (pm), 5 numbered questions, `### Nəticə: cavablanmayıb`, and no answer anywhere;
- LEVEL.md: `am: L3`, `pm: L2` unchanged, `last_weekly_review: 2026-09-27 HH:MM`, Tarixçə line `- 2026-09-27 (2026-W39): dəyişiklik yoxdur`;
- `check.py data` prints `OK`.

- [ ] **Step 4: Record the trigger id**

Put the new id into the `weekly.md` row of `routines/README.md` (`Weekly English Progress Review (AZ) — trig_…`), then:

```bash
git add routines/README.md
git commit -F - <<'EOF'
Record weekly routine trigger id

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01J1dMVideq8JXAMr7R6iTs5
EOF
git push origin HEAD:main
```

---

### Task 7: Create the monthly routine

**Files:**
- Modify: `routines/README.md` (monthly trigger id)

- [ ] **Step 1: Create the trigger**

Same body as Task 6 Step 1 with `"name": "Monthly English Progress Review (AZ)"`, `"cron_expression": "30 17 1 * *"`, the full text of `routines/monthly.md` as content and a new UUID. Apply the same push-notification check.
Expected: HTTP 200; `next_run_at` = `2026-10-01T17:30…Z`. Do not run it manually — on 27 September "previous month" is August, which has no data.

- [ ] **Step 2: Record the trigger id and commit**

Put the id into the `monthly.md` row of `routines/README.md`, then:

```bash
git add routines/README.md
git commit -F - <<'EOF'
Record monthly routine trigger id

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01J1dMVideq8JXAMr7R6iTs5
EOF
git push origin HEAD:main
```

---

### Task 8: Live verification with Ruslan

No files. These checks need real runs and Ruslan's replies; do them as the events happen.

- [ ] **Step 1: Morning run 2026-09-28 10:10 Baku**

After it finishes: `git fetch -q origin && git reset -q --hard origin/main && tail -3 HISTORY.md && python3 scripts/check.py data`.
Expected: the new line ends `| L3 | <n>w` with 90 ≤ n ≤ 132; `OK`. The run log's final message ends with the `am` `## Qiymət kodu` block.

- [ ] **Step 2: First rating**

Ruslan replies in that session with a code (for example `2 4 5 +`). Then:
`tail -8 texts/2026-09-28-am.md; sed -n '/RATINGS:BEGIN/,/RATINGS:END/p' RATINGS.md; python3 scripts/check.py data`.
Expected: `## Qiymət` block at the end of the file; one RATINGS line `2026-09-28 | am | … | L3 | <n>w | cet=2 isl=4 fay=5 uzn=+ | 2026-09-28 HH:MM`; `OK`.

- [ ] **Step 3: W39 quiz answer**

Ruslan answers the W39 quiz in the weekly session. Then `sed -n '/## Söz testi/,/## Həftənin sözləri/p' reviews/2026-W39.md`.
Expected: `### Nəticə: n/5`, one line per question with ✓/✗, and a `Səhv sözlər:` line.

- [ ] **Step 4: First monthly run 2026-10-01 21:30 Baku**

Expected: `reviews/2026-09.md` with the W39 row in the trend table, `Sevimli: -` / `Seyrək: -` (fewer than 2 ratings per category), `## Yeni kateqoriyalar` → `yoxdur`, and a Tarixçə line `(2026-09 aylıq)`.
