# Audit awal refactoring notebook

## Status

Migrasi belum selesai. Tidak ada dataset kanonis atau notebook lama yang diubah. Interpreter .venv_social gagal dijalankan karena Python 3.11.9 yang dirujuk pyvenv.cfg tidak ditemukan. Eksekusi notebook, grafik dan pengujian Python belum dilakukan.

## Pemeriksaan yang dilakukan

- Lima sumber di data/export/source_integrity_manifest.csv cocok dengan SHA-256 manifest.
- Master Instagram memiliki 55 baris dan 27 kolom; master Play Store 417 baris dan 33 kolom.
- Notebook baru 03 dan 08 dapat diparse sebagai JSON dan memuat metadata kernel python3. Ini bukan pengujian eksekusi atau validasi nbformat lengkap.
- Manifest split memuat 333 development dan 84 test.
- README masih menyebut struktur notebook dan dashboard yang tidak sesuai; belum diubah karena migrasi pipeline belum selesai.

## Peta migrasi awal

| Sumber | Fungsi | Notebook tujuan | Status |
| --- | --- | --- | --- |
| scraper/instagram_scraper.py dan notebooks/01_instagram_scraping.ipynb | Akuisisi Instagram publik | 01 | Belum dimigrasi |
| preprocessing/playstore_preprocessing.py dan notebooks/04_playstore_preprocessing.ipynb, notebooks/05_playstore_eda.ipynb | Preprocessing dan EDA review | 02 | Belum dimigrasi |
| scripts/create_gold_set.py dan pedoman anotasi | Gold Set manusia | 03 | Notebook audit baru; eksekusi belum diuji, pembuatan belum dimigrasi |
| analysis/sentiment_benchmarking.py dan notebooks/06_sentiment_benchmarking.ipynb | Benchmark | 04 | Belum dimigrasi |
| analysis/aspect_extraction.py, scripts/build_phase_5_3_final.py dan notebooks/07_aspect_analysis.ipynb | Aspek dan remediation | 05 | Belum dimigrasi |
| preprocessing/instagram_preprocessing.py | Preprocessing Instagram | 06 | Belum dimigrasi |
| analysis/instagram_engagement_analysis.py dan notebooks/07_instagram_engagement_analysis.ipynb | Analisis interaksi | 07 | Belum dimigrasi |
| scripts/build_phase5_8_exports.py dan scripts/verify_phase5_8.py | Konsolidasi dan verifikasi | 08 | Notebook audit sebagian baru; eksekusi dan ekspor belum dimigrasi |

Peta ini belum merupakan inventaris lengkap seluruh input, output, dependensi, sel notebook, skrip historis dan dokumentasi. Jangan memindahkan atau menghapus sumber sebelum audit dan uji kesetaraan selesai. Laporan historis Instagram menyebut Simpson's Paradox; pembalikan agregat dan kelompok harus dibuktikan sebelum menggunakan istilah tersebut.

## Langkah selanjutnya

Pulihkan Python 3.11 atau buat environment baru tanpa menghapus environment lama. Lengkapi audit, checksum master dan paket, migrasi bertahap, verifikasi kesetaraan, eksekusi aman tanpa scraping atau training, serta inspeksi visual grafik.
