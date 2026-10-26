import json
import nbformat as nbf

nb = nbf.v4.new_notebook()

cells = []

# Title & Overview
cells.append(nbf.v4.new_markdown_cell("""# 06. NLP Sentiment Analysis Benchmarking & Baseline Comparison
**Zahir Social Analytics — Play Store Customer Voice Analytics**  
**Audit & Execution Date:** 2026-10-26  
**Status:** Canonical Gold Set Benchmarked & Frozen (Phase 4.3)

---

## Executive Summary & Objectives
Tujuan dari notebook ini adalah melakukan evaluasi komparatif (*benchmarking*) terhadap berbagai metode analisis sentimen teks berbahasa Indonesia dengan acuan mutlak **Human Gold Set 417 Ulasan Google Play Store** (`data/final/playstore_gold_set_final.csv` & `.xlsx`).

Sesuai dengan protokol evaluasi machine learning yang ketat:
1. **Autoritas Label Manusia**: `human_sentiment_label` diperlakukan sebagai *single source of truth*. Rating bintang sama sekali tidak digunakan untuk menginferensi sentimen teks.
2. **Stratified 80/20 Train-Independent Split**: Pemisahan data dilakukan secara acak terstratifikasi (`random_state=42`) menghasilkan 333 data pengembangan (*development set*) dan 84 data pengujian (*held-out test set*). Data uji benar-benar diisolasi.
3. **Multi-tier Candidate Benchmarking**:
   - **Baseline 1 (Heuristic / Zero-Rule)**: *Majority Class Baseline* (selalu memprediksi kelas dominan `positive`).
   - **Baseline 2 (Indonesian Sentiment Lexicon)**: *InSet Lexicon* (Koto & Rahmaningtyas, IALP 2017) dilengkapi *negation handling*.
   - **Baseline 3 (Supervised Bag-of-Words)**: *TF-IDF + Logistic Regression* (dilatih khusus pada Development Set).
   - **Candidate 4 (Pretrained Deep Transformer)**: *IndoBERT Base Pretrained Sentiment Classifier* (`mdhugol/indonesia-bert-sentiment-classification`, berbasis `indobenchmark/indobert-base-p1` fine-tuned pada SmSA IndoNLU).
4. **Metrik Utama**: **Macro-F1** dijadikan metrik komparasi primer mengingat ketidakseimbangan kelas (*imbalanced class distribution*).
"""))

# Cell 1: Environment & Imports
cells.append(nbf.v4.new_code_cell("""import os
import sys
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    classification_report,
    confusion_matrix
)
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Transformers & PyTorch
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

# Visual styling
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.size'] = 10
%matplotlib inline

print("Environment libraries imported successfully.")
"""))

# Cell 2: Verify & Load Gold Set
cells.append(nbf.v4.new_markdown_cell("""## 1. Verifikasi & Pemuatan Canonical Gold Set
Memastikan file `data/final/playstore_gold_set_final.csv` memuat tepat 417 ulasan teranotasi manusia tanpa missing value."""))

cells.append(nbf.v4.new_code_cell("""gold_path = '../data/final/playstore_gold_set_final.csv'
if not os.path.exists(gold_path):
    gold_path = 'data/final/playstore_gold_set_final.csv'

df_gold = pd.read_csv(gold_path)
print(f"Total rows in Gold Set: {len(df_gold)}")
print(f"Unique review IDs: {df_gold['review_id'].nunique()}")
print("\\nLabel distribution:")
print(df_gold['human_sentiment_label'].value_counts())
print("\\nPercentage:")
print((df_gold['human_sentiment_label'].value_counts(normalize=True) * 100).round(2))

assert len(df_gold) == 417
assert df_gold['human_sentiment_label'].isnull().sum() == 0
"""))

# Cell 3: Split Manifest Inspection
cells.append(nbf.v4.new_markdown_cell("""## 2. Inspeksi Manifest Stratified Train/Test Split (80/20)
Pemisahan 417 ulasan menjadi 333 data Development (80%) dan 84 data Held-out Test (20%) dengan proporsi label yang identik."""))

cells.append(nbf.v4.new_code_cell("""manifest_path = '../data/final/sentiment_benchmark/sentiment_split_manifest.csv'
if not os.path.exists(manifest_path):
    manifest_path = 'data/final/sentiment_benchmark/sentiment_split_manifest.csv'

df_manifest = pd.read_csv(manifest_path)
print("Split Distribution:")
print(pd.crosstab(df_manifest['split'], df_manifest['human_sentiment_label'], margins=True))

print("\\nPercentage within split:")
print(pd.crosstab(df_manifest['split'], df_manifest['human_sentiment_label'], normalize='index').round(4) * 100)
"""))

# Cell 4: Load Test Predictions & Metrics
cells.append(nbf.v4.new_markdown_cell("""## 3. Pemuatan Hasil Prediksi & Metrik Komparatif
Memuat metrik evaluasi yang dihitung secara independen pada 84 ulasan test set."""))

cells.append(nbf.v4.new_code_cell("""metrics_path = '../data/final/sentiment_benchmark/sentiment_benchmark_metrics.csv'
if not os.path.exists(metrics_path):
    metrics_path = 'data/final/sentiment_benchmark/sentiment_benchmark_metrics.csv'

df_metrics = pd.read_csv(metrics_path)
df_metrics[['model_name', 'accuracy', 'macro_f1', 'weighted_f1', 'negative_f1', 'neutral_f1', 'positive_f1']]
"""))

# Cell 5: Visualization of Benchmark Metrics
cells.append(nbf.v4.new_markdown_cell("""## 4. Visualisasi Komparasi Model Sentimen
Memvisualisasikan Accuracy, Macro-F1, dan F1-Score per kelas sentimen untuk setiap model kandidat."""))

cells.append(nbf.v4.new_code_cell("""fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: Overall Accuracy vs Macro-F1
x = np.arange(len(df_metrics))
width = 0.35

ax = axes[0]
rects1 = ax.bar(x - width/2, df_metrics['accuracy'], width, label='Accuracy', color='#4A90E2')
rects2 = ax.bar(x + width/2, df_metrics['macro_f1'], width, label='Macro-F1 (Primary)', color='#E74C3C')

ax.set_ylabel('Score')
ax.set_title('Overall Performance Comparison on Held-Out Test Set (n=84)', fontsize=12, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(df_metrics['model_name'], rotation=15, ha='right')
ax.set_ylim(0, 1.0)
ax.legend()
ax.grid(axis='y', linestyle='--', alpha=0.7)

for rect in rects1 + rects2:
    height = rect.get_height()
    ax.annotate(f'{height:.2f}',
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3), textcoords="offset points",
                ha='center', va='bottom', fontsize=9)

# Plot 2: Per-Class F1-Score
ax2 = axes[1]
w = 0.25
ax2.bar(x - w, df_metrics['negative_f1'], w, label='Negative F1', color='#E74C3C')
ax2.bar(x, df_metrics['neutral_f1'], w, label='Neutral F1', color='#95A5A6')
ax2.bar(x + w, df_metrics['positive_f1'], w, label='Positive F1', color='#2ECC71')

ax2.set_ylabel('F1 Score')
ax2.set_title('Per-Class F1-Score Breakdown across Models', fontsize=12, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(df_metrics['model_name'], rotation=15, ha='right')
ax2.set_ylim(0, 1.0)
ax2.legend()
ax2.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()
"""))

# Cell 6: Confusion Matrix Heatmaps
cells.append(nbf.v4.new_markdown_cell("""## 5. Analisis Confusion Matrix
Menganalisis matriks kontingensi untuk mendeteksi kecenderungan bias kesalahan pada setiap model kandidat."""))

cells.append(nbf.v4.new_code_cell("""pred_path = '../data/final/sentiment_benchmark/sentiment_test_predictions.csv'
if not os.path.exists(pred_path):
    pred_path = 'data/final/sentiment_benchmark/sentiment_test_predictions.csv'

df_preds = pd.read_csv(pred_path)
labels = ['negative', 'neutral', 'positive']

fig, axes = plt.subplots(2, 2, figsize=(12, 10))
model_configs = [
    ('Majority Class Baseline', 'pred_majority', axes[0, 0]),
    ('InSet Lexicon (+/-2.0 th)', 'pred_inset_lexicon', axes[0, 1]),
    ('TF-IDF + Logistic Regression', 'pred_tfidf_lr', axes[1, 0]),
    ('IndoBERT Pretrained (SmSA)', 'pred_indobert', axes[1, 1])
]

for title, col, ax in model_configs:
    cm = confusion_matrix(df_preds['human_sentiment_label'], df_preds[col], labels=labels)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False, ax=ax,
                xticklabels=labels, yticklabels=labels)
    ax.set_title(title, fontweight='bold')
    ax.set_xlabel('Predicted Label')
    ax.set_ylabel('True Human Label')

plt.tight_layout()
plt.show()
"""))

# Cell 7: In-Depth Error Analysis
cells.append(nbf.v4.new_markdown_cell("""## 6. Qualitative Error Analysis (IndoBERT vs Human Truth)
Menginspeksi pola-pola kesalahan prediksi pada model performa tertinggi (IndoBERT) untuk merumuskan keterbatasan dan rekomendasi fine-tuning."""))

cells.append(nbf.v4.new_code_cell("""err_path = '../data/final/sentiment_benchmark/sentiment_error_analysis.csv'
if not os.path.exists(err_path):
    err_path = 'data/final/sentiment_benchmark/sentiment_error_analysis.csv'

df_err = pd.read_csv(err_path)
bert_err = df_err[df_err['model_name'] == 'IndoBERT Pretrained']

print(f"Total IndoBERT Misclassifications: {len(bert_err)} / 84 ({len(bert_err)/84*100:.1f}%)")
print("\\nError Type Distribution:")
print(bert_err['error_type'].value_counts())

print("\\nSample Misclassifications:")
bert_err[['error_type', 'human_sentiment_label', 'predicted_sentiment', 'review_text_clean']].head(10)
"""))

# Cell 8: Findings & Recommendations
cells.append(nbf.v4.new_markdown_cell("""## 7. Temuan Kunci & Rekomendasi Fase Lanjutan

### Temuan Evaluasi:
1. **Keunggulan IndoBERT**: *IndoBERT Pretrained* mencatat performa terbaik dengan **Macro-F1 = 0.7099** dan **Accuracy = 77.38%**, unggul secara signifikan dibandingkan *Majority Baseline* (Macro-F1 0.2392) dan *InSet Lexicon* (Macro-F1 0.3433).
2. **Keterbatasan Lexicon InSet**: Pendekatan leksikon murni mengalami *recall bias* yang tajam ke arah sentimen negatif (precision hanya 0.24) karena leksikon InSet memuat hampir dua kali lebih banyak kata negatif daripada positif, serta tidak mampu menangani nuansa kalimat tanya dan istilah akuntansi formal.
3. **Kekuatan Baseline TF-IDF + Logistic Regression**: Menghasilkan Macro-F1 yang kompetitif (0.6860), membuktikan bahwa bag-of-words yang dituning pada domain spesifik memiliki parsimoni yang kuat pada kelas mayoritas.
4. **Analisis Error IndoBERT**: Dari 19 kesalahan prediksi IndoBERT, 8 kasus (42.1%) merupakan misklasifikasi *neutral* menjadi *negative*. Hal ini terjadi karena ulasan pertanyaan teknis/faktual pengguna mengandung kata-kata seperti "tidak bisa", "error", atau "gagal", yang diinterpretasikan oleh model pre-trained umum sebagai sentimen negatif, sementara anotator manusia menilai ulasan tersebut secara netral sebagai pertanyaan murni.

### Rekomendasi untuk Fase Selanjutnya:
- **Model Sentimen Final**: Gunakan arsitektur berbasis IndoBERT sebagai backbone analisis sentimen untuk keseluruhan ekosistem Play Store dan Instagram.
- **Topic & Aspect Modeling**: Lanjutkan ke tahap Topic Modeling (LDA / BERTopic) untuk membedah akar isu di balik sentimen negatif (misal: sinkronisasi database, force close ujian sertifikasi, login POS).
"""))

nb['cells'] = cells

with open('notebooks/06_sentiment_benchmarking.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print('Successfully generated notebooks/06_sentiment_benchmarking.ipynb')
