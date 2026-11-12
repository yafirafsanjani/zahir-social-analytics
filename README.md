# Zahir Social Analytics

**Zahir Social Analytics** adalah repositori riset dan rekayasa data analitik untuk mempelajari interaksi media sosial serta suara pelanggan (*customer voice*) pada ekosistem PT Zahir Internasional. Proyek ini menggabungkan analisis dua kanal publik:
1. **Google Play Store**: Ulasan pelanggan, rating kepuasan, pola responsivitas pengembang, benchmarking pemodelan sentimen NLP, dan ekstraksi taksonomi aspek berbasis aturan (*rule-based aspect taxonomy*).
2. **Instagram (@zahiraccounting)**: Pola interaksi publik (*likes* dan *comments*), performa jenis konten, efektivitas kolaborasi, dinamika temporal publikasi, serta analisis teks takarir (*caption*) dan tagar (*hashtags*).

Proyek ini ditujukan untuk dokumentasi akademik, portofolio Data Science, dan dasar pengambilan keputusan berbasis data. Aplikasi *dashboard* interaktif dikembangkan pada repositori terpisah dan tidak tercakup dalam repositori analitik inti ini.

---

## Struktur Repositori Terkonsolidasi

Repositori telah direfaktor secara menyeluruh menjadi struktur yang bersih dan modular:

```text
zahir-social-analytics/
├── notebooks/                      # 8 Jupyter Notebook kanonikal mandiri
│   ├── 01_data_acquisition.ipynb
│   ├── 02_playstore_preprocessing_eda.ipynb
│   ├── 03_playstore_goldset.ipynb
│   ├── 04_sentiment_benchmark.ipynb
│   ├── 05_aspect_analysis.ipynb
│   ├── 06_instagram_preprocessing.ipynb
│   ├── 07_instagram_engagement_analysis.ipynb
│   └── 08_dataset_validation_export.ipynb
├── data/
│   ├── raw/                        # Sumber data mentah lokal terlindungi (diabaikan Git)
│   ├── final/                      # Dataset hasil pemrosesan dan anotasi lokal (diabaikan Git)
│   └── export/                     # Paket master kanonikal, kamus data, dan inventaris ekspor
├── outputs/
│   ├── figures/                    # 9 visualisasi grafis profesional (High DPI)
│   └── reports/                    # Laporan audit, staging, dan runner pengujian otomatis
├── docs/                           # Dokumentasi metodologi, panduan anotasi, dan laporan fase
├── archive/
│   └── legacy_code/                # Seluruh kode dan notebook historis yang diarsipkan
│       ├── notebooks/              # Notebook lama yang telah digantikan
│       ├── analysis/               # Script analitik historis
│       ├── preprocessing/          # Script preprocessing historis
│       ├── scraper/                # Script scraper historis
│       ├── scripts/                # Suite verifikasi dan audit fase sebelumnya
│       ├── config/                 # Konfigurasi JSON taksonomi awal
│       └── tools/                  # Script generator transisi
├── requirements.txt                # Konfigurasi dependensi Python
├── .gitignore                      # Aturan proteksi Git untuk data lokal dan virtual environment
└── AGENTS.md                       # Jurnal teknis log aktivitas pengembangan
```

---

## Persyaratan Environment & Instalasi

Proyek ini dibangun dan diuji menggunakan **Python 3.11.9**.

### 1. Menyiapkan Virtual Environment
Gunakan virtual environment terisolasi (`.venv_social` atau `.venv`):

```powershell
# Menggunakan virtual environment baru pada Windows PowerShell
py -3.11 -m venv .venv_social
.\.venv_social\Scripts\Activate.ps1

# Instalasi seluruh pustaka yang dipersyaratkan
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 2. Membuka Jupyter Lab / Notebook
```powershell
jupyter lab
```
Pastikan kernel yang dipilih di Jupyter Lab mengarah ke interpreter Python virtual environment proyek.

---

## Urutan & Alur Eksekusi Notebook

Seluruh alur pemrosesan data dan analisis utama dapat dijalankan secara mandiri melalui 8 notebook utama di dalam direktori `notebooks/`. Setiap notebook beroperasi dalam mode aman *read-only* secara default tanpa menimpa data kanonikal:

| No | Notebook | Tujuan & Input Utama | Logika Pemrosesan | Output Utama |
|---|---|---|---|---|
| **01** | `01_data_acquisition.ipynb` | Akuisisi data publik Instagram & Play Store.<br>Input: `data/raw/` | Implementasi scraper (Playwright/BS4 & Google Play Scraper) dengan sakelar offline `RUN_SCRAPER = False`. Validasi integritas baseline. | Profil dataset mentah, verifikasi SHA-256, figure `raw_data_profile.png`. |
| **02** | `02_playstore_preprocessing_eda.ipynb` | Preprocessing ulasan Play Store & Analisis Eksploratif.<br>Input: `playstore_reviews_raw.csv` | Reduksi privasi (SHA-256 `reviewer_id`), pembersihan teks konservatif, analisis bimodal J-curve rating, disparitas 5 aplikasi, anomali 15 respon negatif. | Matriks kepuasan, figure `playstore_rating_balasan.png` & `playstore_per_app_eda.png`. |
| **03** | `03_playstore_goldset.ipynb` | Validasi anotasi sentimen manusia (Gold Set).<br>Input: `playstore_gold_set_final.csv` | Audit keunikan 417 ulasan, verifikasi distribusi sentimen (232 pos, 112 neu, 73 neg), analisis divergensi rating vs teks. | Crosstab rating-sentimen, figure `goldset_distribution.png`. |
| **04** | `04_sentiment_benchmark.ipynb` | Evaluasi komparatif 4 model klasifikasi sentimen NLP.<br>Input: `sentiment_benchmark/` | Evaluasi pada 84 ulasan *held-out test* vs 333 *dev* (Majority, InSet Lexicon, TF-IDF+LR, IndoBERT), confusion matrix heatmaps, error analysis. | Matriks kinerja NLP, figure `sentiment_benchmark.png`. |
| **05** | `05_aspect_analysis.ipynb` | Ekstraksi taksonomi aspek ulasan berbasis aturan.<br>Input: `playstore_reviews_final.csv`, taksonomi | Engine regex in-memory 8 aspek kanonikal, verifikasi kesetaraan paritas 100% terhadap 234 *mentions* remediated, audit manual 30 sampel (90% agreement). | Sebaran multi-label, korelasi aspek-sentimen, figure `aspek_sentimen.png`. |
| **06** | `06_instagram_preprocessing.ipynb` | Standardisasi skema 27 kolom Instagram.<br>Input: `instagram_posts_raw.csv` | Penyesuaian zona waktu WIB (+07:00), klasifikasi konten, pembersihan caption, kebijakan nol-fabrikasi (*views* 100% NaN). | Profil format & kolaborasi, figure `instagram_preprocessing_profile.png`. |
| **07** | `07_instagram_engagement_analysis.ipynb` | Analisis performa interaksi konten media sosial.<br>Input: `instagram_master.csv` | Statistik deskriptif (likes, comments, total interactions), ambang batas outlier IQR (239.0), format vs kolaborasi, korelasi Spearman teks & tagar. | Evaluasi interaksi konten, figure `instagram_format_kolaborasi.png` & `instagram_engagement_deepdive.png`. |
| **08** | `08_dataset_validation_export.ipynb` | Audit kualitas data & verifikasi paket ekspor.<br>Input: `data/export/`, manifest | Verifikasi SHA-256 5 sumber data terlindungi, audit skema master datasets, pemeriksaan kesetaraan 35 pasang CSV/XLSX, generator ekspor staging. | Laporan audit integritas data dan kepatuhan handoff data. |

---

## Dataset Master & Sumber Kanonikal

Master dataset kanonikal tersimpan pada direktori:
- **Instagram Master**: `data/export/instagram/master/instagram_master.csv` (55 baris, 27 kolom, 0 duplikat).
- **Play Store Master**: `data/export/playstore/master/playstore_master.csv` (417 baris, 33 kolom, 0 duplikat).
- **Kamus Data & Relasi**: `data/export/README_data_dictionary.md` dan `data/export/dataset_relationships.md`.
- **Integritas Sumber Data**: `data/export/source_integrity_manifest.csv` (menyimpan hash SHA-256 seluruh sumber terlindungi).

---

## Ringkasan Metodologi & Temuan Analisis

1. **Google Play Store**:
   - Menunjukkan distribusi rating bimodal bertipe *J-curve* (59,47% rating bintang 5 dan 17,75% rating bintang 1).
   - Rata-rata kepuasan tertinggi berada pada Zahir Attendance (4,25) dan Zahir Simple Start (4,19), sedangkan terendah pada Zahir Certification (3,05).
   - Responsivitas pengembang sangat tinggi (87,77% ulasan dibalas pengembang). Anomali selisih hari negatif (15 kasus) terbukti valid karena pengguna mengedit ulasan setelah pengembang membalas.
   - Evaluasi model sentimen pada 84 ulasan *held-out test* menempatkan **IndoBERT** sebagai model terbaik (*Accuracy* 0,7738; *Macro-F1* 0,7099), mengungguli TF-IDF + Logistic Regression (0,7619 / 0,6860), InSet Lexicon (0,3571 / 0,3433), dan Majority Baseline (0,5595 / 0,2392).
   - Ekstraksi 8 aspek menghasilkan tepat 234 *aspect mentions* setelah remediasi kata kunci, dengan tingkat kesesuaian 90,0% pada sampel audit 30 ulasan.

2. **Instagram @zahiraccounting**:
   - Total interaksi terkumpul sebesar 13.147 (12.643 likes dan 504 comments) dengan median 51 interaksi per postingan.
   - Distribusi interaksi sangat condong ke kanan (*right-skewed*), dengan 9 postingan teridentifikasi sebagai *viral outliers* (melebihi ambang IQR 239,0).
   - Konten kolaborasi menghasilkan rata-rata interaksi jauh lebih tinggi (456,7) dibandingkan konten organik murni (43,9) berkat perluasan audiens mitra.
   - Postingan Reels mendominasi volume (44 dari 55 postingan) dan total interaksi (12.472 interaksi).

---

## Keterbatasan Dataset & Kebijakan Data

1. **Sampling Bias Instagram**: Data postingan publik terbatas pada 55 konten yang dapat diakses publik tanpa login. Dominasi format Reels (80%) mencerminkan batasan algoritma akses web publik Instagram, bukan keseluruhan sejarah penerbitan sejak 2017.
2. **Kebijakan Nol-Fabrikasi Metrik**: Instagram web publik tidak menampilkan metrik *views*, *reach*, *impressions*, dan *followers*. Metrik tersebut tetap dipertahankan murni bernilai `NaN` (100% missing) dan **tidak pernah dimanipulasi menjadi nol** atau diisi angka sintetis.
3. **Pemisahan Konseptual Sentimen vs Rating**: Rating bintang adalah variabel bantuan berbasis skor (1–5) dan tidak ekuivalen dengan sentimen teks. Label sentimen manusia pada Gold Set dipertahankan 100% dan tidak pernah ditimpa oleh prediksi model.
4. **Keterbatasan Evaluasi NLP**: Benchmarking NLP dievaluasi pada 84 sampel uji berstrata. Angka performa mencerminkan kinerja pada set data uji lokal dan tidak menjamin generalisasi ke domain bahasa lain.
5. **Korelasi vs Kausalitas**: Hubungan statistik antara panjang caption atau jumlah tagar terhadap interaksi merupakan observasi empiris dan tidak boleh diinterpretasikan sebagai hubungan sebab-akibat langsung.

---

## Pengujian & Verifikasi Kualitas Otomatis

Seluruh pipeline dilengkapi dengan rangkaian pengujian kualitas data dan regresi otomatis. Untuk menjalankan verifikasi menyeluruh:

```powershell
python outputs/reports/run_all_tests.py
```

Rangkaian pengujian mencakup:
- Validasi struktur JSON dan skema `nbformat` v4 pada 8 notebook kanonikal.
- Verifikasi checksum SHA-256 terhadap 5 dataset sumber data terlindungi.
- Validasi skema, ukuran baris, keunikan kunci primer, dan kebijakan privasi pada Instagram Master dan Play Store Master.
- Eksekusi 5 suite pengujian regresi historis (Fase 5.3, 5.4, 5.5, 5.6, dan 5.8) dengan hasil **100% PASS (0 Failed)**.
