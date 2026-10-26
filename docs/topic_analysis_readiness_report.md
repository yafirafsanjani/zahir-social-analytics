# Laporan Audit Kesiapan Analisis Topik & Aspek (Fase 5.1)
**Zahir Social Analytics — Play Store Customer Voice Analytics**  
**Audit & Execution Date:** 2026-10-26  
**Status:** Audit & Perencanaan Selesai (100% Validated)  
**Referensi Data:** `data/final/playstore_reviews_final.csv` (Teks Bersih) & `data/final/playstore_gold_set_final.csv` (Label Sentimen Manusia)

---

## 1. Ringkasan Eksekutif & Tujuan Audit
Fase 5.1 bertujuan mengevaluasi kesiapan teknis, linguistik, dan metodologis dataset ulasan Google Play Store ekosistem Zahir (417 ulasan) sebelum menjalankan pemodelan topik (*topic modeling*) atau pengelompokan aspek (*aspect-based analysis*). 

Sesuai aturan tata kelola proyek:
- Fase ini **murni audit dan perencanaan** (*audit and planning phase only*).
- **Tidak melakukan pemodelan topik, ekstraksi embedding, clustering, maupun penugasan label topik pada fase ini**.
- Label sentimen manusia (`human_sentiment_label`) diperlakukan sebagai acuan ground truth mutlak. Rating bintang tidak dijadikan dasar inferensi topik.
- Dataset mentah dan dataset olahan final dijaga tetap tidak berubah (*immutable*).

---

## 2. Audit Kualitas Data & Karakteristik Teks Ulasan

### A. Integritas Dataset & Skema
- **Jumlah Rekaman**: Tepat **417 ulasan** pada `playstore_reviews_final.csv` dan `playstore_gold_set_final.csv`.
- **Integritas Relasi**: Penggabungan (*inner join*) berbasis `review_id` menghasilkan tepat 417 baris unik (**100% konsisten, 0 dropped, 0 multiplied**).
- **Kelengkapan Kolom Teks**: 0 nilai kosong (*0 missing values*) pada kolom `review_text` maupun `review_text_clean`.

### B. Karakteristik Panjang Teks & Dominansi Ulasan Pendek (*Short-Text Distribution*)
- **Panjang Kata (Word Count)**:
  - Rata-rata (*Mean*): **11.71 kata/ulasan**
  - Nilai Tengah (*Median*): **7.0 kata/ulasan**
  - Standar Deviasi: **14.52 kata**
  - Rentang: Min = 1 kata, Max = 88 kata
  - Persentil: P25 = 4.0 kata, P75 = 13.0 kata, P90 = 27.0 kata
- **Panjang Karakter**: Mean = 73.49 karakter, Median = 44.0 karakter.
- **Frekuensi Ulasan Sangat Pendek**:
  - Ulasan $\le$ 2 kata: **79 ulasan (18.94%)**
  - Ulasan $\le$ 3 kata: **96 ulasan (23.02%)**
  - Ulasan $\le$ 5 kata: **161 ulasan (38.61%)**
  - Ulasan $\ge$ 20 kata: **70 ulasan (16.79%)**
- **Disparitas Panjang Berdasarkan Sentimen**:
  - *Negative* (n=73): Rata-rata **19.16 kata** (median 12.0) — ulasan komplain memuat uraian kendala yang paling rinci.
  - *Neutral* (n=112): Rata-rata **14.15 kata** (median 9.0) — pertanyaan fungsional dan operasional.
  - *Positive* (n=232): Rata-rata **8.19 kata** (median 5.0) — didominasi teks pujian pendek non-deskriptif.

### C. Analisis Duplikasi Teks
- Ditemukan tepat **24 instans teks duplikat persis** (5.76% dari total dataset), yang berasal dari **7 frasa pujian positif**:
  - `"Mantap"` (8 kali)
  - `"Ok"` (4 kali)
  - `"Bagus"` (3 kali)
  - `"Good"` (3 kali)
  - `"Goodjob!"` (2 kali)
  - `"Sangat membantu"` (2 kali)
  - `"Wow sekali"` (2 kali)
- **100% teks duplikat (24/24) berada pada kelas sentimen POSITIF**.
- **0 teks duplikat pada kelas Negatif maupun Netral** (seluruh ulasan kritis dan pertanyaan bersifat unik).

### D. Distribusi Bahasa & Code-Switching
Berdasarkan audit leksikal penanda bahasa:
- **Bahasa Indonesia (Utama)**: 233 ulasan (**55.88%**)
- **Informal / Slang Pendek**: 115 ulasan (**27.58%**) (teks 1-2 kata tanpa stopword formal)
- **Bahasa Inggris Murni**: 43 ulasan (**10.31%**)
- **Mixed Code-Switching**: 26 ulasan (**6.24%**) (istilah teknis bahasa Inggris berbaur dalam struktur kalimat bahasa Indonesia, misal: *"aplikasi sering force close saat mau print struk"*).

### E. Preservasi Sinyal Preprocessing
- Pengecekan emoji pada ulasan mentah vs ulasan olahan menunjukkan tepat **27 ulasan ber-emoji** pada kedua versi (**100% terpreservasi**).
- Pembersihan konservatif pada Fase 2 berhasil mempertahankan kata negasi (*tidak, gak, belum*), tanda baca penegas, dan nama fitur produk tanpa kehilangan informasi semantik esensial.

---

## 3. Evaluasi Pendekatan Pemodelan Kandidat

| Dimensi Evaluasi | A. BERTopic (Transformer + UMAP + HDBSCAN) | B. TF-IDF + Clustering (K-Means) | C. Keyword/Rule-Based Aspect Taxonomy (ABSA) |
| :--- | :--- | :--- | :--- |
| **Kesesuaian Ukuran Sampel (N=417)** | **Sangat Rendah (High Risk)**. HDBSCAN dirancang untuk ribuan dokumen; pada data mikro <500, HDBSCAN membuang 40-70% data sebagai outlier (-1). | **Sedang (Feasible)**. Mampu mempartisi data berapapun ukurannya dengan parameter K yang terkontrol. | **Sangat Tinggi (Optimal)**. Deterministik, akurat untuk data mikro, dan tidak terdistorsi oleh ukuran korpus. |
| **Penanganan Ulasan Pendek ($\le$ 5 kata)** | **Rentan**. Vektor embedding teks 1-2 kata ("Mantap", "Ok") memicu titik densitas artifisial yang merusak koherensi kluster. | **Rentan**. Vektor TF-IDF sangat sparse dan ortogonal pada teks pendek. | **Sangat Kuat**. Dapat mengabaikan teks pendek non-aspek dan memfokuskan ekstraksi pada kata kunci fungsional. |
| **Kesiapan Dependensi Lingkungan** | **Belum Terinstal**. Memerlukan `bertopic`, `umap-learn`, `hdbscan`, `sentence-transformers` (~500MB+ paket & model). | **Siap 100%**. Menggunakan `sklearn` dan `scipy` yang sudah terinstal di `.venv_social`. | **Siap 100%**. Murni pustaka Python standar (`re`, `pandas`). Tanpa instalasi tambahan. |
| **Transparansi & Actionability Bisnis** | *Black-box*. Topik yang terbentuk seringkali berupa campuran kata tanpa batasan modul ERP yang tegas. | *Moderat*. Kata-kata teratas kluster dapat diinspeksi via centroid, tetapi batas topik fuzzy. | **Sangat Tinggi**. Setiap aspek memetakan langsung modul bisnis Zahir (Login, Sinkronisasi, Cetak Struk, dll.). |
| **Rekomendasi Status** | **DITOLAK (NOT RECOMMENDED)** untuk alur kerja utama. | **DIREKOMENDASIKAN SEBAGAI FALLBACK / EKSPLORASI**. | **DIREKOMENDASIKAN SEBAGAI METODE UTAMA (PRIMARY)**. |

---

## 4. Analisis Pilihan Cakupan Data (*Analysis Scope Options*)

Evaluasi dilakukan terhadap 4 opsi cakupan data menggunakan label sentimen manusia:

| Opsi Cakupan | Ukuran (N) | % Gold Set | Rata-rata Kata | Median Kata | Ulasan $\le$ 5 Kata | Duplikat Persis | Analisis Trade-off |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Scope 1: All Reviews** | 417 | 100.0% | 11.71 | 7.0 | 161 (38.6%) | 24 (5.8%) | Cakupan menyeluruh, namun topik sangat terdistorsi oleh 232 ulasan positif pendek ("Mantap", "Bagus"). |
| **Scope 2: Negative Reviews Only** | 73 | 17.5% | 19.16 | 12.0 | 15 (20.5%) | 0 (0.0%) | Sangat spesifik pada keluhan produk/bug teknis dengan teks informatif, tetapi ukuran sampel kecil membatasi clustering otomatis. |
| **Scope 3: Negative + Neutral Reviews** | **185** | **44.4%** | **16.13** | **10.0** | **36 (19.5%)** | **0 (0.0%)** | **KESEIMBANGAN OPTIMAL**: Menggabungkan keluhan kritis dan pertanyaan fitur fungsional. 0 duplikat teks, panjang rata-rata substansial. |
| **Scope 4: Contrastive Pos vs Neg** | 232 Pos / 73 Neg | - | 8.19 (Pos) / 19.16 (Neg) | 5.0 / 12.0 | 53.9% Pos / 20.5% Neg | 24 Pos / 0 Neg | Bermanfaat untuk melihat fitur yang diapresiasi vs fitur yang dikeluhkan, namun dataset positif harus difilter teks pendeknya. |

---

## 5. Pembedaan Konseptual: Topik vs Aspek vs Sentimen-Aspek
Agar analisis tidak rancu, ditetapkan distingsi metodologis yang ketat:
1. **Topic Discovery (Eksplorasi Topik)**: Proses tanpa label terdefinisi untuk menemukan tema tersembunyi yang sering muncul secara alami dalam kumpulan teks (*unsupervised*).
2. **Aspect Analysis (Analisis Aspek Produk)**: Proses mengidentifikasi komponen, modul, atau fitur spesifik produk yang telah didefinisikan sebelumnya (misal: *Otentikasi Login, Sinkronisasi Cloud, Cetak Struk POS, Presensi Wajah, Sistem Ujian*).
3. **Sentiment-Aspect Analysis (Analisis Sentimen per Aspek)**: Proses mengevaluasi polaritas sikap (positif, netral, atau negatif) yang diarahkan pengguna secara spesifik terhadap aspek yang telah teridentifikasi.

---

## 6. Taksonomi Aspek Awal Ekosistem Zahir (Domain-Verified)
Berdasarkan audit awal frekuensi istilah teknis pada 417 ulasan, telah teridentifikasi 8 kluster aspek fungsional yang merepresentasikan kebutuhan bisnis Zahir:

1. **Authentication & Access (`login_auth`)**: *login, masuk, password, sandi, akun, registrasi, lupa sandi* (Muncul di 17.8% ulasan negatif & 14.3% netral).
2. **System Stability & Crash (`crash_stability`)**: *force close, crash, keluar sendiri, error, bug, lemot, lag* (Muncul di 16.4% ulasan negatif).
3. **Pricing & Subscription (`pricing_subscription`)**: *bayar, berbayar, langganan, tarif, biaya, harga, mahal, expired* (Muncul di 12.3% ulasan negatif & 8.0% netral).
4. **Cloud & Database Sync (`sync_cloud_data`)**: *sinkron, sync, cloud, database, server, data hilang* (Terkonsentrasi di Zahir Online & POS X).
5. **POS & Hardware Printing (`pos_hardware_print`)**: *cetak, print, printer, struk, nota, bluetooth, kasir* (Terkonsentrasi di POS X).
6. **Core Accounting & Inventory (`inventory_accounting`)**: *stok, barang, produk, transaksi, laporan, invoice, hutang* (Muncul di 13.7% negatif & 9.5% positif).
7. **Certification Exam Engine (`certification_exam`)**: *ujian, soal, sertifikasi, nilai, waktu habis* (Terkonsentrasi di Zahir Certification).
8. **Face Attendance & Geolocation (`attendance_face`)**: *absen, presensi, wajah, selfie, gps, lokasi* (Terkonsentrasi di Zahir Attendance).

---

## 7. Rekomendasi Final & Langkah Menuju Fase 5.2

### A. Rekomendasi Pendekatan Utama (Primary Approach):
> **Keyword/Rule-Based Aspect Taxonomy (ABSA)**  
> **Alasan**: Mampu mengatasi keterbatasan data mikro (N=417), kebal terhadap distorsi ulasan pendek, menangani *code-switching* dwibahasa secara transparan, tidak memerlukan instalasi dependensi berat, dan menghasilkan wawasan yang langsung dapat ditindaklanjuti oleh tim produk Zahir.

### B. Rekomendasi Pendekatan Pendukung (Fallback Approach):
> **TF-IDF + K-Means / Hierarchical Clustering pada Scope 3 (Negative + Neutral)**  
> **Alasan**: Sebagai alat validasi eksploratif tanpa supervisi (*unsupervised sanity check*) guna memastikan tidak ada kluster kata kunci penting di luar 8 taksonomi utama yang terlewat.

### C. Rekomendasi Cakupan Data:
> **Scope 3 (Negative + Neutral Reviews, N=185)** untuk pembedahan akar masalah dan pertanyaan pelanggan (*Customer Voice Pain Points*), didampingi oleh **Scope 4 (Perbandingan Positif vs Negatif)** untuk pemetaan keunggulan vs kelemahan fitur.

---

## 8. Artefak Output yang Dihasilkan
1. `data/final/topic_analysis_readiness/text_quality_summary.csv` & `.xlsx`
2. `data/final/topic_analysis_readiness/topic_scope_comparison.csv` & `.xlsx`
3. `data/final/topic_analysis_readiness/topic_readiness_audit.csv` & `.xlsx`
4. `analysis/topic_analysis_readiness_audit.py`
5. `scripts/verify_phase5_1.py`
6. `docs/topic_analysis_readiness_report.md`
