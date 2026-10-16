import sys
import pandas as pd
import openpyxl

print("="*60)
print("PHASE 4.1 AUTOMATED VERIFICATION TEST SUITE")
print("="*60)

errors = []

# Load source dataset
src_path = 'data/final/playstore_reviews_final.csv'
df_src = pd.read_csv(src_path)

# Load CSV gold set
csv_path = 'data/final/playstore_gold_set_template.csv'
try:
    df_csv = pd.read_csv(csv_path, keep_default_na=False)
    print("[PASS] Test 1: CSV gold set file opens and reads successfully.")
except Exception as e:
    errors.append(f"Failed to load CSV gold set: {e}")
    print(f"[FAIL] Test 1: {e}")

# Load XLSX gold set
xlsx_path = 'data/final/playstore_gold_set_template.xlsx'
try:
    df_xlsx = pd.read_excel(xlsx_path, sheet_name='Gold Set', keep_default_na=False)
    wb = openpyxl.load_workbook(xlsx_path, read_only=False)
    print("[PASS] Test 2: XLSX gold set file opens and reads successfully.")
except Exception as e:
    errors.append(f"Failed to load XLSX gold set: {e}")
    print(f"[FAIL] Test 2: {e}")

# 1. Record counts
if len(df_csv) == 417 and len(df_xlsx) == 417 and len(df_src) == 417:
    print(f"[PASS] Test 3: Record count is exactly 417 across source, CSV, and XLSX.")
else:
    err = f"Record count mismatch! src={len(df_src)}, csv={len(df_csv)}, xlsx={len(df_xlsx)}"
    errors.append(err)
    print(f"[FAIL] Test 3: {err}")

# 2. All 417 source review_id represented
src_ids = set(df_src['review_id'].astype(str))
csv_ids = set(df_csv['review_id'].astype(str))
xlsx_ids = set(df_xlsx['review_id'].astype(str))

if src_ids == csv_ids and src_ids == xlsx_ids:
    print(f"[PASS] Test 4: All 417 source review_ids are exactly represented.")
else:
    err = f"review_id set mismatch! missing in csv: {len(src_ids - csv_ids)}, missing in xlsx: {len(src_ids - xlsx_ids)}"
    errors.append(err)
    print(f"[FAIL] Test 4: {err}")

# 3. No duplicate review_id
if df_csv['review_id'].nunique() == 417 and df_xlsx['review_id'].nunique() == 417:
    print(f"[PASS] Test 5: No duplicate review_ids in CSV or XLSX (0 duplicates).")
else:
    err = f"Duplicate review_ids found! csv unique={df_csv['review_id'].nunique()}, xlsx unique={df_xlsx['review_id'].nunique()}"
    errors.append(err)
    print(f"[FAIL] Test 5: {err}")

# 4. No source review fabricated, silently changed, or omitted
# Verify that ordered list of review_id, app_name, and review_text_clean exactly matches
txt_match_csv = (df_src['review_text_clean'].astype(str).values == df_csv['review_text_clean'].astype(str).values).all()
txt_match_xlsx = (df_src['review_text_clean'].astype(str).values == df_xlsx['review_text_clean'].astype(str).values).all()
app_match_csv = (df_src['app_name'].astype(str).values == df_csv['app_name'].astype(str).values).all()
app_match_xlsx = (df_src['app_name'].astype(str).values == df_xlsx['app_name'].astype(str).values).all()

if txt_match_csv and txt_match_xlsx and app_match_csv and app_match_xlsx:
    print(f"[PASS] Test 6: Source reviews are 100% authentic, identical, and unaltered.")
else:
    err = f"Content alteration detected! txt_csv={txt_match_csv}, txt_xlsx={txt_match_xlsx}, app_csv={app_match_csv}, app_xlsx={app_match_xlsx}"
    errors.append(err)
    print(f"[FAIL] Test 6: {err}")

# 5. Annotation fields are initially blank
blank_cols = ['human_sentiment_label', 'needs_review', 'annotation_notes']
csv_blanks = all((df_csv[col].astype(str).str.strip() == '').all() for col in blank_cols)
xlsx_blanks = all((df_xlsx[col].astype(str).str.strip() == '').all() for col in blank_cols)

if csv_blanks and xlsx_blanks:
    print(f"[PASS] Test 7: All annotation fields are strictly blank (no pre-assigned labels or flags).")
else:
    err = f"Annotation fields not blank! csv_blanks={csv_blanks}, xlsx_blanks={xlsx_blanks}"
    errors.append(err)
    print(f"[FAIL] Test 7: {err}")

# 6. No reviewer names, user images, or reviewer identifiers included
forbidden = ['userName', 'userImage', 'reviewer_id', 'reply_text', 'replyContent']
expected_cols = ['review_id', 'app_name', 'review_datetime', 'review_text_clean', 'human_sentiment_label', 'needs_review', 'annotation_notes']

csv_has_forbidden = any(f in df_csv.columns for f in forbidden)
xlsx_has_forbidden = any(f in df_xlsx.columns for f in forbidden)
col_match = list(df_csv.columns) == expected_cols and list(df_xlsx.columns) == expected_cols

if not csv_has_forbidden and not xlsx_has_forbidden and col_match:
    print(f"[PASS] Test 8: Privacy preserved. Exactly 7 required columns, 0 identifying/reply fields.")
else:
    err = f"Column structure or privacy violation! csv_cols={list(df_csv.columns)}"
    errors.append(err)
    print(f"[FAIL] Test 8: {err}")

# 7. CSV and XLSX equivalence
equiv = True
for col in expected_cols:
    c_val = df_csv[col].astype(str).values
    x_val = df_xlsx[col].astype(str).values
    if not (c_val == x_val).all():
        equiv = False
        break

if equiv:
    print(f"[PASS] Test 9: CSV and XLSX versions contain 100% equivalent records and values.")
else:
    err = f"Value divergence detected between CSV and XLSX!"
    errors.append(err)
    print(f"[FAIL] Test 9: {err}")

# 8. XLSX Workbook formatting features: sheets, filters, freeze_panes
sheets = wb.sheetnames
has_sheets = 'Gold Set' in sheets and 'Annotation Guide' in sheets
ws_main = wb['Gold Set']
has_freeze = ws_main.freeze_panes == 'A2'
has_filter = ws_main.auto_filter.ref is not None

if has_sheets and has_freeze and has_filter:
    print(f"[PASS] Test 10: XLSX workbook structure confirmed (Sheets: {sheets}, Frozen row: {ws_main.freeze_panes}, AutoFilter: {ws_main.auto_filter.ref}).")
else:
    err = f"XLSX formatting check failed! sheets={sheets}, freeze={ws_main.freeze_panes}, filter={ws_main.auto_filter.ref}"
    errors.append(err)
    print(f"[FAIL] Test 10: {err}")

print("="*60)
if errors:
    print(f"VERIFICATION FAILED WITH {len(errors)} ERRORS:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("ALL 10 VERIFICATION TESTS PASSED SUCCESSFULLY (100% SUCCESS)!")
    print("="*60)
    sys.exit(0)
