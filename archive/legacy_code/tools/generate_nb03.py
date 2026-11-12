# -*- coding: utf-8 -*-
"""
generate_nb03.py
----------------
Generator mandiri untuk notebooks/03_playstore_goldset.ipynb.
Validasi menyeluruh Gold Set sentimen manusia, distribusi kelas, dan perbandingan terhadap rating bintang.
"""

from pathlib import Path
import nbformat as nbf

nb = nbf.v4.new_notebook()
nb.metadata = {
    'kernelspec': {'display_name': 'Python 3 (ipykernel)', 'language': 'python', 'name': 'python3'},
    'language_info': {'name': 'python', 'version': '3.11.9'}
}

cells = []

# Cell 0: Header Markdown
cells.append(nbf.v4.new_markdown_cell("""# 03 - Validasi Kanonikal Gold Set Sentimen Manusia

**Zahir Social Analytics — Ground Truth Sentimen Ulasan Google Play Store**

---

### Deskripsi & Metodologi Gold Set
Notebook ini memvalidasi dataset **Gold Set Sentimen Manusia** (`playstore_gold_set_final.csv`) yang berfungsi sebagai *ground truth* (kebenaran dasar) untuk seluruh evaluasi model pemrosesan bahasa alami (NLP) pada ekosistem Zahir.

Prinsip Utama Gold Set:
- **Anotasi Manual Manusia**: Seluruh 417 ulasan dianotasi secara manual oleh manusia berdasarkan pedoman anotasi linguistik terstandarisasi, **bukan hasil prediksi model machine learning** dan **bukan konversi otomatis dari skor rating**.
- **Distribusi Tiga Kelas**:
  - `positive`: 232 ulasan (55.64%)
  - `neutral`: 112 ulasan (26.86%)
  - `negative`: 73 ulasan (17.51%)
- **Immutabilitas Data**: Label Gold Set kanonikal berstatus beku (*immutable*) dan tidak boleh diubah oleh proses inferensi otomatis.

---

### Metadata Input & Output
- **File Input**:
  - `data/final/playstore_gold_set_final.csv` (Gold Set kanonikal: 417 baris, 4 kolom).
  - `data/final/playstore_reviews_final.csv` (Dataset ulasan terproses: 417 baris, 21 kolom).
- **Output Artefak**:
  - Output grafik: `outputs/figures/goldset_distribution.png`.
- **Prasyarat Lingkungan**:
  - Python 3.11.x, `pandas`, `matplotlib`, `seaborn`.
"""))

# Cell 1: Environment Setup
cells.append(nbf.v4.new_code_cell("""from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display

ROOT = Path.cwd().resolve()
if not (ROOT / 'data' / 'export').is_dir():
    ROOT = ROOT.parent
if not (ROOT / 'data' / 'export').is_dir():
    raise FileNotFoundError('Jalankan Jupyter Notebook dari root repository atau folder notebooks.')

sns.set_theme(style='whitegrid', font_scale=1.0)
plt.rcParams['figure.dpi'] = 150
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'DejaVu Sans', 'Arial']

FIG_DIR = ROOT / 'outputs' / 'figures'
FIG_DIR.mkdir(parents=True, exist_ok=True)

print(f'Root direktori: {ROOT}')
print('Setup library validasi Gold Set selesai.')
"""))

# Cell 2: Data Loading & Verification Markdown
cells.append(nbf.v4.new_markdown_cell("""## 1. Pemuatan Data & Audit Keunikan Kunci Primer

Memuat dataset Gold Set dan dataset ulasan Play Store terproses, memverifikasi bahwa seluruh 417 ulasan terhubung 1-to-1 via `review_id` tanpa ada data yang hilang atau terduplikasi.
"""))

# Cell 3: Data Loading & Verification Code
cells.append(nbf.v4.new_code_cell("""gold_path = ROOT / 'data' / 'final' / 'playstore_gold_set_final.csv'
review_path = ROOT / 'data' / 'final' / 'playstore_reviews_final.csv'

assert gold_path.is_file(), f'Gold Set tidak ditemukan: {gold_path}'
assert review_path.is_file(), f'Review final tidak ditemukan: {review_path}'

gold = pd.read_csv(gold_path)
reviews = pd.read_csv(review_path)

print(f'Gold Set Dimuat: {gold.shape[0]} baris, {gold.shape[1]} kolom.')
print(f'Reviews Dimuat: {reviews.shape[0]} baris, {reviews.shape[1]} kolom.')

# Validasi Keunikan & Kelengkapan
checks = {
    'Jumlah baris tepat 417': len(gold) == 417,
    'ID Gold Set unik & lengkap': gold['review_id'].notna().all() and gold['review_id'].is_unique,
    'ID Review unik & lengkap': reviews['review_id'].notna().all() and reviews['review_id'].is_unique,
    'Cakupan ID identik 100%': set(gold['review_id']) == set(reviews['review_id']),
    'Label sentimen valid (pos/neu/neg)': gold['human_sentiment_label'].isin(['positive', 'neutral', 'negative']).all(),
    'Tanpa missing label sentimen': gold['human_sentiment_label'].notna().all()
}

audit_summary = pd.DataFrame(list(checks.items()), columns=['Dimensi Pemeriksaan', 'Status'])
display(audit_summary)

assert all(checks.values()), 'Pemeriksaan integritas Gold Set gagal!'
print('[PASS] Integritas kunci primer dan kelengkapan label Gold Set terpenuhi 100%.')
"""))

# Cell 4: Sentiment Distribution Markdown
cells.append(nbf.v4.new_markdown_cell("""## 2. Distribusi Sentimen Manusia & Perbandingan Terhadap Rating Bintang

### Distingsi Metodologi: Sentimen Teks vs Skor Rating
- **Rating (Skor 1 - 5)**: Penilaian numerik subjektif saat pengulas mengirimkan review.
- **Sentimen Teks (Positive, Neutral, Negative)**: Evaluasi linguistik terhadap muatan emosi dan opini dalam teks ulasan.
- Terdapat kasus di mana pengulas memberikan rating bintang 5 namun teksnya netral/berupa pertanyaan teknis, atau rating bintang 3 dengan teks bernada apresiasi maupun kritik.
"""))

# Cell 5: Sentiment Distribution Code & Plot
cells.append(nbf.v4.new_code_cell("""counts = gold['human_sentiment_label'].value_counts().reindex(['positive', 'neutral', 'negative'], fill_value=0)
pcts = (counts / len(gold) * 100).round(2)

dist_df = pd.DataFrame({
    'Label Sentimen Manusia': counts.index,
    'Jumlah Ulasan': counts.values,
    'Proporsi (%)': pcts.values
})
display(dist_df)

# Gabungkan dengan ulasan untuk membandingkan rating vs sentimen
merged = gold.merge(reviews[['review_id', 'score', 'rating_category']], on='review_id')
crosstab = pd.crosstab(merged['score'], merged['human_sentiment_label']).reindex(columns=['positive', 'neutral', 'negative'])

print('\\nMatriks Silang: Skor Rating Bintang vs Label Sentimen Teks Manusia:')
display(crosstab)

# Visualisasi Distribusi dan Matriks Silang
fig, axes = plt.subplots(1, 2, figsize=(14, 5), layout='constrained')

# Subplot 1: Distribusi Sentimen Manusia
colors_sent = {'positive': '#2CA02C', 'neutral': '#FF7F0E', 'negative': '#D62728'}
bars = axes[0].barh(counts.index.str.capitalize(), counts.values,
                    color=[colors_sent[c] for c in counts.index], edgecolor='black', alpha=0.85)
axes[0].invert_yaxis()
axes[0].set_title(f'Distribusi Sentimen Ground Truth Manusia\\n(Total n = {len(gold):,} ulasan)', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Jumlah Ulasan', fontsize=11)
axes[0].set_ylabel('Label Sentimen', fontsize=11)
axes[0].grid(axis='x', linestyle='--', alpha=0.7)

for bar in bars:
    w = bar.get_width()
    pct = w / len(gold) * 100
    axes[0].annotate(f'{w:,} ({pct:.1f}%)',
                     xy=(w, bar.get_y() + bar.get_height() / 2),
                     xytext=(5, 0), textcoords="offset points",
                     ha='left', va='center', fontsize=9.5, fontweight='bold')
axes[0].set_xlim(0, max(counts.values) * 1.25)

# Subplot 2: Heatmap Rating Score vs Human Sentiment
sns.heatmap(crosstab, annot=True, fmt='d', cmap='YlGnBu', cbar=False, ax=axes[1],
            annot_kws={'size': 11, 'weight': 'bold'})
axes[1].set_title('Kesesuaian Skor Rating Bintang vs Sentimen Teks', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Label Sentimen Teks Manusia', fontsize=11)
axes[1].set_ylabel('Rating Bintang (Score 1 - 5)', fontsize=11)

fig_path_gold = FIG_DIR / 'goldset_distribution.png'
plt.savefig(fig_path_gold, dpi=200)
print(f'Figur tersimpan: {fig_path_gold}')
plt.show()
"""))

# Cell 6: Discrepancy Qualitative Examples Markdown
cells.append(nbf.v4.new_markdown_cell("""## 3. Contoh Kualitatif Divergensi Rating vs Sentimen Teks

Kasus-kasus di mana rating bintang berbeda dari muatan sentimen teks menegaskan mengapa pelabelan manual manusia sangat krusial dan tidak dapat digantikan oleh aturan skor rating sederhana:
"""))

# Cell 7: Discrepancy Qualitative Examples Code
cells.append(nbf.v4.new_code_cell("""merged_text = gold.merge(reviews[['review_id', 'score', 'rating_category']], on='review_id')

# Contoh: Rating bintang 5 tapi sentimen teks Netral (misal: pertanyaan teknis atau teks minimal)
sample_5_neu = merged_text[(merged_text['score'] == 5) & (merged_text['human_sentiment_label'] == 'neutral')].head(2)
print('=== CONTOH RATING BINTANG 5 DENGAN SENTIMEN TEKS NETRAL ===')
for _, r in sample_5_neu.iterrows():
    txt = r['review_text_clean'][:100]
    print(f"[{r['app_name']}] (Rating {r['score']}★, Teks: {r['human_sentiment_label']}): '{txt}'")

# Contoh: Rating bintang 3 tapi sentimen teks Positif atau Negatif
sample_3_div = merged_text[merged_text['score'] == 3].head(3)
print('\\n=== CONTOH RATING BINTANG 3 DENGAN SENTIMEN TEKS SPESIFIK ===')
for _, r in sample_3_div.iterrows():
    txt = r['review_text_clean'][:100]
    print(f"[{r['app_name']}] (Rating {r['score']}★, Teks: {r['human_sentiment_label']}): '{txt}'")
"""))

# Cell 8: Conclusion Markdown
cells.append(nbf.v4.new_markdown_cell("""## 4. Kesimpulan & Penegasan Metodologi

1. **Keabsahan Ground Truth**: Gold Set kanonikal 417 ulasan terverifikasi lengkap, unik, dan konsisten tanpa nilai hilang.
2. **Distribusi Kelas**: Kelas positif mendominasi (55.64%), diikuti netral (26.86%) dan negatif (17.51%), mencerminkan kurva kepuasan alami pengguna aplikasi Zahir.
3. **Pemisahan Konseptual yang Ketat**: Divergensi nyata antara rating numerik dan sentimen teks membuktikan keharusan membedakan variabel auxiliary rating dari label sentimen manusia murni.
4. **Kesiapan untuk Benchmarking**: Dataset ini menjadi fondasi evaluasi yang adil dan tidak bias bagi notebook pemodelan berikutnya (`04_sentiment_benchmark.ipynb`).
"""))

nb.cells = cells
out_path = Path('notebooks/03_playstore_goldset.ipynb')
with open(out_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f'Successfully generated {out_path} with {len(cells)} cells.')
