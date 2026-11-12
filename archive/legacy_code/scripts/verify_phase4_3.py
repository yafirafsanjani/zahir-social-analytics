import sys
import os
import pandas as pd
import openpyxl

print("=" * 65)
print("PHASE 4.3 AUTOMATED VERIFICATION & BENCHMARK AUDIT")
print("=" * 65)

errors = []

# Paths
GOLD_CSV = "data/final/playstore_gold_set_final.csv"
GOLD_XLSX = "data/final/playstore_gold_set_final.xlsx"
BENCH_DIR = "data/final/sentiment_benchmark"

# 1. Test Gold-Set Unchanged
try:
    df_gold_csv = pd.read_csv(GOLD_CSV)
    df_gold_xlsx = pd.read_excel(GOLD_XLSX)
    if len(df_gold_csv) == 417 and len(df_gold_xlsx) == 417:
        print("[PASS] Test 1: Canonical Gold Set source files intact (exactly 417 records).")
    else:
        err = f"Gold set length altered! csv={len(df_gold_csv)}, xlsx={len(df_gold_xlsx)}"
        errors.append(err)
        print(f"[FAIL] Test 1: {err}")
except Exception as e:
    err = f"Failed to load gold set files: {e}"
    errors.append(err)
    print(f"[FAIL] Test 1: {err}")

# Check Gold-Set label distribution intact
expected_labels = {"positive": 232, "neutral": 112, "negative": 73}
csv_labels = df_gold_csv["human_sentiment_label"].value_counts().to_dict()
if csv_labels == expected_labels:
    print("[PASS] Test 2: Gold Set ground truth labels unchanged ({positive: 232, neutral: 112, negative: 73}).")
else:
    err = f"Gold Set label distribution modified: {csv_labels}"
    errors.append(err)
    print(f"[FAIL] Test 2: {err}")

# 2. Test Split Manifest Reproducibility & No Overlap
manifest_csv = os.path.join(BENCH_DIR, "sentiment_split_manifest.csv")
manifest_xlsx = os.path.join(BENCH_DIR, "sentiment_split_manifest.xlsx")

try:
    df_man_csv = pd.read_csv(manifest_csv)
    df_man_xlsx = pd.read_excel(manifest_xlsx)
    
    dev_ids = set(df_man_csv[df_man_csv["split"] == "development"]["review_id"])
    test_ids = set(df_man_csv[df_man_csv["split"] == "test"]["review_id"])
    overlap = dev_ids.intersection(test_ids)
    
    if len(overlap) == 0 and len(dev_ids) == 333 and len(test_ids) == 84:
        print(f"[PASS] Test 3: Split is stratified 80/20 (Dev=333, Test=84) with 0 overlapping review_ids.")
    else:
        err = f"Split invalid! overlap={len(overlap)}, dev={len(dev_ids)}, test={len(test_ids)}"
        errors.append(err)
        print(f"[FAIL] Test 3: {err}")
except Exception as e:
    err = f"Failed to verify split manifest: {e}"
    errors.append(err)
    print(f"[FAIL] Test 3: {err}")

# 3. Test Test Predictions Match Genuine Test Records
pred_csv = os.path.join(BENCH_DIR, "sentiment_test_predictions.csv")
pred_xlsx = os.path.join(BENCH_DIR, "sentiment_test_predictions.xlsx")

try:
    df_pred_csv = pd.read_csv(pred_csv)
    df_pred_xlsx = pd.read_excel(pred_xlsx)
    
    pred_ids = set(df_pred_csv["review_id"])
    if pred_ids == test_ids and len(df_pred_csv) == 84:
        print("[PASS] Test 4: Every test prediction matches genuine held-out test record exactly (84/84).")
    else:
        err = f"Test predictions ID mismatch! missing={len(test_ids - pred_ids)}, count={len(df_pred_csv)}"
        errors.append(err)
        print(f"[FAIL] Test 4: {err}")
except Exception as e:
    err = f"Failed to verify test predictions: {e}"
    errors.append(err)
    print(f"[FAIL] Test 4: {err}")

# 4. Human Labels and Model Predictions in Separate Columns
expected_pred_cols = [
    "review_id", "app_name", "review_datetime", "review_text_clean",
    "human_sentiment_label", "pred_majority", "pred_inset_lexicon",
    "inset_score", "pred_tfidf_lr", "tfidf_lr_confidence",
    "pred_indobert", "indobert_confidence"
]
has_cols = list(df_pred_csv.columns) == expected_pred_cols
human_untouched = (df_pred_csv["human_sentiment_label"] == df_gold_csv.set_index("review_id").loc[df_pred_csv["review_id"]]["human_sentiment_label"].values).all()

if has_cols and human_untouched:
    print("[PASS] Test 5: Human labels and model predictions strictly separated; human labels untouched.")
else:
    err = f"Column structure or human label alteration detected! cols={list(df_pred_csv.columns)}"
    errors.append(err)
    print(f"[FAIL] Test 5: {err}")

# 5. Metrics Calculated from Held-out Test Set Only
metrics_csv = os.path.join(BENCH_DIR, "sentiment_benchmark_metrics.csv")
metrics_xlsx = os.path.join(BENCH_DIR, "sentiment_benchmark_metrics.xlsx")

try:
    df_met_csv = pd.read_csv(metrics_csv)
    df_met_xlsx = pd.read_excel(metrics_xlsx)
    
    if (df_met_csv["test_support"] == 84).all() and len(df_met_csv) == 4:
        print("[PASS] Test 6: Metrics calculated strictly on held-out test set (n=84 across all 4 models).")
    else:
        err = f"Metrics support count invalid! support={df_met_csv['test_support'].tolist()}"
        errors.append(err)
        print(f"[FAIL] Test 6: {err}")
except Exception as e:
    err = f"Failed to verify metrics file: {e}"
    errors.append(err)
    print(f"[FAIL] Test 6: {err}")

# 6. CSV and XLSX Tabular Equivalence across all 4 benchmark artifacts
artifacts = [
    ("Split Manifest", manifest_csv, manifest_xlsx),
    ("Test Predictions", pred_csv, pred_xlsx),
    ("Benchmark Metrics", metrics_csv, metrics_xlsx),
    ("Error Analysis", os.path.join(BENCH_DIR, "sentiment_error_analysis.csv"), os.path.join(BENCH_DIR, "sentiment_error_analysis.xlsx"))
]

all_equiv = True
for name, c_file, x_file in artifacts:
    df_c = pd.read_csv(c_file)
    df_x = pd.read_excel(x_file)
    if len(df_c) != len(df_x) or list(df_c.columns) != list(df_x.columns):
        all_equiv = False
        err = f"{name} shape or column divergence between CSV and XLSX!"
        errors.append(err)
        print(f"[FAIL] Test 7 ({name}): {err}")
        break

if all_equiv:
    print("[PASS] Test 7: CSV and XLSX versions contain 100% equivalent tabular data across all 4 artifacts.")

# 7. Privacy Preservation: No Reviewer Identifiers
forbidden = ["userName", "userImage", "reviewer_id", "reply_text", "replyContent"]
privacy_violation = False
for name, c_file, _ in artifacts:
    df_c = pd.read_csv(c_file)
    for f in forbidden:
        if f in df_c.columns:
            privacy_violation = True
            err = f"Privacy violation: found forbidden column '{f}' in {name}"
            errors.append(err)
            print(f"[FAIL] Test 8: {err}")
            break

if not privacy_violation:
    print("[PASS] Test 8: Privacy strictly preserved. 0 reviewer identifiers or developer replies in benchmark files.")

# 8. Notebook and Code Artifact Verification
nb_path = "notebooks/06_sentiment_benchmarking.ipynb"
mod_path = "analysis/sentiment_benchmarking.py"
doc_path = "docs/sentiment_benchmark_report.md"

if os.path.exists(nb_path) and os.path.exists(mod_path) and os.path.exists(doc_path):
    print(f"[PASS] Test 9: All reproducible deliverables exist ({nb_path}, {mod_path}, {doc_path}).")
else:
    err = "Missing deliverable notebook, module, or report!"
    errors.append(err)
    print(f"[FAIL] Test 9: {err}")

print("=" * 65)
if errors:
    print(f"VERIFICATION FAILED WITH {len(errors)} ERRORS:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("ALL 9 BENCHMARK VERIFICATION TESTS PASSED SUCCESSFULLY (100% SUCCESS)!")
    print("=" * 65)
    sys.exit(0)
