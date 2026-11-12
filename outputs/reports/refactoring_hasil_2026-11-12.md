# Hasil refactoring dan pengujian - 12 November 2026

## Environment

Python 3.11.9 di lokasi yang direferensikan .venv_social sekarang tersedia dan environment yang ada berjalan tanpa rekonstruksi atau instalasi global. py -0p juga melaporkan Python 3.14.3. Penyebab ketiadaan sebelumnya tidak diketahui; tidak ada klaim perbaikan manual. pip check: no broken requirements found. Versi utama: pandas 3.0.6, NumPy 2.4.6, Matplotlib 3.11.2, Seaborn 0.13.2, scikit-learn 1.9.1, nbformat 5.11.1, nbclient 0.11.0, ipykernel 7.4.0. Kernel default menggunakan environment aktif pada PATH. Gunakan Jupyter yang diluncurkan dari environment proyek.

## Eksekusi

Notebook 01 sampai 08 lulus nbformat.validate dan dieksekusi dengan nbclient pada root proyek: 8/8 PASS. Scraping dan eksperimen training/inference opsional dinonaktifkan; tidak ada pengujian terhadap mode tersebut. Seluruh 14 notebook termasuk notebook lama dan salinan legacy lulus validasi nbformat; notebook lama tidak dieksekusi. Pemeriksaan AST delapan notebook utama tidak menemukan import dari analysis, preprocessing, scraper, atau scripts.

## Regresi

- PASS: perbandingan hasil in-memory notebook 02 dengan dataset final Play Store, 417 baris x 21 kolom, seluruh kolom setelah normalisasi tipe datetime dan toleransi numerik.
- PASS: perbandingan hasil in-memory notebook 06 dengan master Instagram, 55 baris x 27 kolom, seluruh kolom dengan toleransi numerik.
- PASS: scripts/verify_phase5_3.py 15/15, verify_phase5_4.py 13/13, verify_phase5_5.py 15/15, verify_phase5_6.py 15/15, verify_phase5_8.py 10/10.
- PASS: scripts/audit_phase5_6_consistency.ps1 10/10.
- PASS: lima sumber yang terdaftar pada source_integrity_manifest memiliki SHA-256 sesuai manifest; verifikasi historis Fase 5.8 juga mengecek skema dan jumlah baris 35 pasangan CSV/XLSX. Pemeriksaan ini tidak membuktikan tidak adanya PII pada teks bebas.
- Catatan: uji pertama kesetaraan Play Store gagal karena skrip uji mengonversi missing datetime menjadi string secara tidak konsisten. Setelah normalisasi datetime yang setara pada kedua sisi, perbandingan lulus; data dan logika notebook tidak diubah untuk memaksa kelulusan.

## Visual

Grafik rating/balasan, perbandingan model, aspek menurut sentimen dan perbandingan format/kolaborasi dirender dan diinspeksi; salinannya tersedia di outputs/figures/. Grafik waktu dan caption juga diinspeksi. Sumbu symlog semula menampilkan area negatif yang menyesatkan; batas non-negatif dan ukuran sampel per kelompok ditambahkan. Grafik lain hanya diuji rendering saat eksekusi, belum seluruhnya diinspeksi satu per satu.

## Sisa migrasi

Notebook 01 memvalidasi baseline offline tetapi kode scraper historis belum dipindahkan; sumber akuisisi Play Store tidak ada di repository. Notebook 05 membaca assignment remediated namun belum membuat assignment dari aturan. Notebook 08 memvalidasi tetapi belum meregenerasi paket ke staging. Skrip audit, verifikasi, clustering dan artefak fase historis tetap dipertahankan; tidak seluruh logika operasional lama telah dipindahkan. Mode eksperimen benchmark opsional di notebook 04 belum dijalankan, termasuk IndoBERT yang memerlukan transformers dan bobot model. Inventaris heuristik ada di inventaris_source_statis.md; belum menggantikan audit manual seluruh cabang kode dan semua grafik lama. Jangan mengklaim keseluruhan migrasi selesai atau memindahkan/menghapus kode lama sebelum uji kesetaraan tambahan.
