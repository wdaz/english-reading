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
