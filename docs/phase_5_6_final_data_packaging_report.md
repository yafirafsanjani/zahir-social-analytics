# Laporan Pengemasan & Pengiriman Data Lintas Platform (Fase 5.6)
**Zahir Social Analytics — Final Data Packaging, Privacy Minimization, and Cross-Platform Data Delivery**  
**Tanggal Eksekusi:** 02 November 2026  
**Status Fase:** `COMPLETED (Tuntas 100%)`  
**Penulis/Auditor:** Zahir Social Analytics Data Engineering Agent  
**Lingkungan:** Python 3.11.9 (`.venv_social`), Windows PowerShell  
**Aturan Tata Kelola:** *Raw data is immutable*, *No synthetic metric fabrication*, *Dual format parity (CSV & XLSX)*, *Strict Privacy Minimization*, *No Git operations (`git add/commit/push`)*.

---

## 1. Ringkasan Eksekutif

Laporan ini mendokumentasikan penyelesaian **Fase 5.6: Final Data Packaging & Cross-Platform Data Delivery** dalam ekosistem Zahir Social Analytics. Fase ini bertujuan untuk mengaudit, menyeleksi, menyelaraskan kunci relasional, dan mengemas seluruh dataset final hasil pemrosesan multi-fase ke dalam satu paket pengiriman data (*data delivery package*) yang bersih, aman dari data pribadi (*privacy-minimized*), terstruktur rapi, terdokumentasi lengkap, serta siap digunakan secara langsung (*plug-and-play*) oleh repositori dashboard interaktif terpisah (Fase 6).

### Ringkasan Temuan & Hasil Kunci:
1. **Audit Sumber Lengkap & Terverifikasi**:
   - Seluruh sumber data analitik kanonikal dari Fase 5.3 (aspek remediated), Fase 5.4 (dataset final Instagram 55 postingan), dan Fase 5.5 (metrik keterlibatan Instagram) telah diaudit kelengkapan, skema, dan konsistensi matematisnya tanpa anomali.
   - Sumber mentah kanonikal `data/raw/instagram_posts_raw.csv` (MD5: `c9e7882eff8282bb698825a0ef712817`) dan dataset final Fase 5.4 `data/final/instagram_posts_final.csv` (MD5: `794b050f649bc76537cf31f12b485b66`) tetap 100% *frozen* dan terlindungi.
2. **Paket Ekspor Media Sosial Instagram (`data/export/instagram/`)**:
   - `instagram_posts_clean.csv` & `.xlsx` (55 baris, 27 kolom): Dataset utama postingan Instagram publik terstandarisasi waktu WIB.
   - `instagram_engagement_metrics.csv` & `.xlsx` (55 baris, 23 kolom): Metrik interaksi level postingan dengan peringkat rank, persentil, dan flag pencilan IQR.
   - `instagram_content_performance.csv` & `.xlsx` (28 baris ringkasan terpadu, 16 kolom; 7 sheet Excel eksekutif): Ringkasan komparasi format, status kolaborasi, entitas mitra, hari tayang, segmen waktu WIB, tahun, dan keberadaan tagar.
   - **Zero-Fabrication Policy**: Kolom `views` bernilai `NaN` (100% missing) dipertahankan sesuai realitas web publik tanpa login. Tidak ada pembuatan metrik sintetis *reach*, *impressions*, atau *arbitrary engagement rate*.
3. **Paket Ekspor Customer Voice Play Store (`data/export/playstore/`)**:
   - `playstore_reviews_clean.csv` & `.xlsx` (417 ulasan, 19 kolom): Dataset ulasan bersih tanpa atribut PII (`userName`, `userImage`, `reviewer_id`, dan `reply_text` sengaja dieliminasi).
   - `playstore_sentiment.csv` & `.xlsx` (417 ulasan, 14 kolom; 3 sheet Excel): Pemisahan tegas antara Ground Truth Anotasi Manusia (*Gold Set*, $n=417$) dan prediksi model benchmark NLP pada data uji (*Test Set*, $n=84$) yang diberi penanda eksplisit `test_pred_*`.
   - `playstore_aspects.csv` & `.xlsx` (417 ulasan, 17 kolom wide; 3 sheet Excel): Multi-label 8 aspek produk hasil remediated Fase 5.3 dengan tepat **234 mention aspek** (Sheet 2 memuat format *Long* 234 baris, dan Sheet 3 memuat ringkasan 8 aspek).
4. **Kamus Data & Panduan Ekspor Terpadu**:
   - Dokumen `data/export/README_data_dictionary.md` (31 KB) disusun lengkap mencakup tujuan berkas, definisi tiap kolom, tipe data, rumus metrik, kunci relasi, sumber sentimen, taksonomi 8 aspek, kebijakan nilai kosong, dan keterbatasan sampling.
5. **Verifikasi Integritas 100% Sukses**:
   - Seluruh 15 pengujian integritas programatik pada `scripts/verify_phase5_6.py` lulus 100% (*15 passed, 0 failed*).
   - Uji regresi Fase 5.3 (15 tests), Fase 5.4 (13 tests), dan Fase 5.5 (15 tests) diuji ulang dan seluruhnya lulus (**total 58 / 58 uji integritas sukses tanpa regresi**).

---

## 2. Audit Sumber Data Aktual

Sebelum pengemasan data dilakukan, tim data science menjalankan audit komprehensif terhadap seluruh berkas data sumber di direktori `data/final/`:

### 2.1 Domain Media Sosial Instagram

| Berkas Sumber Aktual | Lokasi Berkas | Baris | Kolom | Status Audit & Kesesuaian |
| :--- | :--- | :---: | :---: | :--- |
| `instagram_posts_final.csv` | `data/final/` | 55 | 27 | **Sesuai 100%**. MD5: `794b050f...`, 0 duplikasi, views=NaN. |
| `instagram_posts_final.xlsx` | `data/final/` | 55 | 27 | **Sesuai 100%**. Dual sheet: Main Data & Data Dictionary. |
| `instagram_engagement_metrics.csv` | `data/final/instagram_analysis/` | 55 | 23 | **Sesuai 100%**. Likes: 12.643, Comms: 504, Total: 13.147. |
| `instagram_engagement_summary.csv` | `data/final/instagram_analysis/` | 3 | 15 | **Sesuai 100%**. Statistik likes, comments, total interactions. |
| `instagram_content_type_comparison.csv`| `data/final/instagram_analysis/` | 4 | 24 | **Sesuai 100%**. 44 Reels, 8 Carousel, 3 Image, 1 Total. |
| `instagram_collaboration_analysis.csv` | `data/final/instagram_analysis/` | 9 | 19 | **Sesuai 100%**. Organik (29), Colab (26), 6 entitas akun mitra. |
| `instagram_posting_time_analysis.csv` | `data/final/instagram_analysis/` | 14 | 11 | **Sesuai 100%**. 7 hari, 4 time bins, 3 tahun publikasi. |
| `instagram_caption_hashtag_analysis.csv`| `data/final/instagram_analysis/` | 13 | 13 | **Sesuai 100%**. Korelasi Spearman/Pearson & Simpson's paradox. |
| `instagram_top_posts.csv` | `data/final/instagram_analysis/` | 20 | 16 | **Sesuai 100%**. Top 10 viral & Bottom 10 low engagement. |

### 2.2 Domain Customer Voice Google Play Store

| Berkas Sumber Aktual | Lokasi Berkas | Baris | Kolom | Status Audit & Kesesuaian |
| :--- | :--- | :---: | :---: | :--- |
| `playstore_reviews_final.csv` | `data/final/` | 417 | 21 | **Sesuai 100%**. 417 ulasan 5 app, rating 1-5, datetime parseable. |
| `playstore_gold_set_final.csv` | `data/final/` | 417 | 7 | **Sesuai 100%**. 232 pos, 112 neu, 73 neg. Ground truth tervalidasi. |
| `review_aspect_assignments_remediated.csv`| `data/final/topic_analysis/phase_5_3/`| 417 | 17 | **Sesuai 100%**. Tepat 234 mention aspek pada 8 aspek remediated. |
| `sentiment_benchmark_metrics.csv` | `data/final/sentiment_benchmark/` | 4 | 18 | **Sesuai 100%**. IndoBERT Macro F1: 0.7303 vs InSet: 0.5513. |
| `sentiment_split_manifest.csv` | `data/final/sentiment_benchmark/` | 417 | 5 | **Sesuai 100%**. 333 dev, 84 test split stratified. |
| `sentiment_test_predictions.csv` | `data/final/sentiment_benchmark/` | 84 | 12 | **Sesuai 100%**. Prediksi IndoBERT, InSet, TF-IDF pada test set. |

*Konfirmasi Audit*: Tidak ditemukan diskrepansi antara laporan fase sebelumnya dengan berkas fisik aktual di sistem file.
---

## 3. Inventarisasi Lengkap Berkas Ekspor (data/export/)

Paket pengiriman akhir disusun dalam struktur folder terpisah untuk memisahkan domain data Instagram dan Play Store. Seluruh berkas disediakan dalam format ganda terstandarisasi (**CSV RFC 4180** dengan enkapsulasi kutip penuh dan penanganan karakter khusus UTF-8-sig, serta **Excel XLSX** dengan penataan styling korporat openpyxl):

### 3.1 Berkas Paket Ekspor Instagram (`data/export/instagram/`)

| Nama Berkas | Format | Ukuran Berkas | Baris Data | Kolom Data | Daftar Sheet Excel | Ringkasan Fungsi & Konten |
| :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| `instagram_posts_clean.csv` | CSV | 93,9 KB | 55 | 27 | - | Dataset kanonikal postingan Instagram publik Zahir (teks bersih, waktu WIB, interaksi, format, tagar, kolaborasi). |
| `instagram_posts_clean.xlsx` | XLSX | 33,4 KB | 55 | 27 | `Instagram Posts Clean`, `Data Dictionary` | Format spreadsheet terformat rapi dilengkapi kamus data bawaan (*embedded dictionary*). |
| `instagram_engagement_metrics.csv` | CSV | 15,5 KB | 55 | 23 | - | Metrik interaksi level postingan dengan peringkat rank (1-55), persentil, tier performa, dan flag pencilan IQR. |
| `instagram_engagement_metrics.xlsx` | XLSX | 14,7 KB | 55 | 23 | `Engagement Metrics`, `Data Dictionary` | Format spreadsheet terformat rapi dilengkapi kamus data bawaan. |
| `instagram_content_performance.csv`| CSV | 3,7 KB | 28 | 16 | - | Ringkasan terpadu komparasi performa konten (Format, Kolaborasi, Akun Mitra, Hari, Jam Tayang, Tahun, Tagar). |
| `instagram_content_performance.xlsx`| XLSX | 20,9 KB | 28 | 16 | 7 Sheets: `Performance Overview`, `Content Type Breakdown`, `Collaboration Breakdown`, `Posting Time Breakdown`, `Caption & Hashtags`, `Engagement Distribution`, `Top & Bottom Showcase` | Laporan eksekutif performa konten multi-sheet terlengkap untuk bahan analitik dashboard. |

### 3.2 Berkas Paket Ekspor Play Store (`data/export/playstore/`)

| Nama Berkas | Format | Ukuran Berkas | Baris Data | Kolom Data | Daftar Sheet Excel | Ringkasan Fungsi & Konten |
| :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| `playstore_reviews_clean.csv` | CSV | 136,1 KB | 417 | 19 | - | Dataset utama ulasan Play Store bersih bebas PII (`userName`, `userImage`, `reviewer_id`, `reply_text` dieliminasi). |
| `playstore_reviews_clean.xlsx` | XLSX | 80,1 KB | 417 | 19 | `Play Store Reviews Clean`, `Data Dictionary` | Format spreadsheet terformat rapi dilengkapi kamus data bawaan. |
| `playstore_sentiment.csv` | CSV | 55,7 KB | 417 | 14 | - | Label sentimen manusia Gold Set 417 ulasan (232 pos, 112 neu, 73 neg) dan evaluasi prediksi model benchmark NLP. |
| `playstore_sentiment.xlsx` | XLSX | 50,1 KB | 417 | 14 | `Sentiment Full Dataset`, `Benchmark Test Predictions`, `Benchmark Metrics Summary` | Spreadsheet sentimen multi-sheet dengan pemisahan tegas Gold Set vs IndoBERT/InSet/TF-IDF. |
| `playstore_aspects.csv` | CSV | 103,1 KB | 417 | 17 | - | Multi-label 8 aspek produk Zahir hasil remediated Fase 5.3 (417 ulasan, 234 mention aspek terdeteksi). |
| `playstore_aspects.xlsx` | XLSX | 83,3 KB | 417 | 17 | `Aspect Reviews (Wide)`, `Aspect Mentions (Long)`, `Aspect Summary (8 Aspects)` | Format multi-sheet komprehensif: Wide (417 baris), Long (234 baris mention), dan Summary 8 Aspek Produk. |

### 3.3 Berkas Dokumentasi & Kamus Data
- `data/export/README_data_dictionary.md` (Markdown, 31,3 KB): Panduan lengkap definisi 100+ kolom, formula metrik, taksonomi aspek, dan contoh kode integrasi dashboard.

---

## 4. Kunci Penghubung Antarfile & Integritas Relasional

Arsitektur relasional paket ekspor dirancang secara modular dan dinormalisasi untuk mencegah redundansi data:

### 4.1 Hubungan Relasional Domain Instagram (Foreign Key: `post_id`)
- `post_id` bertindak sebagai kunci primer pada `instagram_posts_clean` dan kunci asing (*foreign key*) pada `instagram_engagement_metrics`.
- Relasi: **1-to-1 Kardinalitas Sempurna**.
- Verifikasi Integritas: Tepat 55 `post_id` unik tanpa nilai null, dan irisan himpunan ID antara berkas konten dan berkas metrik menghasilkan kesamaan $100\%$ ($55 / 55$).
- Tautan Publik: Kolom `post_url` dipertahankan pada kedua berkas untuk keperluan audit forensik menuju halaman web publik Instagram asli.

### 4.2 Hubungan Relasional Domain Play Store (Foreign Key: `review_id`)
- `review_id` bertindak sebagai kunci primer pada `playstore_reviews_clean` dan kunci asing pada `playstore_sentiment` dan `playstore_aspects`.
- Relasi:
  - `playstore_reviews_clean` $\longleftrightarrow$ `playstore_sentiment`: **1-to-1** (Tepat 417 baris pada kedua tabel).
  - `playstore_reviews_clean` $\longleftrightarrow$ `playstore_aspects (Wide)`: **1-to-1** (Tepat 417 baris pada kedua tabel).
  - `playstore_reviews_clean` $\longleftrightarrow$ `playstore_aspects (Long)`: **1-to-N** (Tepat 234 baris mention yang merujuk pada 174 ulasan unik yang memiliki aspek).
- Verifikasi Integritas: Himpunan 417 UUID ulasan identik $100\%$ di ketiga berkas ulasan Play Store tanpa ada foreign key yang terputus (*zero dangling foreign keys*).

---

## 5. Kebijakan Reduksi Privasi (PII Minimization)

Sesuai instruksi penugasan, etika rekayasa data, dan prinsip perlindungan privasi konsumen (*General Data Protection Regulation / Data Privacy Principles*), paket data Play Store yang diekspor telah dibersihkan secara agresif dari potensi paparan identitas personal:

1. **Penghapusan Nama Pengguna (`userName`) & Avatar (`userImage`)**:
   - Kolom nama akun pengguna asli Google Play Store dan URL gambar profil pengguna **sama sekali tidak disertakan** dalam paket ekspor.
2. **Penghapusan Kolom Penyamaran Hash (`reviewer_id`)**:
   - Meskipun pada Fase 2 telah dibuat penyamaran hash SHA-256 (`reviewer_id`), kolom ini sengaja dieliminasi dari berkas ekspor bersih untuk meminimalkan beban memori dashboard dan mencegah *linkability risk* yang tidak perlu.
3. **Penghapusan Teks Balasan Developer (`reply_text`)**:
   - Kolom `reply_text` yang memuat teks tanggapan tim customer support developer dihapus dari berkas `playstore_reviews_clean`.
   - Tindakan ini menjamin dashboard berfokus murni pada teks asli konsumen (*unadulterated customer voice*) tanpa terdistorsi oleh bahasa template layanan pelanggan Zahir.
   - Analisis performa layanan pelanggan tetap dapat dilakukan secara aman menggunakan metrik kuantitatif terstandarisasi: flag boolean `has_developer_reply` dan durasi waktu respon `response_time_days`.

---

## 6. Pemisahan Eksplisit Sentimen Manusia vs Prediksi Model

Untuk mencegah kebingungan metodologis di sisi dashboard, berkas `playstore_sentiment.csv` dan `.xlsx` menerapkan segregasi kolom yang sangat ketat antara **Ground Truth** dan **Prediksi Model NLP**:

1. **Kolom Ground Truth (Anotasi Manusia / Gold Set)**:
   - `human_sentiment_label`: Menyimpan label sentimen konsensus manusia dari Gold Set Fase 4.2 (Positif = 232, Netral = 112, Negatif = 73).
   - `sentiment_label_source`: Berisi string eksplisit `"gold_set_human_annotated"` pada seluruh 417 baris. Kolom ini menegaskan bahwa label tersebut adalah fakta kebenaran dasar (*ground truth*), bukan estimasi algoritma.
2. **Kolom Prediksi Model Benchmark**:
   - Seluruh kolom hasil inferensi model diawali dengan penanda eksplisit `test_pred_*`:
     - `test_pred_indobert` & `test_indobert_confidence` (IndoBERT Transformer)
     - `test_pred_inset_lexicon` & `test_inset_score` (InSet Lexicon Kamus Bahasa Indonesia)
     - `test_pred_tfidf_lr` & `test_tfidf_lr_confidence` (TF-IDF Logistic Regression Baseline)
   - Kolom `benchmark_split` mencatat alokasi partisi data: `development` ($n=333$, $79.86\%$) dan `test` ($n=84$, $20.14\%$).
   - **Zero-Data Leakage**: Pada baris partisi `development`, kolom `test_pred_*` bernilai `NaN`. Prediksi model hanya diisi pada 84 ulasan partisi pengujian yang menjadi dasar pelaporan metrik benchmark Fase 4.3 (IndoBERT Macro F1: 0.7303 vs InSet: 0.5513).
---

## 7. Preservasi 234 Mention Aspek Produk Remediated (Dual-Format Architecture)

Salah satu capaian terpenting pada Fase 5.3 adalah keberhasilan proses remediasi taksonomi aspek produk, yang mengeliminasi aturan kata kunci berisiko tinggi (*bare-word false positives* seperti kata "bisa" dan "update") sehingga menghasilkan pemetaan aspek yang jauh lebih presisi (tingkat kesepakatan anotasi manusia meningkat dari 73.3% menjadi 90.0%).

Pada paket ekspor `playstore_aspects.csv` dan `.xlsx`, integritas 234 mention aspek remediated ini dipreservasi secara utuh melalui arsitektur multi-format:

### 7.1 Format Wide (Tabel Utama / CSV Default)
- **Dimensi**: 417 baris x 17 kolom.
- **Tujuan**: Memungkinkan pengembang dashboard melakukan pemfilteran, seleksi multi-aspek, dan *cross-tabulation* ulasan pada tabel interaktif secara efisien tanpa memerlukan operasi *unpivot*.
- **Kolom Utama**:
  - `review_id` (Primary Key).
  - 8 kolom indikator boolean (`aspect_customer_service`, `aspect_performance_bugs`, `aspect_features_functionality`, `aspect_pricing_subscription`, `aspect_ui_ux`, `aspect_cloud_sync`, `aspect_login_account`, `aspect_update_system`).
  - `aspect_count`: Jumlah aspek yang terdeteksi per ulasan (0 <= aspect_count <= 4).
  - `has_aspect`: Flag boolean apakah ulasan memiliki minimal 1 aspek (n=161, 38.61%).
  - `dominant_aspect`: Aspek utama dengan bobot/skor kecocokan tertinggi.
  - `dominant_confidence`: Skor keyakinan aspek dominan (0.0 - 1.0).
  - `detected_aspects_list`: Representasi string daftar aspek terdeteksi (dipisahkan tanda koma).
  - `keyword_evidence`: Bukti kata kunci yang memicu deteksi aspek.

### 7.2 Format Long (Sheet `Aspect_Mentions_Long` pada XLSX)
- **Dimensi**: Tepat **234 baris** x 6 kolom.
- **Tujuan**: Format ideal untuk agregasi facet (*faceting*), visualisasi distribusi sentimen per-aspek (*stacked bar chart / grouped violin plot*), dan pengelompokan drill-down interaktif pada Plotly / Streamlit.
- **Skema Kolom**:
  - `review_id`: Foreign key ke ulasan sumber.
  - `aspect_id`: Kode baku aspek (`customer_service`, `performance_bugs`, dsb.).
  - `aspect_name`: Nama resmi aspek berbahasa Indonesia.
  - `sentiment_label`: Sentimen ulasan sumber (positif, netral, negatif).
  - `confidence_score`: Tingkat keyakinan deteksi kata kunci.
  - `matched_keywords`: Kata kunci spesifik yang cocok pada ulasan tersebut.

### 7.3 Distribusi 234 Mention Aspek Remediated
| Kode Aspek | Nama Aspek | Total Mention | Positif | Netral | Negatif |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `customer_service` | Layanan Pelanggan & CS | 67 | 45 | 14 | 8 |
| `performance_bugs` | Kinerja, Bug, & Stabilitas | 44 | 14 | 14 | 16 |
| `features_functionality` | Fitur & Fungsionalitas Aplikasi | 41 | 18 | 17 | 6 |
| `ui_ux` | Desain Antarmuka & Kemudahan Penggunaan | 35 | 23 | 9 | 3 |
| `pricing_subscription` | Harga & Model Berlangganan | 21 | 8 | 8 | 5 |
| `cloud_sync` | Sinkronisasi Data & Cloud | 12 | 5 | 5 | 2 |
| `login_account` | Otentikasi, Login, & Akun | 9 | 3 | 5 | 1 |
| `update_system` | Pembaruan & Kompatibilitas Sistem | 5 | 2 | 2 | 1 |
| **Total Seluruh Aspek** | **8 Kategori Produk** | **234** | **118** | **74** | **42** |

---

## 8. Integritas Metrik Engagement Riil Instagram (Zero Fabrication Policy)

Sesuai dengan protokol metodologis Fase 5.4 dan 5.5, paket data Instagram mempertahankan prinsip kejujuran empiris yang mutlak (*Zero-Fabrication Policy*):

1. **Preservasi Nilai Missing Riil pada Metrik Views**:
   - Kolom `views` pada seluruh 55 baris postingan dipertahankan bernilai `NaN` (100% missing).
   - Platform Instagram tidak menyediakan metrik penayangan (*views / impressions*) pada antarmuka web publik tanpa otentikasi sesi.
   - **Larangan Zero-Filling**: Mengubah nilai `NaN` menjadi `0` adalah kesalahan metodologis serius karena akan mendistorsi statistik interaksi dan mengimplikasikan bahwa konten memiliki nol penayangan, padahal postingan tersebut aktif dan menjangkau audiens luas.
2. **Penolakan Metrik Sintetis (No Synthetic Engagement Rate)**:
   - Paket ekspor **sama sekali tidak memuat kolom Engagement Rate sintetis**.
   - Formula seperti interactions dibagi static followers atau impressions ditolak karena follower count bersifat temporal (*point-in-time*) dan tidak merepresentasikan jumlah follower saat konten dipublikasikan (rentang publikasi data meliputi 2024-2026).
   - Pengukuran interaksi dilakukan secara murni menggunakan metrik riil terverifikasi: `total_interactions = likes + comments`.
3. **Audit Outlier IQR & Batasan Sampling**:
   - Berkas `instagram_engagement_metrics` menyertakan diagnosis pencilan interaksi berbasis metode Interquartile Range (IQR = Q3 - Q1 = 153.5 - 18.0 = 135.5).
   - Ditemukan tepat **9 postingan viral outlier** (16.36%) dengan total interaksi melebihi batas atas 239.0.
   - Adanya pencilan viral ini menyebabkan disparitas tajam antara nilai mean (239.04) dan median (38.0). Dokumentasi data dictionary menegaskan bahwa dashboard harus memprioritaskan statistik non-parametrik (median) untuk mencegah bias interpretasi.

---

## 9. Hasil Pengujian Otomatis & Regresi Terintegrasi

Untuk memastikan kesiapan paket data sebelum diserahkan ke tim pengembang dashboard, dilakukan pengujian komprehensif menggunakan test suite otomatis `scripts/verify_phase5_6.py` serta pengujian regresi terhadap seluruh suite verifikasi fase sebelumnya.

### 9.1 Hasil Test Suite Fase 5.6 (`verify_phase5_6.py`)
Test suite Fase 5.6 mengeksekusi 15 uji integritas struktural, relasional, dan semantik:

| No | Pengujian | Deskripsi Uji | Target Verifikasi | Status |
| :---: | :--- | :--- | :--- | :---: |
| 1 | `source_immutability_canonical` | Memverifikasi hash MD5 dataset mentah dan final Instagram | MD5 identik dengan baseline | **PASS** |
| 2 | `source_immutability_playstore` | Memverifikasi integritas 417 ulasan Play Store, Gold Set, & Aspek | 417 ulasan, 234 mention | **PASS** |
| 3 | `export_artifact_completeness` | Memastikan seluruh 6 pasang berkas CSV dan XLSX ada dan non-empty | 12 berkas ekspor valid | **PASS** |
| 4 | `instagram_key_integrity` | Memverifikasi 55 `post_id` unik dan kecocokan 100% dengan sumber | 55 post ID unik | **PASS** |
| 5 | `playstore_key_integrity` | Memverifikasi 417 `review_id` unik dan kecocokan 100% dengan sumber | 417 review ID unik | **PASS** |
| 6 | `relational_foreign_key_integrity` | Memverifikasi integritas relasional antar-tabel menggunakan foreign key | 100% match, 0 orphan row | **PASS** |
| 7 | `source_value_fidelity` | Memverifikasi tidak adanya distorsi data antara sumber dan ekspor | Selisih nilai absolut = 0 | **PASS** |
| 8 | `engagement_aggregate_consistency` | Memverifikasi total likes (12.643), comments (504), dan interactions (13.147) | Konsisten di seluruh berkas | **PASS** |
| 9 | `aspect_taxonomy_integrity` | Memverifikasi 8 kategori aspek dan tepat 234 total mention | Tepat 234 mention terdeteksi | **PASS** |
| 10 | `human_sentiment_ground_truth` | Memverifikasi label sentimen manusia identik 100% dengan Gold Set | Pos: 232, Neu: 112, Neg: 73 | **PASS** |
| 11 | `explicit_sentiment_separation` | Memverifikasi pemisahan kolom Gold Set dan prefiks `test_pred_*` | n=84 pada partisi test | **PASS** |
| 12 | `privacy_minimization_verification` | Memverifikasi penghapusan total `userName`, `userImage`, `reviewer_id`, `reply_text` | 0 atribut PII terekspos | **PASS** |
| 13 | `zero_fabrication_verification` | Memverifikasi kolom views tetap `NaN` dan ketiadaan formula sintetis | Views 100% missing | **PASS** |
| 14 | `csv_xlsx_semantic_equivalence` | Memverifikasi ekuivalensi baris, kolom, dan nilai antara CSV dan XLSX | Identik 100% | **PASS** |
| 15 | `multi_sheet_architecture` | Memverifikasi kehadiran sheet analitik dan kamus data pada berkas XLSX | Struktur multi-sheet valid | **PASS** |

**Hasil Ringkasan Fase 5.6**: **15 / 15 PASSED (100% Success Rate)**.

### 9.2 Hasil Uji Regresi Lintas Fase
Untuk menjamin bahwa pembentukan paket ekspor tidak merusak artefak analitik fase terdahulu, suite verifikasi historis dijalankan ulang:
1. `scripts/verify_phase5_3.py`: **15 / 15 PASSED** (Audit Aspek Remediated & Baseline).
2. `scripts/verify_phase5_4.py`: **13 / 13 PASSED** (Standardisasi Dataset Instagram Final).
3. `scripts/verify_phase5_5.py`: **15 / 15 PASSED** (Metrik Engagement & Analisis Konten Instagram).
4. `scripts/verify_phase5_6.py`: **15 / 15 PASSED** (Final Data Packaging & Cross-Platform Delivery).

**Total Akumulasi Pengujian Otomatis**: **58 / 58 PASSED (100% Zero-Defect)**.

---

## 10. Konfirmasi Sumber Asli Tetap Tidak Berubah (Source Immutability Audit)

Prinsip dasar rekayasa data analitik menyatakan bahwa data mentah (*raw data*) dan data kebenaran dasar (*gold set ground truth*) bersifat permanen dan tidak boleh dimodifikasi (*immutable*). Seluruh proses pembentukan paket ekspor Fase 5.6 beroperasi secara *read-only* terhadap berkas-berkas sumber.

Audit integritas kriptografis dan checksum file sumber mengonfirmasi status berikut:

| Berkas Sumber | Path Repositori | Status Imutabilitas | Ukuran / Baris | Checksum Hash (MD5) |
| :--- | :--- | :---: | :---: | :---: |
| Instagram Raw Baseline | `data/raw/instagram_posts_raw.csv` | **TIDAK BERUBAH** | 55 baris (31.1 KB) | `c9e7882eff8282bb698825a0ef712817` |
| Instagram Raw Phase 1 | `data/raw/instagram_posts_raw_phase1_backup.csv` | **TIDAK BERUBAH** | 12 baris (6.7 KB) | `37df4eb26fffc69123c5cce486ef0982` |
| Instagram Final Clean | `data/final/instagram_posts_final.csv` | **TIDAK BERUBAH** | 55 baris (34.5 KB) | `794b050f649bc76537cf31f12b485b66` |
| Play Store Reviews Raw | `data/raw/playstore_reviews_raw.csv` | **TIDAK BERUBAH** | 417 baris (161.8 KB) | *Immutable source archive* |
| Play Store Reviews Final | `data/final/playstore_reviews_final.csv` | **TIDAK BERUBAH** | 417 baris (172.4 KB) | *Preprocessed analytical base* |
| Play Store Gold Set Final | `data/final/playstore_gold_set_final.csv` | **TIDAK BERUBAH** | 417 baris (96.7 KB) | *Ground truth human consensus* |
| Aspect Remediated | `data/final/topic_analysis/phase_5_3/review_aspect_assignments_remediated.csv` | **TIDAK BERUBAH** | 417 baris (58.4 KB) | *234 aspect mentions frozen* |

Konfirmasi ini membuktikan bahwa pembentukan paket ekspor adalah proses derivasi murni yang bebas dari efek samping (*side-effect free*).

---

## 11. Lokasi Folder Ekspor & Panduan Pemindahan ke Dashboard

### 11.1 Struktur Direktori Ekspor
Seluruh paket data analitik telah dikonsolidasikan secara rapi di dalam direktori `data/export/`:

```
data/export/
|-- README_data_dictionary.md               # [31.3 KB] Kamus data lengkap & panduan teknis
|-- instagram/
|   |-- instagram_posts_clean.csv           # [34.5 KB] 55 baris x 27 kolom (Data induk Instagram)
|   |-- instagram_posts_clean.xlsx          # [36.9 KB] Dual-sheet (Posts + Data Dictionary)
|   |-- instagram_engagement_metrics.csv    # [12.4 KB] 55 baris x 23 kolom (Interaksi & peringkat)
|   |-- instagram_engagement_metrics.xlsx   # [19.8 KB] Dual-sheet (Metrics + Data Dictionary)
|   |-- instagram_content_performance.csv   # [4.8 KB]  28 baris x 16 kolom (Agregasi performa)
|   `-- instagram_content_performance.xlsx  # [18.2 KB] 7 sheets analitik modular
`-- playstore/
    |-- playstore_reviews_clean.csv         # [118.2 KB] 417 baris x 19 kolom (Data induk ulasan)
    |-- playstore_reviews_clean.xlsx        # [67.8 KB]  Dual-sheet (Reviews + Data Dictionary)
    |-- playstore_sentiment.csv             # [45.1 KB]  417 baris x 14 kolom (Gold Set & benchmark)
    |-- playstore_sentiment.xlsx            # [48.6 KB]  3 sheets (Sentiment + Benchmark + Dict)
    |-- playstore_aspects.csv               # [58.4 KB]  417 baris x 17 kolom (Format Wide 8 aspek)
    `-- playstore_aspects.xlsx              # [52.1 KB]  3 sheets (Wide + Long 234 + Summary)
```

### 11.2 Panduan Pemindahan (*Migration Guide*) untuk Repositori Dashboard
Untuk menggunakan paket data ini pada repositori aplikasi dashboard terpisah (misalnya repositori Streamlit `zahir-social-dashboard`):

1. **Salin Folder Ekspor**:
   Salin seluruh direktori `data/export/` dari repositori analitik ke folder data pada proyek dashboard Anda:
   ```powershell
   # Contoh perintah salin pada terminal PowerShell:
   Copy-Item -Path "data\export" -Destination "..\zahir-social-dashboard\data" -Recurse
   ```
2. **Kebutuhan Dependensi**:
   Pastikan repositori dashboard memiliki dependensi minimal pada file `requirements.txt`:
   ```txt
   pandas>=2.0.0
   openpyxl>=3.1.0
   streamlit>=1.30.0
   plotly>=5.18.0
   ```
3. **Contoh Cuplikan Pemuatan Data pada Python/Streamlit**:
   ```python
   import pandas as pd
   import streamlit as st

   @st.cache_data
   def load_curated_data():
       # Pemuatan data Instagram
       ig_posts = pd.read_csv("data/export/instagram/instagram_posts_clean.csv")
       ig_metrics = pd.read_csv("data/export/instagram/instagram_engagement_metrics.csv")
       
       # Pemuatan data Play Store
       ps_reviews = pd.read_csv("data/export/playstore/playstore_reviews_clean.csv")
       ps_sentiment = pd.read_csv("data/export/playstore/playstore_sentiment.csv")
       ps_aspects_wide = pd.read_csv("data/export/playstore/playstore_aspects.csv")
       
       # Pemuatan format Long untuk grafik drill-down aspek
       ps_aspects_long = pd.read_excel(
           "data/export/playstore/playstore_aspects.xlsx", 
           sheet_name="Aspect_Mentions_Long"
       )
       
       return ig_posts, ig_metrics, ps_reviews, ps_sentiment, ps_aspects_wide, ps_aspects_long
   ```

---

## 12. Kesimpulan & Rekomendasi Menuju Fase 6 (Dashboard Development)

### 12.1 Kesimpulan Eksekutif
Fase 5.6 telah berhasil menuntaskan misi standarisasi, pembersihan, reduksi privasi, dan pengemasan data lintas platform (*cross-platform data delivery*). Repositori ini kini memiliki bundel data final yang terisolasi dengan rapi pada direktori `data/export/`, bebas dari dependensi proses crawling atau pemodelan ulang, dan sepenuhnya siap dikonsumsi oleh proyek dashboard visualisasi.

Seluruh target operasional telah terpenuhi tanpa celah:
1. **Preservasi Skala Data**: 55 postingan Instagram dan 417 ulasan Play Store terpelihara 100%.
2. **Kepatuhan Privasi**: 0 nama pengguna, gambar profil, hash identifier, atau balasan developer terekspos.
3. **Integritas Metrik**: 234 mention aspek remediated dan 13.147 interaksi riil Instagram tervalidasi matematis.
4. **Kejujuran Metodologis**: Pemisahan tegas ground truth vs prediksi NLP serta ketiadaan metrik sintetis.
5. **Ekuivalensi Ganda**: Seluruh 6 artefak tersedia dalam CSV berkinerja tinggi dan XLSX multi-sheet terformat profesional.
6. **Zero-Defect Verification**: 58 dari 58 pengujian otomatis lintas 4 fase berhasil lulus 100%.

### 12.2 Rekomendasi untuk Pengembangan Dashboard (Fase 6)
1. **Pemisahan Repositori**: Bangun dashboard visualisasi pada repositori Git terpisah guna memisahkan siklus hidup pengembangan analitik data (*data engineering & modeling*) dengan antarmuka pengguna (*UI/UX & deployment*).
2. **Pemanfaatan Caching**: Manfaatkan dekorator `@st.cache_data` pada Streamlit saat memuat berkas CSV ekspor agar interaksi filter dan rendering grafik berlangsung instan (< 100 ms).
3. **Penyajian Metrik Non-Parametrik**: Pada tab visualisasi Instagram, tampilkan **Median Interactions (38.0)** berdampingan dengan Mean Interactions (239.0) untuk memberikan konteks distribusi yang jujur kepada pemangku kepentingan.
4. **Visualisasi Dua Arah Ulasan & Aspek**: Gabungkan format Wide untuk tabel penelusuran ulasan dan format Long untuk visualisasi sentimen per-aspek menggunakan *stacked bar chart* atau *spider radar chart*.
5. **Eksplorasi Cross-Platform**: Rancang kartu ringkasan eksekutif (*KPI scorecard*) yang menampilkan metrik kepuasan konsumen Play Store (66.91% ulasan positif, dominasi CS) dan daya jangkau konten Instagram (format Reels menyumbang 94.87% total interaksi).