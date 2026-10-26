# Laporan Hasil Benchmarking Model Sentimen NLP (Fase 4.3)
**Zahir Social Analytics — Play Store Customer Voice Analytics**  
**Audit & Execution Date:** 2026-10-26  
**Reference Ground Truth:** Canonical Play Store Gold Set (417 Ulasan Teranotasi Manusia)

---

## 1. Ringkasan Eksekutif
Fase 4.3 bertujuan melakukan evaluasi empiris (*benchmarking*) terhadap berbagai metode analisis sentimen teks berbahasa Indonesia dengan mengacu secara mutlak pada **Canonical Gold Set 417 Ulasan Google Play Store** (`data/final/playstore_gold_set_final.csv` & `.xlsx`). 

Protokol evaluasi machine learning diterapkan secara ketat:
- **Autoritas Label Manusia**: Kolom `human_sentiment_label` diperlakukan sebagai kebenaran mutlak (*single source of truth*). Rating bintang sama sekali tidak digunakan sebagai prediktor sentimen teks.
- **Pemisahan Data Terisolasi**: Dataset dibagi secara terstratifikasi (*stratified 80/20 train-dev/test split*, `random_state=42`) menghasilkan 333 data Development Set dan 84 data Held-Out Test Set. Data uji benar-benar diisolasi dari proses seleksi model, pemilihan fitur, maupun penyesuaian threshold.
- **Metrik Evaluasi Utama**: **Macro-F1** ditetapkan sebagai metrik komparasi primer untuk mengantisipasi ketidakseimbangan kelas (*class imbalance*).

---

## 2. Kandidat Model yang Dievaluasi
Empat pendekatan multi-tier dievaluasi secara independen pada 84 data test set:

1. **Majority Class Baseline (Heuristic / Zero-Rule)**:
   - *Deskripsi*: Model naif yang selalu memprediksi kelas mayoritas (`positive`).
   - *Tujuan*: Menjadi standar dasar minimum sanity check pada dataset imbalanced.
2. **InSet Lexicon Baseline (Indonesian Sentiment Lexicon)**:
   - *Sumber*: Fajri Koto & Gemala Y. Rahmaningtyas, IEEE IALP 2017 (`fajri91/InSet`).
   - *Karakteristik*: Terdiri atas 3.609 kata positif dan 6.609 kata negatif dengan bobot -5 hingga +5. Dilengkapi mekanisme *negation handling* untuk kata ingkar bahasa Indonesia (*tidak, bukan, belum, tak, gak, nggak, ga, kurang, jangan, tanpa*).
   - *Threshold*: Dituning pada Development Set dengan nilai batas netral $\pm 2.0$.
3. **TF-IDF + Logistic Regression (Supervised Bag-of-Words)**:
   - *Deskripsi*: Ekstraksi fitur n-gram (1-2) TF-IDF (1.000 fitur teratas) dengan pengklasifikasi regresi logistik berbobot seimbang (*balanced class weight*), dilatih murni pada 333 ulasan Development Set.
4. **IndoBERT Pretrained Sentiment Classifier (Deep Transformer)**:
   - *Model*: `mdhugol/indonesia-bert-sentiment-classification` berbasis IndoBERT Base Phase 1 (`indobenchmark/indobert-base-p1`).
   - *Pretraining Dataset*: SmSA (Sentence-level Sentiment Analysis) IndoNLU Prosa Dataset (~11.000 data).
   - *Lisensi*: Apache 2.0 / MIT.
   - *Pemetaan Label*: `LABEL_0` $\rightarrow$ `positive`, `LABEL_1` $\rightarrow$ `neutral`, `LABEL_2` $\rightarrow$ `negative`.

---

## 3. Hasil Kuantitatif Benchmarking (Held-Out Test Set, n=84)

| Model / Metode | Accuracy | Macro-F1 (Utama) | Weighted-F1 | Negative F1 | Neutral F1 | Positive F1 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Majority Class Baseline** | 0.5595 | 0.2392 | 0.4015 | 0.0000 | 0.0000 | 0.7176 |
| **InSet Lexicon (+/-2.0 th)** | 0.3571 | 0.3433 | 0.3674 | 0.3667 | 0.2326 | 0.4308 |
| **TF-IDF + Logistic Regression** | 0.7619 | 0.6860 | 0.7626 | 0.5000 | 0.6667 | 0.8913 |
| **IndoBERT Pretrained (SmSA)** | **0.7738** | **0.7099** | **0.7740** | **0.6667** | **0.5500** | **0.9130** |

*Dukungan data uji (support)*: Total 84 ulasan (Positive = 47, Neutral = 22, Negative = 15).

---

## 4. Analisis Confusion Matrix & Karakteristik Model

### A. IndoBERT Pretrained (Performa Tertinggi)
- **Matriks Kontingensi**:
  - True Negative (n=15): 12 terprediksi Negative, 3 terprediksi Neutral, 0 terprediksi Positive.
  - True Neutral (n=22): 8 terprediksi Negative, 11 terprediksi Neutral, 3 terprediksi Positive.
  - True Positive (n=47): 1 terprediksi Negative, 4 terprediksi Neutral, 42 terprediksi Positive.
- **Karakteristik**:
  - Memiliki **Recall Negative sebesar 80.0%** (12/15 keluhan kritis tertangkap secara akurat).
  - Memiliki **Precision Positive sebesar 93.3%** dan **Recall Positive 89.4%**.
  - Nol ulasan negatif yang salah diprediksi menjadi positif.

### B. InSet Lexicon Baseline
- **Kelemahan Mendasar**: Mengalami *negative bias* yang sangat tajam. Dari 84 ulasan, InSet memprediksi 45 ulasan sebagai negatif, sehingga menghasilkan presisi negatif yang sangat rendah (24.4%). Hal ini disebabkan oleh ketidakseimbangan perbendaharaan leksikon InSet yang memuat kata negatif hampir dua kali lebih banyak daripada kata positif.

### C. TF-IDF + Logistic Regression
- Menunjukkan ketahanan yang baik pada kelas Netral (F1 = 0.6667), namun kalah dalam menangkap nuansa keluhan teknis negatif (Recall Negative hanya 46.7% vs IndoBERT 80.0%).

---

## 5. Analisis Kesalahan (Error Analysis) IndoBERT
Dari total 84 ulasan pengujian, IndoBERT menghasilkan 19 kesalahan prediksi (22.6%):

1. **Neutral salah diprediksi sebagai Negative (8 kasus - 42.1% dari error)**:
   - Pola: Pengguna menanyakan cara penggunaan atau kendala login faktual tanpa emosi marah (contoh: *"kenapa not to allowed terus ya? saya ga bisa login"*). Model mendeteksi kata "not allowed" dan "ga bisa" sebagai sentimen negatif, sementara anotator manusia melabelinya sebagai netral (pertanyaan teknis).
2. **Positive salah diprediksi sebagai Neutral (4 kasus - 21.1%)**:
   - Pola: Pujian fungsional singkat yang diiringi saran pengembangan fitur.
3. **Negative salah diprediksi sebagai Neutral (3 kasus - 15.8%)**:
   - Pola: Keluhan halus bernada sopan tanpa kata makian/emosional yang kuat.
4. **Neutral salah diprediksi sebagai Positive (3 kasus - 15.8%)**:
   - Pola: Pertanyaan faktual yang diawali salam atau kalimat sopan pembuka.
5. **Positive salah diprediksi sebagai Negative (1 kasus - 5.3%)**:
   - Pola: Kalimat slang/informal *"Past bisa bangkiiit aku"* yang membingungkan pemecah subword tokenizer.

---

## 6. Keterbatasan yang Diidentifikasi (*Identified Limitations*)
1. **Ukuran Test Set Terbatas**: Dengan 84 ulasan pada test set (khususnya 15 sampel negatif), perbedaan satu sampel mengubah recall sekitar 6.7%. Oleh karena itu, metrik Macro-F1 tidak boleh diinterpretasikan secara mutlak bahwa model pre-trained telah sempurna, melainkan sebagai baseline yang terbukti reliabel.
2. **Ambiguitas Pertanyaan Teknis**: Terdapat batas tipis antara komplain (negatif) dan pertanyaan teknis murni (netral) pada ulasan aplikasi bisnis/akuntansi.
3. **Code-Switching & Slang**: Kehadiran istilah bahasa Inggris ("force close", "not allowed", "login failed") di tengah teks bahasa Indonesia memerlukan model dengan pemahaman konteks dwibahasa yang kuat.

---

## 7. Rekomendasi Langkah Selanjutnya (Menuju Fase 4.4 / Fase 5)
1. **Adopsi IndoBERT**: Tetapkan arsitektur berbasis IndoBERT (`mdhugol/indonesia-bert-sentiment-classification`) sebagai backbone klasifikasi sentimen inferensial untuk seluruh ekosistem Zahir (Play Store dan Instagram).
2. **Lanjut ke Topic / Aspect Modeling**: Membedah aspek dan akar permasalahan keluhan pelanggan (misal: sinkronisasi database cloud, validasi presensi wajah, penambahan master produk POS, dan force close ujian sertifikasi) menggunakan teknik Topic Modeling (BERTopic / LDA).
3. **Dashboard Integration**: Mengintegrasikan distribusi sentimen tervalidasi dan topik ulasan ke dalam dashboard analitik interaktif Streamlit pada Fase 5.
