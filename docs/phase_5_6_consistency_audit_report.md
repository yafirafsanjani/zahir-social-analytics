# Audit Korektif Fase 5.6 - Konsistensi Data Ekspor

Tanggal audit: 2026-11-03

## Ruang Lingkup dan Proteksi Sumber

Audit ini membandingkan paket ekspor Fase 5.6 dengan sumber kanonis Fase 5.3--5.5 secara read-only. Tidak ada file pada `data/raw/`, Gold Set, atau dataset remediated yang diubah. Tidak dilakukan scraping, dashboard, maupun operasi Git tulis.

## 1. Instagram: Median `total_interactions`

- Sumber Fase 5.5 `data/final/instagram_analysis/instagram_engagement_metrics.csv` dan ekspor `data/export/instagram/instagram_engagement_metrics.csv` sama persis per `post_id` untuk 55 postingan.
- Definisi yang konsisten adalah `total_interactions = likes + comments`; seluruh 55 baris memenuhi aritmetika tersebut dan jumlah interaksinya 13.147.
- Median populasi 55 postingan adalah **51**: setelah pengurutan, observasi tengah ke-28 bernilai 51. Ini konsisten dengan `instagram_engagement_summary.csv` dan laporan Fase 5.5.
- Nilai **38** pada laporan Fase 5.6 bukan median populasi. Nilai tersebut adalah median segmen postingan yang memiliki hashtag pada laporan Fase 5.5. Angka itu keliru dipakai kembali sebagai median keseluruhan pada Fase 5.6.
- Tindakan koreksi: dokumentasi Fase 5.6 diperbaiki menjadi median 51. Tidak ada CSV/XLSX yang diubah karena ekspor data sudah benar.

## 2. Taksonomi Aspek Play Store

Sumber kanonis `aspect_taxonomy_remediated.json` menetapkan delapan aspek berikut dan paket ekspor mempertahankannya tanpa pemetaan ulang:

| ID kanonis | Nama taksonomi | Nama tampilan pada `Aspect Mentions (Long)` | Mention |
| :--- | :--- | :--- | ---: |
| `login_auth` | Authentication & Access | Login, Otentikasi & Akses Akun | 38 |
| `crash_stability` | System Stability & Crash | Stabilitas Aplikasi, Bug & Crash | 38 |
| `pricing_subscription` | Pricing & Subscription | Harga, Langganan & Lisensi | 34 |
| `sync_cloud_data` | Cloud & Database Synchronization | Sinkronisasi Cloud & Integritas Data | 15 |
| `pos_hardware_print` | POS & Hardware Printing | POS, Kasir & Integrasi Hardware Printer | 20 |
| `inventory_accounting` | Core Accounting & Inventory | Fitur Akuntansi, Laporan & Inventori | 71 |
| `certification_exam` | Certification Exam Engine | Sertifikasi & Ujian Online Zahir | 11 |
| `attendance_face` | Face Attendance & Geolocation | Presensi & Deteksi Wajah (Attendance) | 7 |

- `review_aspect_assignments_remediated.csv` dan `playstore_aspects.csv` sama persis per `review_id`: 417 ulasan unik dan 234 mention.
- Sheet `Aspect Mentions (Long)` berisi tepat 234 baris data, tujuh kolom, dan setiap pasangan `review_id`--`aspect_id` cocok dengan tabel wide kanonis.
- Kategori `customer_service`, `performance_bugs`, `features_functionality`, `ui_ux`, dan `update_system` tidak ada pada taksonomi Fase 5.3 maupun ekspor Fase 5.6. Pernyataan lama dalam laporan Fase 5.6 adalah dokumentasi salah, bukan perubahan data. Tidak ada mapping kategori lama--baru yang sah karena tidak pernah terjadi pemetaan ulang.
- Tindakan koreksi: bagian taksonomi laporan Fase 5.6 diselaraskan dengan delapan aspek kanonis, skema wide 17 kolom, dan sheet long tujuh kolom.

## 3. Label Sentimen

- `playstore_gold_set_final.csv` memiliki 417 `review_id` unik dengan distribusi label manusia: 232 positif, 112 netral, dan 73 negatif.
- Seluruh 417 `human_sentiment_label` pada `playstore_sentiment.csv` sama dengan human-annotated Gold Set dan seluruhnya memiliki `sentiment_label_source = gold_set_human_annotated`.
- Prediksi model berada pada 84 ulasan test held-out saja; 333 ulasan development tidak memiliki nilai `test_pred_*`. Prediksi tidak menggantikan label manusia.
- Dokumentasi dan pesan verifier Fase 5.6 kini menggunakan istilah **human-annotated Gold Set**, bukan ground truth absolut.

## 4. Hasil Verifikasi dan Tindakan

- Verifier tambahan `scripts/audit_phase5_6_consistency.ps1` selesai dengan **10 PASS, 0 FAIL**.
- Tidak dibuat CSV/XLSX koreksi karena semua data ekspor telah cocok dengan sumber kanonis.
- Suite legacy `verify_phase5_3.py`, `verify_phase5_4.py`, `verify_phase5_5.py`, dan `verify_phase5_6.py` dicoba ulang, tetapi tidak dapat berjalan: `.venv_social` mereferensikan `C:\Users\Yafi Rafsanjani H\AppData\Local\Programs\Python\Python311\python.exe` yang sudah tidak tersedia. Kegagalan ini adalah masalah interpreter lingkungan, bukan kegagalan data atau assertion.
- Audit berhenti pada Fase 5.6. Tidak ada pekerjaan Fase 6 yang dilakukan.