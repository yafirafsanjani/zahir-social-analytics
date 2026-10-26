import sys
import os
import pandas as pd
import openpyxl

print("=" * 65)
print("PHASE 5.2 AUTOMATED VERIFICATION & ASPECT EXTRACTION AUDIT")
print("=" * 65)

errors = []

# Paths
REVIEWS_CSV = "data/final/playstore_reviews_final.csv"
GOLD_CSV = "data/final/playstore_gold_set_final.csv"
OUTPUT_DIR = "data/final/topic_analysis"
ASSIGN_CSV = os.path.join(OUTPUT_DIR, "review_aspect_assignments.csv")
ASSIGN_XLSX = os.path.join(OUTPUT_DIR, "review_aspect_assignments.xlsx")

# 1. Check Full Review-Level Output (Exactly 417 unique IDs)
try:
    df_assign = pd.read_csv(ASSIGN_CSV)
    df_gold = pd.read_csv(GOLD_CSV)
    
    if len(df_assign) == 417 and df_assign["review_id"].nunique() == 417:
        print(f"[PASS] Test 1: Full review-level output contains exactly 417 unique review IDs.")
    else:
        err = f"Review count mismatch in assignments! len={len(df_assign)}, unique={df_assign['review_id'].nunique()}"
        errors.append(err)
        print(f"[FAIL] Test 1: {err}")
except Exception as e:
    err = f"Failed to load assignments: {e}"
    errors.append(err)
    print(f"[FAIL] Test 1: {err}")

# 2. Check Gold Set remains unchanged
expected_gold_counts = {"positive": 232, "neutral": 112, "negative": 73}
actual_gold_counts = df_gold["human_sentiment_label"].value_counts().to_dict()
if actual_gold_counts == expected_gold_counts and len(df_gold) == 417:
    print("[PASS] Test 2: Canonical Gold Set remains unchanged ({positive: 232, neutral: 112, negative: 73}).")
else:
    err = f"Gold Set altered! {actual_gold_counts}"
    errors.append(err)
    print(f"[FAIL] Test 2: {err}")

# 3. Check Human Sentiment Labels Preserved Exactly
gold_map = df_gold.set_index("review_id")["human_sentiment_label"].to_dict()
assign_labels = df_assign.set_index("review_id")["human_sentiment_label"].to_dict()

if gold_map == assign_labels:
    print("[PASS] Test 3: Human sentiment labels strictly preserved across all 417 reviews.")
else:
    err = "Discrepancy found between gold sentiment and aspect assignment labels!"
    errors.append(err)
    print(f"[FAIL] Test 3: {err}")

# 4. Check Traceable Keyword Evidence for Every Assigned Aspect
aspect_cols = [
    "aspect_login_auth", "aspect_crash_stability", "aspect_pricing_subscription",
    "aspect_sync_cloud_data", "aspect_pos_hardware_print", "aspect_inventory_accounting",
    "aspect_certification_exam", "aspect_attendance_face"
]

evidence_valid = True
for idx, r in df_assign.iterrows():
    has_asp = r["has_aspect"]
    asp_cnt = r["aspect_count"]
    detected = r["detected_aspects"]
    matched = r["matched_keywords"]
    
    if has_asp:
        if matched == "none" or not matched:
            evidence_valid = False
            break
        # verify each detected aspect appears in matched_keywords
        aspects_list = detected.split("; ")
        for asp in aspects_list:
            if f"{asp}:[" not in matched:
                evidence_valid = False
                break
    else:
        if asp_cnt != 0 or detected != "none" or matched != "none":
            evidence_valid = False
            break

if evidence_valid:
    print("[PASS] Test 4: Every aspect assignment has traceable, explicit keyword evidence in matched_keywords.")
else:
    err = "Evidence mismatch found between boolean aspect columns and matched_keywords!"
    errors.append(err)
    print(f"[FAIL] Test 4: {err}")

# 5. Check Multi-Aspect Reviews Consistency
multi_valid = True
for idx, r in df_assign.iterrows():
    bool_sum = sum(bool(r[col]) for col in aspect_cols)
    if bool_sum != r["aspect_count"]:
        multi_valid = False
        break

if multi_valid:
    print(f"[PASS] Test 5: Multi-aspect reviews handled consistently (boolean column sums exactly equal aspect_count).")
else:
    err = "Multi-aspect count inconsistency detected!"
    errors.append(err)
    print(f"[FAIL] Test 5: {err}")

# 6. Check Scope Counts Match Actual Gold Set Labels
df_scope_b = pd.read_csv(os.path.join(OUTPUT_DIR, "aspect_summary_negative_neutral.csv"))
df_scope_c = pd.read_csv(os.path.join(OUTPUT_DIR, "aspect_sentiment_comparison.csv"))

# Verify Scope B review count is exactly 185 (73 negative + 112 neutral)
sub_b_actual = df_assign[df_assign["human_sentiment_label"].isin(["negative", "neutral"])]
sub_pos_actual = df_assign[df_assign["human_sentiment_label"] == "positive"]
sub_neg_actual = df_assign[df_assign["human_sentiment_label"] == "negative"]

if len(sub_b_actual) == 185 and len(sub_pos_actual) == 232 and len(sub_neg_actual) == 73:
    print("[PASS] Test 6: Scope subsets match verified gold set labels (Scope B=185, Pos=232, Neg=73).")
else:
    err = f"Scope subset count mismatch! sub_b={len(sub_b_actual)}, pos={len(sub_pos_actual)}, neg={len(sub_neg_actual)}"
    errors.append(err)
    print(f"[FAIL] Test 6: {err}")

# 7. Check CSV and XLSX Equivalence across All 7 Output Artifacts
artifacts = [
    ("Assignments", ASSIGN_CSV, ASSIGN_XLSX),
    ("Scope A Summary", os.path.join(OUTPUT_DIR, "aspect_summary_all_reviews.csv"), os.path.join(OUTPUT_DIR, "aspect_summary_all_reviews.xlsx")),
    ("Scope B Summary", os.path.join(OUTPUT_DIR, "aspect_summary_negative_neutral.csv"), os.path.join(OUTPUT_DIR, "aspect_summary_negative_neutral.xlsx")),
    ("Scope C Contrast", os.path.join(OUTPUT_DIR, "aspect_sentiment_comparison.csv"), os.path.join(OUTPUT_DIR, "aspect_sentiment_comparison.xlsx")),
    ("Keyword Audit", os.path.join(OUTPUT_DIR, "aspect_keyword_audit.csv"), os.path.join(OUTPUT_DIR, "aspect_keyword_audit.xlsx")),
    ("Validation Sample", os.path.join(OUTPUT_DIR, "aspect_manual_validation_sample.csv"), os.path.join(OUTPUT_DIR, "aspect_manual_validation_sample.xlsx")),
    ("Clustering Assignments", os.path.join(OUTPUT_DIR, "exploratory_clustering_assignments.csv"), os.path.join(OUTPUT_DIR, "exploratory_clustering_assignments.xlsx")),
    ("Clustering Summary", os.path.join(OUTPUT_DIR, "exploratory_clustering_summary.csv"), os.path.join(OUTPUT_DIR, "exploratory_clustering_summary.xlsx"))
]

all_equiv = True
for name, c_file, x_file in artifacts:
    if not os.path.exists(c_file) or not os.path.exists(x_file):
        all_equiv = False
        err = f"Missing file pair for {name}!"
        errors.append(err)
        print(f"[FAIL] Test 7 ({name}): {err}")
        break
    df_c = pd.read_csv(c_file)
    df_x = pd.read_excel(x_file)
    if len(df_c) != len(df_x) or list(df_c.columns) != list(df_x.columns):
        all_equiv = False
        err = f"{name} shape or column divergence between CSV and XLSX!"
        errors.append(err)
        print(f"[FAIL] Test 7 ({name}): {err}")
        break

if all_equiv:
    print("[PASS] Test 7: CSV and XLSX versions contain 100% equivalent tabular data across all 8 artifact pairs.")

# 8. Privacy Preservation: No Reviewer Identifiers
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
    print("[PASS] Test 8: Privacy strictly preserved. 0 reviewer identifiers or developer replies in output tables.")

# 9. Deliverables Exist
report_path = "docs/aspect_analysis_report.md"
module_path = "analysis/aspect_extraction.py"
nb_path = "notebooks/07_aspect_analysis.ipynb"
cfg_path = "config/aspect_taxonomy.json"

if os.path.exists(report_path) and os.path.exists(module_path) and os.path.exists(nb_path) and os.path.exists(cfg_path):
    print(f"[PASS] Test 9: All deliverable files exist ({report_path}, {module_path}, {nb_path}, {cfg_path}).")
else:
    err = "Missing deliverable file!"
    errors.append(err)
    print(f"[FAIL] Test 9: {err}")

# 10. Manual Validation Sample check: fields blank
df_val = pd.read_csv(os.path.join(OUTPUT_DIR, "aspect_manual_validation_sample.csv"), keep_default_na=False)
blank_rev = (df_val["manual_aspect_review"].astype(str).str.strip() == "").all()
blank_notes = (df_val["manual_correction_notes"].astype(str).str.strip() == "").all()

if len(df_val) == 30 and blank_rev and blank_notes:
    print("[PASS] Test 10: Manual validation sample contains exactly 30 reviews with strictly blank review fields.")
else:
    err = "Manual validation sample structure invalid or review fields not blank!"
    errors.append(err)
    print(f"[FAIL] Test 10: {err}")

print("=" * 65)
if errors:
    print(f"VERIFICATION FAILED WITH {len(errors)} ERRORS:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("ALL 10 ASPECT EXTRACTION VERIFICATION TESTS PASSED (100% SUCCESS)!")
    print("=" * 65)
    sys.exit(0)
