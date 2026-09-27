# Progress: qiymət, həftəlik və aylıq review — dizayn

Tarix: 2026-09-27 · Status: təsdiqlənib (2026-09-27)

## Məqsəd

Hər mətndən sonra qısa qiymət vermək, həftəlik və aylıq review ilə mətnlərin
çətinliyini avtomatik tənzimləmək: asan gəlirsə çətinləşsin və mövzu dərinləşsin,
çətin gəlirsə asanlaşsın. Mətnin uzunluğu (söz sayı) ölçülür və səviyyədən asılı
olmayaraq ayrıca uzadıla və ya qısaldıla bilir. Progress zamanla görünsün.

Uğur meyarı:

- Qiymət vermək 10 saniyədən az çəkir (bir sətirlik kod).
- Bir ay sonra `reviews/` qovluğunda səviyyə dəyişməsi və trend aydın görünür.
- Səviyyə qərarları avtomatikdir, amma hər biri səbəbi ilə yazılır və geri qaytarıla bilir.

## Qərarlar (istifadəçi ilə razılaşdırılıb)

| Mövzu | Qərar |
|---|---|
| Qiymət harada verilir | Mətnin gəldiyi routine sessiyasında, cavab kimi |
| Səhər qiyməti | `çətinlik · işlədə bilərəm · faydalı` — nümunə `2 4 5` |
| Axşam qiyməti | `çətinlik · bilirdim (b/q/y) · anlama · maraq` — nümunə `3 q 4 5` |
| Oxuma vaxtı | Yoxdur |
| Səviyyə dəyişməsi | Avtomatik tətbiq olunur, sessiyada "geri qaytar" ilə ləğv olunur |
| Pilləkən | L1 A2 → L2 A2+ → L3 B1 → L4 B1+ → L5 B2 → L6 C1 |
| Başlanğıc | Səhər L3, axşam L2 |
| C1 | Slot L5-də fasiləsiz 90 gün qalandan sonra L6-ya keçir |
| Həftəlik söz testi | Var — 5 sual, səhv sözlər növbəti həftəyə keçir |
| Uzunluq | Pillədən asılı deyil. Hər slotun öz hədəf söz sayı (başlanğıc 100–120); həqiqi say hər mətndə ölçülür. Dəyişmə yalnız qiymətdəki istəyə bağlı `+`/`-` ilə → həftəlik review ±20 söz (birbaşa əmr yoxdur) |
| Arxitektura | Repo faylları + 3 routine (gündəlik, həftəlik, aylıq) |

## Arxitektura

Routine-lər bir-biri ilə birbaşa danışmır — yalnız repo faylları vasitəsilə:

```
            oxuyur                     yazır
gündəlik ─────────► LEVEL.md ◄──────────────── həftəlik, aylıq
   │                                               ▲
   │ yazır (qiymət)                                │ oxuyur
   └──────────────► RATINGS.md ────────────────────┘
```

### Fayllar

| Fayl | Status | Kim yazır | Məzmun |
|---|---|---|---|
| `LEVEL.md` | yeni | həftəlik, aylıq (istifadəçi də əl ilə) | cari pillə, pilləkən, hədd rəqəmləri, maraq siyahıları, tarixçə |
| `RATINGS.md` | yeni | gündəlik (Step 7) | hər qiymət bir sətir |
| `reviews/YYYY-Www.md` | yeni | həftəlik | həftənin statistikası, qərar, söz testi |
| `reviews/YYYY-MM.md` | yeni | aylıq | trend, maraq, genişlənmə, C1 yoxlaması |
| `HISTORY.md` | dəyişir | gündəlik | sətrin sonuna `\| L<n> \| <n>w` — pillə və həqiqi söz sayı |
| `texts/*.md` | dəyişir | gündəlik (Step 7) | faylın sonuna `## Qiymət` bölməsi |
| `TOPICS.md` | dəyişir | aylıq | siyahıların sonuna yeni kateqoriyalar |
| `README.md` | dəyişir | bir dəfə, əl ilə | qiymət bələdçisi, şkala anker-ləri, review izahı |

## Qiymət formatı

### Səhər (PRACTICAL)

Kod: `<çətinlik> <işlədə bilərəm> <faydalı>` — hər biri 1–5.

| Sahə | 1 | 3 | 5 |
|---|---|---|---|
| Çətinlik | hər şey tanış idi | bir neçə cümlə çətin idi | lüğətsiz alınmadı |
| İşlədə bilərəm | bu situasiyada özüm danışa bilməzdim | yarımçıq danışardım | rahat danışardım |
| Faydalı | belə situasiya həyatımda olmur | bəzən olur | tez-tez rast gəlirəm |

### Axşam (KNOWLEDGE)

Kod: `<çətinlik> <bilirdim> <anlama> <maraq>` — `bilirdim` ∈ {b, q, y}
(bəli / qismən / yox), qalanları 1–5.

| Sahə | 1 | 3 | 5 |
|---|---|---|---|
| Çətinlik | hər şey tanış idi | bir neçə cümlə çətin idi | lüğətsiz alınmadı |
| Anlama (tərcüməsiz) | ≈ 20% | ≈ 60% | ≈ 100% |
| Maraq | darıxdırıcı | normal | belə mətnlərdən daha çox istəyirəm |

Anlama addımları: 1 ≈ 20% · 2 ≈ 40% · 3 ≈ 60% · 4 ≈ 80% · 5 ≈ 100%.

### Uzunluq (hər iki slot, istəyə bağlı)

Kodun sonuna bir işarə əlavə etmək olar:

| İşarə | Məna | Nümunə |
|---|---|---|
| `+` | daha uzun olsun | `2 4 5 +` |
| `-` | daha qısa olsun | `3 q 4 5 -` |
| (yoxdur) | uzunluq uyğundur | `3 q 4 5` |

### Qəbul qaydaları

- Təbii dil də qəbul olunur ("asan idi, bilmirdim, çox maraqlı") — routine koda çevirir.
- Çatmayan sahə `-` kimi yazılır; heç bir sahə anlaşılmırsa bir dəfə soruşur.
- Qiymət söz sualı ilə eyni mesajda ola bilər — hər ikisi işlənir.
- Başqa mətni qiymətləndirmək: `dünənki axşam: 2 b 5 3` və ya `2026-09-25 pm: ...`.
- Eyni mətn yenidən qiymətləndirilirsə köhnə qiymət **əvəz olunur** (dublikat yox).
- Kodun sahə sayı mətnin slotuna uyğun gəlmirsə (səhər mətninə 4 sahə), bir dəfə soruşur.

### Saxlanma

Mətn faylının sonuna (əvəz edilə bilən blok):

```markdown
## Qiymət

- Çətinlik: 3/5
- Mövzunu bilirdim: qismən
- Anlama: 4/5
- Maraq: 5/5
- Uzunluq: uyğun (112 söz)
```

Səhər variantı: `Çətinlik`, `İşlədə bilərəm`, `Faydalı`, `Uzunluq`.
`Uzunluq` dəyərləri: `uyğun` / `daha uzun olsun` / `daha qısa olsun`, mötərizədə həqiqi söz sayı.

`RATINGS.md` — `<!-- RATINGS:BEGIN -->` / `<!-- RATINGS:END -->` arasında,
açar=dəyər formatında (iki sxem bir faylda qarışmasın deyə):

```
2026-09-28 | am | 5 hotels and accommodation | L3 | 108w | cet=2 isl=4 fay=5 uzn=+ | 2026-09-28 10:42
2026-09-27 | pm | 1 space and planets | L2 | 130w | cet=3 bil=q anl=4 mar=5 uzn=0 | 2026-09-27 21:10
```

Sütunlar: mətn tarixi · slot · kateqoriya · mətnin pilləsi · həqiqi söz sayı · qiymət · qiymət vaxtı (Bakı).
`uzn` ∈ {`+`, `0`, `-`}. Pillə və söz sayı `HISTORY.md` sətrindən götürülür; yoxdursa
pillə `L2`, söz sayı isə mətn faylından sayılır.

## Səviyyə pilləkəni

Qrammatika hər iki slot üçün eynidir; məzmun sütunu slota görə fərqlənir.

| Pillə | CEFR | Yeni söz | Qrammatika | Səhər məzmunu | Axşam məzmunu |
|---|---|---|---|---|---|
| L1 | A2 | 4–5 | present/past simple, can, going to | sadə xahiş | bir fakt və ya hadisə |
| L2 | A2+ | 5–6 | + present perfect, comparatives, because/so | + problem, şikayət | + səbəb |
| L3 | B1 | 6–7 | + passive, first conditional, relative clauses | + izah etmək, danışıq | + nəticə, müqayisə |
| L4 | B1+ | 7–8 | + second conditional, reported speech, phrasal verbs | + rəsmi dil, telefon, e-mail | + fərqli baxışlar |
| L5 | B2 | 8 | mixed tenses, idiomlar, bağlayıcılar | + nəzakət, yumşaltma | + nüans, mübahisəli tərəf |
| L6 | C1 | 8–10 | inversion, cleft sentences, mixed conditionals | + inandırma, diplomatik dil | + abstrakt arqument, gizli məna |

Pilləkən `LEVEL.md`-də saxlanır — gündəlik routine mətni yazarkən öz slotunun
sətrinə baxır. Bütün pillələrdə 2 sual qalır; yuxarı pillələrdə suallar "niyə /
nə olardı" tipinə keçir. Pilləkəndə cümlə sayı yoxdur — uzunluğu ayrıca hədəf
söz sayı idarə edir; cümlə sayı ondan və pillənin cümlə mürəkkəbliyindən çıxır.

## Uzunluq

- **Hədəf:** `LEVEL.md`-də hər slot üçün söz aralığı — `am_words: 100-120`,
  `pm_words: 100-120` (indiki mətnlərin ortası: səhər 107, axşam 114).
- **Ölçmə:** gündəlik routine mətni yazandan sonra passage-ın sözlərini sayır
  (`### ` alt başlığı ilə ilk `## ` arasındakı hissə, `wc -w`). Aralıqdan ±10%-dən
  çox kənardırsa mətni düzəldir (ən çox 2 cəhd), sonra həqiqi sayı `HISTORY.md`-yə
  `| <n>w` kimi yazır.
- **Addım:** 20 söz; hüdud 60–300. Aralığın eni həmişə 20.
- **Pillədən asılı deyil:** pillə dəyişəndə uzunluq dəyişmir, uzunluq dəyişəndə pillə dəyişmir.

### Uzunluğun dəyişməsi

Yeganə yol — həftəlik review, qiymətlərdəki `+`/`-` işarələrinə görə (hər slot ayrıca):
pəncərədəki qiymətlərdə `+` sayı − `-` sayı ≥ 2 → +20 söz; ≤ −2 → −20 söz; qalan → saxla.
Birbaşa əmr (`uzat` / `qısalt`) yoxdur. İstifadəçi istəsə `LEVEL.md`-də `am_words` /
`pm_words`-u əl ilə dəyişə bilər.

## Gündəlik routine dəyişiklikləri

Mövcud routine (`trig_017Pt3sNTiukVCgvymhiu1JK`) yenilənir; git qaydaları dəyişmir.

1. **Step 1** — əlavə olaraq `cat LEVEL.md`.
2. **Step 2 (kateqoriya)** — maraq siyahılarını nəzərə alır:
   1. `Sevimli` kateqoriya son istifadədən ≥ 10 gün keçibsə — üstünlük onundur
     (bir neçəsi varsa ən köhnəsi).
   2. Yoxsa adi LRU; `Seyrək` kateqoriya son istifadədən < 45 gün keçibsə atlanır.
   3. 7 günlük təkrarsızlıq qaydası qalır.
3. **Step 4 (mətn)** — sabit "A2–B1, 5–6 cümlə" qaydası əvəzinə slotun pilləsinin
   sətri (yeni söz sayı, qrammatika, məzmun) və slotun hədəf söz aralığı.
   Yazandan sonra söz sayını ölçür, lazım olsa düzəldir (bax: Uzunluq).
4. **Step 5** — `HISTORY.md` sətrinin sonuna `| L<n> | <n>w`.
5. **Step 6** — mesajın sonuna (fayla yox) `## Qiymət kodu` başlığı və kod bloku
   şəklində format + nümunə. Nümunə rəqəmləri sabitdir (həqiqi qiymət deyil).

   Səhər:

   ~~~
   Qiymət: <çətinlik> <işlədə bilərəm> <faydalı> [uzunluq]
   Nümunə: 2 4 5 +

   çətinlik, işlədə bilərəm, faydalı: 1–5
   uzunluq: + uzun olsun · - qısa olsun · boş = uyğun
   ~~~

   Axşam:

   ~~~
   Qiymət: <çətinlik> <bilirdim> <anlama> <maraq> [uzunluq]
   Nümunə: 3 q 4 5 -

   çətinlik, anlama, maraq: 1–5
   bilirdim: b bəli · q qismən · y yox
   uzunluq: + uzun olsun · - qısa olsun · boş = uyğun
   ~~~

6. **Step 7** — söz axınına əlavə olaraq qiymət axını: fayla `## Qiymət`,
   `RATINGS.md`-yə sətir (upsert), commit `Rate reading text: <title>`, push,
   təsdiq mesajı.

## Həftəlik routine

- **Vaxt:** bazar 21:00 Bakı — cron `0 17 * * 0`.
- **Pəncərə:** qiymət vaxtı `LEVEL.md`-dəki `last_weekly_review`-dan sonra olan
  sətirlər (gecikmiş qiymətlər növbəti həftəyə düşür, itmir).
- **Etiket:** `TZ=Asia/Baku date +%G-W%V` (ISO həftə).
- **Mətn sayı** və söz testi üçün mətnlər: `HISTORY.md`-də tarixi həmin ISO həftəyə
  düşən sətirlər. Ortalamalar isə yuxarıdakı qiymət pəncərəsindən hesablanır.

### Səviyyə qaydaları (hər slot ayrıca)

| Şərt | Səhər | Axşam |
|---|---|---|
| Məlumat az | < 3 qiymət → saxla | < 3 qiymət → saxla |
| +1 | ort. çət ≤ 2.5 **və** ort. işl ≥ 4.0 | ort. anl ≥ 4.3 **və** ort. çət ≤ 2.5 |
| −1 | ort. çət ≥ 4.2 **və ya** ort. işl ≤ 2.0 | ort. anl ≤ 2.5 **və ya** ort. çət ≥ 4.2 |
| Qalan | saxla | saxla |

- Axşam: `bil=b` olan qiymətlər **+1** qərarında sayılmır (3 qiymət minimumu da
  filtrdən sonra yoxlanır); **−1** qərarında hamısı sayılır.
- Həftədə ən çox ±1; hüdud L1–L6.
- L5 → L6 yalnız slot üçün `c1_unlocked: yes` olanda (aylıq routine açır).
- Slot L5-ə çatanda `l5_since` = həmin tarix; L5-dən enəndə `l5_since` silinir.
- Bütün hədd rəqəmləri `LEVEL.md`-də — routine onları oradan oxuyur.
- Uzunluq qərarı səviyyə qərarından ayrı verilir (bax: Uzunluq → həftəlik qayda).

### Söz testi

- 5 sual. Sözlər həftənin mətnlərinin `## Yeni sözlər` siyahılarından:
  1. əvvəlki review-un `Səhv sözlər` siyahısından ən çox 2;
  2. sessiyada soruşulan sözlər (`git log --grep="to vocabulary list"`);
  3. qalanı digər sözlərdən.
- Tiplər qarışıq: EN → AZ məna, AZ → EN söz, cümlədə boşluq doldurma.
- Suallar fayla və mesaja yazılır; **cavablar yoxlanana qədər yazılmır**.
- İstifadəçi review sessiyasında cavab verir (`1 ... 2 ...`). Routine yoxlayır,
  faylda `### Nəticə: 4/5`, düzgün cavablar və `Səhv sözlər: x, y` yazır, commit
  `Grade word quiz: <label>`, push.
- Cavab verilməsə nəticə "cavablanmayıb" qalır; səhv sözlər siyahısı boş qalır.

### Çıxış

`reviews/YYYY-Www.md`:

```markdown
# Həftə 40 (28 sentyabr – 4 oktyabr)

## Xülasə

|                        | Səhər | Axşam |
|------------------------|-------|-------|
| Mətn / qiymətləndirilən | 7 / 6 | 7 / 5 |
| Çətinlik (ort.)        | 2.3   | 3.4   |
| İşlədə bilərəm (ort.)  | 4.2   | —     |
| Faydalı (ort.)         | 3.8   | —     |
| Anlama (ort.)          | —     | 3.6   |
| Maraq (ort.)           | —     | 4.4   |
| Soruşulan söz          | 3     | 9     |
| Söz sayı (ort.)        | 108   | 115   |
| Uzunluq siqnalı (+/−)  | 2 / 0 | 0 / 1 |

## Qərar

- Səhər: L3 → L4. Səbəb: çətinlik 2.3, işlədə bilərəm 4.2.
- Axşam: L2 saxlanır. Səbəb: anlama 3.6 (≥ 4.3 lazımdır).
- Səhər uzunluğu: 100–120 → 120–140. Səbəb: `+` 2, `-` 0.
- Axşam uzunluğu: 100–120 saxlanır.

## Söz testi

1. ...

## Həftənin sözləri

cicada, shiny, through, ...
```

Sonra: `LEVEL.md` yenilənir (pillə, `l5_since`, söz aralığı, `last_weekly_review`, Tarixçə
sətri), commit `Weekly review: <label>`, push, xülasə + test mesajı.

### "Geri qaytar"

Review sessiyasında istifadəçi "geri qaytar" yazsa: `LEVEL.md`-nin `Cari vəziyyət`
bölməsində pillə, `l5_since` və söz aralığı dəyərləri review-dan əvvəlkinə qayıdır
(`last_weekly_review` dəyişmir), Tarixçəyə `geri qaytarıldı` sətri, commit
`Revert level change: <label>`, push.

## Aylıq routine

- **Vaxt:** ayın 1-i 21:30 Bakı — cron `30 17 1 * *` (həftəlik ilə üst-üstə düşməsin).
- **Pəncərə:** əvvəlki təqvim ayı.

### Məzmun

1. **Trend** — həftə-həftə: ortalamalar, söz testi nəticəsi, soruşulan söz sayı,
   orta mətn uzunluğu, pillə və uzunluq dəyişmələri (`reviews/*W*.md` + `RATINGS.md`).
2. **Maraq** — kateqoriya üzrə **bütün tarixçə** boyu ortalama (axşam `mar`, səhər
   `fay`), ən azı 2 qiymət:
   - ≥ 4.5 → `Sevimli`; ≤ 2.0 → `Seyrək`; aradakı → siyahıdan çıxır.
3. **Genişlənmə** — yeni `Sevimli` olan hər kateqoriya üçün `TOPICS.md`-nin həmin
   siyahısının sonuna 1 əlaqəli kateqoriya (ayda ən çox 3). Sona yazıldığı üçün
   mövcud indekslər dəyişmir.
4. **C1 yoxlaması** — slot L5-dədirsə və `l5_since`-dən ≥ 90 gün keçibsə:
   pillə L6, `c1_unlocked: yes`. Bundan sonra L5 ↔ L6 adi həftəlik qaydalarla.
5. **Çıxış** — `reviews/YYYY-MM.md`, `LEVEL.md` (maraq, C1, `last_monthly_review`,
   Tarixçə), commit `Monthly review: <YYYY-MM>`, push, xülasə mesajı.

## `LEVEL.md` strukturu

```markdown
# Səviyyə

Routine-lər bu faylı oxuyur və yeniləyir. Rəqəmləri əl ilə dəyişmək olar.

## Cari vəziyyət

- am: L3
- pm: L2
- am_words: 100-120
- pm_words: 100-120
- am_l5_since: -
- pm_l5_since: -
- am_c1_unlocked: no
- pm_c1_unlocked: no
- last_weekly_review: -    ("-" = bütün qiymətlər pəncərəyə düşür)
- last_monthly_review: -

## Pilləkən

<yuxarıdakı "Səviyyə pilləkəni" cədvəli, olduğu kimi>

## Hədd rəqəmləri

- min_ratings: 3
- am_up: cet <= 2.5 and isl >= 4.0
- am_down: cet >= 4.2 or isl <= 2.0
- pm_up: anl >= 4.3 and cet <= 2.5   (bil=b sayılmır)
- pm_down: anl <= 2.5 or cet >= 4.2
- c1_after_days: 90
- favorite: avg >= 4.5, min 2 ratings, repeat after 10 days
- rare: avg <= 2.0, min 2 ratings, skip for 45 days
- max_new_categories_per_month: 3
- length_step: 20
- length_min: 60
- length_max: 300
- length_vote: net (+) − (−) >= 2 → +step; <= −2 → −step
- length_tolerance: 10%

## Maraq

- Sevimli: -
- Seyrək: -

## Tarixçə

- 2026-09-27: başlanğıc — am L3 100-120 söz, pm L2 100-120 söz
```

## Xəta halları

| Hal | Davranış |
|---|---|
| Qiymət anlaşılmır | bir dəfə soruşur |
| Həftədə qiymət yoxdur | review yazılır (mətn sayı, sözlər, test), pillə dəyişmir, xatırlatma |
| `HISTORY.md` sətrində pillə yoxdur | `L2` hesab olunur |
| `HISTORY.md` sətrində söz sayı yoxdur | mətn faylından sayılır |
| Mətn 2 cəhddən sonra da hədəfə düşmür | olduğu kimi göndərilir, həqiqi say yazılır |
| Həftəlik uzunluq addımı hüdudu keçir (60–300) | hüdudda saxlanır, review-da qeyd olunur |
| Review run-u düşdü | növbəti run `last_weekly_review`-dan bəri hamısını götürür |
| Həftəlik və aylıq eyni gün | 30 dəqiqə fərq; push rədd olunarsa `pull --rebase` |
| Git | `checkout -B main origin/main` + `push origin HEAD:main` (mövcud qayda) |

## Test planı

1. `LEVEL.md`, `RATINGS.md`, README yenilənməsi — commit, push.
2. Gündəlik prompt yenilənir. İlk real sınaq: növbəti səhər run-u — mətn L3-də,
   100–120 söz, HISTORY-də `| L3 | <n>w`, mesajın sonunda xatırlatma.
3. İstifadəçi həmin sessiyada qiymət yazır (məs. `2 4 5 +`) → `## Qiymət` +
   `RATINGS.md` sətri (`uzn=+`) yoxlanır; mesajın sonunda `## Qiymət kodu` bloku görünür.
4. Həftəlik routine yaradılır və bu gün (W39) bir dəfə əl ilə işlədilir: qiymət
   yoxdur halı + söz testi yoxlanır; istifadəçi testə cavab verir → qiymətləndirmə
   yoxlanır.
5. Aylıq routine yaradılır; ilk run 2026-10-01 — sentyabr üçün baza report.

## Kənarda qalanlar (YAGNI)

- Oxuma vaxtı / sürət.
- Mətnin suallarına cavab yazıb yoxlatmaq.
- Hesablama skripti — lazım olsa sonra əlavə olunar.
- Artifact / vizual dashboard.
