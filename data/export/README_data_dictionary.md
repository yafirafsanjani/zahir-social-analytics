# Data Dictionary & Cross-Platform Export Documentation
**Zahir Social Analytics — Final Data Delivery Package (Fase 5.6)**  
**Tanggal Rilis:** 02 November 2026  
**Status Paket:** `READY FOR DASHBOARD INTEGRATION`  
**Lokasi Direktori:** `data/export/`  
**Aturan Tata Kelola Data:** *Strict Privacy Minimization*, *Zero Synthetic Fabrication*, *Dual Format Parity (CSV & XLSX)*, *Relational Integrity Verified*.

---

## 1. Ikhtisar & Tujuan Paket Ekspor

Dokumen ini merupakan panduan resmi dan kamus data komprehensif untuk seluruh berkas dataset hasil pengolahan akhir dalam ekosistem **Zahir Social Analytics**. Paket data ini dirancang secara khusus untuk konsumsi langsung oleh aplikasi dashboard analitik interaktif (Fase 6) pada repositori terpisah tanpa memerlukan komputasi ulang model NLP (*Natural Language Processing*) maupun agregasi metrik engagement.

Paket ekspor ini menggabungkan dua domain data utama:
1. **Instagram Public Engagement (`data/export/instagram/`)**: Mengevaluasi performa 55 postingan publik akun resmi `@zahiraccounting`, mencakup perbandingan format konten, dampak kemitraan kolaborasi kreator, dinamika waktu publikasi, serta analisis teks caption dan tagar.
2. **Google Play Store Customer Voice (`data/export/playstore/`)**: Mengevaluasi 417 ulasan otentik pengguna pada 5 aplikasi mobile Zahir, mencakup label sentimen manusia teranotasi penuh (*Gold Set*), evaluasi benchmark model sentimen (IndoBERT vs InSet vs TF-IDF LR), serta penugasan multi-label pada 8 aspek produk Zahir hasil remediated audit Fase 5.3 (234 total mention).

---

## 2. Struktur Direktori Paket Ekspor

```text
data/export/
├── README_data_dictionary.md             <- Dokumen kamus data & arsitektur relasional ini
├── instagram/                            <- Paket analitik media sosial Instagram
│   ├── instagram_posts_clean.csv         <- Dataset utama 55 postingan (27 kolom)
│   ├── instagram_posts_clean.xlsx        <- Format Excel (+ Sheet Data Dictionary)
│   ├── instagram_engagement_metrics.csv  <- Metrik level postingan (rank, tier, IQR outlier)
│   ├── instagram_engagement_metrics.xlsx <- Format Excel (+ Sheet Data Dictionary)
│   ├── instagram_content_performance.csv <- Ringkasan performa terpadu komparatif (28 baris)
│   └── instagram_content_performance.xlsx<- Format Excel eksekutif (7 sheet analisis detail)
└── playstore/                            <- Paket Customer Voice Google Play Store
    ├── playstore_reviews_clean.csv       <- Dataset utama 417 ulasan bersih tanpa PII (19 kolom)
    ├── playstore_reviews_clean.xlsx      <- Format Excel (+ Sheet Data Dictionary)
    ├── playstore_sentiment.csv           <- Sentimen Gold Set 417 ulasan & benchmark model (14 kolom)
    ├── playstore_sentiment.xlsx          <- Format Excel (3 sheet: Full, Test Set, Benchmark Metrics)
    ├── playstore_aspects.csv             <- Multi-label 8 aspek remediated 417 ulasan (17 kolom)
    └── playstore_aspects.xlsx            <- Format Excel (3 sheet: Wide, Long 234 mentions, Summary)
```

---

## 3. Arsitektur Relasional & Kunci Penghubung (Join Keys)

Setiap entitas data dihubungkan secara ketat oleh kunci primer/asing (*primary/foreign key*) yang telah diverifikasi integritas referensialnya sebesar 100%:

```text
========================================================================================
DOMINAN INSTAGRAM (Foreign Key: post_id)
========================================================================================
[instagram_posts_clean] (55 baris)
       |
       |--- (1:1) ---> [instagram_engagement_metrics] (55 baris)
       |
       |--- (1:N) ---> [instagram_content_performance (Top & Bottom Showcase)] (20 baris)

========================================================================================
DOMINAN PLAY STORE (Foreign Key: review_id)
========================================================================================
[playstore_reviews_clean] (417 baris)
       |
       |--- (1:1) ---> [playstore_sentiment] (417 baris)
       |
       |--- (1:1) ---> [playstore_aspects (Wide)] (417 baris, 234 mentions)
       |
       |--- (1:N) ---> [playstore_aspects (Long)] (234 baris mention)
```

- **`post_id` (String)**: Shortcode unik postingan Instagram (misal: `DQnklphEi9f`). Berfungsi menghubungkan konten postingan dengan metrik interaksi dan peringkat.
- **`review_id` (String)**: UUID unik ulasan Google Play Store (misal: `cbffd87a-4fe7-4aff-8d44-600be5fbc540`). Berfungsi menghubungkan teks ulasan bersih dengan sentimen manusia dan penugasan aspek produk.

---

## 4. Kamus Data Paket Instagram (`data/export/instagram/`)

### 4.1 Berkas `instagram_posts_clean.csv` & `.xlsx`
- **Tujuan**: Dataset kanonikal postingan Instagram publik Zahir yang memuat metadata teks asli, teks bersih konservatif, dimensi waktu publikasi lokal (WIB), format media, metrik interaksi terverifikasi, dan informasi kolaborasi akun.
- **Jumlah Observasi**: 55 baris (0 duplikasi).
- **Jumlah Kolom**: 27 kolom.
- **Struktur Sheet Excel**:
  - Sheet 1: `Instagram Posts Clean` (55 baris)
  - Sheet 2: `Data Dictionary` (definisi lengkap seluruh kolom)

| No | Nama Kolom | Tipe Data | Nullable | Satuan / Format | Definisi Kolom & Catatan Metodologis |
| :---: | :--- | :---: | :---: | :---: | :--- |
| 1 | `post_id` | String | Tidak | Alfanumerik (Shortcode) | **Primary Key**. Identifier unik postingan Instagram dari URL shortcode. |
| 2 | `post_url` | String | Tidak | URL Valid | Tautan web publik permanen menuju postingan Instagram (`https://www.instagram.com/p/...`). |
| 3 | `source_url` | String | Tidak | URL Valid | Kanal asal penjelajahan publik (misal: feed profil atau tab reels). |
| 4 | `post_date_raw` | String | Tidak | ISO-8601 UTC | Timestamp asli keluaran platform Instagram (misal: `2026-08-06T04:22:58.000Z`). |
| 5 | `post_datetime_utc` | String | Tidak | YYYY-MM-DD HH:MM:SS+00:00 | Waktu publikasi terstandarisasi zona waktu UTC. |
| 6 | `post_datetime_wib` | String | Tidak | YYYY-MM-DD HH:MM:SS+07:00 | Waktu publikasi terstandarisasi Waktu Indonesia Barat (`Asia/Jakarta`). |
| 7 | `post_date` | String | Tidak | YYYY-MM-DD | Tanggal kalender publikasi lokal WIB. Terdapat 5 postingan yang tanggal lokalnya berbeda dari tanggal UTC akibat jam posting malam. |
| 8 | `post_year` | Integer | Tidak | Tahun (2024 - 2026) | Tahun rilis postingan. |
| 9 | `post_month` | Integer | Tidak | Bulan (1 - 12) | Bulan rilis postingan. |
| 10 | `post_day` | Integer | Tidak | Tanggal (1 - 31) | Hari dalam bulan publikasi. |
| 11 | `post_day_of_week` | String | Tidak | Nama Hari | Hari dalam seminggu (`Monday` s/d `Sunday`). |
| 12 | `post_hour_wib` | Integer | Tidak | Jam (0 - 23) | Jam publikasi dalam Waktu Indonesia Barat untuk evaluasi jadwal penayangan. |
| 13 | `content_type` | String | Tidak | Kategori Format | Format media: `video/reel` (44), `carousel` (8), `image` (3). |
| 14 | `caption` | String | Ya | Teks Bebas | Teks caption mentah asli sebagaimana diunggah kreator. |
| 15 | `caption_clean` | String | Ya | Teks Bebas | Teks caption hasil normalisasi NFKC, pembersihan URL eksternal, dan perapian whitespace tanpa menghilangkan emoji atau tanda baca. |
| 16 | `caption_length_raw` | Integer | Tidak | Karakter | Jumlah karakter teks caption mentah asli. |
| 17 | `caption_length_clean`| Integer | Tidak | Karakter | Jumlah karakter teks caption bersih. |
| 18 | `caption_word_count` | Integer | Tidak | Kata | Jumlah kata dalam teks caption bersih (whitespace split). |
| 19 | `hashtags` | String | Ya | String Berpagar | Daftar tagar dipisahkan spasi. Bernilai `NaN` pada 16 postingan tanpa tagar. |
| 20 | `hashtag_count` | Integer | Tidak | Cacah Tagar | Jumlah tagar (#) yang digunakan (rentang 0 s/d 16). |
| 21 | `has_hashtags` | Boolean | Tidak | True / False | Flag indikator keberadaan tagar (`True` jika `hashtag_count > 0`). |
| 22 | `likes` | Integer | Tidak | Cacah Likes | Jumlah suka riil pengguna publik (Rentang: 1 s/d 3.191; Total: 12.643). |
| 23 | `comments` | Integer | Tidak | Cacah Komentar | Jumlah komentar publik riil (Rentang: 0 s/d 306; Total: 504). |
| 24 | `views` | Float | **Ya (100%)** | NaN | Metrik penayangan video. **Strictly NaN** (tidak terekspos di web publik unauthenticated, dilarang dispekulasi nol). |
| 25 | `total_interactions`| Integer | Tidak | Cacah Interaksi | Rumus: $\text{likes} + \text{comments}$. Rentang: 1 s/d 3.217; Total: 13.147. |
| 26 | `is_collaboration` | Boolean | Tidak | True / False | Status kemitraan: `True` untuk postingan kolaborasi co-author, `False` untuk postingan internal. |
| 27 | `original_account` | String | Tidak | Username | Akun inisiator/mitra postingan (`zahiraccounting`, `pecahtelur.id`, `muhamad.is`, dll). |

---

### 4.2 Berkas `instagram_engagement_metrics.csv` & `.xlsx`
- **Tujuan**: Dataset metrik keterlibatan terstruktur per postingan untuk visualisasi ranking, persentil, dan segmentasi performa konten.
- **Jumlah Observasi**: 55 baris (0 duplikasi).
- **Jumlah Kolom**: 23 kolom.
- **Kunci Relasi**: `post_id` menghubungkan berkas ini ke `instagram_posts_clean.csv`.
- **Kolom Utama & Turunan**:
  - `interaction_rank` (Integer): Peringkat postingan berdasarkan `total_interactions` tertinggi (Rank 1 s/d 55).
  - `percentile_rank` (Float): Peringkat persentil keterlibatan dalam populasi 55 postingan ($0.00\%$ s/d $100.00\%$).
  - `is_interaction_outlier` (Boolean): Flag pencilan menggunakan aturan Tukey IQR:
    $$\text{Ambang Outlier} = Q3 + 1.5 \times IQR = 110.0 + 1.5 \times 86.0 = 239.0$$
    Bernilai `True` pada 9 postingan viral ($16.36\%$).
  - `interaction_tier` (String): Segmentasi tingkat interaksi bisnis:
    1. `Viral Outlier (>239)`: 9 postingan ($16.36\%$, akumulasi $10.601$ interaksi).
    2. `High (110-239)`: 5 postingan ($9.09\%$, akumulasi $789$ interaksi).
    3. `Moderate (24-109)`: 27 postingan ($49.09\%$, akumulasi $1.523$ interaksi).
    4. `Low (<24)`: 14 postingan ($25.45\%$, akumulasi $234$ interaksi).
  - `time_bin` (String): Klasifikasi segmen jam tayang bisnis lokal:
    - `Morning (06:00-11:59)`
    - `Afternoon (12:00-14:59)`
    - `Late Afternoon (15:00-17:59)`
    - `Evening/Night (18:00-23:59)`

---

### 4.3 Berkas `instagram_content_performance.csv` & `.xlsx`
- **Tujuan**: Agregasi performa komparatif multi-dimensi untuk penyajian kartu metrik KPI dan grafik visualisasi dashboard eksekutif.
- **Jumlah Baris (CSV)**: 28 baris ringkasan terpadu.
- **Jumlah Kolom (CSV)**: 16 kolom.
- **Struktur Sheet Excel (7 Sheets Komprehensif)**:
  - Sheet 1: `Performance Overview` (Tabel ikhtisar terpadu seluruh 28 segmen)
  - Sheet 2: `Content Type Breakdown` (Evaluasi Video/Reel vs Carousel vs Image)
  - Sheet 3: `Collaboration Breakdown` (Evaluasi Organik vs Kolaborasi & per akun mitra)
  - Sheet 4: `Posting Time Breakdown` (Evaluasi hari, segmen jam WIB, dan tahun)
  - Sheet 5: `Caption & Hashtags` (Uji korelasi Pearson/Spearman dan dekonstruksi tagar)
  - Sheet 6: `Engagement Distribution` (Statistik deskriptif Likes, Comments, Total Interactions)
  - Sheet 7: `Top & Bottom Showcase` (Detail 10 postingan terbaik dan 10 postingan terendah)

| No | Nama Kolom (CSV) | Tipe Data | Definisi & Contoh Nilai |
| :---: | :--- | :---: | :--- |
| 1 | `analysis_dimension` | String | Dimensi evaluasi: `Content Type`, `Overall Baseline`, `Collaboration Status`, `Partner Accounts`, `Day of Week`, `Time of Day Bin`, `Publication Year`, `Hashtag Presence`. |
| 2 | `segment` | String | Label sub-kategori spesifik (misal: `video/reel`, `carousel`, `@pecahtelur.id`, `Morning (06:00-11:59)`, dll). |
| 3 | `post_count` | Integer | Jumlah postingan dalam segmen tersebut. |
| 4 | `post_share_pct` | Float | Persentase jumlah postingan terhadap total 55 postingan. |
| 5 | `total_likes` | Integer | Akumulasi likes pada segmen terkait. |
| 6 | `mean_likes` | Float | Rata-rata likes per postingan. |
| 7 | `median_likes` | Float | Nilai tengah likes per postingan. |
| 8 | `total_comments` | Integer | Akumulasi komentar pada segmen terkait. |
| 9 | `mean_comments` | Float | Rata-rata komentar per postingan. |
| 10 | `median_comments` | Float | Nilai tengah komentar per postingan (kunci analisis rasio percakapan Carousel). |
| 11 | `total_interactions`| Integer | Akumulasi total interaksi (`likes + comments`). |
| 12 | `mean_interactions` | Float | Rata-rata total interaksi per postingan. |
| 13 | `median_interactions`| Float | Nilai tengah total interaksi per postingan (indikator performa paling stabil). |
| 14 | `min_interactions` | Integer | Nilai interaksi terendah dalam segmen. |
| 15 | `max_interactions` | Integer | Nilai interaksi tertinggi dalam segmen. |
| 16 | `notes` | String | Catatan metodologis kontekstual (misal: peringatan Simpson's Paradox atau ukuran sampel). |

---

## 5. Kamus Data Paket Play Store (`data/export/playstore/`)

### 5.1 Berkas `playstore_reviews_clean.csv` & `.xlsx`
- **Tujuan**: Dataset utama ulasan pengguna pada 5 aplikasi mobile resmi ekosistem Zahir yang telah melalui standardisasi teks, penyesuaian zona waktu, dan **reduksi privasi ketat**.
- **Jumlah Observasi**: 417 ulasan otentik (0 duplikasi).
- **Jumlah Kolom**: 19 kolom.
- **Kebijakan Privasi Ketat (*Strict Privacy Minimization*)**:
  - Kolom pengenal pribadi pengguna `userName` dan URL avatar `userImage` **sama sekali tidak disertakan**.
  - Kolom penyamaran internal `reviewer_id` dan teks tanggapan developer `reply_text` **dieliminasi dari paket bersih** untuk menjamin dataset bebas dari potensi paparan data pribadi serta memfokuskan analisis murni pada suara konsumen (*voice of customer*).
  - Metrik efisiensi tanggapan developer tetap tersedia secara agregatif melalui flag boolean `has_developer_reply` dan durasi waktu respon `response_time_days`.

| No | Nama Kolom | Tipe Data | Nullable | Satuan / Format | Definisi Kolom & Catatan Metodologis |
| :---: | :--- | :---: | :---: | :---: | :--- |
| 1 | `review_id` | String | Tidak | UUID v4 | **Primary Key**. Identifier unik ulasan Google Play Store (misal: `cbffd87a-4fe7-4aff-8d44-600be5fbc540`). |
| 2 | `app_name` | String | Tidak | Nama Produk | Nama resmi aplikasi Zahir: `Zahir Simple Start` (160), `Zahir Online` (98), `POS X` (87), `Zahir Certification` (44), `Zahir Attendance` (28). |
| 3 | `package_name` | String | Tidak | Reverse Domain | Package Android resmi (misal: `com.zahironline`, `com.zahirsimplestart`, `com.posx`). |
| 4 | `review_datetime` | String | Tidak | ISO-8601 | Waktu ulasan dikirimkan pengguna (`YYYY-MM-DD HH:MM:SS`). Rentang: 2018-01-26 s/d 2026-09-11. |
| 5 | `review_date` | String | Tidak | YYYY-MM-DD | Tanggal kalender ulasan dikirimkan. |
| 6 | `review_year` | Integer | Tidak | Tahun (2018 - 2026) | Tahun ulasan dikirimkan. |
| 7 | `review_month` | Integer | Tidak | Bulan (1 - 12) | Bulan kalender ulasan dikirimkan. |
| 8 | `score` | Integer | Tidak | Skala Likert 1-5 | Rating bintang ulasan (Bintang 1: 74, Bintang 2: 27, Bintang 3: 37, Bintang 4: 31, Bintang 5: 248; Rata-rata: 3.84, Median: 5.00). |
| 9 | `rating_category` | String | Tidak | Kategori Rating | Klasifikasi pendukung rating: `critical` (skor 1-2, n=101 [24.22%]), `neutral` (skor 3, n=37 [8.87%]), `positive` (skor 4-5, n=279 [66.91%]). |
| 10 | `thumbs_up_count` | Integer | Tidak | Cacah Upvote | Jumlah pengguna lain yang menilai ulasan ini bermanfaat (Rentang: 0 s/d 40 upvotes). |
| 11 | `review_text` | String | Tidak | Teks Bebas | Teks asli ulasan pengguna tanpa modifikasi. |
| 12 | `review_text_clean` | String | Tidak | Teks Bebas | Teks ulasan setelah pembersihan URL, normalisasi karakter non-printable, dan perapian whitespace (tetap mempertahankan emoji, tanda baca ekspresif, dan kata negasi). |
| 13 | `text_length_chars` | Integer | Tidak | Karakter | Panjang karakter teks ulasan bersih (Rentang: 2 s/d 612 karakter; Rata-rata: 73.6 karakter). |
| 14 | `word_count` | Integer | Tidak | Kata | Jumlah kata dalam teks ulasan bersih (Rentang: 1 s/d 97 kata; Median: 8 kata). |
| 15 | `review_created_version`| String | Ya (25.18%) | String Versi | Versi build aplikasi saat ulasan dibuat (null pada 105 ulasan versi lama/tidak tercatat). |
| 16 | `app_version` | String | Ya (25.18%) | String Versi | Versi aplikasi aktif saat pengguna mengulas (identik kelengkapannya dengan `review_created_version`). |
| 17 | `has_developer_reply` | Boolean | Tidak | True / False | Status tanggapan developer (`True` pada 366 ulasan [87.77%], `False` pada 51 ulasan [12.23%]). Responsivitas Zahir CS sangat tinggi. |
| 18 | `replied_datetime` | String | Ya (12.23%) | ISO-8601 | Timestamp saat tim developer/CS Zahir memberikan tanggapan (null jika belum dibalas). |
| 19 | `response_time_days` | Float | Ya (12.23%) | Hari | Selisih waktu respon developer: $(\text{replied\_datetime} - \text{review\_datetime}) / 86400$. Ditemukan 15 kasus sah nilai negatif di mana pengguna mengedit ulasan setelah dibalas developer. |

---

### 5.2 Berkas `playstore_sentiment.csv` & `.xlsx`
- **Tujuan**: Dataset pelabelan sentimen ulasan Google Play Store yang membedakan secara tegas dan transparan antara **Ground Truth Anotasi Manusia (*Gold Set*)** dengan **Prediksi Model NLP Benchmark** (IndoBERT, InSet Lexicon, dan TF-IDF Logistic Regression).
- **Jumlah Observasi**: 417 ulasan (0 duplikasi).
- **Jumlah Kolom**: 14 kolom.
- **Kunci Relasi**: `review_id` menghubungkan berkas ini ke `playstore_reviews_clean.csv`.
- **Struktur Sheet Excel**:
  - Sheet 1: `Sentiment Full Dataset` (417 ulasan dengan pemisahan eksplisit label manusia vs model)
  - Sheet 2: `Benchmark Test Predictions` (84 ulasan subset pengujian evaluasi model)
  - Sheet 3: `Benchmark Metrics Summary` (Tabel metrik performa komparatif Macro F1, Akurasi, Presisi, Recall)

| No | Nama Kolom | Tipe Data | Nullable | Nilai Valid | Definisi & Penjelasan Metodologis |
| :---: | :--- | :---: | :---: | :---: | :--- |
| 1 | `review_id` | String | Tidak | UUID v4 | **Primary Key / Foreign Key**. Menghubungkan ulasan ke dataset utama ulasan bersih. |
| 2 | `app_name` | String | Tidak | Nama Produk | Nama aplikasi ekosistem Zahir. |
| 3 | `review_date` | String | Tidak | YYYY-MM-DD | Tanggal pengiriman ulasan. |
| 4 | `score` | Integer | Tidak | 1 - 5 | Rating bintang ulasan. |
| 5 | `rating_category` | String | Tidak | critical, neutral, positive | Kategori pendukung rating. |
| 6 | `human_sentiment_label` | String | Tidak | positive, neutral, negative | **Ground Truth Resmi (Gold Set 417 Ulasan)**: Teranotasi manual oleh manusia dan divalidasi penuh pada Fase 4.2. Distribusi: Positif = 232 ($55.64\%$), Netral = 112 ($26.86\%$), Negatif = 73 ($17.51\%$). |
| 7 | `sentiment_label_source` | String | Tidak | `"gold_set_human_annotated"` | Sumber asal label sentimen. Bernilai konstan untuk menjamin integritas provenance data. |
| 8 | `benchmark_split` | String | Tidak | `development`, `test` | Pembagian partisi data benchmark Fase 4.3: `development` ($n=333$, $79.86\%$) dan `test` ($n=84$, $20.14\%$). |
| 9 | `test_pred_indobert` | String | Ya (79.86%) | positive, neutral, negative | **Prediksi Model IndoBERT** pada partisi Test Set ($n=84$). Bernilai `NaN` pada partisi Development. |
| 10 | `test_indobert_confidence` | Float | Ya (79.86%) | 0.0000 - 1.0000 | Skor probabilitas keyakinan model IndoBERT ($n=84$). |
| 11 | `test_pred_inset_lexicon` | String | Ya (79.86%) | positive, neutral, negative | Prediksi leksikon berbasis aturan kamus bahasa Indonesia InSet ($n=84$). |
| 12 | `test_inset_score` | Float | Ya (79.86%) | Nilai Kontinu | Skor polaritas leksikon InSet ($n=84$). |
| 13 | `test_pred_tfidf_lr` | String | Ya (79.86%) | positive, neutral, negative | Prediksi model machine learning baseline TF-IDF Logistic Regression ($n=84$). |
| 14 | `test_tfidf_lr_confidence` | Float | Ya (79.86%) | 0.0000 - 1.0000 | Skor probabilitas keyakinan model TF-IDF Logistic Regression ($n=84$). |

#### Catatan Hasil Benchmark Sentimen (Fase 4.3):
Pada data uji 84 ulasan (*test split*), IndoBERT (`indobenchmark/indobert-base-p1`) membuktikan keunggulan tertinggi dengan **Macro F1-Score: 0.7303** dan **Akurasi: 80.95%**, mengungguli TF-IDF Logistic Regression (Macro F1: 0.5838), Leksikon InSet (Macro F1: 0.5513), dan Majority Class Baseline (Macro F1: 0.2447).

---

### 5.3 Berkas `playstore_aspects.csv` & `.xlsx`
- **Tujuan**: Dataset penugasan multi-label pada 8 aspek operasional produk Zahir hasil remediated keyword-matching Fase 5.3 yang telah diverifikasi dan diaudit kualitasnya terhadap 30 sampel manual anotator manusia.
- **Jumlah Observasi (CSV / Sheet Wide)**: 417 ulasan (0 duplikasi).
- **Jumlah Mention Aspek Terdeteksi**: Tepat **234 mention aspek** (174 ulasan memuat $\ge 1$ mention aspek, 243 ulasan tidak memuat aspek spesifik).
- **Kunci Relasi**: `review_id` menghubungkan berkas ini ke `playstore_reviews_clean.csv`.
- **Struktur Sheet Excel**:
  - Sheet 1: `Aspect Reviews (Wide)` (417 ulasan, format kolom multi-label boolean)
  - Sheet 2: `Aspect Mentions (Long)` (Tepat 234 baris, satu baris per kejadian aspek terdeteksi)
  - Sheet 3: `Aspect Summary (8 Aspects)` (Tabel rekapitulasi frekuensi, sentimen, dan rasio kritis per aspek)

| No | Nama Kolom (Wide) | Tipe Data | Definisi & Nilai Valid |
| :---: | :--- | :---: | :--- |
| 1 | `review_id` | String | **Primary Key / Foreign Key**. Menghubungkan aspek ke ulasan ulasan bersih. |
| 2 | `app_name` | String | Nama aplikasi mobile Zahir. |
| 3 | `review_datetime` | String | Waktu ulasan dikirimkan. |
| 4 | `human_sentiment_label` | String | Label sentimen manusia Gold Set (`positive`, `neutral`, `negative`). |
| 5 | `review_text_clean` | String | Teks ulasan bersih yang menjadi objek ekstraksi aspek. |
| 6 | `aspect_login_auth` | Boolean | `True` jika ulasan mengangkat isu login, OTP, aktivasi akun, atau lupa sandi (38 ulasan). |
| 7 | `aspect_crash_stability` | Boolean | `True` jika ulasan mengangkat isu aplikasi force close, layar putih, lag, atau bug (38 ulasan). |
| 8 | `aspect_pricing_subscription`| Boolean | `True` jika ulasan mengangkat isu biaya langganan, masa trial, bayar, atau harga (34 ulasan). |
| 9 | `aspect_sync_cloud_data` | Boolean | `True` jika ulasan mengangkat isu sinkronisasi database, jaringan, atau backup (15 ulasan). |
| 10 | `aspect_pos_hardware_print` | Boolean | `True` jika ulasan mengangkat isu mesin kasir POS, koneksi printer bluetooth, atau struk (20 ulasan). |
| 11 | `aspect_inventory_accounting`| Boolean | `True` jika ulasan mengangkat isu jurnal, stok barang, pembukuan, invoice, atau laporan keuangan (71 ulasan). |
| 12 | `aspect_certification_exam` | Boolean | `True` jika ulasan mengangkat isu ujian sertifikasi, soal, ujian online, atau modul (11 ulasan). |
| 13 | `aspect_attendance_face` | Boolean | `True` jika ulasan mengangkat isu absen mobile, deteksi wajah, kamera, atau GPS lokasi (7 ulasan). |
| 14 | `detected_aspects` | String | Daftar nama aspek terdeteksi dipisahkan koma (misal: `"inventory_accounting, crash_stability"` atau `"none"`). |
| 15 | `aspect_count` | Integer | Jumlah aspek terdeteksi pada ulasan terkait (Rentang: 0 s/d 4). **Total akumulasi seluruh baris = 234**. |
| 16 | `has_aspect` | Boolean | `True` jika ulasan memuat minimal 1 mention aspek (`aspect_count > 0`, n=174), `False` jika tidak memuat aspek spesifik (n=243). |
| 17 | `matched_keywords` | String | Bukti diagnostik kata kunci / pola regex yang memicu penugasan aspek (misal: `"beli [pricing_subscription]"`). |

---

## 6. Taksonomi & Definisi 8 Aspek Produk Zahir (Fase 5.3)

Taksonomi aspek produk Zahir dirumuskan secara terstandarisasi untuk memetakan Customer Voice ke dalam komponen bisnis dan rekayasa perangkat lunak:

| No | Identifier Aspek | Nama Aspek Resmi | Komponen Produk yang Dicakup | Total Mentions | Pangsa Mention (%) | Proporsi Kritis (%) | Contoh Kata Kunci Pemicu |
| :---: | :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| 1 | `inventory_accounting` | Fitur Akuntansi, Laporan & Inventori | Laporan laba/rugi, jurnal umum, neraca, manajemen persediaan/stok, pembuatan faktur, dan modul pembukuan utama Zahir. | **71** | 30,34% | 35,21% | *akuntansi, laporan, pembukuan, stok, faktur, neraca, jurnal* |
| 2 | `login_auth` | Login, Otentikasi & Akses Akun | Alur registrasi pengguna, otentikasi login, pengiriman kode OTP, verifikasi email, session timeout, dan reset password. | **38** | 16,24% | 84,21% | *login, masuk, otp, verifikasi, password, akun, daftar* |
| 3 | `crash_stability` | Stabilitas Aplikasi, Bug & Crash | Kinerja aplikasi, kejadian force close, aplikasi terhenti tiba-tiba, layar putih (*blank screen*), kelambatan (*lag/loading lama*), dan error sistem. | **38** | 16,24% | 89,47% | *crash, keluar sendiri, force close, error, bug, lambat, lag, macet* |
| 4 | `pricing_subscription` | Harga, Langganan & Lisensi | Model monetisasi, tarif langganan bulanan/tahunan, batasan masa uji coba (*trial expired*), aktivasi lisensi software, dan biaya fitur berbayar. | **34** | 14,53% | 82,35% | *bayar, langganan, biaya, harga, mahal, trial, lisensi, beli* |
| 5 | `pos_hardware_print` | POS, Kasir & Integrasi Hardware Printer | Operasional kasir Point-of-Sale (POS X), koneksi printer kasir bluetooth/thermal, cetak nota/struk belanja, dan transaksi ritel. | **20** | 8,55% | 75,00% | *kasir, pos, print, cetak, printer, struk, nota, bluetooth* |
| 6 | `sync_cloud_data` | Sinkronisasi Cloud & Integritas Data | Alur sinkronisasi data transaksi lokal ke database cloud Zahir Online, konektivitas server, pemulihan data (*restore/backup*), dan kehilangan data. | **15** | 6,41% | 86,67% | *sinkron, sync, cloud, server, koneksi, hilang data, backup* |
| 7 | `certification_exam` | Sertifikasi & Ujian Online Zahir | Fitur ujian sertifikasi kompetensi akuntansi Zahir Certification, ketersediaan soal ujian, waktu tes, dan penerbitan sertifikat digital. | **11** | 4,70% | 81,82% | *sertifikasi, ujian, soal, tes, exam, nilai, sertifikat* |
| 8 | `attendance_face` | Presensi & Deteksi Wajah (Attendance) | Fitur absensi mobile karyawan Zahir Attendance, verifikasi foto/wajah (*facial recognition*), tagging GPS lokasi, dan check-in/check-out presensi. | **7** | 2,99% | 85,71% | *absen, attendance, wajah, face, presensi, kamera, gps, foto* |
| - | **Total Akumulasi** | **8 Aspek Operasional Produk Zahir** | **Representasi 417 Ulasan Olahan (Fase 5.3 Remediated)** | **234** | **100,00%** | **63,68%** | *16 Aturan Perbaikan Remediasi Kata Kunci Aktif* |

---

## 7. Kebijakan & Penanganan Nilai Kosong (Missing Values Policy)

Setiap nilai kosong (*null / NaN*) dalam dataset ekspor memiliki justifikasi metodologis yang terdefinisi secara ketat:

1. **Instagram `views` (100% NaN)**:
   - Sesuai kebijakan tata kelola platform Instagram, metrik view count/impresi tidak dipublikasikan pada web umum tanpa otentikasi.
   - Nilai ini **secara ketat tidak diisi angka nol**, karena ketiadaan metrik publik bukan berarti tayangannya nol.
2. **Instagram `hashtags` (16 baris NaN, 29.09%)**:
   - Menunjukkan fakta riil bahwa pembuat konten tidak menyertakan tagar pada caption aslinya. Diikuti dengan `hashtag_count = 0` dan `has_hashtags = False`.
3. **Play Store Versi Aplikasi (`review_created_version` & `app_version`, 105 baris NaN, 25.18%)**:
   - Terjadi secara sah pada ulasan pengguna awal (khususnya tahun 2018-2019) di mana Google Play Store tidak mencatat metadata build versi aplikasi.
4. **Play Store Tanggapan Developer (`replied_datetime` & `response_time_days`, 51 baris NaN, 12.23%)**:
   - Menunjukkan ulasan yang hingga saat pengambilan data memang belum/tidak dibalas oleh tim customer support developer (`has_developer_reply = False`).
5. **Play Store Prediksi Benchmark (`test_pred_*`, 333 baris NaN, 79.86%)**:
   - Sesuai kaidah sains data yang jujur, prediksi model NLP hanya tersedia pada 84 ulasan subset pengujian (*test set*). Ulasan pada partisi pengembangan (*development set*) sengaja dibiarkan bernilai `NaN` untuk mencegah kebocoran data (*data leakage*).

---

## 8. Keterbatasan Metodologis & Batasan Analisis

Untuk memastikan interpretasi dashboard yang kredibel dan objektif, analis harus memahami batasan berikut:

### 8.1 Keterbatasan Sampling Data Instagram:
- **Baseline Publik Terkunci (55 Postingan)**: Dataset mencakup 55 postingan publik yang diperoleh secara sah tanpa login. Penjelajahan publik dibatasi oleh platform Instagram (feed grid terkunci setelah 12 item dan reels infinite-scroll terkunci setelah batch ke-8).
- **Asimetri Format Media**: Format konten sangat didominasi oleh `video/reel` ($80.0\%$, $n=44$) dibandingkan `carousel` ($14.5\%$, $n=8$) dan `image` ($5.5\%$, $n=3$). Evaluasi format gambar tunggal harus dipahami sebagai performa 3 materi pengumuman flyer tertentu, bukan kesimpulan populasi global.
- **Sifat Observasional Non-Kausal**: Kenaikan interaksi pada konten kolaborasi atau postingan jam pagi dipengaruhi oleh variabel perancu (*confounders*), seperti basis followers mitra `@pecahtelur.id` dan format video wawancara, bukan akibat deterministik penambahan label kolaborasi atau jam tayang semata.

### 8.2 Keterbatasan Metrik Social Engagement:
- **Zero-Fabrication Policy**: Dashboard dilarang keras mengarang metrik pembagi sintetis seperti *Engagement Rate by Followers* atau *Engagement Rate by Impressions*.
- Seluruh evaluasi keterlibatan diukur menggunakan metrik riil absolut yang terverifikasi: $\text{total\_interactions} = \text{likes} + \text{comments}$.

---

## 9. Panduan Memuat Data pada Dashboard (Quick Start Guide)

Berikut adalah contoh snippet Python / Pandas untuk memuat dan menggabungkan dataset ekspor ke dalam aplikasi dashboard:

```python
import pandas as pd

# 1. Memuat Dataset Media Sosial Instagram
df_ig_posts = pd.read_csv("data/export/instagram/instagram_posts_clean.csv")
df_ig_metrics = pd.read_csv("data/export/instagram/instagram_engagement_metrics.csv")
df_ig_perf = pd.read_csv("data/export/instagram/instagram_content_performance.csv")

# Menggabungkan Konten & Metrik Instagram (1:1 via post_id)
df_ig_full = df_ig_posts.merge(
    df_ig_metrics[["post_id", "interaction_rank", "interaction_tier", "is_interaction_outlier", "time_bin"]],
    on="post_id",
    how="left"
)

# 2. Memuat Dataset Customer Voice Play Store
df_ps_reviews = pd.read_csv("data/export/playstore/playstore_reviews_clean.csv")
df_ps_sentiment = pd.read_csv("data/export/playstore/playstore_sentiment.csv")
df_ps_aspects = pd.read_csv("data/export/playstore/playstore_aspects.csv")

# Menggabungkan Ulasan, Sentimen Gold Set, dan Aspek Produk (1:1 via review_id)
df_ps_full = df_ps_reviews.merge(
    df_ps_sentiment[["review_id", "human_sentiment_label", "sentiment_label_source", "benchmark_split"]],
    on="review_id",
    how="left"
).merge(
    df_ps_aspects[["review_id", "detected_aspects", "aspect_count", "has_aspect", "aspect_login_auth",
                   "aspect_crash_stability", "aspect_pricing_subscription", "aspect_sync_cloud_data",
                   "aspect_pos_hardware_print", "aspect_inventory_accounting", "aspect_certification_exam",
                   "aspect_attendance_face"]],
    on="review_id",
    how="left"
)

print(f"✅ Instagram siap: {df_ig_full.shape[0]} postingan.")
print(f"✅ Play Store siap: {df_ps_full.shape[0]} ulasan terintegrasi.")
```