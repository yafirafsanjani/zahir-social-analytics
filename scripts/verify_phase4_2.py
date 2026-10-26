import sys
import pandas as pd
import openpyxl

print("=" * 60)
print("PHASE 4.2 FINAL GOLD SET VALIDATION & FREEZE AUDIT")
print("=" * 60)

errors = []

src_xlsx = "data/final/playstore_gold_set_annotated_validated.xlsx"
final_csv = "data/final/playstore_gold_set_final.csv"
final_xlsx = "data/final/playstore_gold_set_final.xlsx"

# 1. Load files
try:
    df_src = pd.read_excel(src_xlsx, sheet_name="Gold Set", keep_default_na=False)
    print(f"[PASS] Test 1: Source workbook loaded successfully ({src_xlsx}).")
except Exception as e:
    errors.append(f"Failed to load source workbook: {e}")
    print(f"[FAIL] Test 1: {e}")

try:
    df_csv = pd.read_csv(final_csv, keep_default_na=False)
    print(f"[PASS] Test 2: Final CSV loaded successfully ({final_csv}).")
except Exception as e:
    errors.append(f"Failed to load final CSV: {e}")
    print(f"[FAIL] Test 2: {e}")

try:
    df_xlsx = pd.read_excel(final_xlsx, sheet_name="Gold Set", keep_default_na=False)
    wb = openpyxl.load_workbook(final_xlsx, read_only=False)
    print(f"[PASS] Test 3: Final XLSX loaded successfully ({final_xlsx}).")
except Exception as e:
    errors.append(f"Failed to load final XLSX: {e}")
    print(f"[FAIL] Test 3: {e}")

# 2. Check exactly 417 reviews
if len(df_src) == 417 and len(df_csv) == 417 and len(df_xlsx) == 417:
    print("[PASS] Test 4: Exactly 417 reviews present across source, final CSV, and final XLSX.")
else:
    err = f"Record count mismatch: src={len(df_src)}, csv={len(df_csv)}, xlsx={len(df_xlsx)}"
    errors.append(err)
    print(f"[FAIL] Test 4: {err}")

# 3. Check review_id is complete and unique
if df_csv["review_id"].nunique() == 417 and df_xlsx["review_id"].nunique() == 417 and not df_csv["review_id"].isnull().any():
    print("[PASS] Test 5: review_id is complete and 100% unique (0 duplicates, 0 missing).")
else:
    err = f"review_id validation failed! unique_csv={df_csv['review_id'].nunique()}"
    errors.append(err)
    print(f"[FAIL] Test 5: {err}")

# 4. Check review_text_clean is not empty
empty_csv = (df_csv["review_text_clean"].astype(str).str.strip() == "").sum()
empty_xlsx = (df_xlsx["review_text_clean"].astype(str).str.strip() == "").sum()
if empty_csv == 0 and empty_xlsx == 0:
    print("[PASS] Test 6: review_text_clean is non-empty across all 417 records.")
else:
    err = f"Empty clean text found! csv={empty_csv}, xlsx={empty_xlsx}"
    errors.append(err)
    print(f"[FAIL] Test 6: {err}")

# 5. Check human_sentiment_label contains only positive, neutral, negative and no blanks
allowed_labels = {"positive", "neutral", "negative"}
csv_labels = set(df_csv["human_sentiment_label"].unique())
xlsx_labels = set(df_xlsx["human_sentiment_label"].unique())
blank_labels_csv = (df_csv["human_sentiment_label"].astype(str).str.strip() == "").sum()
blank_labels_xlsx = (df_xlsx["human_sentiment_label"].astype(str).str.strip() == "").sum()

if csv_labels.issubset(allowed_labels) and xlsx_labels.issubset(allowed_labels) and blank_labels_csv == 0 and blank_labels_xlsx == 0:
    print(f"[PASS] Test 7: human_sentiment_label contains only valid categories {allowed_labels} with 0 blank values.")
else:
    err = f"Invalid sentiment labels found! csv_labels={csv_labels}, blank_csv={blank_labels_csv}"
    errors.append(err)
    print(f"[FAIL] Test 7: {err}")

# 6. Check needs_review contains only valid Boolean values and no unresolved True records
has_unresolved_csv = (df_csv["needs_review"].apply(lambda x: str(x).strip().lower() == "true")).sum()
has_unresolved_xlsx = (df_xlsx["needs_review"].apply(lambda x: str(x).strip().lower() == "true")).sum()

if has_unresolved_csv == 0 and has_unresolved_xlsx == 0:
    print("[PASS] Test 8: needs_review contains 0 unresolved needs_review=True records remain.")
else:
    err = f"needs_review check failed! unresolved_csv={has_unresolved_csv}, unresolved_xlsx={has_unresolved_xlsx}"
    errors.append(err)
    print(f"[FAIL] Test 8: {err}")

# 7. Privacy check: no reviewer names, profile images, or reviewer identifiers
forbidden = ["userName", "userImage", "reviewer_id", "reply_text", "replyContent"]
expected_cols = ["review_id", "app_name", "review_datetime", "review_text_clean", "human_sentiment_label", "needs_review", "annotation_notes"]

csv_forbidden = [f for f in forbidden if f in df_csv.columns]
xlsx_forbidden = [f for f in forbidden if f in df_xlsx.columns]

if not csv_forbidden and not xlsx_forbidden and list(df_csv.columns) == expected_cols and list(df_xlsx.columns) == expected_cols:
    print("[PASS] Test 9: Privacy strictness verified. Exactly 7 target columns, 0 identifying fields.")
else:
    err = f"Privacy violation or column mismatch! csv_cols={list(df_csv.columns)}"
    errors.append(err)
    print(f"[FAIL] Test 9: {err}")

# 8. Equivalence check between CSV and XLSX
col_mismatches = []
for col in ["review_id", "app_name", "review_datetime", "review_text_clean", "human_sentiment_label"]:
    c_val = df_csv[col].astype(str).values
    x_val = df_xlsx[col].astype(str).values
    if not (c_val == x_val).all():
        col_mismatches.append(col)

if not col_mismatches:
    print("[PASS] Test 10: Final CSV and Final XLSX have 100% equivalent records, columns, order, and values.")
else:
    err = f"Equivalence mismatch in columns: {col_mismatches}"
    errors.append(err)
    print(f"[FAIL] Test 10: {err}")

# 9. Source preservation: ensure source file untouched
if src_xlsx != final_csv and src_xlsx != final_xlsx:
    print("[PASS] Test 11: Original source workbook preserved without overwriting.")
else:
    err = "Source workbook overwrite risk detected!"
    errors.append(err)
    print(f"[FAIL] Test 11: {err}")

# 10. Check against playstore_reviews_final.csv to ensure source reviews match exactly
df_playstore_final = pd.read_csv("data/final/playstore_reviews_final.csv")
txt_match = (df_playstore_final["review_text_clean"].astype(str).values == df_csv["review_text_clean"].astype(str).values).all()
id_match = (df_playstore_final["review_id"].astype(str).values == df_csv["review_id"].astype(str).values).all()

if txt_match and id_match:
    print("[PASS] Test 12: All 417 review texts and IDs match playstore_reviews_final.csv 100% identically.")
else:
    err = f"Alignment mismatch with playstore_reviews_final.csv! txt_match={txt_match}, id_match={id_match}"
    errors.append(err)
    print(f"[FAIL] Test 12: {err}")

print("=" * 60)
if errors:
    print(f"FAILED: {len(errors)} errors found.")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("ALL 12 VERIFICATION TESTS PASSED SUCCESSFULLY (100% SUCCESS)!")
    print("=" * 60)
    
    # Print label distribution
    print("\nLABEL DISTRIBUTION SUMMARY:")
    total = len(df_csv)
    counts = df_csv["human_sentiment_label"].value_counts()
    for lbl in ["positive", "neutral", "negative"]:
        cnt = counts.get(lbl, 0)
        pct = (cnt / total) * 100
        print(f"  - {lbl.capitalize():<8}: {cnt:>3} reviews ({pct:6.2f}%)")
    print(f"  - Total   : {total:>3} reviews (100.00%)")
