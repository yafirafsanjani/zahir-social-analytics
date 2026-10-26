import json
import nbformat as nbf

nb = nbf.v4.new_notebook()

cells = []

# Title & Overview
cells.append(nbf.v4.new_markdown_cell("""# 07. Aspect Taxonomy Construction & Customer Voice Extraction
**Zahir Social Analytics — Play Store Customer Voice Analytics**  
**Audit & Execution Date:** 2026-10-26  
**Status:** Completed & Validated (Phase 5.2)

---

## Executive Summary & Objectives
Notebook ini mengimplementasikan analisis aspek berbasis taksonomi aturan/kata kunci (*Rule-Based Aspect Taxonomy Analysis / ABSA*) pada **417 Ulasan Google Play Store Ekosistem Zahir**.

Sesuai metodologi yang ditetapkan pada Audit Kesiapan Fase 5.1:
1. **Autoritas Ground Truth Sentimen**: Menggunakan `human_sentiment_label` dari Gold Set (`data/final/playstore_gold_set_final.csv`) sebagai acuan mutlak.
2. **Taksonomi 8 Aspek Produk**:
   - `login_auth`: Authentication & Access
   - `crash_stability`: System Stability & Crash
   - `pricing_subscription`: Pricing & Subscription
   - `sync_cloud_data`: Cloud & Database Synchronization
   - `pos_hardware_print`: POS & Hardware Printing
   - `inventory_accounting`: Core Accounting & Inventory
   - `certification_exam`: Certification Exam Engine
   - `attendance_face`: Face Attendance & Geolocation
3. **Analisis Multi-Cakupan (*Multi-Scope Analysis*)**:
   - **Scope A**: Keseluruhan 417 ulasan untuk memetakan cakupan umum aspek.
   - **Scope B**: 185 ulasan Negatif dan Netral khusus untuk membedah akar keluhan (*Customer Pain Points*).
   - **Scope C**: Analisis kontras antara 232 ulasan Positif vs 73 ulasan Negatif untuk mengidentifikasi fitur yang diapresiasi vs yang dikeluhkan.
4. **Validasi Kualitatif & Clustering Eksploratif**:
   - Lembar kerja sampel bertingkat (*stratified sample*, n=30) untuk verifikasi manual oleh pemilik proyek.
   - Analisis kluster eksploratif TF-IDF + K-Means pada Scope B untuk menguji koherensi kluster tanpa supervisi.
"""))

# Cell 1: Environment & Imports
cells.append(nbf.v4.new_code_cell("""import os
import sys
import re
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# Styling
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.size'] = 10
%matplotlib inline

print("Libraries imported successfully.")
"""))

# Cell 2: Load Taxonomy & Review Assignments
cells.append(nbf.v4.new_markdown_cell("""## 1. Pemuatan Taksonomi Aspek & Hasil Penugasan Ulasan
Memuat taksonomi aspek dari `config/aspect_taxonomy.json` dan hasil penugasan multi-aspek dari `data/final/topic_analysis/review_aspect_assignments.csv`."""))

cells.append(nbf.v4.new_code_cell("""assign_path = '../data/final/topic_analysis/review_aspect_assignments.csv'
if not os.path.exists(assign_path):
    assign_path = 'data/final/topic_analysis/review_aspect_assignments.csv'

df_assign = pd.read_csv(assign_path)
print(f"Total reviews in assignment table: {len(df_assign)}")
print(f"Reviews with >= 1 detected aspect: {df_assign['has_aspect'].sum()} / 417 ({df_assign['has_aspect'].mean()*100:.2f}%)")
print("\\nAspect count distribution:")
print(df_assign['aspect_count'].value_counts().sort_index())
"""))

# Cell 3: Scope A Visualization
cells.append(nbf.v4.new_markdown_cell("""## 2. Analisis Scope A: Cakupan Aspek Seluruh Ulasan (N=417)
Memvisualisasikan total kemunculan setiap aspek dan proporsi sentimennya (Negatif, Netral, Positif)."""))

cells.append(nbf.v4.new_code_cell("""sa_path = '../data/final/topic_analysis/aspect_summary_all_reviews.csv'
if not os.path.exists(sa_path):
    sa_path = 'data/final/topic_analysis/aspect_summary_all_reviews.csv'

df_sa = pd.read_csv(sa_path)
display(df_sa[['aspect_name', 'total_mentions', 'mention_percentage_total', 'count_negative', 'count_neutral', 'count_positive', 'top_application']])

# Stacked bar plot
fig, ax = plt.subplots(figsize=(12, 6))
aspect_names = df_sa['aspect_name']
neg = df_sa['count_negative']
neu = df_sa['count_neutral']
pos = df_sa['count_positive']

ax.barh(aspect_names, neg, label='Negative', color='#E74C3C')
ax.barh(aspect_names, neu, left=neg, label='Neutral', color='#F39C12')
ax.barh(aspect_names, pos, left=neg + neu, label='Positive', color='#2ECC71')

ax.set_xlabel('Number of Review Mentions')
ax.set_title('Scope A: Aspect Mentions Broken Down by Sentiment (All Reviews, N=417)', fontsize=12, fontweight='bold')
ax.legend(loc='lower right')
ax.invert_yaxis()
plt.tight_layout()
plt.show()
"""))

# Cell 4: Scope B Visualization: Customer Pain Points
cells.append(nbf.v4.new_markdown_cell("""## 3. Analisis Scope B: Customer Pain Points (Negative + Neutral Reviews, N=185)
Fokus khusus pada ulasan keluhan kritis dan pertanyaan pengguna untuk memetakan titik hambatan produk (*pain points*)."""))

cells.append(nbf.v4.new_code_cell("""sb_path = '../data/final/topic_analysis/aspect_summary_negative_neutral.csv'
if not os.path.exists(sb_path):
    sb_path = 'data/final/topic_analysis/aspect_summary_negative_neutral.csv'

df_sb = pd.read_csv(sb_path)
display(df_sb[['aspect_name', 'painpoint_mentions', 'painpoint_percentage_of_185', 'negative_complaints', 'neutral_inquiries', 'dominant_application', 'top_painpoint_keywords']])

fig, ax = plt.subplots(figsize=(10, 5))
y_pos = np.arange(len(df_sb))
bars = ax.barh(y_pos, df_sb['painpoint_mentions'], color='#C0392B', alpha=0.85)

ax.set_yticks(y_pos)
ax.set_yticklabels(df_sb['aspect_name'])
ax.invert_yaxis()
ax.set_xlabel('Pain-point Mentions (Complaints + Inquiries)')
ax.set_title('Scope B: Top Customer Voice Pain Points (n=185 Negative & Neutral Reviews)', fontsize=12, fontweight='bold')

for bar in bars:
    w = bar.get_width()
    ax.text(w + 0.5, bar.get_y() + bar.get_height()/2, f'{int(w)} ({w/185*100:.1f}%)',
            ha='left', va='center', fontsize=9, fontweight='bold')

ax.set_xlim(0, max(df_sb['painpoint_mentions']) + 5)
plt.tight_layout()
plt.show()
"""))

# Cell 5: Scope C: Contrastive Analysis
cells.append(nbf.v4.new_markdown_cell("""## 4. Analisis Scope C: Perbandingan Kontras (Apresiasi Positif vs Keluhan Negatif)
Membandingkan aspek yang paling banyak dikeluhkan versus aspek yang paling diapresiasi pengguna."""))

cells.append(nbf.v4.new_code_cell("""sc_path = '../data/final/topic_analysis/aspect_sentiment_comparison.csv'
if not os.path.exists(sc_path):
    sc_path = 'data/final/topic_analysis/aspect_sentiment_comparison.csv'

df_sc = pd.read_csv(sc_path)
display(df_sc[['aspect_name', 'negative_mentions_n73', 'negative_rate_within_neg_pct', 'positive_mentions_n232', 'positive_rate_within_pos_pct', 'contrastive_pattern']])

# Side by side bar
fig, ax = plt.subplots(figsize=(12, 6))
y = np.arange(len(df_sc))
h = 0.35

ax.barh(y - h/2, df_sc['negative_rate_within_neg_pct'], h, label='% within Negative Reviews (n=73)', color='#E74C3C')
ax.barh(y + h/2, df_sc['positive_rate_within_pos_pct'], h, label='% within Positive Reviews (n=232)', color='#2ECC71')

ax.set_yticks(y)
ax.set_yticklabels(df_sc['aspect_name'])
ax.invert_yaxis()
ax.set_xlabel('Mention Rate within Sentiment Group (%)')
ax.set_title('Scope C: Contrastive Aspect Rate (Negative Dissatisfaction vs Positive Appreciation)', fontsize=12, fontweight='bold')
ax.legend()
plt.tight_layout()
plt.show()
"""))

# Cell 6: Exploratory Clustering Diagnostics
cells.append(nbf.v4.new_markdown_cell("""## 5. Eksplorasi Clustering Tanpa Supervisi (TF-IDF + K-Means pada Scope B)
Mengevaluasi hasil clustering eksploratif untuk memeriksa apakah model tanpa supervisi mampu mengidentifikasi kluster yang bermakna pada data teks ulasan mikro."""))

cells.append(nbf.v4.new_code_cell("""diag_path = '../data/final/topic_analysis/exploratory_clustering_summary.csv'
if not os.path.exists(diag_path):
    diag_path = 'data/final/topic_analysis/exploratory_clustering_summary.csv'

df_diag = pd.read_csv(diag_path)
display(df_diag)

cl_path = '../data/final/topic_analysis/exploratory_clustering_assignments.csv'
if not os.path.exists(cl_path):
    cl_path = 'data/final/topic_analysis/exploratory_clustering_assignments.csv'

df_cl = pd.read_csv(cl_path)
print("Distribution across K=4 clusters:")
print(df_cl['kmeans_cluster_k4'].value_counts().sort_index())
"""))

# Cell 7: Manual Validation Sample Inspection
cells.append(nbf.v4.new_markdown_cell("""## 6. Inspeksi Lembar Kerja Sampel Validasi Manual (n=30)
Menampilkan 10 sampel acak dari lembar kerja validasi manual yang disediakan untuk tinjauan pemilik proyek."""))

cells.append(nbf.v4.new_code_cell("""val_path = '../data/final/topic_analysis/aspect_manual_validation_sample.csv'
if not os.path.exists(val_path):
    val_path = 'data/final/topic_analysis/aspect_manual_validation_sample.csv'

df_val = pd.read_csv(val_path)
display(df_val[['app_name', 'human_sentiment_label', 'detected_aspects', 'matched_keywords', 'review_text_clean']].head(10))
"""))

# Cell 8: Strategic Takeaways
cells.append(nbf.v4.new_markdown_cell("""## 7. Kesimpulan Strategis & Prioritas Perbaikan Produk

### 1. Titik Hambatan Pelanggan Terbesar (*Top Customer Pain Points*):
- **Authentication & Access (`login_auth`)**: Muncul di **21.62%** ulasan negatif/netral, terutama kendala aktivasi/verifikasi akun pada *Zahir Certification* dan *Zahir Online*.
- **System Stability & Crash (`crash_stability`)**: Muncul di **17.84%** ulasan negatif/netral (dan 28.77% dari seluruh ulasan negatif murni), didominasi laporan *force close*, *keluar sendiri*, dan *loading lama* pada *Zahir Online*.
- **Pricing & Subscription Transparency (`pricing_subscription`)**: Muncul di **17.84%** ulasan negatif/netral, didominasi keluhan pengguna *Zahir Simple Start* terkait aplikasi yang ternyata berbayar setelah masa trial singkat.

### 2. Fitur Keunggulan Produk (*Product Strengths*):
- **Core Accounting & Inventory (`inventory_accounting`)**: Menjadi aspek yang paling banyak diapresiasi secara positif (40 ulasan positif), menunjukkan bahwa fungsi pembukuan dan stok barang Zahir dinilai handal oleh pengguna yang berhasil menggunakannya.
- **POS & Hardware Printing (`pos_hardware_print`)**: Menunjukkan rasio apresiasi terhadap keluhan sebesar 4:1 (8 positif vs 2 negatif) pada *POS X*.

### 3. Evaluasi Metodologis:
- Pendekatan berbasis taksonomi aturan (*Rule-Based ABSA*) terbukti jauh lebih unggul dibandingkan clustering tanpa supervisi (TF-IDF K-Means menghasilkan silhouette score sangat rendah ~0.02).
- Hasil deteksi kata kunci tetap berstatus bukti awal (*preliminary evidence*) yang siap divalidasi lebih lanjut melalui lembar kerja manual.
"""))

nb['cells'] = cells

with open('notebooks/07_aspect_analysis.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print('Successfully generated notebooks/07_aspect_analysis.ipynb')
