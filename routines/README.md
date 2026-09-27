# Routine prompt-ları

Bu fayllar claude.ai-dakı cloud routine-lərin prompt-larıdır — mənbə buradır.
Routine işləyəndə prompt-u trigger-dən oxuyur, bu fayldan yox: faylı dəyişəndən sonra
trigger-i də yeniləmək lazımdır (RemoteTrigger `update`).

| Fayl | Routine | Vaxt (Bakı) | Cron (UTC) |
|---|---|---|---|
| `daily.md` | Daily English Reading (AZ) — `trig_017Pt3sNTiukVCgvymhiu1JK` | hər gün 10:00, 19:00 | `0 6,15 * * *` |
| `weekly.md` | Weekly English Progress Review (AZ) | bazar 21:00 | `0 17 * * 0` |
| `monthly.md` | Monthly English Progress Review (AZ) | ayın 1-i 21:30 | `30 17 1 * *` |
