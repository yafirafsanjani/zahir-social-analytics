# Pedoman Anotasi Sentimen Manusia (Human Sentiment Annotation Guideline)
*Proyek: Zahir Social Analytics*  
*Dokumen: Panduan Anotasi Manual Dataset Ulasan Google Play Store*  
*Versi: 1.0 (Fase 4.1)*  

---

## 1. Pendahuluan & Tujuan

Dokumen ini merupakan panduan terstandar bagi anotator manusia (*project owner*) dalam memberikan label sentimen pada dataset ulasan Google Play Store ekosistem aplikasi Zahir (`playstore_gold_set_template.csv` dan `playstore_gold_set_template.xlsx`).

Tujuan pembuatan *Gold Set* ini adalah menyediakan dataset acuan kebenaran (*ground truth*) berkualitas tinggi untuk evaluasi dan tolok ukur model NLP (klasifikasi sentimen berbasis *lexicon* maupun *transformer/IndoBERT*) pada fase berikutnya.

> **Prinsip Utama:** Anotasi dilakukan **murni secara manual oleh manusia**. Tidak ada pelabelan otomatis berbasis model, kata kunci, ataupun skor rating bintang.

---

## 2. Taksonomi Label Sentimen

Anotator memilih salah satu dari 4 kategori label berikut untuk kolom `human_sentiment_label`:

| Label | Definisi Operasional | Kriteria Utama |
| :--- | :--- | :--- |
| `positive` | Teks ulasan mengekspresikan kepuasan, pujian, apresiasi, rekomendasi, atau pengalaman pengguna yang menyenangkan. | Memuat ungkapan kepuasan fitur, kemudahan pemakaian, kehandalan aplikasi, ucapan terima kasih atas manfaat aplikasi. |
| `neutral` | Teks ulasan bersifat faktual, informatif murni, pertanyaan tanpa keluhan/pujian, atau memiliki opini berimbang (positif dan negatif seimbang tanpa polaritas dominan). | Memuat pernyataan netral, pertanyaan fungsional murni ("Apakah bisa sinkron ke PC?"), atau saran fitur tanpa nada kekecewaan/pujian tajam. |
| `negative` | Teks ulasan mengekspresikan ketidakpuasan, kritik, keluhan kendala teknis/bug, kekecewaan layanan, atau pengalaman pengguna yang buruk. | Memuat laporan error, aplikasi crash/force close, gagal login, data hilang, sistem lambat, atau kekecewaan terhadap biaya/kebijakan. |
| `needs_review` | Teks ulasan tidak dapat dipahami, tidak memiliki konteks yang cukup, rancu/ambigu secara ekstrem, atau tidak dapat diberi label dengan percaya diri. | Teks berupa karakter acak (*typo berat*), bahasa daerah yang tidak jelas maknanya, simbol tanpa konteks, atau sarkasme ambigu. |

---

## 3. Aturan Anotasi (Annotation Rules)

1. **Anotasi Berdasarkan Teks, Bukan Skor Rating:**
   - Label sentimen wajib ditentukan semata-mata dari makna semantik teks ulasan pada kolom `review_text_clean`.
   - Rating bintang rendah (1-2) **TIDAK** otomatis berarti sentimen teks negatif (misal teks memuji tapi salah tekan bintang).
   - Rating bintang tinggi (4-5) **TIDAK** otomatis berarti sentimen teks positif (misal ulasan berisi komplain tajam namun pengguna memberi bintang 5 agar terbaca).
2. **Penanganan Ulasan Campuran (Mixed Sentiment):**
   - Jika teks memuat unsur positif dan negatif sekaligus:
     - Tentukan polaritas dominan jika secara wajar salah satu polaritas lebih menonjol (contoh: pujian singkat diikuti komplain panjang mendetail mengenai data hilang -> cenderung `negative`).
     - Jika bobot positif dan negatif setara atau berimbang tanpa dominasi yang jelas -> beri label `neutral`.
3. **Penggunaan Label `needs_review`:**
   - Gunakan `needs_review` secara bijak apabila ulasan benar-benar tidak memungkinkan penentuan sentimen secara andal.
   - Kolom pendukung `needs_review` pada lembar kerja dapat diisi nilai `True` atau `1` jika ulasan tersebut memerlukan diskusi/tinjauan ulang.
4. **Preservasi Teks Ulasan:**
   - Teks ulasan tidak boleh diedit, diperbaiki tata bahasanya, atau diubah selama proses anotasi.
5. **Catatan Tambahan (`annotation_notes`):**
   - Kolom `annotation_notes` dapat diisi catatan kualitatif opsional oleh anotator (misal mencatat adanya sarkasme, dugaan salah beri rating bintang, atau kosakata slang tertentu).

---

## 4. Contoh Ilustratif (Hypothetical Illustrative Examples)

*Catatan: Seluruh contoh di bawah ini merupakan data ilustratif hipotetis untuk keperluan panduan, BUKAN cuplikan ulasan asli dari dataset.*

### A. Contoh Label `positive`
- **Contoh 1:** `"Aplikasi sangat membantu pembukuan toko saya, tampilan simpel dan mudah dipahami."`  
  *Alasan:* Ungkapan kepuasan yang eksplisit terhadap manfaat dan kemudahan aplikasi.
- **Contoh 2:** `"Mantap sekali! Sinkronisasinya lancar jaya."`  
  *Alasan:* Pujian performa teknis aplikasi.
- **Contoh 3:** `"Good app, really helpful for small business accounting."`  
  *Alasan:* Ulasan positif dalam bahasa Inggris yang mengapresiasi kegunaan produk.

### B. Contoh Label `neutral`
- **Contoh 1:** `"Apakah aplikasi ini support cetak struk via bluetooth thermal 58mm?"`  
  *Alasan:* Pertanyaan fungsional murni tanpa ekspresi kepuasan atau kekecewaan.
- **Contoh 2:** `"Sudah update ke versi terbaru."`  
  *Alasan:* Pernyataan faktual status penggunaan tanpa muatan emosi.
- **Contoh 3:** `"Aplikasi bagus fiturnya lengkap, tapi kadang loadingnya agak lama kalau data banyak."`  
  *Alasan:* Sentimen campuran seimbang antara pujian fitur dan catatan minor performa tanpa polaritas dominan yang ekstrem.

### C. Contoh Label `negative`
- **Contoh 1:** `"Kecewa banget, pas update malah force close terus dan data transaksi kemarin hilang."`  
  *Alasan:* Keluhan kritis mengenai kegagalan sistem dan hilangnya data penting.
- **Contoh 2:** `"Gagal login terus padahal password sudah benar. Tolong diperbaiki."`  
  *Alasan:* Laporan kendala teknis dan ketidakmampuan menggunakan fungsi utama aplikasi.
- **Contoh 3:** `"Very slow and frequently crashes when opening reports."`  
  *Alasan:* Ulasan negatif bahasa Inggris terkait ketidakstabilan aplikasi.

### D. Contoh Label `needs_review`
- **Contoh 1:** `"asdfghjk"`  
  *Alasan:* Rangkaian karakter acak tanpa arti yang dapat diinterpretasikan.
- **Contoh 2:** `"Tes 123"`  
  *Alasan:* Teks uji coba pengguna tanpa konteks opini terhadap performa/layanan aplikasi.
- **Contoh 3:** `"Hahahaha ya sudahlah ya"`  
  *Alasan:* Ekspresi ambigu yang tidak memuat konteks jelas mengenai aplikasi.

---

## 5. Format Kolom pada Lembar Kerja Gold Set

Lembar kerja anotasi (`playstore_gold_set_template.csv` dan `playstore_gold_set_template.xlsx`) memuat 7 kolom:
1. `review_id`: Pengidentifikasi unik ulasan dari Google Play Store (tetap dipertahankan untuk keterlacakan data).
2. `app_name`: Nama aplikasi resmi ekosistem Zahir.
3. `review_datetime`: Tanggal dan waktu ulasan dibuat (format standar ISO-8601 YYYY-MM-DD HH:MM:SS).
4. `review_text_clean`: Teks ulasan yang telah dibersihkan secara konservatif (siap dibaca oleh anotator).
5. `human_sentiment_label`: **Kolom utama anotasi** (isi dengan salah satu: `positive`, `neutral`, `negative`, atau `needs_review`).
6. `needs_review`: Kolom penanda khusus (isi dengan `TRUE` jika ulasan ragu-ragu dan butuh ditinjau ulang; kosongkan jika yakin).
7. `annotation_notes`: Kolom teks bebas untuk catatan tambahan anotator.
