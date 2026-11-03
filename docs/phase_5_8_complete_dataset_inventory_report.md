# Fase 5.8 - Complete Dataset Inventory & Master Data Consolidation

Tanggal: 2026-11-03

## 1. Hasil Inventaris

Audit mencakup seluruh artefak CSV, XLSX, dan JSON pada `data/raw/`, `data/final/`, subfolder analisis, serta ekspor legacy Fase 5.6. Inventaris hasil audit tersedia di `data/export/dataset_inventory.csv` dan `data/export/dataset_inventory.xlsx`.

- Artefak sumber yang didokumentasikan: **99**.
- Status keputusan: **36 exported**, **40 not_exported**, dan **23 duplicate**.
- Artefak raw, backup, baseline, template Gold Set, dan ekspor flat legacy tidak dihapus. Mereka diberi status sesuai alasan metodologis pada kolom `decision_reason`.
- Raw Play Store tidak diekspor ulang karena memuat `userName` dan `userImage`; data master privacy-reduced digunakan sebagai penggantinya.

## 2. Dataset Master yang Dipilih

### Instagram

`data/export/instagram/master/instagram_master.csv` dan `.xlsx` adalah dataset induk Instagram kanonis.

- **55** postingan unik, **27** kolom, kunci primer `post_id`.
- Periode: **2024-03-01** hingga **2026-08-06**.
- Memuat URL, tanggal, tipe konten, caption, hashtag, likes, comments, `total_interactions`, kolaborasi, akun asal, serta metadata waktu publikasi yang valid.
- `views` tetap missing sesuai sumber publik. Tidak terdapat `reach`, `impressions`, maupun engagement rate sintetis.

### Google Play Store

`data/export/playstore/master/playstore_master.csv` dan `.xlsx` adalah dataset induk Play Store privacy-reduced.

- **417** ulasan unik, **33** kolom, kunci primer `review_id`.
- Menggabungkan satu-ke-satu data review akhir, `human_sentiment_label` dari human-annotated Gold Set, serta delapan assignment aspek remediated.
- Label manusia dipisahkan dari prediksi model; master tidak memuat kolom `test_pred_*`.
- Tidak mengandung `userName`, `userImage`, `reviewer_id`, atau teks balasan developer.
- Menjaga **234** mention aspek pada delapan flag kanonis.

## 3. Paket Ekspor Terstruktur

Paket baru berada di `data/export/` tanpa menghapus ekspor flat lama.

| Platform | Folder | Dataset kanonis |
| :--- | :--- | ---: |
| Instagram | `instagram/master/` | 1 |
| Instagram | `instagram/engagement/` | 2 |
| Instagram | `instagram/analysis/` | 7 |
| Play Store | `playstore/master/` | 1 |
| Play Store | `playstore/sentiment/` | 5 |
| Play Store | `playstore/aspects/` | 13 |
| Play Store | `playstore/analysis/` | 6 |
| **Total** |  | **35** |

Setiap dari 35 dataset kanonis tersedia sebagai pasangan CSV/XLSX. `README_data_dictionary.md` memuat tabel fungsi, lokasi, kunci primer, baris, dan kolom; `dataset_relationships.md` mendokumentasikan relasi `post_id` dan `review_id`; `source_integrity_manifest.csv/.xlsx` menyimpan checksum SHA-256 sumber terlindungi.

## 4. Dataset Analisis dan NLP

- Instagram: engagement detail dan summary, content-type comparison, collaboration, posting time, caption/hashtag, top/bottom posts, content performance, dan data-quality audit.
- Sentimen: benchmark metrics, split manifest, prediksi test-only 84 ulasan, error analysis, serta file 417 label manusia yang tetap berprovenance `gold_set_human_annotated`.
- Aspek: assignment remediated, taksonomi delapan aspek, summary seluruh ulasan, summary negative/neutral, comparison sentimen, audit keyword, log remediation, dan rekonsiliasi/validasi manual.
- Analisis Play Store: missing values, kualitas teks, readiness audit, scope comparison, serta exploratory clustering assignments dan summary.

## 5. Dataset yang Tidak Diekspor

- Raw Play Store: tidak diekspor karena PII pengguna.
- Raw Instagram, backup, baseline, expansion test, dan test artifact: dipertahankan immutable sebagai provenance tetapi digantikan oleh master final.
- Gold Set template dan duplikasi annotated/validated: tidak diekspor sendiri karena labelnya telah digabung secara transparan ke master dan sentiment package.
- Assignment aspek pra-remediasi: tidak diekspor karena telah digantikan canonical remediated assignments.
- Export flat Fase 5.6: tetap tersedia agar backward compatible, tetapi paket nested Fase 5.8 adalah handoff yang direkomendasikan.

## 6. Pemeriksaan Integritas

`python scripts/verify_phase5_8.py` selesai dengan **10 PASS, 0 FAIL**:

1. 55 post Instagram dan field wajib master terjaga.
2. Kebijakan zero-fabrication Instagram terjaga.
3. 417 review master privacy-reduced terjaga.
4. Human-annotated Gold Set terjaga pada seluruh baris.
5. 234 mention aspek remediated terjaga.
6. Prediksi model tetap terbatas pada 84 test review.
7. Checksum sumber terlindungi cocok dengan manifest.
8. Inventory mendokumentasikan exported/not_exported/duplicate.
9. Dokumentasi relasi dan data dictionary tersedia.
10. Seluruh pasangan CSV/XLSX kanonis memiliki jumlah baris dan skema primary sheet yang konsisten.

## 7. Catatan Operasional

- Tidak ada raw data, Gold Set, remediated assignments, baseline Instagram, maupun notebook sumber yang dimodifikasi.
- Tidak ada scraping, pelatihan model, dashboard, Git staging, commit, atau push.
- Dua file `data/export/instagram/engagement/metric.csv` dan `.xlsx` merupakan duplikat sementara dari build awal; keduanya tidak tercantum dalam inventory, dictionary, relationships, atau summary kanonis. Gunakan `instagram_engagement_summary.csv/.xlsx` sebagai file resmi.
- Fase 5.8 selesai dan berhenti sebelum Fase 6.