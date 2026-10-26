# Laporan Analisis Aspek Produk & Customer Voice Extraction (Fase 5.2)
**Zahir Social Analytics — Play Store Customer Voice Analytics**  
**Audit & Execution Date:** 2026-10-26  
**Status Metodologis:** Selesai & Tervalidasi Otomatis (100% Passed)  
**Referensi Data:** `data/final/playstore_reviews_final.csv` (Teks Bersih) & `data/final/playstore_gold_set_final.csv` (Label Sentimen Manusia)

---

## 1. Ringkasan Eksekutif & Tujuan
Fase 5.2 bertujuan membangun pipeline ekstraksi aspek berbasis aturan kata kunci (*Keyword/Rule-Based Aspect-Based Sentiment Analysis / ABSA*) yang transparan dan dapat direproduksi pada **417 Ulasan Google Play Store Ekosistem Zahir**.

Berdasarkan hasil Audit Kesiapan Fase 5.1:
- Korpus mikro (*N=417*) dengan dominansi teks pendek ($\le 5$ kata: 38.6%) tidak cocok untuk model clustering tanpa supervisi (seperti BERTopic atau K-Means murni).
- Oleh karena itu, pendekatan berbasis taksonomi modul bisnis terstruktur (*Domain-Verified Rule-Based ABSA*) diimplementasikan sebagai metode utama.
- **Autoritas Sentimen**: Label sentimen manusia (`human_sentiment_label`) dari Gold Set menjadi acuan kebenaran mutlak; skor bintang **tidak pernah digunakan** untuk menginferensi aspek atau polaritas.
- Fokus analitik diarahkan pada **Scope B (185 Ulasan Negatif dan Netral)** untuk membedah titik hambatan pelanggan (*Customer Pain Points*), didampingi **Scope C** untuk analisis kontras fitur yang diapresiasi vs yang dikeluhkan.

---

## 2. Arsitektur Taksonomi 8 Aspek Produk Zahir
Taksonomi diformalkan dalam file konfigurasi `config/aspect_taxonomy.json` dan memetakan 193 aturan kata kunci/variasi frasa:

1. **Authentication & Access (`login_auth`)**:
   - *Fokus*: Otentikasi pengguna, pembuatan akun, kata sandi, verifikasi OTP, dan sesi login.
   - *Penanganan Ambiguitas*: Kata `akun` dipasangkan dengan konteks registrasi/akses guna menghindari kerancuan dengan bagan akun akuntansi (*chart of accounts / nama akun kas*).
2. **System Stability & Crash (`crash_stability`)**:
   - *Fokus*: Penutupan mendadak (*force close*), layar membeku (*hang/freeze*), *loading* berkepanjangan, aplikasi *ngelag*, dan pesan *error* sistem.
   - *Penanganan Ambiguitas*: Kata `close` dipasangkan dengan predikat (*force close, close sendiri, auto close*) agar tidak tertukar dengan tutup buku akuntansi (*period closing*).
3. **Pricing & Subscription (`pricing_subscription`)**:
   - *Fokus*: Model monetisasi aplikasi, biaya langganan bulanan/tahunan, transparansi masa uji coba (*trial*), dan perpanjangan lisensi.
   - *Penanganan Ambiguitas*: Kata `bayar` dalam aplikasi kasir (POS) dibedakan dari pembayaran langganan aplikasi.
4. **Cloud & Database Synchronization (`sync_cloud_data`)**:
   - *Fokus*: Sinkronisasi data multi-perangkat (mobile ke web/desktop), konektivitas database cloud, kegagalan backup/restore, dan kehilangan data riwayat transaksi.
   - *Penanganan Ambiguitas*: Kata `data` wajib muncul bersama kata kerja sinkronisasi, simpan, atau kehilangan data (*data hilang, data tidak tersimpan*).
5. **POS & Hardware Printing (`pos_hardware_print`)**:
   - *Fokus*: Integrasi perangkat keras kasir, konektivitas printer thermal Bluetooth, pencetakan struk/nota transaksi, pemindai barcode, dan laci uang (*cash drawer*).
   - *Penanganan Ambiguitas*: Kata `pos` dicocokkan dengan batas kata (*word boundary*) untuk mencegah kecocokan parsial dengan kata seperti 'posisi'.
6. **Core Accounting & Inventory (`inventory_accounting`)**:
   - *Fokus*: Fitur inti akuntansi: pencatatan transaksi penjualan/pembelian, manajemen stok barang, laporan laba rugi, neraca, faktur/invoice, hutang, dan piutang.
   - *Penanganan Ambiguitas*: Mengakomodasi istilah teknis akuntansi dan singkatan dokumen bisnis (*po = purchase order*).
7. **Certification Exam Engine (`certification_exam`)**:
   - *Fokus*: Fitur aplikasi *Zahir Certification*: navigasi soal ujian kompetensi (*ujikom*), batasan waktu pengerjaan, kalkulasi nilai/skor, dan penerbitan sertifikat digital.
   - *Penanganan Ambiguitas*: Kata `nilai` dicocokkan dalam konteks ujian/skor kelulusan, bukan penilaian aset finansial.
8. **Face Attendance & Geolocation (`attendance_face`)**:
   - *Fokus*: Fitur aplikasi *Zahir Attendance*: validasi biometrik wajah, swafoto (*selfie*), deteksi titik koordinat GPS, dan pencatatan jam kerja (*clock-in / clock-out*).
   - *Penanganan Ambiguitas*: Kata `lokasi` dan `kamera` dipasangkan dengan konteks presensi kerja.

---

## 3. Temuan Kuantitatif Scope A: Cakupan Aspek Seluruh Ulasan (N=417)

Dari 417 ulasan yang dianalisis secara multi-label:
- **154 ulasan (36.93%)** memuat setidaknya 1 aspek produk konkret.
- Sebanyak **263 ulasan (63.07%)** tidak memuat aspek spesifik (didominasi 181 ulasan positif pendek non-aspek seperti *"Mantap"*, *"Bagus"*, *"Good"*).

| Aspek Produk | Total Mentions | % dari Korpus (N=417) | Negatif | Netral | Positif | Aplikasi Terbanyak | Kata Kunci Teratas |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| **Core Accounting & Inventory** | **71** | **17.03%** | 16 | 15 | 40 | Zahir Simple Start (36) | transaksi (29), barang (19), laporan (13), stok (10) |
| **Authentication & Access** | **41** | **9.83%** | 20 | 20 | 1 | Zahir Certification (19) | masuk (13), akun (13), login (8), daftar (7) |
| **Pricing & Subscription** | **40** | **9.59%** | 17 | 16 | 7 | Zahir Simple Start (16) | bayar (18), gratis (15), langganan (7), biaya (3) |
| **System Stability & Crash** | **37** | **8.87%** | 21 | 12 | 4 | Zahir Online (18) | error (20), force close (6), keluar sendiri (5), loading (4) |
| **POS & Hardware Printing** | **18** | **4.32%** | 2 | 8 | 8 | POS X (14) | cetak (8), pos (5), print (3), printer (3) |
| **Cloud & Database Sync** | **15** | **3.60%** | 5 | 2 | 8 | Zahir Simple Start (6) | server (7), cloud (4), sync (2), sinkron (2) |
| **Certification Exam Engine** | **12** | **2.88%** | 4 | 8 | 0 | Zahir Certification (12) | ujian (5), soal (5), sertifikasi (3), sertifikat (2) |
| **Face Attendance & Geolocation** | **8** | **1.92%** | 3 | 2 | 3 | Zahir Attendance (7) | absen (4), absensi (3), wajah (2), presensi (1) |

*Catatan Metodologis*: Ulasan yang memuat beberapa aspek dihitung pada masing-masing aspek yang relevan (*multi-label non-mutually exclusive*).

---

## 4. Temuan Kunci Scope B: Customer Pain Points (Negative + Neutral, N=185)

Pada subset 185 ulasan keluhan dan pertanyaan pengguna, cakupan aspek mencapai **65.41% (121 ulasan)**. Tabel ini memetakan titik hambatan kritis pelanggan:

| Peringkat Pain Point | Aspek Produk | Jumlah Ulasan (N=185) | % Pain Points | Keluhan Negatif | Pertanyaan Netral | Aplikasi Dominan | Interpretasi Customer Voice |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| **#1** | **Authentication & Access** | **40** | **21.62%** | **20** | **20** | *Zahir Certification* (19) & *Zahir Online* (10) | Hambatan login massal saat ujian sertifikasi ("user not allowed", registrasi gagal) dan akun ter-logout sendiri di Zahir Online. |
| **#2** | **System Stability & Crash** | **33** | **17.84%** | **21** | **12** | *Zahir Online* (16) & *Zahir Certification* (9) | Keluhan force close dan aplikasi tertutup sendiri saat input data transaksi dan saat ujian kompetensi berlangsung. |
| **#3** | **Pricing & Subscription** | **33** | **17.84%** | **17** | **16** | *Zahir Simple Start* (14) & *Zahir Online* (9) | Kekecewaan terhadap transparansi monetisasi ("ujung-ujungnya bayar", biaya langganan dinilai mahal untuk UMKM pemula). |
| **#4** | **Core Accounting & Inventory** | **31** | **16.76%** | **16** | **15** | *Zahir Online* (12) & *Zahir Simple Start* (10) | Kesulitan penyesuaian stok barang, pembatalan transaksi, dan kendala pembuatan Purchase Order (PO) pada aplikasi mobile. |
| **#5** | **Certification Exam Engine** | **12** | **6.49%** | **4** | **8** | *Zahir Certification* (12) | Pertanyaan terkait sertifikat yang belum terbit, waktu ujian yang terpotong akibat sistem lag, dan kode referal ujian. |
| **#6** | **POS & Hardware Printing** | **10** | **5.41%** | **2** | **8** | *POS X* (8) | Pertanyaan teknis dan kendala pencocokan printer thermal Bluetooth untuk mencetak struk kasir. |
| **#7** | **Cloud & Database Sync** | **7** | **3.78%** | **5** | **2** | *Zahir Online* (4) | Isu kritis kehilangan data transaksi lokal setelah sinkronisasi server gagal (*data hilang/tidak tersimpan*). |
| **#8** | **Face Attendance & Geolocation** | **5** | **2.70%** | **3** | **2** | *Zahir Attendance* (4) | Kegagalan deteksi wajah dan verifikasi radius GPS saat jam masuk kerja. |

---

## 5. Analisis Kontras Scope C: Apresiasi vs Keluhan (Positif vs Negatif)

Membandingkan tingkat kemunculan aspek pada kelompok ulasan Negatif (*n=73*) versus kelompok Positif (*n=232*):

| Aspek Produk | Rate pada Negatif (%) | Rate pada Positif (%) | Rasio Pos/Neg | Pola Kontras | Wawasan Strategis Bisnis |
| :--- | :---: | :---: | :---: | :--- | :--- |
| **System Stability & Crash** | **28.77%** (21 ulasan) | **1.72%** (4 ulasan) | **0.19** | **Dominansi Keluhan Ekstrem** | Titik kerapuhan sistem tertinggi; stabilitas aplikasi mobile menjadi prioritas perbaikan mendesak tim rekayasa. |
| **Authentication & Access** | **27.40%** (20 ulasan) | **0.43%** (1 ulasan) | **0.05** | **Dominansi Keluhan Ekstrem** | Pengguna yang tidak bisa masuk ke akun tidak akan pernah merasakan fitur aplikasi; titik friksi onboarding kritis. |
| **Pricing & Subscription** | **23.29%** (17 ulasan) | **3.02%** (7 ulasan) | **0.41** | **Dominansi Keluhan** | Kebutuhan komunikasi transparan mengenai fitur gratis vs fitur berbayar pada etalase Play Store. |
| **Certification Exam Engine** | **5.48%** (4 ulasan) | **0.00%** (0 ulasan) | **0.00** | **Dominansi Keluhan** | Siswa/peserta ujian hanya mengulas jika mengalami kendala teknis dalam proses ujian sertifikasi. |
| **Core Accounting & Inventory** | **21.92%** (16 ulasan) | **17.24%** (40 ulasan) | **2.50** | **Dominansi Apresiasi** | **Fitur Unggulan**: Modul pencatatan transaksi dan pembukuan Zahir dinilai sangat bermanfaat oleh pengguna aktif. |
| **POS & Hardware Printing** | **2.74%** (2 ulasan) | **3.45%** (8 ulasan) | **4.00** | **Dominansi Apresiasi** | Kehandalan cetak struk kasir POS diapresiasi positif jika printer terhubung dengan baik. |
| **Cloud & Database Sync** | **6.85%** (5 ulasan) | **3.45%** (8 ulasan) | **1.60** | **Aspek Campuran** | Kemampuan cloud sangat disukai saat bekerja normal, namun memicu kemarahan ekstrem saat sinkronisasi menghilangkan data. |
| **Face Attendance & Geolocation** | **4.11%** (3 ulasan) | **1.29%** (3 ulasan) | **1.00** | **Aspek Campuran** | Pengenalan wajah diapresiasi cepat saat berhasil, namun dikeluhkan saat pencahayaan minim. |

---

## 6. Evaluasi Clustering Eksploratif (TF-IDF + K-Means pada Scope B)
Sesuai instruksi audit, eksperimen clustering tanpa supervisi dijalankan sebagai pembanding empiris:
- **Parameter**: TF-IDF dengan n-gram (1-2), stopword bahasa Indonesia kustom, $K \in [3, 4, 5, 6]$, `random_state = 42`.
- **Hasil Diagnostik Koherensi**:
  - $K=3$: Silhouette Score = **0.0227** | Inertia = 168.99
  - $K=4$: Silhouette Score = **0.0204** | Inertia = 167.17
  - $K=5$: Silhouette Score = **0.0218** | Inertia = 165.23
  - $K=6$: Silhouette Score = **0.0202** | Inertia = 163.60
- **Kesimpulan Evaluasi**: Nilai silhouette score yang sangat rendah ($< 0.05$) mengindikasikan bahwa dokumen dalam ruang TF-IDF sangat tumpang tindih (*high overlap*) dan tidak membentuk kluster yang terpisah secara tegas. Kluster 2 pada $K=4$ menyerap **120 dari 185 dokumen (64.8%)** karena memuat kata-kata umum seperti *['buka', 'apakah', 'update', 'data', 'setelah']*.
- **Implikasi**: Hal ini membuktikan secara empiris bahwa pemodelan topik tanpa supervisi pada korpus mikro ulasan pendek menghasilkan kluster yang tidak reliabel, sehingga **Rule-Based ABSA adalah pendekatan yang paling valid secara metodologis**.

---

## 7. Verifikasi & Dukungan Validasi Manual
Untuk memastikan integritas hasil deteksi aturan kata kunci:
1. Telah digenerasi lembar kerja sampel bertingkat (*stratified manual review worksheet*): `data/final/topic_analysis/aspect_manual_validation_sample.csv` & `.xlsx`.
2. Lembar kerja memuat **30 ulasan representatif**:
   - 10 ulasan Negatif terdeteksi aspek.
   - 10 ulasan Netral terdeteksi aspek.
   - 5 ulasan Positif terdeteksi aspek.
   - 5 ulasan tanpa deteksi aspek (*non-detections*).
3. Kolom `manual_aspect_review` dan `manual_correction_notes` dibiarkan kosong (*strictly blank*) untuk diisi oleh pemilik proyek/peneliti dalam tinjauan kualitas kualitatif.

---

## 8. Keterbatasan Metodologis yang Diidentifikasi
1. **Bukti Kata Kunci vs Fakta Terverifikasi**: Deteksi aspek berbasis kata kunci berstatus bukti awal (*preliminary evidence*). Walaupun aturan inklusi/eksklusi telah diterapkan ketat, tetap ada potensi ulasan yang memuat kata kunci dalam konteks sarkasme atau perbandingan dengan aplikasi lain.
2. **Keterbatasan Ulasan Non-Aspek**: 263 ulasan (terutama positif pendek) tidak memuat aspek produk. Hal ini wajar dalam ulasan toko aplikasi, namun perlu diingat bahwa analisis aspek berfokus pada ulasan yang memang membahas fitur fungsional.
3. **Cakupan Kamus Aturan**: Istilah slang daerah yang sangat baru atau singkatan typo ekstrem yang tidak terdaftar dalam taksonomi mungkin masuk ke dalam kategori ulasan tanpa aspek.

---

## 9. Rekomendasi Langkah Selanjutnya (Menuju Fase 6)
1. **Validasi Lembar Kerja Manual**: Pemilik proyek dapat meninjau 30 sampel pada `aspect_manual_validation_sample.xlsx` untuk memverifikasi akurasi taksonomi.
2. **Sintesis Cross-Platform (Fase 6)**: Mengintegrasikan temuan aspek Play Store (misal: isu stabilitas dan otentikasi) dengan metrik keterlibatan konten Instagram `@zahiraccounting` untuk melihat keselarasan antara materi promosi media sosial dengan sentimen operasional pengguna aplikasi.
3. **Pembangunan Dashboard Interaktif Streamlit**: Memvisualisasikan matriks aspek, filter per aplikasi Zahir, dan tren sentimen ke dalam antarmuka web interaktif yang siap disajikan.
