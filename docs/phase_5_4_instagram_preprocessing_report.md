# Laporan Preprocessing & Pembuatan Dataset Final Instagram (Fase 5.4)
**Zahir Social Analytics — Instagram Public Data Preprocessing, Data Integrity Audit, and Canonical Final Dataset Delivery**  
**Tanggal Eksekusi:** 28 Oktober 2026  
**Status Fase:** `COMPLETED (Tuntas 100%)`  
**Penulis/Auditor:** Zahir Social Analytics Data Engineering Agent  
**Lingkungan:** Python 3.11.9 (`.venv_social`), Windows PowerShell  
**Aturan Tata Kelola:** *Raw data is immutable*, *No synthetic metric fabrication*, *Dual format parity (CSV & XLSX)*, *No Git operations (`git add/commit/push`)*.

---

## 1. Ringkasan Eksekutif

Laporan ini mendokumentasikan implementasi teknis dan audit kualitas data pada **Fase 5.4: Instagram Preprocessing & Final Dataset** dalam ekosistem Zahir Social Analytics. Pipeline ini mentransformasikan 55 postingan publik mentah hasil ekstraksi web unauthenticated (@zahiraccounting) yang telah dikunci pada Fase 1.5–1.7 menjadi dataset analitik final yang siap digunakan untuk analisis engagement (Fase 5.5) dan integrasi dashboard (Fase 6).

### Ringkasan Temuan & Hasil Utama:
1. **Sumber Kanonikal Terverifikasi**: Sumber data mentah kanonikal yang digunakan adalah `data/raw/instagram_posts_raw.csv` (MD5: `c9e7882eff8282bb698825a0ef712817`). Berkas ini identik 100% *byte-for-byte* dengan berkas arsip pengunci baseline `data/raw/instagram_posts_raw_phase1_6_baseline.csv`. Seluruh 12 postingan awal dari Fase 1 terbukti merupakan subset utuh dari 55 postingan ini.
2. **Preservasi 100% Data (Zero Data Loss)**: Tepat **55 baris postingan unik** diproses dan dipertahankan secara utuh tanpa ada baris yang dihapus atau terbuang (0 dropped rows). Tidak terdapat duplikasi ID postingan maupun URL (55 `post_id` unik, 55 `post_url` unik).
3. **Standardisasi Temporal**: Seluruh timestamp ISO-8601 UTC mentah distandarisasi ke Waktu Indonesia Barat (WIB, UTC+7, `Asia/Jakarta`). Ditemukan 5 postingan yang tanggal publikasi lokalnya (WIB) berbeda dari tanggal UTC akibat jam posting di atas 17:00 UTC (00:00 WIB keesokan harinya). Hal ini membuktikan pentingnya standardisasi zona waktu bisnis lokal.
4. **Pembersihan Teks Konservatif**: Teks caption dibersihkan secara konservatif dengan normalisasi unicode (NFKC), perapian spasi tunggal, dan penghapusan URL, dengan tetap mempertahankan seluruh karakter emoji, tanda baca ekspresif, kapitalisasi, serta tagar (#) asli. Teks caption asli tetap disimpan utuh berdampingan dengan kolom teks bersih.
5. **Kebijakan Nilai Kosong & Zero-Fabrication**: Sesuai batasan platform web publik Instagram tanpa login, kolom `views` bernilai `NaN` (100% kosong). Nilai ini **secara ketat tidak diisi dengan angka nol**, dan metrik sintetis (*engagement rate*, *reach*, *impressions*, atau estimasi *followers*) **sama sekali tidak dikarang**. Kolom `total_interactions` dihitung secara eksak dari tindakan interaksi riil yang dapat diverifikasi (`likes + comments`).
6. **Verifikasi Otomatis Sukses 100%**: Pengujian otomatis pada `scripts/verify_phase5_4.py` menghasilkan kelulusan penuh pada 13 pengujian integritas data (*13 passed, 0 failed*). Seluruh data Play Store dan Gold Set tetap terlindungi dan tidak berubah.

---

## 2. Provenance Sumber Data & Audit Pra-Pemrosesan

Sebelum pemrosesan dimulai, dilakukan audit komparatif terhadap seluruh berkas data Instagram yang tersedia di direktori `data/raw/`.

### 2.1 Evaluasi Berkas Mentah & Pemilihan Sumber Kanonikal

| Nama Berkas | Ukuran (Bytes) | Hash MD5 | Baris | Kolom | Status / Klasifikasi |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `instagram_posts_raw.csv` | 53.207 | `c9e7882eff8282bb698825a0ef712817` | 55 | 14 | **Kanonikal Aktif Resmi** |
| `instagram_posts_raw_phase1_6_baseline.csv` | 53.207 | `c9e7882eff8282bb698825a0ef712817` | 55 | 14 | **Arsip Pengunci Baseline Resmi (Fase 1.6)** |
| `instagram_posts_raw_phase15_backup.csv` | 53.207 | `c9e7882eff8282bb698825a0ef712817` | 55 | 14 | Arsip Backup Ekspansi (Fase 1.5) |
| `instagram_expansion_test.csv` | 53.207 | `c9e7882eff8282bb698825a0ef712817` | 55 | 14 | Berkas Uji Coba Ekspansi |
| `instagram_posts_raw.xlsx` | 25.332 | `4a2e471dbf4ef3195f2d858194bc7243` | 55 | 14 | Berkas Excel Mentah Aktif |
| `instagram_posts_raw_phase1_backup.csv` | 11.460 | `89a9b26a635afad98aefd6c1d20195c1` | 12 | 14 | Arsip Mentah Awal (Fase 1) |

**Rasional Pemilihan Sumber Kanonikal:**
`data/raw/instagram_posts_raw.csv` dipilih sebagai satu-satunya sumber kanonikal (*single source of truth*) karena berkas ini merupakan artefak resmi yang ditetapkan oleh pipeline proyek, divalidasi pada Fase 1.5, dan terkunci identik dengan baseline Fase 1.6. Pemeriksaan interseksi himpunan membuktikan bahwa 12 postingan awal Fase 1 merupakan subset 100% dari dataset 55 postingan ini.

---

## 3. Pipeline Preprocessing & Transformasi Data

Pipeline diimplementasikan secara modular dan reproducible pada skrip `preprocessing/instagram_preprocessing.py`. Transformasi dilakukan melalui langkah-langkah terstruktur berikut:

### 3.1 Standardisasi Temporal & Zona Waktu
- Postingan Instagram mencatat waktu publikasi dalam format ISO-8601 UTC string (`post_date`, misal: `2026-08-06T04:22:58.000Z`).
- Konversi dilakukan menggunakan `pandas.to_datetime(utc=True)` lalu ditransformasikan ke zona waktu lokal operasional Zahir Accounting, yaitu Waktu Indonesia Barat (`Asia/Jakarta`, UTC+7).
- Dihasilkan variabel temporal turunan:
  - `post_datetime_utc`: Timestamp format ISO-8601 dengan offset `+00:00`.
  - `post_datetime_wib`: Timestamp format ISO-8601 dengan offset `+07:00`.
  - `post_date`: Tanggal publikasi lokal format `YYYY-MM-DD` berbasis WIB.
  - `post_year`: Tahun publikasi (2024, 2025, atau 2026).
  - `post_month`: Bulan publikasi (1 s/d 12).
  - `post_day`: Hari dalam bulan (1 s/d 31).
  - `post_day_of_week`: Nama hari publikasi dalam bahasa Inggris (`Monday` s/d `Sunday`).
  - `post_hour_wib`: Jam publikasi lokal (0 s/d 23) untuk keperluan optimasi jadwal penayangan (*posting time analysis*).

### 3.2 Pembersihan Teks Caption Konservatif
- Fungsi `clean_caption_text()` melakukan:
  - Normalisasi unicode standar `NFKC` untuk menyelaraskan karakter gabungan.
  - Pembersihan karakter kontrol tak kasat mata (ASCII 0–31 selain spasi dan baris baru).
  - Eliminasi URL eksternal menggunakan ekspresi reguler `https?://\S+|www\.\S+`.
  - Normalisasi whitespace: mengganti rangkaian newline/tab/spasi berlebih menjadi spasi tunggal.
  - Menjaga integritas emoji, tanda baca ekspresif, huruf kapital, dan tagar (#) asli.
- Teks caption mentah asli tetap dipertahankan pada kolom `caption`, sementara teks olahan disimpan pada kolom `caption_clean`.
- Dihitung metrik kuantitatif teks:
  - `caption_length_raw`: Jumlah karakter caption asli.
  - `caption_length_clean`: Jumlah karakter caption setelah pembersihan.
  - `caption_word_count`: Jumlah kata pada caption bersih (whitespace split).

### 3.3 Penanganan Tagar (Hashtags)
- Tagar yang telah diekstraksi pada dataset mentah diverifikasi ulang dengan regex `#\w+` pada teks caption. Dikonfirmasi kecocokan 100%.
- Dihasilkan kolom flag boolean `has_hashtags` (`True` jika `hashtag_count > 0`, `False` jika 0).
- Sebanyak 16 baris postingan memiliki nilai `hashtags = NaN` dan `hashtag_count = 0`. Nilai ini adalah fakta riil bahwa pembuat konten tidak menyertakan tagar pada postingan tersebut.

### 3.4 Agregasi Interaksi & Kebijakan Strict Zero-Fabrication
- Sesuai prinsip etika rekayasa data:
  - Kolom `views` dipertahankan bernilai `NaN` (float null). Platform web publik Instagram tanpa login tidak mengekspos angka penayangan (*view count*). Nilai ini **tidak boleh dikonversi menjadi angka 0** karena ketiadaan data bukan berarti penayangannya nol.
  - Metrik keterlibatan sintetis seperti *impressions*, *reach*, *profile visits*, *followers count*, atau *engagement rate percentage* **sama sekali tidak dikarang**.
  - Kolom `total_interactions` dihitung secara deterministik:
    $$\text{total\_interactions} = \text{likes} + \text{comments}$$

---

## 4. Skema Dataset Final (`data/final/instagram_posts_final.csv` & `.xlsx`)

Dataset final memuat tepat **55 baris** dan **27 kolom analitik** dengan definisi skema sebagai berikut:

| No | Nama Kolom | Tipe Data | Sumber / Asal | Kelengkapan | Definisi & Catatan Metodologis |
| :---: | :--- | :---: | :---: | :---: | :--- |
| 1 | `post_id` | String | Raw Source | 100% (55/55) | Identifier alfanumerik unik postingan Instagram dari shortcode URL. |
| 2 | `post_url` | String | Raw Source | 100% (55/55) | URL publik postingan Instagram (`/p/...` atau `/reel/...`). |
| 3 | `source_url` | String | Raw Source | 100% (55/55) | URL navigasi penjelajahan awal yang merekam kanal/profil asal. |
| 4 | `post_date_raw` | String | Raw Source | 100% (55/55) | String timestamp ISO-8601 UTC asli dari platform Instagram. |
| 5 | `post_datetime_utc` | Datetime | Derived | 100% (55/55) | Timestamp UTC terstandar ISO-8601 (`+00:00`). |
| 6 | `post_datetime_wib` | Datetime | Derived | 100% (55/55) | Timestamp Waktu Indonesia Barat (`+07:00`, `Asia/Jakarta`). |
| 7 | `post_date` | Date String | Derived | 100% (55/55) | Tanggal publikasi resmi format `YYYY-MM-DD` berbasis WIB. |
| 8 | `post_year` | Integer | Derived | 100% (55/55) | Tahun publikasi berbasis WIB (2024 s/d 2026). |
| 9 | `post_month` | Integer | Derived | 100% (55/55) | Bulan publikasi berbasis WIB (1 s/d 12). |
| 10 | `post_day` | Integer | Derived | 100% (55/55) | Hari dalam bulan berbasis WIB (1 s/d 31). |
| 11 | `post_day_of_week` | String | Derived | 100% (55/55) | Nama hari publikasi dalam bahasa Inggris (`Monday` s/d `Sunday`). |
| 12 | `post_hour_wib` | Integer | Derived | 100% (55/55) | Jam publikasi berbasis WIB (0 s/d 23) untuk analisis waktu posting. |
| 13 | `content_type` | String | Raw Source | 100% (55/55) | Format media: `video/reel` (80.0%), `carousel` (14.5%), atau `image` (5.5%). |
| 14 | `caption` | String | Raw Source | 100% (55/55) | Teks takarir (caption) asli tanpa modifikasi. |
| 15 | `caption_clean` | String | Derived | 100% (55/55) | Teks caption bersih (NFKC, spasi tunggal, URL dibersihkan, emoji dijaga). |
| 16 | `caption_length_raw` | Integer | Raw Source | 100% (55/55) | Panjang karakter caption asli (rentang 115 s/d 1.665 karakter). |
| 17 | `caption_length_clean`| Integer | Derived | 100% (55/55) | Panjang karakter caption bersih setelah normalisasi whitespace. |
| 18 | `caption_word_count` | Integer | Derived | 100% (55/55) | Jumlah kata pada caption bersih (whitespace split). |
| 19 | `hashtags` | String | Raw Source | 70.9% (39/55) | Daftar tagar (#) dari caption. Bernilai null jika tidak ada tagar. |
| 20 | `hashtag_count` | Integer | Raw Source | 100% (55/55) | Jumlah tagar pada postingan (rentang 0 s/d 16 tagar). |
| 21 | `has_hashtags` | Boolean | Derived | 100% (55/55) | Flag penanda ketersediaan tagar (`True` jika `hashtag_count > 0`). |
| 22 | `likes` | Integer | Raw Source | 100% (55/55) | Jumlah suka publik riil (rentang 1 s/d 3.191 suka). |
| 23 | `comments` | Integer | Raw Source | 100% (55/55) | Jumlah komentar publik riil (rentang 0 s/d 306 komentar). |
| 24 | `views` | Float (null) | Raw Platform Limit | 0.0% (0/55) | Selalu NaN/null. Platform web publik tidak mengekspos view count. |
| 25 | `total_interactions`| Integer | Derived | 100% (55/55) | Total interaksi terverifikasi (`likes + comments`, rentang 1 s/d 3.497). |
| 26 | `is_collaboration` | Boolean | Raw Source | 100% (55/55) | Flag kolaborasi (`True` jika dipublikasikan bersama akun mitra). |
| 27 | `original_account` | String | Raw Source | 100% (55/55) | Akun pembuat konten (`zahiraccounting`, `muhamad.is`, dll.). |

---

## 5. Audit Kualitas Data & Profil Statistik

Laporan audit kualitas data terstruktur dihasilkan pada:
- `data/final/instagram_analysis/instagram_data_quality_audit.csv`
- `data/final/instagram_analysis/instagram_data_quality_audit.xlsx` (5 sheet komprehensif)

### 5.1 Kelengkapan Kolom (*Completeness Profile*)
- Dari 27 kolom final, sebanyak **25 kolom memiliki tingkat kelengkapan 100.0% (55/55 non-null)**.
- Sebanyak 2 kolom memiliki nilai kosong yang memiliki legitimasi metodologis:
  1. `hashtags`: 16 nilai null (29.09% missing). Ini terjadi secara sah karena 16 postingan tersebut tidak memuat tagar sama sekali pada caption aslinya (`hashtag_count = 0`, `has_hashtags = False`).
  2. `views`: 55 nilai null (100.0% missing). Ini merupakan konsekuensi arsitektural antarmuka web Instagram publik tanpa otentikasi. Nilai ini dijaga `NaN` secara transparan.

### 5.2 Profil Statistik Metrik Keterlibatan (*Engagement Profile*)

| Metrik | N Valid | Min | Kuartil 1 (25%) | Median | Mean | Kuartil 3 (75%) | Max | Akumulasi Total | Standar Deviasi |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `likes` | 55 | 1 | 23,0 | 44,0 | 229,87 | 109,0 | 3.191 | 12.643 | 590,43 |
| `comments` | 55 | 0 | 0,0 | 1,0 | 9,16 | 6,5 | 306 | 504 | 41,14 |
| `total_interactions` | 55 | 1 | 23,0 | 45,0 | 239,04 | 114,0 | 3.497 | 13.147 | 629,08 |
| `caption_length_clean`| 55 | 114 | 419,0 | 587,0 | 647,24 | 888,5 | 1.659 | 35.598 | 308,60 |
| `caption_word_count` | 55 | 16 | 56,5 | 87,0 | 94,15 | 128,5 | 226 | 5.178 | 44,95 |
| `hashtag_count` | 55 | 0 | 0,0 | 5,0 | 4,91 | 6,5 | 16 | 270 | 4,55 |
| `views` | 0 | NaN | NaN | NaN | NaN | NaN | NaN | NaN | NaN |

### 5.3 Distribusi Format Konten & Karakteristik Interaksi

| Format Konten (`content_type`) | Jumlah Postingan | Pangsa (%) | Total Likes | Rata-Rata Likes | Total Comments | Rata-Rata Comments | Total Interaksi | Rata-Rata Interaksi |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `video/reel` | 44 | 80,00% | 12.019 | 273,16 | 486 | 11,05 | 12.505 | 284,20 |
| `carousel` | 8 | 14,55% | 400 | 50,00 | 11 | 1,38 | 411 | 51,38 |
| `image` | 3 | 5,45% | 224 | 74,67 | 7 | 2,33 | 231 | 77,00 |
| **Total / Keseluruhan** | **55** | **100,00%** | **12.643** | **229,87** | **504** | **9,16** | **13.147** | **239,04** |

### 5.4 Distribusi Akun & Efektivitas Kolaborasi

| Akun Asal (`original_account`) | Status Kolaborasi | Jumlah Postingan | Pangsa (%) | Total Likes | Total Comments | Total Interaksi |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `zahiraccounting` | False (Direct) | 29 | 52,73% | 1.849 | 98 | 1.947 |
| `muhamad.is` | True (Collab) | 14 | 25,45% | 3.513 | 140 | 3.653 |
| `pecahtelur.id` | True (Collab) | 8 | 14,55% | 7.070 | 252 | 7.322 |
| `zahironlineid` | True (Collab) | 2 | 3,64% | 141 | 11 | 152 |
| `modalngobrol` | True (Collab) | 1 | 1,82% | 47 | 1 | 48 |
| `zahirerp` | True (Collab) | 1 | 1,82% | 23 | 2 | 25 |
| **Subtotal Kolaborasi** | **True** | **26** | **47,27%** | **10.794** | **406** | **11.200** |
| **Subtotal Non-Kolaborasi**| **False** | **29** | **52,73%** | **1.849** | **98** | **1.947** |

*Insight Kunci Kolaborasi:* Konten kolaborasi co-authored (47,27% postingan) menghasilkan **85,19% dari total interaksi publik** (11.200 dari 13.147 interaksi), dengan mitra utama `pecahtelur.id` (rata-rata 915 interaksi per postingan) dan `muhamad.is` (rata-rata 261 interaksi per postingan). Hal ini mengindikasikan strategi kemitraan kreator bisnis Zahir sangat efektif meningkatkan eksposur brand.

---

## 6. Batasan Akses Publik & Potensi Sampling Bias

Laporan ini secara eksplisit mendokumentasikan batasan metodologis dataset publik unauthenticated:
1. **Bias Format Video/Reel (80.0% Dominasi)**:
   Pada penjelajahan publik tanpa login, feed grid utama profil Instagram memotong pagination setelah 12 kartu konten awal, sedangkan tab Reels publik dapat digulir bertahap hingga 44 item sebelum muncul dialog pencegat login. Akibatnya, dataset baseline publik didominasi oleh konten format video/reel.
2. **Keterbatasan Cakupan Historis (Maret 2024 s/d Agustus 2026)**:
   Profil `@zahiraccounting` memiliki ~1.059 postingan sejak tahun 2017 pada visibilitas akun terotentikasi. Namun, akses publik unauthenticated hanya mampu menjangkau 55 postingan terkini (~2,5 tahun). Dataset ini sangat valid untuk merepresentasikan *kinerja media sosial publik terkini*, tetapi bukan merupakan sensus historis menyeluruh dari seluruh riwayat akun.
3. **Ketiadaan Data Metrik Impresi Privat**:
   Metrik privat seperti penayangan video (*views*), jangkauan akun unik (*reach*), impresi (*impressions*), dan klik tautan profil (*profile link clicks*) hanya tersedia melalui Meta Business Suite atau Graph API terotentikasi. Analisis selanjutnya pada Fase 5.5 berfokus murni pada metrik tindakan publik yang dapat diverifikasi (*likes, comments, total interactions, hashtag engagement*).

---

## 7. Hasil Pengujian Integritas Otomatis (`scripts/verify_phase5_4.py`)

Suite verifikasi otomatis 13-bagian dieksekusi untuk memastikan kualitas dan kepatuhan arsitektural:

```text
===========================================================================
PHASE 5.4 AUTOMATED VERIFICATION & QUALITY AUDIT SUITE
===========================================================================
[PASS] Test 1: Canonical raw Instagram data is 100% frozen & immutable (MD5: c9e7882eff8282bb698825a0ef712817).
[PASS] Test 2: Play Store reviews & Gold Set remain strictly unaltered (417 reviews: 232 pos, 112 neu, 73 neg).
[PASS] Test 3: Row completeness confirmed (100% of 55 raw posts preserved, 0 dropped).
[PASS] Test 4: Uniqueness verified (55 unique post_id, 55 unique post_url, 0 duplicates).
[PASS] Test 5: Engagement metrics verified (Total likes: 12643, Total comments: 504; match raw 100%).
[PASS] Test 6: Views metric integrity confirmed (Strictly 100% NaN; platform web unauthenticated truth preserved, not zeroed).
[PASS] Test 7: Total interactions arithmetic verified (Sum = 13147 == 12,643 likes + 504 comments).
[PASS] Test 8: Datetime parsing & WIB (+07:00) standardizations verified across all 55 posts.
[PASS] Test 9: Caption & text processing verified (Original caption preserved 100%, conservative cleaning valid).
[PASS] Test 10: Hashtags logic verified (39 posts with hashtags [count 1-16], 16 posts without hashtags).
[PASS] Test 11: CSV and XLSX semantic & structural equivalence confirmed (27 columns, 55 rows, dual sheets).
[PASS] Test 12: Privacy verified (Zero personal commenter identifiers or credentials; verified brand accounts only).
[PASS] Test 13: Data quality audit reports verified (CSV: 22 rows, XLSX: 5 comprehensive sheets).
===========================================================================
VERIFICATION SUMMARY: 13 PASSED, 0 FAILED
===========================================================================
ALL 13 PHASE 5.4 AUTOMATED INTEGRITY TESTS PASSED SUCCESSFULLY!
```

---

## 8. Ringkasan Artefak yang Dihasilkan pada Fase 5.4

1. **Skrip Pipeline Reproducible**:
   - `preprocessing/instagram_preprocessing.py` *(Modul preprocessing terstandar, memuat ingestion, transformasi, pembersihan teks, pembuatan XLSX dual-sheet, dan laporan audit kualitas)*.
2. **Dataset Final Instagram**:
   - `data/final/instagram_posts_final.csv` *(55 baris, 27 kolom analitik, serialisasi RFC 4180 quoting=QUOTE_ALL, utf-8-sig)*.
   - `data/final/instagram_posts_final.xlsx` *(55 baris, memuat Sheet 'Instagram Posts Final' dan Sheet 'Data Dictionary & Quality' dengan styling openpyxl)*.
3. **Laporan Audit Kualitas Data**:
   - `data/final/instagram_analysis/instagram_data_quality_audit.csv` *(22 metrik ringkasan dimensi audit)*.
   - `data/final/instagram_analysis/instagram_data_quality_audit.xlsx` *(5 sheet: Audit Summary, Column Completeness, Content Types & Engagement, Account & Collaboration, Engagement Statistics)*.
4. **Dokumentasi & Suite Pengujian**:
   - `scripts/verify_phase5_4.py` *(Suite verifikasi otomatis 13-bagian)*.
   - `docs/phase_5_4_instagram_preprocessing_report.md` *(Laporan komprehensif audit kualitas & tata kelola preprocessing)*.

---

## 9. Kesimpulan & Rekomendasi Menuju Fase 5.5

Fase 5.4 telah selesai 100% dengan status **`COMPLETED`**. Seluruh dataset Instagram publik terkini telah dibersihkan, distandarisasi secara temporal, diverifikasi integritasnya, dan didokumentasikan secara transparan tanpa mengorbankan prinsip integritas data.

Proyek kini berada dalam status siap untuk melanjutkan ke **Fase 5.5: Instagram Social Engagement & Content Performance Analysis**, di mana dataset final `data/final/instagram_posts_final.csv` akan dianalisis secara deskriptif untuk mengeksplorasi efektivitas format konten, performa kolaborasi mitra, dinamika waktu posting, korelasi panjang caption/tagar terhadap interaksi, serta sintesis awal menuju dashboard terpadu di Fase 6.
