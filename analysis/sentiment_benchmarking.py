import os
import sys
import csv
import json
import re
import numpy as np
import pandas as pd
import openpyxl

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

# Disable Hugging Face symlink warnings on Windows
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

print("=" * 70)
print("PHASE 4.3: NLP SENTIMENT BENCHMARKING & BASELINE PIPELINE")
print("=" * 70)

# Paths
GOLD_CSV = "data/final/playstore_gold_set_final.csv"
GOLD_XLSX = "data/final/playstore_gold_set_final.xlsx"
BENCHMARK_DIR = "data/final/sentiment_benchmark"
os.makedirs(BENCHMARK_DIR, exist_ok=True)

# 1. Load Gold Set
print(f"[1/6] Loading canonical gold set from {GOLD_CSV}...")
df_gold = pd.read_csv(GOLD_CSV)
assert len(df_gold) == 417, f"Expected 417 reviews, got {len(df_gold)}"
print(f"Loaded {len(df_gold)} reviews. Unique IDs: {df_gold['review_id'].nunique()}")

# 2. Reproducible Stratified 80/20 Train-Dev / Test Split
RANDOM_SEED = 42
print(f"[2/6] Generating stratified 80/20 split (random_state={RANDOM_SEED})...")

train_df, test_df = train_test_split(
    df_gold,
    test_size=0.20,
    random_state=RANDOM_SEED,
    stratify=df_gold["human_sentiment_label"]
)

# Create split manifest
manifest_df = df_gold[["review_id", "app_name", "review_datetime", "human_sentiment_label"]].copy()
manifest_df["split"] = manifest_df["review_id"].apply(
    lambda rid: "test" if rid in set(test_df["review_id"]) else "development"
)

# Save split manifest
manifest_csv = os.path.join(BENCHMARK_DIR, "sentiment_split_manifest.csv")
manifest_xlsx = os.path.join(BENCHMARK_DIR, "sentiment_split_manifest.xlsx")
manifest_df.to_csv(manifest_csv, index=False, quoting=csv.QUOTE_ALL, encoding="utf-8")
manifest_df.to_excel(manifest_xlsx, index=False)
print(f"  - Saved manifest: {manifest_csv} & {manifest_xlsx}")
print(f"  - Split distribution: Dev={len(train_df)}, Test={len(test_df)}")

# 3. Model 1: Majority Class Baseline
print("[3/6] Running Candidate 1: Majority Class Baseline...")
dummy = DummyClassifier(strategy="most_frequent")
dummy.fit(train_df["review_text_clean"], train_df["human_sentiment_label"])
preds_dummy = dummy.predict(test_df["review_text_clean"])

# 4. Model 2: InSet Lexicon Baseline
print("[4/6] Running Candidate 2: InSet Lexicon with Negation Handling...")
pos_lex_path = "data/raw/lexicons/inset_positive.tsv"
neg_lex_path = "data/raw/lexicons/inset_negative.tsv"

df_pos = pd.read_csv(pos_lex_path, sep="\t")
df_neg = pd.read_csv(neg_lex_path, sep="\t")
inset_lexicon = {str(row["word"]).strip().lower(): float(row["weight"]) for _, row in df_pos.iterrows()}
inset_lexicon.update({str(row["word"]).strip().lower(): float(row["weight"]) for _, row in df_neg.iterrows()})
negations = {"tidak", "bukan", "belum", "tak", "gak", "nggak", "ga", "kurang", "jangan", "tanpa"}

def score_inset(text):
    tokens = re.findall(r"\b\w+\b", str(text).lower())
    score = 0.0
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if i + 1 < len(tokens):
            bigram = f"{tok} {tokens[i+1]}"
            if bigram in inset_lexicon:
                score += inset_lexicon[bigram]
                i += 2
                continue
        if tok in negations and i + 1 < len(tokens):
            next_tok = tokens[i+1]
            if next_tok in inset_lexicon:
                score += -1.0 * inset_lexicon[next_tok]
                i += 2
                continue
        if tok in inset_lexicon:
            score += inset_lexicon[tok]
        i += 1
    return score

test_inset_scores = test_df["review_text_clean"].apply(score_inset)
# Dev-tuned threshold +/- 2.0 (neutral if -2.0 <= score <= 2.0)
preds_inset = test_inset_scores.apply(
    lambda s: "positive" if s > 2.0 else ("negative" if s < -2.0 else "neutral")
).values

# 5. Model 3: TF-IDF + Logistic Regression (Dev-Trained Baseline)
print("[5/6] Running Candidate 3: TF-IDF + Logistic Regression (Dev-Trained)...")
vec = TfidfVectorizer(ngram_range=(1, 2), max_features=1000)
X_train = vec.fit_transform(train_df["review_text_clean"])
X_test = vec.transform(test_df["review_text_clean"])

clf_lr = LogisticRegression(class_weight="balanced", random_state=RANDOM_SEED, max_iter=1000)
clf_lr.fit(X_train, train_df["human_sentiment_label"])
preds_lr = clf_lr.predict(X_test)
proba_lr = clf_lr.predict_proba(X_test).max(axis=1)

# 6. Model 4: IndoBERT Pretrained Sentiment Classifier
print("[6/6] Running Candidate 4: IndoBERT Pretrained (mdhugol/indonesia-bert-sentiment-classification)...")
model_name = "mdhugol/indonesia-bert-sentiment-classification"
tokenizer = AutoTokenizer.from_pretrained(model_name)
bert_model = AutoModelForSequenceClassification.from_pretrained(model_name)
classifier = pipeline("sentiment-analysis", model=bert_model, tokenizer=tokenizer, truncation=True, max_length=512)

label_map = {"LABEL_0": "positive", "LABEL_1": "neutral", "LABEL_2": "negative"}
bert_raw = classifier(test_df["review_text_clean"].tolist())
preds_bert = [label_map[r["label"]] for r in bert_raw]
conf_bert = [round(float(r["score"]), 4) for r in bert_raw]

# -------------------------------------------------------------------------
# Compile Test Predictions DataFrame
# -------------------------------------------------------------------------
pred_df = test_df[["review_id", "app_name", "review_datetime", "review_text_clean", "human_sentiment_label"]].copy()
pred_df["pred_majority"] = preds_dummy
pred_df["pred_inset_lexicon"] = preds_inset
pred_df["inset_score"] = test_inset_scores.values
pred_df["pred_tfidf_lr"] = preds_lr
pred_df["tfidf_lr_confidence"] = np.round(proba_lr, 4)
pred_df["pred_indobert"] = preds_bert
pred_df["indobert_confidence"] = conf_bert

test_pred_csv = os.path.join(BENCHMARK_DIR, "sentiment_test_predictions.csv")
test_pred_xlsx = os.path.join(BENCHMARK_DIR, "sentiment_test_predictions.xlsx")
pred_df.to_csv(test_pred_csv, index=False, quoting=csv.QUOTE_ALL, encoding="utf-8")
pred_df.to_excel(test_pred_xlsx, index=False)
print(f"Saved test predictions: {test_pred_csv} & {test_pred_xlsx}")

# -------------------------------------------------------------------------
# Calculate Detailed Benchmark Metrics
# -------------------------------------------------------------------------
y_true = test_df["human_sentiment_label"].values
models = [
    ("Majority Class Baseline", preds_dummy),
    ("InSet Lexicon (+/-2.0 th)", preds_inset),
    ("TF-IDF + Logistic Regression", preds_lr),
    ("IndoBERT Pretrained (SmSA)", preds_bert)
]

metrics_records = []
classes = ["negative", "neutral", "positive"]

for name, y_pred in models:
    acc = accuracy_score(y_true, y_pred)
    macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
    weighted_f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)
    macro_prec = precision_score(y_true, y_pred, average="macro", zero_division=0)
    macro_rec = recall_score(y_true, y_pred, average="macro", zero_division=0)
    
    rep = classification_report(y_true, y_pred, labels=classes, output_dict=True, zero_division=0)
    
    rec = {
        "model_name": name,
        "accuracy": round(acc, 4),
        "macro_f1": round(macro_f1, 4),
        "weighted_f1": round(weighted_f1, 4),
        "macro_precision": round(macro_prec, 4),
        "macro_recall": round(macro_rec, 4),
        "negative_precision": round(rep["negative"]["precision"], 4),
        "negative_recall": round(rep["negative"]["recall"], 4),
        "negative_f1": round(rep["negative"]["f1-score"], 4),
        "neutral_precision": round(rep["neutral"]["precision"], 4),
        "neutral_recall": round(rep["neutral"]["recall"], 4),
        "neutral_f1": round(rep["neutral"]["f1-score"], 4),
        "positive_precision": round(rep["positive"]["precision"], 4),
        "positive_recall": round(rep["positive"]["recall"], 4),
        "positive_f1": round(rep["positive"]["f1-score"], 4),
        "test_support": len(y_true),
        "failed_predictions": 0,
        "coverage_rate": 1.0
    }
    metrics_records.append(rec)

metrics_df = pd.DataFrame(metrics_records)
metrics_csv = os.path.join(BENCHMARK_DIR, "sentiment_benchmark_metrics.csv")
metrics_xlsx = os.path.join(BENCHMARK_DIR, "sentiment_benchmark_metrics.xlsx")
metrics_df.to_csv(metrics_csv, index=False, quoting=csv.QUOTE_ALL, encoding="utf-8")
metrics_df.to_excel(metrics_xlsx, index=False)
print(f"Saved benchmark metrics: {metrics_csv} & {metrics_xlsx}")

# -------------------------------------------------------------------------
# Compile Error Analysis
# -------------------------------------------------------------------------
error_records = []
for idx, row in pred_df.iterrows():
    true_label = row["human_sentiment_label"]
    for m_label, col_pred in [
        ("Majority Class Baseline", "pred_majority"),
        ("InSet Lexicon", "pred_inset_lexicon"),
        ("TF-IDF + Logistic Regression", "pred_tfidf_lr"),
        ("IndoBERT Pretrained", "pred_indobert")
    ]:
        pred_label = row[col_pred]
        if pred_label != true_label:
            error_records.append({
                "review_id": row["review_id"],
                "app_name": row["app_name"],
                "review_text_clean": row["review_text_clean"],
                "human_sentiment_label": true_label,
                "predicted_sentiment": pred_label,
                "model_name": m_label,
                "error_type": f"{true_label}_as_{pred_label}"
            })

err_df = pd.DataFrame(error_records)
err_csv = os.path.join(BENCHMARK_DIR, "sentiment_error_analysis.csv")
err_xlsx = os.path.join(BENCHMARK_DIR, "sentiment_error_analysis.xlsx")
err_df.to_csv(err_csv, index=False, quoting=csv.QUOTE_ALL, encoding="utf-8")
err_df.to_excel(err_xlsx, index=False)
print(f"Saved error analysis: {err_csv} & {err_xlsx} ({len(err_df)} error instances)")

print("=" * 70)
print("BENCHMARK SUMMARY (HELD-OUT TEST SET n=84):")
print(metrics_df[["model_name", "accuracy", "macro_f1", "weighted_f1", "negative_f1", "neutral_f1", "positive_f1"]].to_string(index=False))
print("=" * 70)
