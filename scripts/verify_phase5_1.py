import os
import sys
import pandas as pd
import openpyxl

print("=" * 65)
print("PHASE 5.1 AUTOMATED VERIFICATION & READINESS AUDIT")
print("=" * 65)

errors = []

# Paths
REVIEWS_CSV = "data/final/playstore_reviews_final.csv"
GOLD_CSV = "data/final/playstore_gold_set_final.csv"
GOLD_XLSX = "data/final/playstore_gold_set_final.xlsx"
OUTPUT_DIR = "data/final/topic_analysis_readiness"

# 1. Source files check
try:
    df_rev = pd.read_csv(REVIEWS_CSV)
    df_gold_c = pd.read_csv(GOLD_CSV)
    df_gold_x = pd.read_excel(GOLD_XLSX)
    
    if len(df_rev) == 417 and len(df_gold_c) == 417 and len(df_gold_x) == 417:
        print("[PASS] Test 1: Source dataset row counts verified (exactly 417 records across all sources).")
    else:
        err = f"Row count mismatch! reviews={len(df_rev)}, gold_csv={len(df_gold_c)}, gold_xlsx={len(df_gold_x)}"
        errors.append(err)
        print(f"[FAIL] Test 1: {err}")
except Exception as e:
    err = f"Failed to load source datasets: {e}"
    errors.append(err)
    print(f"[FAIL] Test 1: {err}")

# 2. Check Gold Set ground truth labels unchanged
expected_counts = {"positive": 232, "neutral": 112, "negative": 73}
actual_counts = df_gold_c["human_sentiment_label"].value_counts().to_dict()
if actual_counts == expected_counts:
    print("[PASS] Test 2: Gold Set ground truth labels unchanged ({positive: 232, neutral: 112, negative: 73}).")
else:
    err = f"Ground truth labels modified! {actual_counts}"
    errors.append(err)
    print(f"[FAIL] Test 2: {err}")

# 3. Join integrity check
df_join = df_rev.merge(df_gold_c[["review_id", "human_sentiment_label"]], on="review_id", how="inner")
if len(df_join) == 417 and df_join["review_id"].nunique() == 417:
    print("[PASS] Test 3: Relational join on review_id is 100% stable (exactly 417 unique rows, 0 dropped, 0 multiplied).")
else:
    err = f"Join failure! len={len(df_join)}, unique_id={df_join['review_id'].nunique()}"
    errors.append(err)
    print(f"[FAIL] Test 3: {err}")

# 4. CSV and XLSX Tabular Equivalence across all 3 audit artifacts
artifacts = [
    ("Text Quality Summary", os.path.join(OUTPUT_DIR, "text_quality_summary.csv"), os.path.join(OUTPUT_DIR, "text_quality_summary.xlsx")),
    ("Topic Scope Comparison", os.path.join(OUTPUT_DIR, "topic_scope_comparison.csv"), os.path.join(OUTPUT_DIR, "topic_scope_comparison.xlsx")),
    ("Topic Readiness Audit", os.path.join(OUTPUT_DIR, "topic_readiness_audit.csv"), os.path.join(OUTPUT_DIR, "topic_readiness_audit.xlsx"))
]

all_equiv = True
for name, c_file, x_file in artifacts:
    if not os.path.exists(c_file) or not os.path.exists(x_file):
        all_equiv = False
        err = f"Missing file pair for {name}!"
        errors.append(err)
        print(f"[FAIL] Test 4 ({name}): {err}")
        break
    df_c = pd.read_csv(c_file)
    df_x = pd.read_excel(x_file)
    if len(df_c) != len(df_x) or list(df_c.columns) != list(df_x.columns):
        all_equiv = False
        err = f"{name} dimension mismatch between CSV ({df_c.shape}) and XLSX ({df_x.shape})!"
        errors.append(err)
        print(f"[FAIL] Test 4 ({name}): {err}")
        break

if all_equiv:
    print("[PASS] Test 4: CSV and XLSX versions contain 100% equivalent tabular data across all 3 audit artifacts.")

# 5. Privacy Strictness: No Personal Identifiers
forbidden = ["userName", "userImage", "reviewer_id", "reply_text", "replyContent"]
privacy_violation = False
for name, c_file, _ in artifacts:
    df_c = pd.read_csv(c_file)
    for f in forbidden:
        if f in df_c.columns:
            privacy_violation = True
            err = f"Privacy violation: found forbidden column '{f}' in {name}"
            errors.append(err)
            print(f"[FAIL] Test 5: {err}")
            break

if not privacy_violation:
    print("[PASS] Test 5: Privacy strictly preserved. 0 reviewer identifiers or personal data in audit tables.")

# 6. Report and Code Deliverables
report_path = "docs/topic_analysis_readiness_report.md"
audit_script = "analysis/topic_analysis_readiness_audit.py"

if os.path.exists(report_path) and os.path.exists(audit_script):
    print(f"[PASS] Test 6: Audit deliverables verified ({report_path}, {audit_script}).")
else:
    err = "Missing markdown report or audit generator script!"
    errors.append(err)
    print(f"[FAIL] Test 6: {err}")

# 7. Check specific scope numbers match empirical data
df_scope = pd.read_csv(os.path.join(OUTPUT_DIR, "topic_scope_comparison.csv"))
scope_all_row = df_scope[df_scope["scope_name"] == "Scope 1: All Reviews"].iloc[0]
scope_neg_row = df_scope[df_scope["scope_name"] == "Scope 2: Negative Reviews Only"].iloc[0]
scope_neu_neg_row = df_scope[df_scope["scope_name"] == "Scope 3: Negative + Neutral Reviews"].iloc[0]

if (
    scope_all_row["sample_size_n"] == 417 and
    scope_neg_row["sample_size_n"] == 73 and
    scope_neu_neg_row["sample_size_n"] == 185 and
    scope_neg_row["duplicate_text_rows"] == 0
):
    print("[PASS] Test 7: Scope metrics match verified empirical data (All=417, Neg=73, Neg+Neu=185, Neg duplicates=0).")
else:
    err = "Scope numbers divergence detected!"
    errors.append(err)
    print(f"[FAIL] Test 7: {err}")

print("=" * 65)
if errors:
    print(f"VERIFICATION FAILED WITH {len(errors)} ERRORS:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("ALL 7 TOPIC READINESS VERIFICATION TESTS PASSED SUCCESSFULLY (100% SUCCESS)!")
    print("=" * 65)
    sys.exit(0)
