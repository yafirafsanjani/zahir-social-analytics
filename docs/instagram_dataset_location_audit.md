# Laporan Audit Lokasi & Kesiapan Dataset Instagram (Fase 1 – 1.7)
**Zahir Social Analytics — Instagram Public Data Location, Lineage, and Readiness Audit**  
**Tanggal Audit:** 2026-10-28  
**Status Audit:** `SELESAI (AUDIT COMPLETED)`  
**Lingkup Pemeriksaan:** Seluruh direktori repositori (`data/raw/`, `data/final/`, `scraper/`, `notebooks/`, `docs/`, `scripts/`)  
**Penulis/Auditor:** Zahir Social Analytics Automated Audit Agent  

---

## 1. Ringkasan Eksekutif

Audit komprehensif ini dilakukan untuk melacak, menginventarisasi, dan memvalidasi seluruh dataset postingan Instagram `@zahiraccounting` yang dihasilkan sepanjang **Fase 1, Fase 1.5, Fase 1.6, dan Fase 1.7**. 

### Temuan Utama Audit:
1. **Lokasi Dataset 55 Postingan Aktif**: Dataset postingan Instagram hasil ekspansi Fase 1.5–1.7 yang valid, lengkap, dan terdeduplikasi (55 postingan unik) berlokasi di direktori mentah:
   - **`data/raw/instagram_posts_raw.csv`** (53.207 bytes, MD5: `c9e7882eff8282bb698825a0ef712817`)
   - **`data/raw/instagram_posts_raw.xlsx`** (25.332 bytes, MD5: `4a2e471dbf4ef3195f2d858194bc7243`)
   - **Arsip Pengunci Baseline Resmi (Fase 1.6)**: `data/raw/instagram_posts_raw_phase1_6_baseline.csv` & `.xlsx` (identik 100% byte-for-byte).
2. **Karakteristik Dataset 55 Postingan**:
   - Jumlah Baris: **Tepat 55 postingan** (0 duplikasi `post_id`, 0 duplikasi `post_url`).
   - Skema Kolom: **14 kolom analitik** terstandarisasi.
   - Rentang Temporal: **01 Maret 2024 s/d 06 Agustus 2026** (~2,5 tahun cakupan).
   - Metrik Keterlibatan (*Engagement*): `likes` 100% lengkap (min 1, median 44, mean 229,87, max 3.191), `comments` 100% lengkap (min 0, median 1, mean 9,16, max 306), sedangkan `views` bernilai `NaN` (100% kosong karena pembatasan platform web publik Instagram tanpa otentikasi).
3. **Status Dataset Final Instagram di `data/final/`**:
   - **BELUM TERSEDIA DI `data/final/`**: Saat ini di direktori `data/final/` hanya terdapat dataset olahan Google Play Store (`playstore_reviews_final.csv`, Gold Set, benchmark sentimen, dan analisis aspek).
   - **Alasan Metodologis**: Setelah Fase 1.7 membekukan baseline publik 55 postingan mentah, fokus proyek beralih sepenuhnya ke pipeline Play Store (Fase 2 Preprocessing, Fase 3 EDA, Fase 4 Sentimen, dan Fase 5 Analisis Topik/Aspek). Preprocessing dan normalisasi Instagram direncanakan untuk tahap sintesis lintas-platform (Fase 6).
4. **Keputusan Scraping**: **TIDAK PERLU SCRAPING ULANG**. Dataset mentah 55 postingan yang sudah tersedia memiliki kualitas data yang sangat tinggi, integritas skema teruji, dan telah mewakili batas maksimal akses publik unauthenticated Instagram (@zahiraccounting). Data ini siap diproses langsung ke pipeline preprocessing `data/final/`.

---

## 2. Inventaris Lengkap Berkas Data Instagram di Repositori

Berdasarkan penelusuran menyeluruh pada sistem berkas repositori, ditemukan **11 berkas data** terkait Instagram yang seluruhnya tersimpan di dalam folder `data/raw/`.

### Tabel Inventaris Berkas Data Instagram

| No | Nama Berkas | Lokasi Relatif | Format | Ukuran (Bytes) | Hash MD5 | Jumlah Baris | Jumlah Kolom | Klasifikasi Tahapan Data |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| 1 | `instagram_posts_raw.csv` | `data/raw/` | CSV | 53.207 | `c9e7882eff8282bb698825a0ef712817` | 55 | 14 | **Active Raw Baseline (Fase 1.5/1.6/1.7)** |
| 2 | `instagram_posts_raw.xlsx` | `data/raw/` | XLSX | 25.332 | `4a2e471dbf4ef3195f2d858194bc7243` | 55 | 14 | **Active Raw Baseline (Fase 1.5/1.6/1.7)** |
| 3 | `instagram_posts_raw_phase1_6_baseline.csv` | `data/raw/` | CSV | 53.207 | `c9e7882eff8282bb698825a0ef712817` | 55 | 14 | **Frozen Baseline Lock (Fase 1.6)** |
| 4 | `instagram_posts_raw_phase1_6_baseline.xlsx` | `data/raw/` | XLSX | 25.332 | `4a2e471dbf4ef3195f2d858194bc7243` | 55 | 14 | **Frozen Baseline Lock (Fase 1.6)** |
| 5 | `instagram_posts_raw_phase15_backup.csv` | `data/raw/` | CSV | 53.207 | `c9e7882eff8282bb698825a0ef712817` | 55 | 14 | **Arsip Backup (Fase 1.5)** |
| 6 | `instagram_posts_raw_phase15_backup.xlsx` | `data/raw/` | XLSX | 25.332 | `4a2e471dbf4ef3195f2d858194bc7243` | 55 | 14 | **Arsip Backup (Fase 1.5)** |
| 7 | `instagram_expansion_test.csv` | `data/raw/` | CSV | 53.207 | `c9e7882eff8282bb698825a0ef712817` | 55 | 14 | **Uji Coba Ekspansi (Fase 1.5)** |
| 8 | `instagram_posts_raw_phase1_backup.csv` | `data/raw/` | CSV | 11.460 | `89a9b26a635afad98aefd6c1d20195c1` | 12 | 14 | **Arsip Backup Raw Awal (Fase 1)** |
| 9 | `instagram_posts_raw_phase1_backup.xlsx` | `data/raw/` | XLSX | 10.630 | `ec8329fd57ba57b70dd7f5f52529f880` | 12 | 14 | **Arsip Backup Raw Awal (Fase 1)** |
| 10 | `instagram_test.csv` | `data/raw/` | CSV | 11.133 | `9a60223f467289f76863f1339096093e` | 12 | 14 | **Uji Coba Scraping Awal (Fase 1)** |
| 11 | `instagram_test.xlsx` | `data/raw/` | XLSX | 10.638 | `b9c983b3d2340c64feb5044988697bc4` | 12 | 14 | **Uji Coba Scraping Awal (Fase 1)** |

> **Catatan Integritas Kriptografis**:  
> Berkas No. 1, 3, 5, dan 7 memiliki nilai hash MD5 yang **identik sempurna** (`c9e7882eff8282bb698825a0ef712817`), membuktikan bahwa seluruh salinan dataset 55 postingan di repositori terjaga integritasnya tanpa modifikasi atau desinkronisasi. Demikian pula berkas XLSX No. 2, 4, dan 6 memiliki hash MD5 identik (`4a2e471dbf4ef3195f2d858194bc7243`).

---

## 3. Klasifikasi Kategori Dataset (Lineage & Provenance)

Untuk mematuhi kaidah tata kelola data yang ketat, dataset dikategorikan ke dalam 4 kelompok status:

### 3.1 Dataset Mentah Awal (*Initial Raw Extract* - Fase 1)
- **Berkas**: `data/raw/instagram_posts_raw_phase1_backup.csv` & `.xlsx` (disertai `instagram_test.csv` & `.xlsx`).
- **Karakteristik**: Memuat **12 postingan** yang diekstraksi dari halaman grid profil publik Instagram (`https://www.instagram.com/zahiraccounting/`) pada muatan DOM awal (12 kartu postingan).
- **Komposisi Format**: 8 carousel, 3 gambar statis (*image*), 1 reel/video.
- **Rentang Waktu**: 02 Januari 2026 s/d 06 Agustus 2026 (~7 bulan).
- **Peran**: Diarsipkan sebagai rekam jejak historis hasil scraping Fase 1 sebelum dilakukan ekspansi multi-surface.

### 3.2 Dataset Hasil Ekspansi & Deduplikasi (*Expanded & Deduplicated* - Fase 1.5)
- **Berkas**: `data/raw/instagram_expansion_test.csv`, `data/raw/instagram_posts_raw_phase15_backup.csv` & `.xlsx`.
- **Karakteristik**: Hasil penggabungan multi-surface antara 12 postingan feed utama dan 44 video dari tab Reels publik (`/reels/`).
- **Deduplikasi**: Ditemukan 1 postingan reel yang beririsan (*overlap*) antara feed utama dan tab reels. Scraper melakukan deduplikasi otomatis berbasis kunci primer `post_id` dan `post_url`, menghasilkan tepat **55 postingan unik** ($12 + 44 - 1 = 55$). Seluruh 12 postingan Fase 1 dipertahankan 100%.

### 3.3 Dataset Baseline Publik Terkunci (*Frozen Public Baseline* - Fase 1.6 & 1.7)
- **Berkas Utama**: `data/raw/instagram_posts_raw.csv` & `data/raw/instagram_posts_raw.xlsx`.
- **Berkas Kunci Resmi**: `data/raw/instagram_posts_raw_phase1_6_baseline.csv` & `data/raw/instagram_posts_raw_phase1_6_baseline.xlsx`.
- **Karakteristik**: Merupakan dataset mentah resmi proyek yang dibekukan (*locked*) pada Fase 1.6 dan ditegaskan kembali pada Fase 1.7.
- **Kebijakan Pembekuan**: Pada Fase 1.7, pengujian penjelajahan manual terotentikasi membuktikan adanya postingan historis (>500 postingan sejak 2017). Namun, demi kepatuhan terhadap regulasi platform (Meta Terms of Service), perlindungan keamanan akun pengguna, dan etika riset, proyek menolak scraping berbasis sesi login dan secara konsisten membekukan 55 postingan publik sebagai baseline acuan resmi.

### 3.4 Dataset Hasil Preprocessing & Dataset Final (*Analytical & Final Dataset*)
- **Status di Repositori**: **BELUM TERSEDIA (NOT YET CREATED)**.
- **Penjelasan**: Belum ada berkas seperti `data/final/instagram_posts_final.csv` atau `instagram_posts_preprocessed.csv`.
- **Justifikasi**: Pipeline pemrosesan data proyek pada Fase 2 hingga Fase 5.3 diprioritaskan untuk menyelesaikan pipeline analitik Google Play Store (417 ulasan). Ekstraksi dan pengolahan data mentah Instagram menjadi dataset analitik final dijadwalkan untuk dikerjakan pada **Fase 6** sebagai bagian dari sintesis multi-platform.

---

## 4. Analisis Mendalam Karakteristik Dataset 55 Postingan

Audit dilakukan pada berkas acuan kanonikal: `data/raw/instagram_posts_raw.csv`.

### 4.1 Skema Kolom (14 Kolom Standar Proyek)

| No | Nama Kolom | Tipe Data Aktual | Kelengkapan (Non-Null) | Persentase Missing | Deskripsi & Isi Kolom |
| :---: | :--- | :---: | :---: | :---: | :--- |
| 1 | `post_id` | `str` | 55 / 55 | 0.0% | Shortcode unik postingan Instagram (contoh: `Dbr2KN3gZjt`) |
| 2 | `post_url` | `str` | 55 / 55 | 0.0% | Tautan permanen kanonikal postingan (`https://www.instagram.com/p/...`) |
| 3 | `source_url` | `str` | 55 / 55 | 0.0% | URL asal discovery (Feed profil atau Tab Reels) |
| 4 | `post_date` | `str (ISO-8601)` | 55 / 55 | 0.0% | Timestamp UTC penerbitan konten (contoh: `2026-08-06T04:22:58.000Z`) |
| 5 | `content_type` | `str` | 55 / 55 | 0.0% | Format konten: `video/reel`, `carousel`, atau `image` |
| 6 | `caption` | `str` | 55 / 55 | 0.0% | Teks takarir asli lengkap postingan (termasuk emoji & baris baru) |
| 7 | `likes` | `int64` | 55 / 55 | 0.0% | Jumlah suka (*likes/upvotes*) publik |
| 8 | `comments` | `int64` | 55 / 55 | 0.0% | Jumlah komentar publik pada postingan |
| 9 | `views` | `float64` | 0 / 55 | **100.0%** | Jumlah tayangan (*views*) video/reels (selalu NaN pada web publik) |
| 10 | `hashtags` | `str` | 39 / 55 | 29.1% | Daftar tagar yang diekstrak dari caption (16 postingan tanpa tagar) |
| 11 | `hashtag_count` | `int64` | 55 / 55 | 0.0% | Jumlah tagar dalam caption (rentang 0 s/d 16 tagar) |
| 12 | `caption_length` | `int64` | 55 / 55 | 0.0% | Panjang teks caption dalam karakter (rentang 115 s/d 1.665 karakter) |
| 13 | `is_collaboration` | `bool` | 55 / 55 | 0.0% | Penanda apakah postingan merupakan kolaborasi dengan akun lain |
| 14 | `original_account` | `str` | 55 / 55 | 0.0% | Akun pembuat/mitra asli konten (terlacak dari header postingan) |

### 4.2 Analisis Metrik Keterlibatan (*Engagement Metrics Profile*)

| Metrik Engagement | Jumlah Tersedia | Missing | Min | Kuartil 1 (25%) | Median (50%) | Mean (Rata-rata) | Kuartil 3 (75%) | Max | Standar Deviasi |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`likes`** | 55 (100%) | 0 (0%) | 1 | 23,0 | 44,0 | 229,87 | 109,0 | 3.191 | 590,43 |
| **`comments`** | 55 (100%) | 0 (0%) | 0 | 0,0 | 1,0 | 9,16 | 6,5 | 306 | 41,14 |
| **`views`** | 0 (0%) | 55 (100%) | NaN | NaN | NaN | NaN | NaN | NaN | NaN |
| **`hashtag_count`**| 55 (100%) | 0 (0%) | 0 | 0,0 | 5,0 | 4,91 | 6,5 | 16 | 4,55 |
| **`caption_length`**| 55 (100%) | 0 (0%) | 115 | 423,5 | 591,0 | 651,42 | 894,0 | 1.665 | 310,34 |

#### Temuan Analisis Metrik Engagement:
1. **Total Interaksi**: Total `likes` yang terkumpul dari 55 postingan adalah **12.643 likes**, dan total `comments` adalah **504 komentar** (Total interaksi mentah = 13.147).
2. **Distribusi Skewed (Miring ke Kanan)**: Terdapat beberapa konten viral dengan keterlibatan sangat tinggi (maksimal 3.191 likes dan 306 komentar), sementara nilai tengah (median) berada pada 44 likes dan 1 komentar. Hal ini menunjukkan dinamika distribusi konten media sosial yang wajar (*power-law distribution*).
3. **Ketiadaan Metrik Views (100% Missing)**: Platform web publik Instagram tidak menampilkan angka tayangan (*view count*) video reels kepada pengguna yang tidak login (anonim). Nilai `views` yang bernilai `NaN` pada seluruh baris adalah **representasi fakta teknis platform**, bukan kerusakan data (*corrupted data*). Dalam analisis berikutnya, metrik views tidak boleh direkayasa atau diisi angka tiruan.

### 4.3 Distribusi Format Konten (*Content Types*) & Sampling Bias
- **`video/reel`**: **44 postingan (80.00%)**
- **`carousel`**: **8 postingan (14.55%)**
- **`image`**: **3 postingan (5.45%)**

> **Audit Sampling Bias (Fase 1.6)**:  
> Dataset baseline publik ini mengalami *sampling bias* teknis terhadap format Reels (80%). Hal ini terjadi karena Instagram mengunci muatan feed foto/carousel pada 12 item pertama untuk akses publik anonim, sedangkan tab Reels memungkinkan infinite scroll bertahap hingga scroll ke-8 (44 reels) sebelum diinterupsi oleh dialog login. Keterbatasan sampling ini telah didokumentasikan secara transparan pada laporan metodologi proyek.

### 4.4 Distribusi Kepemilikan Akun & Kolaborasi (*Collaboration Provenance*)
- **Non-Kolaborasi (`is_collaboration == False`)**: **29 postingan (52.73%)** — Dipublikasikan langsung oleh akun `@zahiraccounting`.
- **Kolaborasi Publik (`is_collaboration == True`)**: **26 postingan (47.27%)** — Konten kemitraan/co-author yang tampil resmi di feed Zahir.
- **Rincian Akun Pembuat Asli (`original_account`)**:
  1. `zahiraccounting`: 29 postingan (52.7%)
  2. `muhamad.is` (CEO/Founder Zahir): 14 postingan (25.5%)
  3. `pecahtelur.id`: 8 postingan (14.5%)
  4. `zahironlineid`: 2 postingan (3.6%)
  5. `modalngobrol`: 1 postingan (1.8%)
  6. `zahirerp`: 1 postingan (1.8%)

---

## 5. Perbandingan Detail: Dataset Mentah vs Dataset Final Terencana

Untuk memperjelas mengapa dataset final belum ada dan apa perbedaannya dengan dataset mentah saat ini:

| Dimensi | Dataset Mentah Saat Ini (`data/raw/instagram_posts_raw.csv`) | Dataset Final Terencana (`data/final/instagram_posts_final.csv`) |
| :--- | :--- | :--- |
| **Lokasi Direktori** | `data/raw/` | `data/final/` |
| **Jumlah Baris** | 55 postingan | 55 postingan (100% data dipertahankan) |
| **Status Pemrosesan** | Ekstraksi scraper murni (*raw immutable*) | Terstandarisasi, bersih, siap analitik (*preprocessed*) |
| **Format Tanggal** | String ISO-8601 (`2026-08-06T04:22:58.000Z`) | Datetime terurai: `post_datetime`, `post_date`, `year`, `month`, `day`, `day_of_week` |
| **Pembersihan Teks** | Teks mentah dengan URL eksternal dan format spasi tak beraturan | `caption_clean` (bebas URL, whitespace rapi, tokenisasi NLP terstandar) |
| **Metrik Teks** | Hanya `caption_length` karakter | `text_length_chars`, `word_count`, `emoji_count` |
| **Metrik Interaksi** | `likes`, `comments`, `views` mentah | `total_interactions`, `engagement_proxy`, dokumentasi status `views` |
| **Metrik Tagar** | String koma tagar mentah | `hashtags_list`, `primary_hashtag`, `hashtag_count` |
| **Status Keberadaan** | **TERSEDIA & TERVALIDASI 100%** | **SIAP DIBANGUN PADA FASE 6** |

---

## 6. Langkah-Langkah Konkret Membangun Dataset Final Instagram (Roadmap Fase 6)

Karena dataset mentah 55 postingan telah lengkap dan terverifikasi tanpa anomali, **tidak diperlukan scraping ulang**. Untuk menghasilkan `data/final/instagram_posts_final.csv` dan `.xlsx`, langkah-langkah yang diperlukan adalah:

1. **Membuat Modul Preprocessing Modular**:
   - Membangun skrip `preprocessing/instagram_preprocessing.py` (serupa dengan `playstore_preprocessing.py` di Fase 2).
2. **Pembersihan & Ekstraksi Fitur Teks**:
   - Menghapus URL tautan web dari teks caption (`caption_clean`).
   - Melakukan normalisasi spasi tanpa menghilangkan ekspresi emoji yang relevan untuk analisis sentimen media sosial.
   - Menghitung metrik linguistik: `caption_char_count` dan `caption_word_count`.
3. **Penguraian Tanggal Terstruktur**:
   - Mengonversi `post_date` ISO-8601 menjadi `post_datetime` waktu lokal (WIB / UTC+7).
   - Mengekstrak komponen temporal: `post_year`, `post_month`, `post_day`, dan `post_day_of_week` untuk memetakan tren postingan bulanan/mingguan.
4. **Kalkulasi Metrik Keterlibatan (*Engagement Rate Proxy*)**:
   - Menghitung `total_interactions = likes + comments`.
   - Mengelompokkan postingan ke dalam kuartil performa keterlibatan (*High, Medium, Low Engagement*).
   - Mempertahankan `views` sebagai `NaN` secara transparan dengan dokumentasi bahwa views tidak tersedia di web publik tanpa login.
5. **Penyimpanan Output Ganda (*Dual Format Export*)**:
   - Menyimpan ke `data/final/instagram_posts_final.csv` dengan standardisasi RFC 4180 (`quoting=csv.QUOTE_ALL`, encoding `utf-8-sig`).
   - Menyimpan ke `data/final/instagram_posts_final.xlsx` dengan format styling profesional openpyxl (header biru navy, border tipis, auto-fit lebar kolom).
6. **Verifikasi Integritas Data**:
   - Membuat skrip verifikasi otomatis `scripts/verify_instagram_final.py` untuk menguji kesetaraan semantik CSV/XLSX, kelengkapan 55 baris, dan keunikan ID.

---

## 7. Kesimpulan & Rekomendasi Langkah Berikutnya

### Kesimpulan Audit:
1. **Dataset Instagram 55 Postingan Berada di Tempat yang Tepat**: Seluruh data postingan publik hasil ekspansi Fase 1.5–1.7 tersimpan aman di `data/raw/instagram_posts_raw.csv` dan `data/raw/instagram_posts_raw.xlsx` (serta terkunci di `data/raw/instagram_posts_raw_phase1_6_baseline.csv`).
2. **Dataset Final Belum Ada Bukan Merupakan Anomali**: Ketiadaan berkas Instagram di `data/final/` adalah konsekuensi dari pembagian urutan kerja proyek di mana Fase 2–5.3 didedikasikan untuk ulasan Play Store.
3. **Data Sumber Sangat Sehat**: 0 duplikasi, 100% kelengkapan likes/comments/caption/date, mencakup rentang 2024–2026, dan memuat 14 kolom lengkap.

### Rekomendasi Langkah Berikutnya:
1. **Pertahankan Dataset Mentah Tetap Immutable**: Jangan mengubah atau menimpa `data/raw/instagram_posts_raw.csv`.
2. **Lanjutkan ke Pembangunan Preprocessing Instagram**: Jalankan pipeline preprocessing untuk memproduksi `data/final/instagram_posts_final.csv` dan `.xlsx` sebelum memulai pembuatan dashboard lintas-platform.
3. **Integrasikan ke Dashboard Streamlit (Fase 6)**: Tampilkan visualisasi metrik Instagram (seperti tren postingan, distribusi format Reels vs Carousel, perbandingan performa kolaborasi vs non-kolaborasi, serta top postingan berdasarkan likes/komentar) berdampingan dengan metrik Voice of Customer Play Store.

---
*Laporan audit ini disusun secara independen dan objektif sebagai rujukan data provenance resmi proyek Zahir Social Analytics.*
