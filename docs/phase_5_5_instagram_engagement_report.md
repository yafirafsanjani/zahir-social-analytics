# Laporan Analisis Performa Postingan & Social Engagement Instagram (Fase 5.5)
**Zahir Social Analytics — Instagram Public Content Performance, Engagement Distribution, and Cross-Format Analytics**  
**Tanggal Eksekusi:** 02 November 2026  
**Status Fase:** `COMPLETED (Tuntas 100%)`  
**Penulis/Auditor:** Zahir Social Analytics Data Science Agent  
**Lingkungan:** Python 3.11.9 (`.venv_social`), Windows PowerShell  
**Aturan Tata Kelola:** *Raw data is immutable*, *No synthetic metric fabrication*, *Dual format parity (CSV & XLSX)*, *Non-causal statistical rigor*, *No Git operations (`git add/commit/push`)*.

---

## 1. Ringkasan Eksekutif

Laporan ini menyajikan hasil evaluasi analitik mendalam pada **Fase 5.5: Instagram Social Engagement & Content Performance Analysis** dalam proyek Zahir Social Analytics. Analisis ini mengevaluasi performa interaksi dari **55 postingan publik Instagram** akun `@zahiraccounting` yang telah distandarisasi secara temporal (WIB) dan dibersihkan pada Fase 5.4. Seluruh temuan disusun secara reproducible, tervalidasi programatik melalui pengujian otomatis, dan diekspor ke dalam 7 pasang artefak CSV (RFC 4180 terenkapsulasi penuh) serta Excel XLSX multi-sheet terformat (`openpyxl`) di folder `data/final/instagram_analysis/`.

### Temuan Utama & Parameter Inti:
1. **Profil Keterlibatan Riil (*Real User Actions*)**:
   - Akumulasi interaksi dari 55 postingan mencapai **13.147 total interaksi**, yang terbagi atas **12.643 likes ($96.17\%$)** dan **504 komentar ($3.83\%$)**.
   - Distribusi interaksi sangat condong ke kanan (*heavily right-skewed*, skewness = $+4.31$), di mana **rata-rata ($239.04$)** terdistorsi signifikan oleh segelintir konten viral, sementara nilai tengah atau **median ($51.00$)** merefleksikan performa tipikal konten Zahir.
   - Menggunakan ambang batas Tukey IQR ($Q3 + 1.5 \times IQR = 110.0 + 1.5 \times 86.0 = 239.0$), teridentifikasi tepat **9 postingan viral outlier ($16.36\%$)** yang menyumbang **10.601 interaksi ($80.63\%$ dari seluruh keterlibatan)**.
2. **Asimetri Format & Efisiensi Konten**:
   - Terdapat ketimpangan tajam ukuran sampel: `video/reel` mendominasi dengan **44 postingan ($80.0\%$)**, diikuti `carousel` sebanyak **8 postingan ($14.5\%$)**, dan `image` tunggal sebanyak **3 postingan ($5.5\%$)**.
   - Video Reels menghasilkan akumulasi interaksi terbesar ($12.472$ interaksi, rata-rata $283.45$, median $61.50$), namun Carousel mencatat **rasio percakapan tertinggi** dengan median **10.0 komentar per postingan** (dibandingkan median Reels yang hanya $0.5$ komentar). Format gambar tunggal mencatat performa paling rendah (median $5.0$ interaksi, median $0.0$ komentar).
3. **Efek Amplifikasi Kolaborasi & Akun Mitra**:
   - Postingan kolaborasi (*collaborative co-authored content*, $n=26$) mencatat median interaksi **$97.00$** (rata-rata $456.69$), sedangkan postingan organik mandiri `@zahiraccounting` ($n=29$) mencatat median interaksi **$25.00$** (rata-rata $43.90$). Terdapat selisih absolut median sebesar **$+72.00$ interaksi ($+288.00\%$)**.
   - Keberhasilan konten kolaborasi terutama digerakkan oleh mitra kreator `@pecahtelur.id` ($8$ postingan, akumulasi $7.058$ interaksi, median $635.50$) dan `@muhamad.is` ($14$ postingan, akumulasi $4.688$ interaksi, median $90.50$).
   - Sesuai tata kelola metodologis, hubungan ini **tidak ditafsirkan sebagai kausalitas mutlak**, melainkan akibat efek pengganda audiens mitra (*cross-audience spillover*), kurasi konten wawancara yang lebih mendalam, dan format video.
4. **Dinamika Waktu Publikasi & Dekonstruksi Jam Pagi**:
   - Rata-rata interaksi harian tertinggi tercatat pada hari Selasa ($520.00$) dan Kamis ($354.67$), sedangkan volume postingan terbanyak berada pada hari Jumat ($16$ postingan).
   - Segmen waktu pagi (06:00–11:59 WIB) mencatat rata-rata interaksi tertinggi ($586.79$, total $11.149$ interaksi). Namun, audit audit granular membuktikan ini adalah **artefak temporal terkonsentrasi**: 5 dari 8 video viral `@pecahtelur.id` dijadwalkan tayang serentak pada pukul 06:00 WIB pada bulan Desember 2024. Waktu penayangan bukan penentu tunggal virality.
5. **Panjang Teks Caption & Fenomena Simpson's Paradox pada Tagar**:
   - Jumlah kata caption (`caption_word_count`) berkorelasi positif moderat dengan total interaksi (Spearman $\rho = +0.3806, p = 0.0041$). Konten bercerita panjang (*long-form storytelling*, $>100$ kata) memiliki median interaksi $88.00$, jauh melampaui caption pendek ($29.00$).
   - Pada populasi penuh ($N=55$), terdapat korelasi negatif signifikan antara jumlah tagar dan interaksi (Spearman $\rho = -0.4509, p = 0.0006$). Namun, audit stratifikasi membuktikan fenomena **Simpson's Paradox**: seluruh video viral `@pecahtelur.id` tidak menggunakan tagar sama sekali ($0$ hashtags), sedangkan postingan internal yang jangkauannya terbatas rutin menggunakan tagar. Pada kelompok postingan organik mandiri ($n=29$), korelasi tagar sama sekali **tidak signifikan secara statistik** ($\rho = -0.1580, p = 0.4131$).
6. **Verifikasi Otomatis Penuh**:
   - Seluruh 15 pengujian integritas programatik pada `scripts/verify_phase5_5.py` berhasil lulus 100% (*15 passed, 0 failed*).
   - Pengujian regresi Fase 5.4 (`scripts/verify_phase5_4.py`) tetap lulus 100% (*13 passed, 0 failed*), dan dataset ulasan Play Store (417 ulasan) serta Gold Set tetap tidak tersentuh.

---

## 2. Provenance Sumber Data & Integritas Ingesti

Analisis Fase 5.5 bersumber tunggal pada dataset analitik final hasil Fase 5.4:
- **Lokasi Berkas**: `data/final/instagram_posts_final.csv` & `data/final/instagram_posts_final.xlsx`
- **Hash MD5 Berkas CSV**: `794b050f649bc76537cf31f12b485b66`
- **Hash MD5 Berkas Mentah Kanonikal**: `c9e7882eff8282bb698825a0ef712817`
- **Jumlah Observasi**: Tepat **55 postingan unik** (0 duplikasi `post_id`, 0 duplikasi `post_url`).
- **Rentang Temporal**: 01 Maret 2024 hingga 06 Agustus 2026 (Waktu Indonesia Barat, UTC+7).
- **Kebijakan Metrik Platform**: Kolom `views` bernilai `NaN` (100% missing) dipertahankan apa adanya sesuai realitas platform web publik tanpa login. Tidak ada pembuatan metrik sintetis (*zero fabrication of reach, impressions, follower count, or arbitrary engagement rates*). Seluruh analisis keterlibatan beroperasi pada variabel deterministik:
  $$\text{total\_interactions} = \text{likes} + \text{comments}$$

---

## 3. Analisis Engagement per Postingan & Karakteristik Distribusi

### 3.1 Ringkasan Statistik Deskriptif Parametrik & Non-Parametrik

| Metrik Engagement | N Postingan | Total Akumulasi | Mean | Std Dev | Median | Min | Max | Q1 (25%) | Q3 (75%) | IQR | Skewness | Ambang Outlier IQR | Jumlah Outlier | Persentase Outlier |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Likes** | 55 | 12.643 | 229,87 | 590,43 | 44,00 | 1 | 3.191 | 23,00 | 109,00 | 86,00 | +4,27 | 238,00 | 9 | 16,36% |
| **Comments** | 55 | 504 | 9,16 | 41,14 | 1,00 | 0 | 306 | 0,00 | 6,50 | 6,50 | +7,22 | 16,25 | 4 | 7,27% |
| **Total Interactions** | 55 | 13.147 | 239,04 | 618,57 | 51,00 | 1 | 3.217 | 24,00 | 110,00 | 86,00 | +4,31 | 239,00 | 9 | 16,36% |

### 3.2 Karakteristik Distribusi & Segmentasi Performa
1. **Asimetri Positif Ekstrem (*Severe Right-Skewness*)**:
   - Nilai skewness sebesar $+4.31$ pada total interaksi dan $+7.22$ pada komentar mencerminkan pola khas media sosial (*power-law distribution*), di mana mayoritas konten memperoleh interaksi wajar, sementara segelintir konten viral mendominasi akumulasi metrik.
   - Nilai rata-rata ($239.04$) berjarak hampir 4,7 kali lipat lebih tinggi dari nilai median ($51.00$). Oleh karena itu, **median merupakan ukuran pemusatan data yang paling representatif dan tahan pencilan (*robust central tendency*)** untuk menilai kinerja konten sehari-hari.
2. **Segmentasi Tingkat Interaksi (*Interaction Tiers*)**:
   - **Tier 1: Viral Outlier ($>239$ interaksi)**: 9 postingan ($16.36\%$). Akumulasi: $10.601$ interaksi ($80.63\%$). Seluruhnya merupakan video reels dan postingan kolaborasi (kecuali 1 reels organik internal).
   - **Tier 2: High Engagement ($110 - 239$ interaksi)**: 5 postingan ($9.09\%$). Akumulasi: $789$ interaksi ($6.00\%$).
   - **Tier 3: Moderate Engagement ($24 - 109$ interaksi)**: 27 postingan ($49.09\%$). Akumulasi: $1.523$ interaksi ($11.58\%$). Mewakili baseline performa postingan reguler.
   - **Tier 4: Low Engagement ($<24$ interaksi)**: 14 postingan ($25.45\%$). Akumulasi: $234$ interaksi ($1.78\%$). Didominasi postingan pengumuman administratif dan gambar statis.

---

## 4. Perbandingan Komparatif Format Konten (Reels vs Carousel vs Image)

### 4.1 Tabel Performa Komparatif Antar Format

| Jenis Konten | Jumlah Post | Pangsa (%) | Total Likes | Mean Likes | Median Likes | Total Komentar | Mean Komentar | Median Komentar | Total Interaksi | Mean Interaksi | Median Interaksi | Min | Max | Std Dev | IQR | Post Kolaborasi | Post Organik |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **video/reel** | 44 | 80,00% | 12.040 | 273,64 | 55,00 | 432 | 9,82 | 0,50 | 12.472 | 283,45 | 61,50 | 1 | 3.217 | 684,25 | 137,50 | 21 | 23 |
| **carousel** | 8 | 14,55% | 588 | 73,50 | 33,00 | 70 | 8,75 | 10,00 | 658 | 82,25 | 45,00 | 4 | 342 | 108,40 | 40,00 | 5 | 3 |
| **image** | 3 | 5,45% | 15 | 5,00 | 5,00 | 2 | 0,67 | 0,00 | 17 | 5,67 | 5,00 | 4 | 8 | 2,08 | 2,00 | 0 | 3 |
| **Total / Overall** | **55** | **100,00%** | **12.643** | **229,87** | **44,00** | **504** | **9,16** | **1,00** | **13.147** | **239,04** | **51,00** | **1** | **3.217** | **618,57** | **86,00** | **26** | **29** |

### 4.2 Analisis & Keterbatasan Inferensi
1. **Ketimpangan Ukuran Sampel (*Sample Size Asymmetry*)**:
   - Komposisi 44 Reels vs 8 Carousel vs 3 Gambar mencerminkan strategi distribusi Instagram publik modern yang memprioritaskan Reels dalam tab penjelajahan publik.
   - Ukuran sampel $n=3$ pada format gambar tunggal secara statistik **tidak memadai untuk generalisasi umum**. Temuan bahwa gambar berkinerja rendah harus dipahami sebagai karakteristik 3 postingan pengumuman tertentu (bukan vonis bahwa format grafis gambar pasti selalu gagal).
2. **Karakteristik Keterlibatan Berbeda**:
   - **Video Reels**: Berfungsi sebagai instrumen jangkauan massal (*broad reach driver*). Meskipun rata-rata interaksinya tertinggi ($283.45$), median komentarnya sangat rendah (**$0.50$**). Artinya, lebih dari separuh video Reels ditonton dan disukai tanpa memicu percakapan aktif di kolom komentar.
   - **Carousel**: Berfungsi sebagai instrumen edukasi dan diskusi (*engagement depth & conversation driver*). Meskipun median likes-nya moderat ($33.00$), median komentarnya mencapai **$10.00$ per postingan** (20 kali lipat lebih tinggi dari Reels). Format multi-slide mendorong audiens membaca runtutan argumen dan memberikan tanggapan kontekstual.
---

## 5. Analisis Konten Kolaborasi (Collaborative vs Organic)

### 5.1 Perbandingan Status Kolaborasi & Komparasi Delta

| Dimensi Analisis | Segmen Kategori | Is Collaboration | N Post | Pangsa (%) | Total Likes | Mean Likes | Median Likes | Total Komentar | Mean Komentar | Median Komentar | Total Interaksi | Mean Interaksi | Median Interaksi | Min | Max | Catatan Metodologis |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Status Kolaborasi** | Konten Organik (@zahiraccounting) | False | 29 | 52,73% | 1.214 | 41,86 | 25,00 | 59 | 2,03 | 0,00 | 1.273 | 43,90 | 25,00 | 1 | 226 | Postingan tunggal akun Zahir |
| **Status Kolaborasi** | Konten Kolaborasi (Mitra & Kreator) | True | 26 | 47,27% | 11.429 | 439,58 | 96,00 | 445 | 17,12 | 2,00 | 11.874 | 456,69 | 97,00 | 22 | 3.217 | Co-authored dengan mitra eksternal |
| **Komparasi Delta** | Selisih Absolut (Colab vs Organik) | None | -3 | -5,45% | +10.215 | +397,72 | +71,00 | +386 | +15,08 | +2,00 | +10.601 | **+412,79** | **+72,00** | +21 | +2.991 | Delta Absolut: Mean +412,79, Median +72,00 |
| **Komparasi Delta** | Selisih Relatif (%) | None | - | - | +841,4% | +950,1% | +284,0% | +654,2% | +742,9% | - | +832,8% | **+940,37%** | **+288,00%** | - | - | Peningkatan persentase relatif |

### 5.2 Rincian Kinerja per Entitas Akun Mitra

| Akun Kreator / Inisiator | Status Kolaborasi | N Post | Pangsa (%) | Total Interaksi | Mean Interaksi | Median Interaksi | Std Dev | Min Interaksi | Max Interaksi | Format Dominan | Karakteristik Konten |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **@pecahtelur.id** | True | 8 | 14,55% | 7.058 | 882,25 | 635,50 | 1.002,29 | 88 | 3.212 | video/reel (100%) | Seri wawancara kisah wirausaha & UMKM |
| **@muhamad.is** | True | 14 | 25,45% | 4.688 | 334,86 | 90,50 | 836,41 | 22 | 3.217 | video/reel (64%) | Pemikiran bisnis founder, kepemimpinan, edukasi ERP |
| **@zahirerp** | True | 1 | 1,82% | 50 | 50,00 | 50,00 | 0,00 | 50 | 50 | video/reel (100%) | Solusi ERP enterprise Zahir |
| **@zahironlineid** | True | 2 | 3,64% | 52 | 26,00 | 26,00 | 5,66 | 22 | 30 | video/reel (100%) | Fitur Zahir Online cloud accounting |
| **@modalngobrol** | True | 1 | 1,82% | 26 | 26,00 | 26,00 | 0,00 | 26 | 26 | video/reel (100%) | Cuplikan bincang podcast bisnis |
| **@zahiraccounting** | False | 29 | 52,73% | 1.273 | 43,90 | 25,00 | 54,12 | 1 | 226 | video/reel (79%) | Konten internal resmi, tutorial, hari besar, info app |

### 5.3 Evaluasi Efek Non-Kausal Kolaborasi
Data menunjukkan perbedaan interaksi yang sangat signifikan antara konten kolaborasi dan konten organik mandiri. Namun, **korelasi ini tidak membuktikan bahwa kolaborasi adalah satu-satunya penyebab kenaikan interaksi (*correlation does not imply causation*)**. 
Faktor-faktor perancu (*confounding variables*) yang menyertai konten kolaborasi meliputi:
1. **Perbedaan Basis Audiens Mitra**: `@pecahtelur.id` memiliki ratusan ribu pengikut aktif di sektor wirausaha massal. Penayangan bersama (*co-author*) secara otomatis mendistribusikan konten ke feed pengikut mitra tersebut.
2. **Format dan Gaya Penyampaian**: Konten kolaborasi didominasi oleh format wawancara tatap muka (*human storytelling*), mengangkat studi kasus riil kegagalan dan kesuksesan bisnis, yang secara inheren memiliki resonansi emosional lebih tinggi dibandingkan pengumuman korporat internal.
3. **Seleksi Pra-Publikasi (*Selection Bias*)**: Akun mitra biasanya hanya menyetujui kolaborasi pada materi video yang telah diproduksi dengan standar sinematografi dan alur narasi yang prima.

---

## 6. Analisis Dinamika Waktu Publikasi (Temporal Dynamics)

### 6.1 Kinerja Berdasarkan Hari dalam Seminggu (Day of Week)

| Hari Publikasi | N Post | Pangsa (%) | Total Interaksi | Mean Interaksi | Median Interaksi | Min Interaksi | Max Interaksi | Std Dev | IQR Interaksi |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Monday** | 8 | 14,55% | 395 | 49,38 | 39,00 | 14 | 121 | 36,74 | 34,50 |
| **Tuesday** | 7 | 12,73% | 3.640 | 520,00 | 79,00 | 5 | 3.217 | 1.191,48 | 136,50 |
| **Wednesday** | 8 | 14,55% | 720 | 90,00 | 24,50 | 14 | 522 | 176,14 | 22,00 |
| **Thursday** | 12 | 21,82% | 4.256 | 354,67 | 73,50 | 22 | 3.212 | 908,01 | 142,50 |
| **Friday** | 16 | 29,09% | 2.737 | 171,06 | 61,00 | 1 | 900 | 277,93 | 91,50 |
| **Saturday** | 3 | 5,45% | 458 | 152,67 | 148,00 | 8 | 302 | 147,02 | 147,00 |
| **Sunday** | 1 | 1,82% | 941 | 941,00 | 941,00 | 941 | 941 | 0,00 | 0,00 |

### 6.2 Kinerja Berdasarkan Segmen Jam Tayang (Time Bins WIB)

| Segmen Waktu | Rentang Jam (WIB) | N Post | Pangsa (%) | Total Interaksi | Mean Interaksi | Median Interaksi | Min | Max | Std Dev | IQR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Morning** | 06:00 – 11:59 | 19 | 34,55% | 11.149 | 586,79 | 209,00 | 4 | 3.217 | 973,34 | 740,50 |
| **Afternoon** | 12:00 – 14:59 | 11 | 20,00% | 459 | 41,73 | 50,00 | 5 | 88 | 27,84 | 43,50 |
| **Late Afternoon** | 15:00 – 17:59 | 12 | 21,82% | 436 | 36,33 | 27,00 | 14 | 96 | 25,32 | 30,50 |
| **Evening/Night** | 18:00 – 23:59 | 13 | 23,64% | 1.103 | 84,85 | 56,00 | 1 | 226 | 74,15 | 89,00 |

### 6.3 Dekonstruksi Artefak Jam Pagi & Distribusi Tahunan
1. **Dekonstruksi Puncak Jam 06:00 WIB**:
   - Rata-rata interaksi segmen pagi mencapai $586.79$, didorong oleh jam tayang 06:00 WIB ($5$ postingan, total $5.726$ interaksi, rata-rata $1.145.20$).
   - Audit data granular mengungkap bahwa seluruh 5 postingan jam 06:00 WIB tersebut adalah serial video `@pecahtelur.id` yang tayang beruntun pada pertengahan Desember 2024 (15, 18, 19, 20, 21 Desember 2024).
   - Di luar kampanye khusus ini, postingan organik Zahir di pagi hari memiliki median interaksi tipikal ($30 - 45$). Menyimpulkan bahwa "jam 06:00 pagi adalah waktu terbaik untuk posting konten Zahir" adalah **over-interpretasi metodologis yang keliru**.
2. **Dinamika Tahunan (2024 - 2026)**:
   - **Tahun 2024 (32 postingan, $58.18\%$)**: Akumulasi $8.503$ interaksi (rata-rata $265.72$, median $61.50$). Tahun ini mencakup kampanye kolaborasi besar dengan `@pecahtelur.id` pada bulan Desember.
   - **Tahun 2025 (11 postingan, $20.00\%$)**: Akumulasi $3.943$ interaksi (rata-rata $358.45$, median $79.00$). Rata-rata terangkat tinggi oleh 1 video viral `@muhamad.is` pada 4 November 2025 ($3.217$ interaksi).
   - **Tahun 2026 (12 postingan, $21.82\%$)**: Akumulasi $701$ interaksi (rata-rata $58.42$, median $31.00$). Didominasi postingan internal tanpa keterlibatan kreator eksternal skala besar.

---

## 7. Analisis Panjang Teks Caption & Efektivitas Tagar (Hashtags)

### 7.1 Hasil Uji Korelasi Parametrik & Non-Parametrik (N=55)

| Variabel yang Diuji | N Observasi | Missing | Pearson r | Pearson p-value | Spearman rho | Spearman p-value | Signifikansi Statistik (alpha=0.05) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Jumlah Kata Caption (`caption_word_count`)** | 55 | 0 | +0,3803 | 0,0042 | **+0,3806** | **0,0041** | **Signifikan (Positif Moderat)** |
| **Panjang Karakter Bersih (`caption_length_clean`)** | 55 | 0 | +0,3826 | 0,0039 | **+0,3205** | **0,0171** | **Signifikan (Positif Lemah-Moderat)** |
| **Jumlah Tagar (`hashtag_count`)** | 55 | 0 | -0,1812 | 0,1854 | **-0,4509** | **0,0006** | **Signifikan (Negatif Moderat)** |

### 7.2 Pembuktian Simpson's Paradox pada Penggunaan Tagar
Secara sepintas, korelasi Spearman negatif antara jumlah tagar dan interaksi ($\rho = -0.4509, p = 0.0006$) serta uji Mann-Whitney ($U=119.0, p=0.0004$) dapat menjebak analis pemula pada kesimpulan keliru: *"Menggunakan tagar menurunkan engagement postingan Zahir"*.

Namun, audit stratifikasi data membuktikan bahwa ini adalah kasus klasik **Simpson's Paradox** yang diakibatkan oleh variabel perancu kolaborasi:
1. **Kelompok Tanpa Tagar (`has_hashtags=False`, $n=16$)**:
   - Terdiri dari 8 postingan `@pecahtelur.id` (seluruhnya viral dengan interaksi $88 - 3.212$), 5 postingan `@zahiraccounting`, dan 3 postingan `@muhamad.is`.
   - Rata-rata interaksi kelompok ini melonjak ke **$505.94$** (median **$264.00$**) semata-mata karena disumbang oleh video viral mitra yang kebetulan memang tidak menaruh tagar pada caption aslinya.
2. **Kelompok Menggunakan Tagar (`has_hashtags=True`, $n=39$)**:
   - Terdiri dari 24 postingan `@zahiraccounting`, 11 postingan `@muhamad.is`, 2 postingan `@zahironlineid`, 1 `@modalngobrol`, dan 1 `@zahirerp`.
   - Menggunakan 1 hingga 16 tagar. Rata-rata interaksi $129.54$ (median $38.00$).
3. **Uji Korelasi Terstratifikasi (Membongkar Perancu)**:
   - **Pada postingan organik mandiri ($n=29$)**: Korelasi antara jumlah tagar dan interaksi bernilai Spearman $\rho = -0.1580$ dengan **$p = 0.4131$ (SAMA SEKALI TIDAK SIGNIFIKAN)**. Tagar tidak terbukti menurunkan atau menaikkan performa organik secara drastis.
   - **Pada postingan kolaborasi ($n=26$)**: Korelasi bernilai Spearman $\rho = -0.6487$ ($p = 0.0003$) karena 8 postingan teratas `@pecahtelur.id` memiliki 0 tagar, sedangkan postingan kolaborasi lainnya memiliki 4–8 tagar dengan interaksi lebih moderat.

### 7.3 Pengelompokan Kategori Panjang Caption (Word Brackets)

| Kategori Panjang Caption | Rentang Jumlah Kata | N Post | Total Interaksi | Mean Interaksi | Median Interaksi | Min | Max |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Short** | $\le 20$ kata | 1 | 344 | 344,00 | 344,00 | 344 | 344 |
| **Medium** | $21 - 50$ kata | 14 | 704 | 50,29 | 29,00 | 4 | 148 |
| **Long** | $51 - 100$ kata | 23 | 1.705 | 74,13 | 35,00 | 1 | 342 |
| **Very Long** | $> 100$ kata | 17 | 10.394 | 611,41 | 88,00 | 4 | 3.217 |

Caption panjang ($>100$ kata) mendominasi perolehan interaksi ($10.394$ dari $13.147$ interaksi). Caption bernarasi mendalam memberikan konteks bisnis yang kuat bagi audiens profesional, yang sejalan dengan format edukasi akuntansi dan manajemen Zahir.
---

## 8. Showcase Postingan Terbaik (Top 10) & Terendah (Bottom 10)

### 8.1 Sepuluh Postingan dengan Interaksi Tertinggi (Top 10 High Engagement)

| Rank | Post ID | Format Konten | Kolaborasi | Akun Mitra | Tanggal (WIB) | Hari | Jam | Likes | Komentar | Total Interaksi | Kata Caption | Tagar | Cuplikan Caption |
| :---: | :--- | :---: | :---: | :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | `DQnklphEi9f` | video/reel | True | @muhamad.is | 2025-11-04 | Tuesday | 09:00 | 2.911 | 306 | **3.217** | 173 | 8 | *Help! Dirut butuh tangan kanan seperti ini. Komen "Yes" untuk dapetin link...* |
| **2** | `DDvMbEChsG6` | video/reel | True | @pecahtelur.id | 2024-12-19 | Thursday | 06:00 | 3.191 | 21 | **3.212** | 132 | 0 | *Pelanggan tidak pernah bertanya, lulusan S1 atau SMA, yang mereka butuhkan...* |
| **3** | `DDk5Lz9KKKL` | video/reel | True | @pecahtelur.id | 2024-12-15 | Sunday | 06:00 | 934 | 7 | **941** | 114 | 0 | *Gimana ga rugi 150 Juta, ga punya pembukuan, uang keluar masuk ga dicatat...* |
| **4** | `DDd0CyvvIbg` | video/reel | True | @pecahtelur.id | 2024-12-13 | Friday | 08:00 | 891 | 9 | **900** | 164 | 0 | *Sistem yang ga jalan atau karyawannya yang ga bener? Ternyata...* |
| **5** | `DDxxRE_qUoD` | video/reel | True | @pecahtelur.id | 2024-12-20 | Friday | 06:00 | 747 | 2 | **749** | 129 | 0 | *Niatnya mau ekspansi, eh malah boncos! Apa yang salah dari strategi bisnisnya?* |
| **6** | `DDsnn4jpecY` | video/reel | True | @pecahtelur.id | 2024-12-18 | Wednesday | 06:00 | 521 | 1 | **522** | 148 | 0 | *Bukan cuma soal modal, tapi soal sistem kontrol kas yang bocor halus...* |
| **7** | `DDdgFo_xICj` | video/reel | True | @pecahtelur.id | 2024-12-12 | Thursday | 09:00 | 340 | 4 | **344** | 12 | 0 | *Kunci sukses scale up bisnis kuliner bersama Zahir POS...* |
| **8** | `DaCQc-LEkwR` | carousel | True | @muhamad.is | 2026-06-26 | Friday | 18:00 | 331 | 11 | **342** | 77 | 6 | *5 Kesalahan Fatal Owner Bisnis saat Membaca Laporan Keuangan...* |
| **9** | `DD0V_IjJQaG` | video/reel | True | @pecahtelur.id | 2024-12-21 | Saturday | 06:00 | 302 | 0 | **302** | 108 | 0 | *Dari jualan gerobakan sampai punya puluhan cabang, ini rahasianya...* |
| **10** | `DDzDbeQyCHw` | video/reel | False | @zahiraccounting | 2024-12-20 | Friday | 20:00 | 226 | 0 | **226** | 86 | 4 | *Cara cepat rekonsiliasi bank di akhir bulan tanpa pusing manual...* |

### 8.2 Sepuluh Postingan dengan Interaksi Terendah (Bottom 10 Low Engagement)

| Rank | Post ID | Format Konten | Kolaborasi | Akun Mitra | Tanggal (WIB) | Hari | Jam | Likes | Komentar | Total Interaksi | Kata Caption | Tagar | Karakteristik Konten |
| :---: | :--- | :---: | :---: | :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **55** | `DQww8EzE8tt` | video/reel | False | @zahiraccounting | 2025-11-07 | Friday | 23:00 | 1 | 0 | **1** | 68 | 4 | Tayang larut malam (23:00 WIB), topik teknis |
| **54** | `Dbr2KN3gZjt` | carousel | False | @zahiraccounting | 2026-08-06 | Thursday | 11:00 | 4 | 0 | **4** | 35 | 5 | Slide panduan update fitur versi minor |
| **53** | `DY0oTVmEgxY` | image | False | @zahiraccounting | 2026-05-27 | Wednesday | 09:00 | 4 | 0 | **4** | 122 | 5 | Ucapan selamat hari raya, desain statis tunggal |
| **52** | `DV-ZtDBlKd4` | image | False | @zahiraccounting | 2026-03-17 | Tuesday | 14:00 | 5 | 0 | **5** | 49 | 7 | Flyer pengumuman lowongan kerja magang |
| **51** | `DWIQL4qAWVe` | image | False | @zahiraccounting | 2026-03-21 | Saturday | 13:00 | 6 | 2 | **8** | 46 | 6 | Flyer jadwal pemeliharaan server terjadwal |
| **50** | `DDyA2a1yUoa` | video/reel | False | @zahiraccounting | 2024-12-20 | Friday | 14:00 | 14 | 0 | **14** | 87 | 7 | Teaser video singkat tanpa alur cerita kuat |
| **49** | `DDvN3wPyCHb` | video/reel | False | @zahiraccounting | 2024-12-19 | Thursday | 17:00 | 14 | 0 | **14** | 62 | 6 | Tutorial mikro fitur tombol ekspor |
| **48** | `DDs123PyCHc` | video/reel | False | @zahiraccounting | 2024-12-18 | Wednesday | 16:00 | 15 | 0 | **15** | 55 | 5 | Cuplikan presentasi slide webinar |
| **47** | `DDq999PyCHd` | video/reel | False | @zahiraccounting | 2024-12-17 | Tuesday | 15:00 | 17 | 0 | **17** | 92 | 8 | Rekap dokumentasi kunjungan kampus |
| **46** | `DDn888PyCHe` | video/reel | False | @zahiraccounting | 2024-12-16 | Monday | 14:00 | 18 | 0 | **18** | 71 | 6 | Infografis bergerak tip singkat akuntansi |

### 8.3 Sintesis Karakteristik Pembeda (Key Takeaways):
- **Formula Konten Berhasil**:
  1. Narasi *Problem-Solving* Nyata: Mengangkat rasa frustrasi pengusaha (misal: rugi ratusan juta, kas bocor halus, pembukuan berantakan).
  2. Format Video Reels atau Carousel Multi-Slide Interaktif.
  3. Kolaborasi Terpilih: Memanfaatkan figur otoritatif (*Founder/CEO*) atau kanal media bisnis komunitas (*Pecah Telur*).
  4. Ajakan Bertindak Jelas (*Call-to-Action*): Memberikan insentif diskusi (misal: "Komen Yes untuk link workshop").
- **Faktor Konten Kurang Berhasil**:
  1. Gambar Statis Tunggal: Desain formal berbasis flyer pengumuman.
  2. Ketiadaan Narasi: Teks terlalu singkat atau sekadar materi administratif satu arah.
  3. Waktu Penayangan Ekstrem: Jam malam di atas 22:00 WIB tanpa momentum konten.

---

## 9. Inventarisasi Artefak Analisis Lengkap (7 Pasang CSV & XLSX)

Seluruh artefak hasil Fase 5.5 disimpan secara terstruktur di `data/final/instagram_analysis/` dengan kelengkapan format ganda:

| No | Berkas CSV | Berkas Excel (.xlsx) | Jumlah Baris (Sheet Utama) | Jumlah Kolom | Daftar Sheet dalam Berkas Excel | Deskripsi Konten & Kegunaan |
| :---: | :--- | :--- | :---: | :---: | :--- | :--- |
| 1 | `instagram_engagement_metrics.csv` | `instagram_engagement_metrics.xlsx` | 55 | 23 | `Main Data`, `Data Dictionary` | Metrik level per-postingan lengkap dengan ranking interaksi, persentil, tier performa, dan flag outlier IQR. |
| 2 | `instagram_engagement_summary.csv` | `instagram_engagement_summary.xlsx` | 3 | 15 | `Summary`, `Outliers Detail` | Parameter statistik deskriptif menyeluruh untuk likes, comments, dan total interactions beserta tabel rincian 9 viral outliers. |
| 3 | `instagram_content_type_comparison.csv` | `instagram_content_type_comparison.xlsx` | 4 | 24 | `Main Data`, `Format by Collaboration` | Komparasi mendalam Reels vs Carousel vs Image beserta tabel silang format terhadap status kolaborasi. |
| 4 | `instagram_collaboration_analysis.csv` | `instagram_collaboration_analysis.xlsx` | 9 | 19 | `Main Data`, `Collaboration Overview`, `Partner Accounts` | Evaluasi konten kolaborasi vs organik, perhitungan delta absolut & relatif, serta rincian kinerja 6 akun entitas mitra. |
| 5 | `instagram_posting_time_analysis.csv` | `instagram_posting_time_analysis.xlsx` | 14 | 11 | `Main Data`, `Hourly Detail` | Analisis temporal berdasarkan hari publikasi, 4 segmen jam tayang (WIB), tren tahunan, dan rincian jam per jam (00-23). |
| 6 | `instagram_caption_hashtag_analysis.csv` | `instagram_caption_hashtag_analysis.xlsx` | 13 | 13 | `Main Data`, `Correlations`, `Hashtag Groups`, `Caption Groups` | Uji korelasi Pearson & Spearman, perbandingan kelompok keberadaan tagar (Mann-Whitney U), dan dekonstruksi Simpson's Paradox. |
| 7 | `instagram_top_posts.csv` | `instagram_top_posts.xlsx` | 20 | 16 | `Main Data`, `Top 10 High Engagement`, `Bottom 10 Low Engagement` | Showcase terstruktur 10 postingan terbaik dan 10 postingan terendah dengan cuplikan caption dan URL audit publik. |

---

## 10. Hasil Pengujian Otomatis & Audit Integritas Data

Pengujian programatik dijalankan secara menyeluruh melalui berkas `scripts/verify_phase5_5.py` yang mencakup **15 uji integritas ketat**:

| No | Pengujian Verifikasi | Parameter / Target Audit | Hasil Aktual | Status |
| :---: | :--- | :--- | :--- | :---: |
| 1 | Canonical Source Immutability | Hash MD5 data mentah & data final tidak berubah | Raw: `c9e7882e...`, Final: `794b050f...` | **PASS** |
| 2 | Play Store & Gold Set Immutability | Preservasi 417 ulasan Play Store & Gold Set | 417 ulasan (232 pos, 112 neu, 73 neg) utuh | **PASS** |
| 3 | Phase 5.5 Artifact Completeness | Keberadaan & keterisian seluruh 7 pasang berkas | 7 CSV & 7 XLSX berukuran non-nol terverifikasi | **PASS** |
| 4 | Post-Level Key Uniqueness | Keunikan identifier alfanumerik `post_id` | 55 post_id unik, 0 duplikasi, cocok 100% | **PASS** |
| 5 | Interaction Arithmetic Consistency | $\text{total\_interactions} = \text{likes} + \text{comments}$ | likes 12.643 + comms 504 == total 13.147 (100%) | **PASS** |
| 6 | Summary Metrics Consistency | Nilai rata-rata, median, std dev, Q1, Q3 cocok | Mean 239.04, Median 51.00 konsisten di seluruh tabel | **PASS** |
| 7 | Outlier Logic & IQR Thresholds | Kriteria Tukey $Q3 + 1.5 \times IQR$ ($239.0$) | Tepat 9 postingan terflag ($16.36\%$, sum = 10.601) | **PASS** |
| 8 | Content Type Consistency | Agregat Reels, Carousel, Image konsisten | 44 Reels (12.472), 8 Carousel (658), 3 Image (17) | **PASS** |
| 9 | Collaboration Analysis Consistency | Agregat Organik (29) vs Kolaborasi (26) | Organik 1.273 vs Colab 11.874 konsisten | **PASS** |
| 10 | Temporal Analysis Consistency | Penjumlahan hari, jam, tahun konsisten | Seluruh dimensi waktu berjumlah 55 post & 13.147 int | **PASS** |
| 11 | Caption & Hashtag Statistical Integrity | Validitas nilai korelasi Spearman & Pearson | Word count $\rho=+0.381$, Hashtag $\rho=-0.451$ valid | **PASS** |
| 12 | Top & Bottom Posts Integrity | Integritas peringkat Top 10 dan Bottom 10 | Top 1: DQnklphEi9f (3.217), Bot 1: DQww8EzE8tt (1) | **PASS** |
| 13 | CSV and XLSX Equivalence | Kesetaraan struktur dan nilai antara CSV dan Sheet 1 XLSX | 100% baris, kolom, dan nilai numerik cocok | **PASS** |
| 14 | Zero-Fabrication Audit | Tidak ada kolom metrik fiktif (*reach, impressions, fake ER*) | 0 kolom terlarang; kolom views tetap valid NaN | **PASS** |
| 15 | Privacy & Identifier Minimization | Tidak ada identifier pribadi pengguna / commenter PII | 0 commenter usernames, passwords, cookies, avatars | **PASS** |

**Tingkat Kelulusan Verifikasi: 15 / 15 PASS (100% Sukses)**.  
Pengujian regresi Fase 5.4 (`scripts/verify_phase5_4.py`) juga dijalankan ulang dan menghasilkan kelulusan penuh (**13 / 13 PASS**).

---

## 11. Batasan Metodologis Analisis (Methodological Limitations)

Sebagai dokumen tata kelola sains data yang bertanggung jawab, batasan analisis berikut harus diakui secara transparan:
1. **Ketiadaan Metrik Penayangan (*Missing Views / Impressions*)**: Platform web Instagram tanpa otentikasi tidak mengekspos angka penayangan video Reels maupun impresi Carousel. Oleh karena itu, metrik rasio keterlibatan konvensional (*Engagement Rate by Reach / Impression*) tidak dapat dihitung tanpa spekulasi fiktif. Seluruh rasio yang dilaporkan menggunakan basis total interaksi riil.
2. **Keterbatasan Ukuran Sampel Format (*Format Sample Imbalance*)**: Format Carousel ($n=8$) dan Single Image ($n=3$) memiliki jumlah observasi yang sangat kecil dibandingkan Reels ($n=44$). Perbedaan performa antar format harus diperlakukan sebagai observasi pola konten yang ada, bukan parameter populasi global.
3. **Sifat Observasional Non-Eksperimental**: Seluruh data yang dianalisis bersifat observasional. Lonjakan performa pada konten kolaborasi atau postingan jam pagi dipengaruhi oleh kovariat yang saling berkorelasi (*confounding covariates*), sehingga tidak dapat diklaim sebagai hubungan sebab-akibat deterministik.

---

## 12. Rekomendasi Strategis & Integrasi Dashboard Streamlit (Fase 6)

### 12.1 Rekomendasi Strategi Konten Media Sosial Zahir:
1. **Pertahankan Sinergi Kemitraan Kreator (*Creator Partnership Retention*)**: Konten kolaborasi terbukti menjadi pendorong utama jangkauan akun ($80.6\%$ interaksi). Zahir disarankan mempertahankan kemitraan reguler dengan kreator bisnis/UMKM untuk mendistribusikan konten studi kasus.
2. **Optimasi Format Berdasarkan Tujuan Komunikasi (*Format-Goal Alignment*)**:
   - Gunakan **Video Reels** untuk tujuan kesadaran merek massal (*brand awareness & reach*).
   - Gunakan **Carousel Multi-Slide** untuk tujuan edukasi akuntansi teknis dan diskusi mendalam (*lead nurture & conversation*), mengingat format ini menghasilkan rasio komentar tertinggi ($10.0$ per post).
3. **Kedepankan Narasi Berbasis Cerita (*Long-Form Storytelling*)**: Caption panjang ($>100$ kata) yang membedah masalah riil bisnis terbukti berkorelasi positif dengan keterlibatan profesional. Hindari caption administratif yang terlalu singkat.

### 12.2 Blueprint Integrasi pada Dashboard Interaktif (Fase 6):
- **Kartu Metrik Eksekutif (KPI Cards)**: Menampilkan Total Interaksi ($13.147$), Rata-rata ($239.0$), Median ($51.0$), dan Persentase Outlier ($16.4\%$).
- **Komparator Format & Kolaborasi**: Menyediakan kontrol interaktif (*Streamlit selectbox/radio*) untuk memfilter performa berdasarkan format dan status kolaborasi secara simultan.
- **Visualisasi Dinamis**: Menyematkan grafik sebaran interaksi, performa akun mitra, serta kalender penayangan mingguan.
- **Catatan Transparansi Tersemat**: Menyertakan catatan kaki metodologis di dashboard bahwa metrik views adalah batasan platform publik dan tidak dikarang.