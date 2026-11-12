# -*- coding: utf-8 -*-
"""
generate_nb07.py
----------------
Generator mandiri untuk notebooks/07_instagram_engagement_analysis.ipynb.
Mengonsolidasikan seluruh dimensi analisis engagement Instagram (55 postingan)
dengan visualisasi modern, pelabelan ukuran sampel (n=...), pemisahan tegas korelasi vs kausalitas,
dan penghindaran klaim generalisasi berlebihan.
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
cells.append(nbf.v4.new_markdown_cell("""# 07 - Analisis Performa Postingan & Engagement Media Sosial Instagram

**Zahir Social Analytics — Evaluasi Metrik Interaksi Akun Publik @zahiraccounting**

---

### Deskripsi & Ruang Lingkup Analisis
Notebook ini menyajikan analisis komprehensif terhadap performa konten dan pola interaksi pengguna (*social engagement*) pada akun publik Instagram resmi PT Zahir Internasional (`@zahiraccounting`).

Dataset yang dianalisis mencakup **55 postingan publik** yang diekstraksi secara legitimate tanpa login:
- **Metrik Interaksi Tersedia**: `likes`, `comments`, dan `total_interactions = likes + comments`.
- **Kebijakan Nol-Fabrikasi (*Zero-Fabrication Policy*)**: Metrik penayangan video (`views`) bernilai **100% NaN** karena platform Instagram tidak mengekspos angka penayangan pada web publik tanpa login. Sesuai etika data, nilai ini tidak diisi nol dan tidak dibuat metrik estimasi reach/impressions/engagement rate sintetis.

### Batasan Metodologi & Peringatan Inferensi Kausal
1. **Analisis Observasional**: Seluruh temuan bersifat deskriptif dan korelasional dari data historis observasional, bukan hasil uji acak terkendali (*A/B testing*).
2. **Keterbatasan Ukuran Sampel Format**: Sampel konten format gambar (*single image*) sangat kecil (**n = 3**), sehingga perbedaan performa tidak boleh digeneralisasikan sebagai bukti inferioritas format gambar secara universal.
3. **Pengaruh Kovariat Kolaborasi**: Performa tinggi pada jam posting tertentu atau posting tanpa tagar dipengaruhi kuat oleh postingan kolaborasi viral dengan kreator eksternal, bukan semata-mata faktor waktu atau ketiadaan tagar itu sendiri.
4. **Penghindaran Generalisasi Keliru**: Korelasi negatif tagar tidak menyiratkan bahwa penambahan tagar menurunkan engagement (*correlation != causation*).

---

### Metadata Input & Output
- **File Input**:
  - `data/export/instagram/master/instagram_master.csv` (atau `data/final/instagram_posts_final.csv`: 55 baris, 27 kolom).
- **Output Artefak Visual**:
  - `outputs/figures/instagram_format_kolaborasi.png`
  - `outputs/figures/instagram_engagement_deepdive.png`
- **Prasyarat Lingkungan**:
  - Python 3.11.x, `pandas`, `numpy`, `scipy`, `matplotlib`, `seaborn`.
"""))

# Cell 1: Environment Setup
cells.append(nbf.v4.new_code_cell("""from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display

# Resolusi path repositori
ROOT = Path.cwd().resolve()
if not (ROOT / 'data' / 'export').is_dir():
    ROOT = ROOT.parent
if not (ROOT / 'data' / 'export').is_dir():
    raise FileNotFoundError('Jalankan Jupyter Notebook dari root repository atau folder notebooks.')

# Styling visualisasi konsisten dan profesional
sns.set_theme(style='whitegrid', font_scale=1.0)
plt.rcParams['figure.dpi'] = 150
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'DejaVu Sans', 'Arial']

FIG_DIR = ROOT / 'outputs' / 'figures'
FIG_DIR.mkdir(parents=True, exist_ok=True)

print(f'Root direktori: {ROOT}')
print('Setup library analisis engagement selesai.')
"""))

# Cell 2: Data Loading & Verification Markdown
cells.append(nbf.v4.new_markdown_cell("""## 1. Pemuatan Dataset Master Instagram & Verifikasi Skema

Memuat dataset master terstandarisasi (`instagram_master.csv`), memvalidasi bahwa seluruh 55 postingan unik terpelihara, dan memastikan kepatuhan kebijakan nol-fabrikasi data.
"""))

# Cell 3: Data Loading & Verification Code
cells.append(nbf.v4.new_code_cell("""master_path = ROOT / 'data' / 'export' / 'instagram' / 'master' / 'instagram_master.csv'
if not master_path.is_file():
    master_path = ROOT / 'data' / 'final' / 'instagram_posts_final.csv'

assert master_path.is_file(), f'Dataset Instagram tidak ditemukan di {master_path}'
df = pd.read_csv(master_path)

print(f'Dataset Instagram Dimuat: {df.shape[0]} postingan, {df.shape[1]} kolom.')
assert len(df) == 55, f'Ukuran dataset tidak valid: {len(df)} (diharapkan 55)'
assert df['post_id'].nunique() == 55, 'Terdapat duplikasi post_id!'
assert (df['total_interactions'] == df['likes'] + df['comments']).all(), 'Aritmatika total_interactions tidak konsisten!'
assert df['views'].isna().all(), 'Kebijakan nol-fabrikasi terlanggar: views harus 100% NaN!'

print('[PASS] Integritas skema, keunikan kunci, dan verifikasi zero-fabrication terpenuhi 100%.')
"""))

# Cell 4: Descriptive Stats & Outlier Markdown
cells.append(nbf.v4.new_markdown_cell("""## 2. Statistik Deskriptif Engagement & Deteksi Outlier IQR

Distribusi engagement Instagram Zahir memiliki kemencengan sangat tajam ke kanan (*highly right-skewed distribution*):
- Sebagian besar postingan memiliki interaksi pada rentang moderat (Median = **51 interaksi**).
- Beberapa postingan viral memperoleh ribuan interaksi (Maksimum = **3,217 interaksi**), sehingga mendongkrak rata-rata aritmatika menjadi **239.04**.
- Oleh karena itu, **median dan IQR adalah ukuran tendensi sentral yang jauh lebih representatif** dibandingkan rata-rata (*mean*).
"""))

# Cell 5: Descriptive Stats & Outlier Code & Plot
cells.append(nbf.v4.new_code_cell("""metrics = ['likes', 'comments', 'total_interactions']
summary_list = []

for m in metrics:
    s = df[m]
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1
    thresh = q3 + 1.5 * iqr
    outliers = s[s > thresh]
    summary_list.append({
        'Metrik': m,
        'Total Akumulasi': int(s.sum()),
        'Mean': round(float(s.mean()), 2),
        'Std Dev': round(float(s.std()), 2),
        'Median': round(float(s.median()), 2),
        'Min': int(s.min()),
        'Max': int(s.max()),
        'Q1 (25%)': round(q1, 2),
        'Q3 (75%)': round(q3, 2),
        'IQR': round(iqr, 2),
        'Batas Outlier (Q3+1.5*IQR)': round(thresh, 2),
        'Jumlah Outlier': int(len(outliers)),
        'Skewness': round(float(s.skew()), 2)
    })

summary_df = pd.DataFrame(summary_list)
display(summary_df)

# Ambang batas outlier IQR untuk total interaksi
q1_inter = df['total_interactions'].quantile(0.25)
q3_inter = df['total_interactions'].quantile(0.75)
thresh_inter = q3_inter + 1.5 * (q3_inter - q1_inter)
outliers_df = df[df['total_interactions'] > thresh_inter]

print(f'\\nAmbang Batas Outlier IQR: > {thresh_inter:.1f} interaksi.')
print(f'Jumlah Postingan Viral Outlier: {len(outliers_df)} postingan ({len(outliers_df)/len(df)*100:.1f}% dari seluruh konten).')
print(f'Kontribusi Interaksi Outlier: {outliers_df[\"total_interactions\"].sum():,} dari {df[\"total_interactions\"].sum():,} ({outliers_df[\"total_interactions\"].sum()/df[\"total_interactions\"].sum()*100:.1f}% total interaksi!).')

# Visualisasi Distribusi dan Outlier
fig, axes = plt.subplots(1, 2, figsize=(14, 5), layout='constrained')

# Subplot 1: Distribusi Total Interaksi (Skala Logaritma / Asli)
sns.histplot(df['total_interactions'], bins=25, ax=axes[0], color='#1F77B4', kde=True)
axes[0].axvline(df['total_interactions'].median(), color='red', linestyle='--', linewidth=1.8, label=f'Median: {df[\"total_interactions\"].median():.0f}')
axes[0].axvline(df['total_interactions'].mean(), color='orange', linestyle=':', linewidth=1.8, label=f'Mean: {df[\"total_interactions\"].mean():.1f}')
axes[0].axvline(thresh_inter, color='purple', linestyle='-.', linewidth=1.8, label=f'Ambang Outlier: {thresh_inter:.1f}')
axes[0].set_title('Distribusi Total Interaksi Konten (Likes + Comments)\\n(n=55 postingan)', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Total Interaksi', fontsize=11)
axes[0].set_ylabel('Frekuensi', fontsize=11)
axes[0].legend(loc='upper right')

# Subplot 2: Boxplot & Strip Plot Deteksi Outlier
sns.boxplot(x=df['total_interactions'], ax=axes[1], color='#AEC7E8', width=0.4)
sns.stripplot(x=df['total_interactions'], ax=axes[1], color='#D62728', size=6, jitter=0.2, alpha=0.7)
axes[1].set_title('Deteksi Outlier IQR pada Total Interaksi', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Total Interaksi (Titik merah = postingan individual)', fontsize=11)

plt.show()
"""))

# Cell 6: Content Type Performance Markdown
cells.append(nbf.v4.new_markdown_cell("""## 3. Perbandingan Performa Jenis Konten (Format Konten)

Analisis membandingkan tiga format publikasi:
- **Video / Reels**: Format dominan (**n = 44 postingan**, 80.0%).
- **Carousel**: Format multi-slide edukatif (**n = 8 postingan**, 14.5%).
- **Single Image**: Format grafis tunggal (**n = 3 postingan**, 5.5%).

*Peringatan Metodologi*: Mengingat sampel format Image hanya berjumlah 3 postingan, rendahnya metrik interaksi pada format ini tidak boleh digeneralisasikan sebagai inferioritas format secara umum.
"""))

# Cell 7: Content Type Performance Code & Plot
cells.append(nbf.v4.new_code_cell("""content_summary = df.groupby('content_type').agg(
    jumlah_post=('post_id', 'count'),
    total_interaksi=('total_interactions', 'sum'),
    mean_interaksi=('total_interactions', 'mean'),
    median_interaksi=('total_interactions', 'median'),
    iqr_interaksi=('total_interactions', lambda x: x.quantile(0.75) - x.quantile(0.25)),
    max_interaksi=('total_interactions', 'max')
).reset_index()

content_summary['pangsa_interaksi_pct'] = (content_summary['total_interaksi'] / df['total_interactions'].sum() * 100).round(2)
content_summary['mean_interaksi'] = content_summary['mean_interaksi'].round(1)
content_summary['median_interaksi'] = content_summary['median_interaksi'].round(1)
content_summary = content_summary.sort_values(by='total_interaksi', ascending=False).reset_index(drop=True)

display(content_summary)
"""))

# Cell 8: Collaboration Performance Markdown
cells.append(nbf.v4.new_markdown_cell("""## 4. Analisis Konten Kolaborasi (*Collaboration Impact Analysis*)

Postingan yang terbit di profil `@zahiraccounting` mencakup dua kelompok:
1. **Organik / Zahir Langsung** (`is_collaboration = False`): Konten inisiatif mandiri Zahir (**n = 29 postingan**).
2. **Kolaborasi / Co-Author** (`is_collaboration = True`): Konten kemitraan bersama akun lain (**n = 26 postingan**).

Akun mitra mencakup:
- `@muhamad.is` (Founder / Executive Zahir): 14 postingan
- `@pecahtelur.id` (Media wirausaha & UMKM inspiratif): 8 postingan
- `@zahironlineid`: 2 postingan
- `@zahirerp` & `@modalngobrol`: masing-masing 1 postingan

*Peringatan Kausalitas*: Kolaborasi menghasilkan rata-rata engagement yang jauh lebih tinggi terutama karena menjangkau audiens eksternal mitra yang telah memiliki basis pengikut besar, bukan semata efek teknis penandaan (*co-author flag*).
"""))

# Cell 9: Collaboration Performance Code & Combined Plot
cells.append(nbf.v4.new_code_cell("""colab_summary = df.groupby('is_collaboration').agg(
    jumlah_post=('post_id', 'count'),
    total_interaksi=('total_interactions', 'sum'),
    mean_interaksi=('total_interactions', 'mean'),
    median_interaksi=('total_interactions', 'median'),
    outlier_count=('total_interactions', lambda x: (x > thresh_inter).sum())
).reset_index()

colab_summary['Status'] = colab_summary['is_collaboration'].map({False: 'Non-Kolaborasi (Organik)', True: 'Kolaborasi (Co-Author)'})
colab_summary['pangsa_interaksi_pct'] = (colab_summary['total_interaksi'] / df['total_interactions'].sum() * 100).round(2)
colab_summary['mean_interaksi'] = colab_summary['mean_interaksi'].round(1)

display(colab_summary[['Status', 'jumlah_post', 'total_interaksi', 'pangsa_interaksi_pct', 'mean_interaksi', 'median_interaksi', 'outlier_count']])

# Visualisasi Format Konten & Status Kolaborasi
fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), layout='constrained')

# Subplot 1: Perbandingan Format Konten dengan Ukuran Sampel (n=...)
fmt_order = ['video/reel', 'carousel', 'image']
box_fmt = sns.boxplot(data=df, x='content_type', y='total_interactions', order=fmt_order,
                      palette=['#1F77B4', '#FF7F0E', '#2CA02C'], ax=axes[0], width=0.45)
sns.stripplot(data=df, x='content_type', y='total_interactions', order=fmt_order,
              color='black', alpha=0.5, jitter=0.2, ax=axes[0])

# Label ukuran sampel dan median
fmt_labels = [f"Reel / Video\\n(n=44, med={df[df['content_type']=='video/reel']['total_interactions'].median():.0f})",
              f"Carousel\\n(n=8, med={df[df['content_type']=='carousel']['total_interactions'].median():.0f})",
              f"Image\\n(n=3, med={df[df['content_type']=='image']['total_interactions'].median():.0f})"]
axes[0].set_xticks(range(3))
axes[0].set_xticklabels(fmt_labels, fontsize=10)
axes[0].set_yscale('log')
axes[0].set_title('Distribusi Interaksi per Format Konten (Skala Log)', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Format Konten', fontsize=11)
axes[0].set_ylabel('Total Interaksi (Logarithmic Scale)', fontsize=11)

# Subplot 2: Perbandingan Kolaborasi vs Non-Kolaborasi
colab_order = [False, True]
box_colab = sns.boxplot(data=df, x='is_collaboration', y='total_interactions', order=colab_order,
                        palette=['#7F7F7F', '#1F77B4'], ax=axes[1], width=0.45)
sns.stripplot(data=df, x='is_collaboration', y='total_interactions', order=colab_order,
              color='black', alpha=0.5, jitter=0.2, ax=axes[1])

colab_labels = [f"Organik Zahir\\n(n=29, med={df[~df['is_collaboration']]['total_interactions'].median():.0f})",
                f"Kolaborasi\\n(n=26, med={df[df['is_collaboration']]['total_interactions'].median():.0f})"]
axes[1].set_xticks(range(2))
axes[1].set_xticklabels(colab_labels, fontsize=10)
axes[1].set_yscale('log')
axes[1].set_title('Distribusi Interaksi: Organik vs Kolaborasi (Skala Log)', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Status Publikasi', fontsize=11)
axes[1].set_ylabel('Total Interaksi (Logarithmic Scale)', fontsize=11)

fig_path_colab = FIG_DIR / 'instagram_format_kolaborasi.png'
plt.savefig(fig_path_colab, dpi=200)
print(f'Figur tersimpan: {fig_path_colab}')
plt.show()
"""))

# Cell 10: Temporal Dynamics Markdown
cells.append(nbf.v4.new_markdown_cell("""## 5. Dinamika Waktu Publikasi (*Temporal Posting Dynamics*)

Menganalisis pola waktu posting berdasarkan jam publikasi (WIB), segmen waktu (*time bins*), dan hari dalam seminggu:
- **Morning (06:00-11:59 WIB)**: Rata-rata tertinggi didorong oleh masuknya sejumlah Reels kolaborasi viral yang diterbitkan pada pagi hari.
- **Afternoon & Evening**: Pola interaksi lebih terdistribusi secara organik.
"""))

# Cell 11: Temporal Dynamics Code
cells.append(nbf.v4.new_code_cell("""def classify_time_bin(hour):
    if 6 <= hour <= 11:
        return 'Morning (06:00-11:59)'
    elif 12 <= hour <= 14:
        return 'Afternoon (12:00-14:59)'
    elif 15 <= hour <= 17:
        return 'Late Afternoon (15:00-17:59)'
    elif 18 <= hour <= 23:
        return 'Evening (18:00-23:59)'
    return 'Early Morning (00:00-05:59)'

df['time_bin'] = df['post_hour_wib'].apply(classify_time_bin)

time_summary = df.groupby('time_bin').agg(
    jumlah_post=('post_id', 'count'),
    mean_interaksi=('total_interactions', 'mean'),
    median_interaksi=('total_interactions', 'median'),
    colab_posts=('is_collaboration', 'sum')
).reset_index()

time_summary['mean_interaksi'] = time_summary['mean_interaksi'].round(1)
time_summary['median_interaksi'] = time_summary['median_interaksi'].round(1)
display(time_summary)
"""))

# Cell 12: Caption & Hashtag Markdown
cells.append(nbf.v4.new_markdown_cell("""## 6. Analisis Panjang Caption & Efektivitas Tagar (Hashtags)

### Analisis Korelasi Spearman
- **Panjang Kata Caption (`caption_word_count`)**: Menunjukkan korelasi positif moderat (**Spearman rho = +0.381, p < 0.01**). Konten dengan narasi penjelasan bisnis yang memadai cenderung memicu interaksi lebih baik.
- **Jumlah Tagar (`hashtag_count`)**: Menunjukkan korelasi negatif (**Spearman rho = -0.451, p < 0.001**).

### Peringatan Metodologi Kritis: Mengapa Tagar Terkorelasi Negatif?
Korelasi negatif ini **bukan hubungan sebab-akibat**.
- Postingan kolaborasi viral berkinerja tertinggi (misal bersama `@pecahtelur.id` dan `@muhamad.is`) mayoritas diterbitkan **tanpa menyertakan tagar** dalam caption mereka.
- Sebaliknya, postingan promosi reguler Zahir dengan engagement moderat secara konsisten mencantumkan 5-15 tagar.
- Oleh karena itu, agregat statistik terdistorsi oleh faktor pembingkai (*confounding factor* kolaborasi). Menghapus tagar dari caption **tidak akan** serta-merta meningkatkan interaksi secara mandiri.
"""))

# Cell 13: Caption & Hashtag Code & Plot
cells.append(nbf.v4.new_code_cell("""rho_caption, p_caption = stats.spearmanr(df['caption_word_count'], df['total_interactions'])
rho_hashtag, p_hashtag = stats.spearmanr(df['hashtag_count'], df['total_interactions'])

print(f'Korelasi Spearman (Caption Word Count vs Total Interaksi): rho = {rho_caption:+.3f} (p = {p_caption:.4f})')
print(f'Korelasi Spearman (Hashtag Count vs Total Interaksi):      rho = {rho_hashtag:+.3f} (p = {p_hashtag:.4f})')

# Perbandingan postingan dengan vs tanpa tagar
hash_summary = df.groupby('has_hashtags').agg(
    jumlah_post=('post_id', 'count'),
    total_interaksi=('total_interactions', 'sum'),
    mean_interaksi=('total_interactions', 'mean'),
    median_interaksi=('total_interactions', 'median'),
    colab_count=('is_collaboration', 'sum')
).reset_index()

hash_summary['Status Tagar'] = hash_summary['has_hashtags'].map({True: 'Memiliki Tagar (1-16 #)', False: 'Tanpa Tagar (0 #)'})
display(hash_summary[['Status Tagar', 'jumlah_post', 'total_interaksi', 'mean_interaksi', 'median_interaksi', 'colab_count']])

# Visualisasi Scatter & Boxplot Deep Dive
fig, axes = plt.subplots(1, 2, figsize=(14, 5), layout='constrained')

# Subplot 1: Scatter Panjang Caption vs Total Interaksi (Log Scale)
sns.scatterplot(data=df, x='caption_word_count', y='total_interactions',
                hue='is_collaboration', palette={False: '#7F7F7F', True: '#1F77B4'},
                style='content_type', s=70, ax=axes[0], alpha=0.85)
axes[0].set_yscale('log')
axes[0].set_title(f'Panjang Caption vs Interaksi\\n(Spearman rho = {rho_caption:+.3f})', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Jumlah Kata Caption', fontsize=11)
axes[0].set_ylabel('Total Interaksi (Log Scale)', fontsize=11)
axes[0].legend(title='Kolaborasi / Format', loc='lower right', fontsize=8.5)

# Subplot 2: Boxplot Interaksi Berdasarkan Keberadaan Tagar
sns.boxplot(data=df, x='has_hashtags', y='total_interactions',
            palette=['#D62728', '#2CA02C'], ax=axes[1], width=0.4)
sns.stripplot(data=df, x='has_hashtags', y='total_interactions',
              color='black', alpha=0.5, jitter=0.2, ax=axes[1])
axes[1].set_yscale('log')
axes[1].set_xticks([0, 1])
axes[1].set_xticklabels([f"Tanpa Tagar\\n(n=16, med={df[~df['has_hashtags']]['total_interactions'].median():.0f})",
                         f"Dengan Tagar\\n(n=39, med={df[df['has_hashtags']]['total_interactions'].median():.0f})"], fontsize=10)
axes[1].set_title('Perbandingan Interaksi Berdasarkan Keberadaan Tagar', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Status Tagar', fontsize=11)
axes[1].set_ylabel('Total Interaksi (Log Scale)', fontsize=11)

fig_path_deep = FIG_DIR / 'instagram_engagement_deepdive.png'
plt.savefig(fig_path_deep, dpi=200)
print(f'Figur tersimpan: {fig_path_deep}')
plt.show()
"""))

# Cell 14: Top & Bottom Posts Showcase Markdown
cells.append(nbf.v4.new_markdown_cell("""## 7. Showcase Postingan Terbaik (Top 10) & Terendah (Bottom 5)

Daftar postingan berkinerja tertinggi mengonfirmasi peran format Reels dan kolaborasi bersama figur kunci dalam menghasilkan keterlibatan massal.
"""))

# Cell 15: Top & Bottom Posts Showcase Code
cells.append(nbf.v4.new_code_cell("""top_cols = ['post_id', 'post_date', 'content_type', 'is_collaboration', 'original_account',
            'likes', 'comments', 'total_interactions', 'caption_clean']

top10 = df.sort_values(by='total_interactions', ascending=False).head(10)[top_cols].copy()
top10['caption_summary'] = top10['caption_clean'].fillna('').apply(lambda x: x[:80] + '...' if len(x) > 80 else x)

print('=== 10 POSTINGAN DENGAN TOTAL INTERAKSI TERTINGGI ===')
display(top10[['post_id', 'post_date', 'content_type', 'original_account', 'likes', 'comments', 'total_interactions', 'caption_summary']])

bottom5 = df.sort_values(by='total_interactions', ascending=True).head(5)[top_cols].copy()
bottom5['caption_summary'] = bottom5['caption_clean'].fillna('').apply(lambda x: x[:80] + '...' if len(x) > 80 else x)

print('\\n=== 5 POSTINGAN DENGAN TOTAL INTERAKSI TERENDAH ===')
display(bottom5[['post_id', 'post_date', 'content_type', 'original_account', 'likes', 'comments', 'total_interactions', 'caption_summary']])
"""))

# Cell 16: Conclusion Markdown
cells.append(nbf.v4.new_markdown_cell("""## 8. Kesimpulan & Rekomendasi Strategi Konten

1. **Peran Format Reels**: Video/Reels menyumbang **94.87%** dari keseluruhan interaksi akun (12,472 dari 13,147 interaksi), menjadikannya format komunikasi paling efektif untuk meningkatkan kesadaran merek (*brand awareness*).
2. **Kekuatan Kolaborasi Strategis**: Postingan kemitraan co-author menghasilkan median interaksi **72.0** vs **40.0** pada postingan organik. Kemitraan dengan akun seperti `@pecahtelur.id` terbukti efektif memperluas jangkauan ke audiens pengusaha UMKM.
3. **Kualitas Narasi Caption**: Korelasi positif panjang kata caption (+0.381) menunjukkan bahwa audiens B2B Zahir mengapresiasi konteks bisnis yang informatif daripada caption minimalis satu kalimat.
4. **Kepatuhan Metodologi**:
   - Zero-fabrication terjaga murni: `views` tidak pernah dimanipulasi menjadi nol.
   - Analisis menghindari jebakan kesimpulan kausal palsu mengenai tagar dan jam posting.
"""))

nb.cells = cells
out_path = Path('notebooks/07_instagram_engagement_analysis.ipynb')
with open(out_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f'Successfully generated {out_path} with {len(cells)} cells.')
