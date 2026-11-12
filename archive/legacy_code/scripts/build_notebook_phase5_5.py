# -*- coding: utf-8 -*-
"""
build_notebook_phase5_5.py
--------------------------
Membangun dan mengeksekusi notebooks/07_instagram_engagement_analysis.ipynb
secara otomatis dan reproducible (Fase 5.5).
"""

import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
from nbclient import NotebookClient

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTEBOOK_PATH = os.path.join(BASE_DIR, "notebooks", "07_instagram_engagement_analysis.ipynb")

nb = new_notebook()
nb.metadata = {
    "kernelspec": {
        "display_name": "Python 3 (.venv_social)",
        "language": "python",
        "name": "python3"
    },
    "language_info": {
        "name": "python",
        "version": "3.11.9"
    }
}

# --- Cell 0: Header Markdown ---
nb.cells.append(new_markdown_cell("""# 📊 Analisis Performa Postingan & Social Engagement Instagram (@zahiraccounting)
**Zahir Social Analytics — Fase 5.5: Instagram Social Engagement & Content Performance Analysis**  
*Reproducible Data Science & Analytical Pipeline*

---

## 📌 1. Pendahuluan & Ringkasan Eksekutif
Notebook ini menyajikan analisis komprehensif terhadap performa keterlibatan (*engagement*) dari **55 postingan publik Instagram** akun `@zahiraccounting` yang telah diproses secara kanonikal pada **Fase 5.4** (`data/final/instagram_posts_final.csv`).

### Metodologi & Batasan Tata Kelola Data:
1. **Integritas Sumber Data (*Immutable Source*)**: Dataset sumber berisi tepat 55 postingan unik tanpa perubahan byte pada sumber data kanonikal.
2. **Keterlibatan Riil (*Zero Synthetic Fabrication*)**: Metrik `views` tetap bernilai `NaN` sesuai fakta web publik Instagram unauthenticated. Analisis berfokus murni pada tindakan pengguna terverifikasi: $\\text{total\\_interactions} = \\text{likes} + \\text{comments}$. Tidak ada pembagian fiktif untuk mengarang *engagement rate percentage*, *reach*, *impressions*, atau estimasi *followers*.
3. **Kewaspadaan Ukuran Sampel (*Sample Size Caution*)**: Distribusi format didominasi oleh video/reel ($80.0\\%$, $n=44$) dibandingkan carousel ($14.5\\%$, $n=8$) dan image ($5.5\\%$, $n=3$). Setiap inferensi komparatif mencantumkan peringatan ukuran sampel.
4. **Pemisahan Korelasi dan Sebab-Akibat (*Non-Causal Inference*)**: Hubungan antara kolaborasi, waktu posting, caption, atau hashtag tidak diinterpretasikan sebagai hubungan kausal mutlak tanpa bukti eksperimental terkontrol.
"""))

# --- Cell 1: Environment Setup ---
nb.cells.append(new_code_cell(r"""# Setup Lingkungan & Import Library
import os
import sys
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
%matplotlib inline
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Konfigurasi Tampilan & Visualisasi
pd.set_option('display.max_columns', 30)
pd.set_option('display.width', 1000)
pd.set_option('display.float_format', lambda x: f'{x:.2f}')

sns.set_theme(style='whitegrid', font='sans-serif')
plt.rcParams['font.sans-serif'] = ['Calibri', 'Arial', 'DejaVu Sans']
plt.rcParams['axes.edgecolor'] = '#CCCCCC'
plt.rcParams['axes.linewidth'] = 0.8

print("[OK] Library analisis & visualisasi berhasil dimuat.")
"""))
# --- Cell 2: Section 1 Markdown ---
nb.cells.append(new_markdown_cell("""## 📁 2. Pemuatan Dataset Final & Verifikasi Skema
Dataset dimuat dari `data/final/instagram_posts_final.csv`. Seluruh 55 baris diverifikasi keunikannya.
"""))

# --- Cell 3: Data Ingestion Code ---
nb.cells.append(new_code_cell(r"""# Pemuatan Dataset Final Fase 5.4
DATA_PATH = os.path.join('..', 'data', 'final', 'instagram_posts_final.csv')
if not os.path.exists(DATA_PATH):
    DATA_PATH = os.path.join('data', 'final', 'instagram_posts_final.csv')

df = pd.read_csv(DATA_PATH)
print(f"📊 Dataset dimuat: {df.shape[0]} baris, {df.shape[1]} kolom.")
assert len(df) == 55, f"Jumlah baris tidak valid: {len(df)}"
assert df['post_id'].nunique() == 55, "Terdapat duplikasi post_id!"

# Tampilkan 5 baris pertama
display_cols = ['post_id', 'post_date', 'content_type', 'is_collaboration', 'original_account', 'likes', 'comments', 'total_interactions']
df[display_cols].head()
"""))

# --- Cell 4: Section 2 Markdown ---
nb.cells.append(new_markdown_cell("""## 📈 3. Analisis Engagement per Postingan & Distribusi Keseluruhan
Menghitung likes, comments, dan `total_interactions = likes + comments`. Menganalisis parameter tendensi sentral (mean, median), dispersi (std, IQR), serta mendeteksi pencilan (*outliers*) menggunakan kriteria Tukey IQR ($Q3 + 1.5 \\times IQR$).
"""))

# --- Cell 5: Overall Engagement Statistics Code ---
nb.cells.append(new_code_cell(r"""# Perhitungan Ringkasan Statistik Engagement
summary_stats = []
for col in ['likes', 'comments', 'total_interactions']:
    s = df[col]
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1
    outlier_thresh = q3 + 1.5 * iqr
    outliers = s[s > outlier_thresh]
    
    summary_stats.append({
        'Metrik': col,
        'N (Posts)': len(s),
        'Total Akumulasi': int(s.sum()),
        'Mean': s.mean(),
        'Std Dev': s.std(),
        'Median': s.median(),
        'Min': int(s.min()),
        'Max': int(s.max()),
        'Q1 (25%)': q1,
        'Q3 (75%)': q3,
        'IQR': iqr,
        'Skewness': s.skew(),
        'Batas Outlier (Q3+1.5*IQR)': outlier_thresh,
        'Jumlah Outlier': len(outliers),
        'Persentase Outlier (%)': len(outliers) / len(s) * 100
    })

df_summary = pd.DataFrame(summary_stats)
print("=== RINGKASAN STATISTIK DESKRIPTIF ENGAGEMENT (N=55) ===")
df_summary
"""))

# --- Cell 6: Distribution Visualization Code ---
nb.cells.append(new_code_cell(r"""# Visualisasi Distribusi Interaksi & Deteksi Outlier
fig, axes = plt.subplots(1, 2, figsize=(15, 5))

# 1. Histogram & KDE (Right Skewed Distribution)
sns.histplot(df['total_interactions'], bins=25, kde=True, color='#1F4E78', ax=axes[0], edgecolor='white')
axes[0].axvline(df['total_interactions'].median(), color='#E67E22', linestyle='--', linewidth=2, label=f"Median: {df['total_interactions'].median():.0f}")
axes[0].axvline(df['total_interactions'].mean(), color='#C0392B', linestyle='-', linewidth=2, label=f"Mean: {df['total_interactions'].mean():.1f}")
axes[0].axvline(239.0, color='#8E44AD', linestyle=':', linewidth=2, label="Ambang Outlier IQR: 239.0")
axes[0].set_title("Distribusi Total Interaksi (Right-Skewed Tail, Skew=4.31)", fontsize=12, fontweight='bold', pad=10)
axes[0].set_xlabel("Total Interaksi (Likes + Comments)")
axes[0].set_ylabel("Frekuensi Postingan")
axes[0].legend(frameon=True, facecolor='white')

# 2. Boxplot dengan Sebaran Titik Data
sns.boxplot(x=df['total_interactions'], color='#D6EAF8', ax=axes[1], fliersize=0)
sns.stripplot(x=df['total_interactions'], hue=df['is_collaboration'], palette={False: '#2980B9', True: '#E74C3C'},
              size=7, jitter=0.2, alpha=0.8, ax=axes[1])
axes[1].axvline(239.0, color='#8E44AD', linestyle=':', linewidth=2, label="Batas Outlier (239.0)")
axes[1].set_title("Boxplot Total Interaksi & 9 Viral Outliers", fontsize=12, fontweight='bold', pad=10)
axes[1].set_xlabel("Total Interaksi")
axes[1].legend(title="Is Collaboration", frameon=True, facecolor='white')

plt.tight_layout()
plt.show()
"""))
# --- Cell 7: Section 3 Markdown ---
nb.cells.append(new_markdown_cell("""## 🎭 4. Perbandingan Performa Jenis Konten (Video/Reels vs Carousel vs Image)
Membandingkan ketiga format postingan berdasarkan jumlah tayang, total likes, total komentar, serta mean dan median interaksi.

> **Catatan Keterbatasan Inferensi**: Terdapat asimetri tajam dalam distribusi format konten pada akun `@zahiraccounting`:
> - `video/reel`: 44 postingan ($80.0\\%$)
> - `carousel`: 8 postingan ($14.5\\%$)
> - `image`: 3 postingan ($5.5\\%$)
> Ukuran sampel gambar tunggal ($n=3$) terlalu kecil untuk generalisasi statistik. Perbandingan harus ditekankan pada metrik median dan distribusi interquartil.
"""))

# --- Cell 8: Content Type Stats Code ---
nb.cells.append(new_code_cell(r"""# Perhitungan Agregat per Jenis Konten
ct_comparison = df.groupby('content_type').agg(
    post_count=('post_id', 'count'),
    total_likes=('likes', 'sum'),
    mean_likes=('likes', 'mean'),
    median_likes=('likes', 'median'),
    total_comments=('comments', 'sum'),
    mean_comments=('comments', 'mean'),
    median_comments=('comments', 'median'),
    total_interactions=('total_interactions', 'sum'),
    mean_interactions=('total_interactions', 'mean'),
    median_interactions=('total_interactions', 'median'),
    std_interactions=('total_interactions', 'std'),
    min_interactions=('total_interactions', 'min'),
    max_interactions=('total_interactions', 'max')
).reset_index()

ct_comparison['post_share_pct'] = (ct_comparison['post_count'] / len(df) * 100)
ct_comparison = ct_comparison[['content_type', 'post_count', 'post_share_pct', 'total_likes', 'mean_likes', 'median_likes',
                               'total_comments', 'mean_comments', 'median_comments', 'total_interactions',
                               'mean_interactions', 'median_interactions', 'std_interactions', 'min_interactions', 'max_interactions']]

print("=== PERBANDINGAN PERFORMA FORMAT KONTEN ===")
ct_comparison
"""))

# --- Cell 9: Content Type Visualization Code ---
nb.cells.append(new_code_cell(r"""# Visualisasi Performa Antar Format Konten
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 1. Perbandingan Mean vs Median Total Interaksi
bar_width = 0.35
indices = np.arange(len(ct_comparison))

axes[0].bar(indices - bar_width/2, ct_comparison['mean_interactions'], width=bar_width, label='Mean Interactions', color='#1F4E78')
axes[0].bar(indices + bar_width/2, ct_comparison['median_interactions'], width=bar_width, label='Median Interactions', color='#E67E22')
axes[0].set_xticks(indices)
axes[0].set_xticklabels(ct_comparison['content_type'], fontweight='bold')
axes[0].set_title("Mean vs Median Interaksi per Format Konten", fontsize=12, fontweight='bold', pad=10)
axes[0].set_ylabel("Jumlah Interaksi")
axes[0].legend(frameon=True, facecolor='white')

# 2. Pola Percakapan: Rasio Komentar per Format
comment_ratios = df.groupby('content_type')['comments'].median()
axes[1].bar(comment_ratios.index, comment_ratios.values, color=['#27AE60', '#95A5A6', '#2980B9'], edgecolor='white', width=0.5)
axes[1].set_title("Median Komentar per Format (Carousel Mendorong Diskusi)", fontsize=12, fontweight='bold', pad=10)
axes[1].set_ylabel("Median Komentar")
for i, v in enumerate(comment_ratios.values):
    axes[1].text(i, v + 0.3, f"{v:.1f}", ha='center', fontweight='bold')

plt.tight_layout()
plt.show()
"""))

# --- Cell 10: Section 4 Markdown ---
nb.cells.append(new_markdown_cell("""## 🤝 5. Analisis Konten Kolaborasi (*Collaboration Impact Analysis*)
Mengevaluasi perbedaan engagement antara postingan organik mandiri `@zahiraccounting` ($n=29$) dengan postingan kolaborasi co-author ($n=26$).

> **Penegasan Tata Kelola Metodologis**:
> - Peningkatan engagement pada konten kolaborasi **bukan bukti kausal mutlak** bahwa kolaborasi pasti menyebabkan virality.
> - Efek ini dipengaruhi oleh faktor perancu (*confounding factors*): basis followers akun mitra (misal: `@pecahtelur.id` dengan audiens wirausaha massal), format video wawancara, waktu penayangan, serta proses kurasi konten berkualitas tinggi sebelum diajak kolaborasi.
"""))

# --- Cell 11: Collaboration Stats Code ---
nb.cells.append(new_code_cell(r"""# Analisis Statistik Kolaborasi
colab_stats = df.groupby('is_collaboration').agg(
    post_count=('post_id', 'count'),
    total_likes=('likes', 'sum'),
    mean_likes=('likes', 'mean'),
    median_likes=('likes', 'median'),
    total_comments=('comments', 'sum'),
    mean_comments=('comments', 'mean'),
    median_comments=('comments', 'median'),
    total_interactions=('total_interactions', 'sum'),
    mean_interactions=('total_interactions', 'mean'),
    median_interactions=('total_interactions', 'median'),
    std_interactions=('total_interactions', 'std'),
    min_interactions=('total_interactions', 'min'),
    max_interactions=('total_interactions', 'max')
).reset_index()

colab_stats['post_share_pct'] = (colab_stats['post_count'] / len(df) * 100)
colab_stats['label'] = colab_stats['is_collaboration'].map({False: 'Organik (@zahiraccounting)', True: 'Kolaborasi (Mitra / Co-author)'})

print("=== PERBANDINGAN ORGANIK VS KOLABORASI ===")
display(colab_stats[['label', 'post_count', 'post_share_pct', 'total_interactions', 'mean_interactions', 'median_interactions', 'min_interactions', 'max_interactions']])

# Rincian per Akun Mitra
print("\n=== PERINCIAN PER AKUN MITRA ===")
acc_summary = df.groupby(['original_account', 'is_collaboration']).agg(
    post_count=('post_id', 'count'),
    total_interactions=('total_interactions', 'sum'),
    mean_interactions=('total_interactions', 'mean'),
    median_interactions=('total_interactions', 'median'),
    max_interactions=('total_interactions', 'max')
).reset_index().sort_values(by='total_interactions', ascending=False)
display(acc_summary)
"""))

# --- Cell 12: Collaboration Visualization Code ---
nb.cells.append(new_code_cell(r"""# Visualisasi Performa Kolaborasi & Akun Mitra
fig, axes = plt.subplots(1, 2, figsize=(15, 5))

# 1. Boxplot Distribusi Interaksi Organik vs Kolaborasi
sns.boxplot(x='is_collaboration', y='total_interactions', data=df, palette=['#3498DB', '#E74C3C'], ax=axes[0])
axes[0].set_xticklabels(['Organik (N=29)', 'Kolaborasi (N=26)'], fontweight='bold')
axes[0].set_title("Distribusi Interaksi: Organik vs Kolaborasi", fontsize=12, fontweight='bold', pad=10)
axes[0].set_ylabel("Total Interaksi")

# 2. Bar Chart Rata-rata & Median Interaksi per Akun Mitra
acc_sorted = acc_summary.sort_values(by='median_interactions', ascending=True)
axes[1].barh(acc_sorted['original_account'], acc_sorted['median_interactions'], color='#16A085', edgecolor='white', height=0.6)
axes[1].set_title("Median Interaksi per Akun Mitra (Kekuatan Jangkauan @pecahtelur.id)", fontsize=12, fontweight='bold', pad=10)
axes[1].set_xlabel("Median Total Interaksi")
for i, v in enumerate(acc_sorted['median_interactions']):
    axes[1].text(v + 15, i, f"{v:.1f} (N={acc_sorted['post_count'].iloc[i]})", va='center', fontweight='bold', fontsize=9)

plt.tight_layout()
plt.show()
"""))
# --- Cell 13: Section 5 Markdown ---
nb.cells.append(new_markdown_cell("""## ⏰ 6. Analisis Dinamika Waktu Publikasi (*Temporal Posting Dynamics*)
Mengevaluasi performa interaksi berdasarkan:
1. `post_day_of_week` (Senin - Minggu)
2. `time_bin` (Morning, Afternoon, Late Afternoon, Evening/Night)
3. `post_year` (2024, 2025, 2026)

> **Peringatan Artefak & Confounding Time**:
> - Jam tayang pagi (06:00 WIB) menunjukkan rata-rata interaksi sangat tinggi ($586.8$).
> - Namun, audit granular membuktikan bahwa seluruh lonjakan pagi terkonsentrasi pada kampanye wawancara video kolaborasi `@pecahtelur.id` pada Desember 2024 (5 dari 8 postingannya tayang jam 06:00 WIB).
> - Oleh karena itu, jam 06:00 WIB tidak boleh diartikan sebagai jam magis untuk konten organik Zahir, melainkan mencerminkan kesuksesan distribusi mitra spesifik.
"""))

# --- Cell 14: Temporal Stats Code ---
nb.cells.append(new_code_cell(r"""# Analisis Berdasarkan Hari dalam Seminggu
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_analysis = df.groupby('post_day_of_week').agg(
    post_count=('post_id', 'count'),
    total_interactions=('total_interactions', 'sum'),
    mean_interactions=('total_interactions', 'mean'),
    median_interactions=('total_interactions', 'median'),
    min_interactions=('total_interactions', 'min'),
    max_interactions=('total_interactions', 'max')
).reindex(day_order).reset_index()

print("=== DISTRIBUSI & INTERAKSI BERDASARKAN HARI PUBLIKASI ===")
display(day_analysis)

# Analisis Berdasarkan Segmen Waktu Penayangan (Time Bin)
def get_time_bin(hour):
    if 6 <= hour <= 11:
        return 'Morning (06:00-11:59)'
    elif 12 <= hour <= 14:
        return 'Afternoon (12:00-14:59)'
    elif 15 <= hour <= 17:
        return 'Late Afternoon (15:00-17:59)'
    elif 18 <= hour <= 23:
        return 'Evening/Night (18:00-23:59)'
    else:
        return 'Early Morning (00:00-05:59)'

df['time_bin'] = df['post_hour_wib'].apply(get_time_bin)
bin_order = ['Morning (06:00-11:59)', 'Afternoon (12:00-14:59)', 'Late Afternoon (15:00-17:59)', 'Evening/Night (18:00-23:59)']
time_bin_analysis = df.groupby('time_bin').agg(
    post_count=('post_id', 'count'),
    total_interactions=('total_interactions', 'sum'),
    mean_interactions=('total_interactions', 'mean'),
    median_interactions=('total_interactions', 'median'),
    min_interactions=('total_interactions', 'min'),
    max_interactions=('total_interactions', 'max')
).reindex(bin_order).reset_index()

print("\n=== DISTRIBUSI & INTERAKSI BERDASARKAN SEGMEN JAM TAYANG ===")
display(time_bin_analysis)
"""))

# --- Cell 15: Temporal Visualization Code ---
nb.cells.append(new_code_cell(r"""# Visualisasi Dinamika Temporal Publikasi
fig, axes = plt.subplots(1, 2, figsize=(15, 5))

# 1. Bar Chart Interaksi per Hari (Mean vs Median)
x = np.arange(len(day_analysis))
w = 0.35
axes[0].bar(x - w/2, day_analysis['mean_interactions'], width=w, label='Mean Interactions', color='#2C3E50')
axes[0].bar(x + w/2, day_analysis['median_interactions'], width=w, label='Median Interactions', color='#E67E22')
axes[0].set_xticks(x)
axes[0].set_xticklabels(day_analysis['post_day_of_week'], rotation=30, ha='right', fontweight='bold')
axes[0].set_title("Interaksi per Hari dalam Seminggu", fontsize=12, fontweight='bold', pad=10)
axes[0].set_ylabel("Total Interaksi")
axes[0].legend(frameon=True, facecolor='white')

# 2. Segmen Jam Tayang (Time Bin)
axes[1].bar(time_bin_analysis['time_bin'], time_bin_analysis['mean_interactions'], color='#16A085', width=0.5, label='Mean Interactions')
axes[1].plot(time_bin_analysis['time_bin'], time_bin_analysis['median_interactions'], color='#C0392B', marker='o', linewidth=2.5, label='Median Interactions')
axes[1].set_xticklabels(['Pagi (06-11)', 'Siang (12-14)', 'Sore (15-17)', 'Malam (18-23)'], fontweight='bold')
axes[1].set_title("Interaksi Berdasarkan Segmen Waktu (Confounded by @pecahtelur.id)", fontsize=12, fontweight='bold', pad=10)
axes[1].set_ylabel("Interaksi")
axes[1].legend(frameon=True, facecolor='white')

plt.tight_layout()
plt.show()
"""))

# --- Cell 16: Section 6 Markdown ---
nb.cells.append(new_markdown_cell("""## ✍️ 7. Analisis Caption dan Tagar (*Caption Length & Hashtags Efficacy*)
Memeriksa hubungan linier parametrik (Pearson $r$) dan monotonik non-parametrik (Spearman $\\rho$) antara jumlah kata caption serta jumlah tagar terhadap total interaksi.

### Temuan Menarik: Simpson's Paradox pada Tagar (#)
- Pada populasi penuh ($N=55$), terdapat korelasi negatif signifikan antara `hashtag_count` dan `total_interactions` (Spearman $\\rho = -0.4509$, $p=0.0006$).
- Postingan tanpa tagar (`has_hashtags=False`, $n=16$) memiliki rata-rata interaksi $505.9$ dan median $264.0$, jauh melampaui postingan bertagar ($129.5$, median $38.0$).
- **Namun, ini adalah contoh nyata Simpson's Paradox / Confounder**:
  - Seluruh 8 postingan viral dari mitra `@pecahtelur.id` **sama sekali tidak menyertakan tagar** dalam teks caption aslinya.
  - Sebaliknya, postingan internal akun `@zahiraccounting` yang memiliki jangkauan lebih terbatas secara disiplin menyertakan 4–7 tagar.
  - Saat dianalisis khusus pada postingan organik ($n=29$), korelasi tagar sama sekali tidak signifikan ($\rho = -0.158$, $p=0.413$).
"""))

# --- Cell 17: Caption & Hashtag Stats Code ---
nb.cells.append(new_code_cell(r"""# Analisis Korelasi Parametrik & Non-Parametrik
corr_results = []
for var, lbl in [('caption_word_count', 'Jumlah Kata Caption'), ('hashtag_count', 'Jumlah Tagar')]:
    pr, pp = stats.pearsonr(df[var], df['total_interactions'])
    sr, sp = stats.spearmanr(df[var], df['total_interactions'])
    corr_results.append({
        'Variabel': lbl,
        'Pearson r': pr,
        'Pearson p-value': pp,
        'Spearman rho': sr,
        'Spearman p-value': sp,
        'Signifikansi (alpha=0.05)': 'Signifikan' if sp < 0.05 else 'Tidak Signifikan'
    })

print("=== HASIL UJI KORELASI DENGAN TOTAL INTERAKSI (N=55) ===")
display(pd.DataFrame(corr_results))

# Perbandingan Kehadiran Tagar (has_hashtags: True vs False)
ht_comparison = df.groupby('has_hashtags').agg(
    post_count=('post_id', 'count'),
    total_interactions=('total_interactions', 'sum'),
    mean_interactions=('total_interactions', 'mean'),
    median_interactions=('total_interactions', 'median'),
    min_interactions=('total_interactions', 'min'),
    max_interactions=('total_interactions', 'max')
).reset_index()
ht_comparison['status'] = ht_comparison['has_hashtags'].map({False: 'Tanpa Tagar (0 Hashtags)', True: 'Menggunakan Tagar (>=1 Hashtags)'})

u_stat, u_pval = stats.mannwhitneyu(
    df[df['has_hashtags']==True]['total_interactions'],
    df[df['has_hashtags']==False]['total_interactions']
)
print(f"\nUji Mann-Whitney U: Stat = {u_stat:.1f}, p-value = {u_pval:.4f}")
display(ht_comparison[['status', 'post_count', 'total_interactions', 'mean_interactions', 'median_interactions', 'min_interactions', 'max_interactions']])
"""))

# --- Cell 18: Caption & Hashtag Visualization Code ---
nb.cells.append(new_code_cell(r"""# Visualisasi Scatter Plot & Pembuktian Simpson's Paradox
fig, axes = plt.subplots(1, 2, figsize=(15, 5))

# 1. Caption Word Count vs Total Interactions
sns.regplot(x='caption_word_count', y='total_interactions', data=df, color='#2980B9',
            scatter_kws={'alpha': 0.7, 's': 50}, line_kws={'color': '#C0392B', 'linewidth': 2}, ax=axes[0])
axes[0].set_title("Jumlah Kata Caption vs Total Interaksi (Spearman rho = +0.381)", fontsize=12, fontweight='bold', pad=10)
axes[0].set_xlabel("Jumlah Kata Caption (Word Count)")
axes[0].set_ylabel("Total Interaksi")

# 2. Hashtag Count vs Total Interactions (Dengan Hue Akun Kolaborasi)
sns.scatterplot(x='hashtag_count', y='total_interactions', hue='original_account',
                data=df, palette='Set1', s=70, alpha=0.9, ax=axes[1])
axes[1].set_title("Jumlah Tagar vs Interaksi: Fenomena Simpson's Paradox", fontsize=12, fontweight='bold', pad=10)
axes[1].set_xlabel("Jumlah Tagar (Hashtag Count)")
axes[1].set_ylabel("Total Interaksi")
axes[1].legend(title="Original Account", bbox_to_anchor=(1.05, 1), loc='upper left', frameon=True)

plt.tight_layout()
plt.show()
"""))
# --- Cell 19: Section 7 Markdown ---
nb.cells.append(new_markdown_cell("""## 🏆 8. Showcase Postingan Terbaik (Top 10) dan Terendah (Bottom 10)
Identifikasi postingan dengan interaksi tertinggi untuk memetakan formula konten yang berhasil, serta postingan terendah untuk bahan evaluasi.
"""))

# --- Cell 20: Top and Bottom Posts Code ---
nb.cells.append(new_code_cell(r"""# Menampilkan Top 10 dan Bottom 10 Postingan
df_sorted = df.sort_values(by='total_interactions', ascending=False).reset_index(drop=True)

print("=== TOP 10 POSTINGAN DENGAN INTERAKSI TERTINGGI ===")
top10 = df_sorted.head(10)[['post_id', 'content_type', 'is_collaboration', 'original_account', 'post_date', 'likes', 'comments', 'total_interactions']]
display(top10)

print("\n=== BOTTOM 10 POSTINGAN DENGAN INTERAKSI TERENDAH ===")
bot10 = df_sorted.tail(10)[['post_id', 'content_type', 'is_collaboration', 'original_account', 'post_date', 'likes', 'comments', 'total_interactions']].sort_values(by='total_interactions', ascending=True)
display(bot10)
"""))

# --- Cell 21: Section 8 Markdown ---
nb.cells.append(new_markdown_cell("""## [RUN] 9. Sintesis Artefak & Rekomendasi Dashboard (Fase 6)
Seluruh 7 artefak data analitik telah diekspor secara berpasangan dalam format CSV (RFC 4180 terenkapsulasi penuh) dan format Excel multi-sheet terformat (`openpyxl`) pada folder `data/final/instagram_analysis/`:

1. `instagram_engagement_metrics.csv` & `.xlsx` (Data level 55 postingan dengan ranking, persentil, dan tier)
2. `instagram_engagement_summary.csv` & `.xlsx` (Statistik deskriptif parametrik & non-parametrik)
3. `instagram_content_type_comparison.csv` & `.xlsx` (Evaluasi format konten)
4. `instagram_collaboration_analysis.csv` & `.xlsx` (Analisis status & rincian akun mitra)
5. `instagram_posting_time_analysis.csv` & `.xlsx` (Dinamika temporal hari, jam tayang, dan tahun)
6. `instagram_caption_hashtag_analysis.csv` & `.xlsx` (Korelasi & audit fenomena perancu tagar)
7. `instagram_top_posts.csv` & `.xlsx` (Showcase 20 postingan performa ekstrem)

### Rekomendasi untuk Dashboard Streamlit (Fase 6):
- **Tab Media Sosial / Instagram**: Tampilkan metrik ringkasan kartu KPI (Total Interaksi: 13.147, Rata-rata: 239.0, Median: 51.0, Outlier Rate: 16.4%).
- **Interactive Slicers**: Berikan filter interaktif untuk membedah postingan berdasarkan `content_type` dan `is_collaboration`.
- **Nuanced Storytelling**: Cantumkan catatan metodologis transparan bahwa metrik views tidak tersedia dan lonjakan pagi dipengaruhi oleh kolaborasi `@pecahtelur.id`.
"""))

# --- Cell 22: Closing Verification Code ---
nb.cells.append(new_code_cell(r"""# Verifikasi Keberadaan Seluruh 7 Pasang Artefak Analisis
import glob
artifacts = glob.glob(os.path.join(os.path.dirname(DATA_PATH), 'instagram_analysis', '*.*'))
print("=== ARTEFAK ANALISIS FASE 5.5 DI DATA/FINAL/INSTAGRAM_ANALYSIS/ ===")
for p in sorted(artifacts):
    size_kb = os.path.getsize(p) / 1024
    print(f"[FILE] {os.path.basename(p):<45} ({size_kb:.1f} KB)")
"""))

# --- Eksekusi dan Simpan Notebook ---
print("[RUN] Menjalankan NotebookClient untuk mengeksekusi seluruh sel notebook...")
client = NotebookClient(nb, timeout=600, kernel_name="python3")
client.execute()

with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
    nbformat.write(nb, f)

print(f"[OK] Notebook berhasil dibangun, dieksekusi, dan disimpan di: {NOTEBOOK_PATH}")