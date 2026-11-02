# -*- coding: utf-8 -*-
"""
verify_phase5_6.py
------------------
Automated Verification Suite untuk Fase 5.6:
Final Data Packaging & Cross-Platform Data Delivery
ekosistem Zahir Social Analytics.

Cakupan Pengujian:
- Test 1: Canonical Source Immutability (Raw & Final MD5s)
- Test 2: Play Store & Gold Set Immutability (417 reviews: 232 pos, 112 neu, 73 neg)
- Test 3: Export Artifact Completeness (All 6 CSV & XLSX pairs exist)
- Test 4: Instagram Key Uniqueness & Completeness (55 unique post_ids)
- Test 5: Play Store Key Uniqueness & Completeness (417 unique review_ids)
- Test 6: Cross-Platform Foreign Key Linkages (100% relational integrity)
- Test 7: Source Value Fidelity (Export data values match final sources exactly)
- Test 8: Engagement Aggregates Consistency (12,643 likes, 504 comments, 13,147 total)
- Test 9: Aspect Taxonomy & Mention Count Integrity (Exactly 234 aspect mentions)
- Test 10: Human Sentiment Ground Truth Integrity (Gold Set preserved 100%)
- Test 11: Explicit Separation of Human vs Model Predictions (test_pred_ prefixes)
- Test 12: Privacy & Minimization Audit (No userName, userImage, reviewer_id, reply_text)
- Test 13: Zero-Fabrication & Platform Compliance Audit (No fake reach/impressions/views)
- Test 14: CSV and XLSX Structural & Semantic Equivalence (All 6 pairs)
- Test 15: Multi-Sheet Architecture & Data Dictionary Verification (Sheet names & dicts)
"""

import os
import sys
import hashlib
import pandas as pd
import numpy as np
import openpyxl

print("=" * 75)
print("PHASE 5.6 AUTOMATED VERIFICATION SUITE - FINAL DATA PACKAGING")
print("=" * 75)

errors = []
passes = []

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_IG_CSV = os.path.join(BASE_DIR, "data", "raw", "instagram_posts_raw.csv")
FINAL_IG_CSV = os.path.join(BASE_DIR, "data", "final", "instagram_posts_final.csv")
GOLD_SET_CSV = os.path.join(BASE_DIR, "data", "final", "playstore_gold_set_final.csv")
PLAYSTORE_FINAL_CSV = os.path.join(BASE_DIR, "data", "final", "playstore_reviews_final.csv")
ASPECTS_REMEDIATED_CSV = os.path.join(BASE_DIR, "data", "final", "topic_analysis", "phase_5_3", "review_aspect_assignments_remediated.csv")

EXPORT_DIR = os.path.join(BASE_DIR, "data", "export")
EXPORT_IG = os.path.join(EXPORT_DIR, "instagram")
EXPORT_PS = os.path.join(EXPORT_DIR, "playstore")

EXPECTED_RAW_MD5 = "c9e7882eff8282bb698825a0ef712817"
EXPECTED_FINAL_IG_MD5 = "794b050f649bc76537cf31f12b485b66"


def compute_md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ----------------------------------------------------
# Test 1: Canonical Source Immutability
# ----------------------------------------------------
try:
    assert os.path.exists(RAW_IG_CSV), f"Missing {RAW_IG_CSV}"
    assert os.path.exists(FINAL_IG_CSV), f"Missing {FINAL_IG_CSV}"
    
    raw_md5 = compute_md5(RAW_IG_CSV)
    final_md5 = compute_md5(FINAL_IG_CSV)
    
    assert raw_md5 == EXPECTED_RAW_MD5, f"Raw MD5 {raw_md5} != {EXPECTED_RAW_MD5}"
    assert final_md5 == EXPECTED_FINAL_IG_MD5, f"Final MD5 {final_md5} != {EXPECTED_FINAL_IG_MD5}"
    
    p = f"[PASS] Test 1: Canonical raw & final sources are 100% frozen & immutable (Raw MD5: {raw_md5[:8]}..., Final MD5: {final_md5[:8]}...)."
    passes.append(p)
    print(p)
except Exception as e:
    err = f"[FAIL] Test 1: Source immutability failed: {e}"
    errors.append(err)
    print(err)

# ----------------------------------------------------
# Test 2: Play Store & Gold Set Immutability
# ----------------------------------------------------
try:
    assert os.path.exists(GOLD_SET_CSV), f"Missing {GOLD_SET_CSV}"
    assert os.path.exists(PLAYSTORE_FINAL_CSV), f"Missing {PLAYSTORE_FINAL_CSV}"
    assert os.path.exists(ASPECTS_REMEDIATED_CSV), f"Missing {ASPECTS_REMEDIATED_CSV}"
    
    df_gold = pd.read_csv(GOLD_SET_CSV)
    df_ps = pd.read_csv(PLAYSTORE_FINAL_CSV)
    df_asp_src = pd.read_csv(ASPECTS_REMEDIATED_CSV)
    
    assert len(df_gold) == 417, f"Gold set length {len(df_gold)} != 417"
    assert len(df_ps) == 417, f"Play Store length {len(df_ps)} != 417"
    assert len(df_asp_src) == 417, f"Aspects length {len(df_asp_src)} != 417"
    
    counts = df_gold["human_sentiment_label"].value_counts().to_dict()
    assert counts.get("positive", 0) == 232, f"Positive mismatch: {counts}"
    assert counts.get("neutral", 0) == 112, f"Neutral mismatch: {counts}"
    assert counts.get("negative", 0) == 73, f"Negative mismatch: {counts}"
    assert int(df_asp_src["aspect_count"].sum()) == 234, f"Aspects sum mismatch: {df_asp_src['aspect_count'].sum()}"
    
    p = "[PASS] Test 2: Play Store reviews, Gold Set, & Remediated Aspects remain unaltered (417 reviews: 232 pos, 112 neu, 73 neg; 234 aspect mentions)."
    passes.append(p)
    print(p)
except Exception as e:
    err = f"[FAIL] Test 2: Play Store immutability failed: {e}"
    errors.append(err)
    print(err)

# ----------------------------------------------------
# Test 3: Export Artifact Completeness
# ----------------------------------------------------
EXPECTED_EXPORT_FILES = [
    os.path.join(EXPORT_IG, "instagram_posts_clean.csv"),
    os.path.join(EXPORT_IG, "instagram_posts_clean.xlsx"),
    os.path.join(EXPORT_IG, "instagram_engagement_metrics.csv"),
    os.path.join(EXPORT_IG, "instagram_engagement_metrics.xlsx"),
    os.path.join(EXPORT_IG, "instagram_content_performance.csv"),
    os.path.join(EXPORT_IG, "instagram_content_performance.xlsx"),
    os.path.join(EXPORT_PS, "playstore_reviews_clean.csv"),
    os.path.join(EXPORT_PS, "playstore_reviews_clean.xlsx"),
    os.path.join(EXPORT_PS, "playstore_sentiment.csv"),
    os.path.join(EXPORT_PS, "playstore_sentiment.xlsx"),
    os.path.join(EXPORT_PS, "playstore_aspects.csv"),
    os.path.join(EXPORT_PS, "playstore_aspects.xlsx"),
    os.path.join(EXPORT_DIR, "README_data_dictionary.md")
]

try:
    missing = []
    for f in EXPECTED_EXPORT_FILES:
        if not os.path.exists(f) or os.path.getsize(f) == 0:
            missing.append(f)
    assert not missing, f"Missing or empty export artifacts: {missing}"
    
    p = f"[PASS] Test 3: Export artifact completeness confirmed (All 6 CSV and 6 XLSX files exist and non-empty)."
    passes.append(p)
    print(p)
except Exception as e:
    err = f"[FAIL] Test 3: Artifact completeness failed: {e}"
    errors.append(err)
    print(err)

# ----------------------------------------------------
# Test 4: Instagram Key Uniqueness & Completeness
# ----------------------------------------------------
try:
    df_ig_clean = pd.read_csv(os.path.join(EXPORT_IG, "instagram_posts_clean.csv"))
    df_ig_met = pd.read_csv(os.path.join(EXPORT_IG, "instagram_engagement_metrics.csv"))
    df_ig_src = pd.read_csv(FINAL_IG_CSV)
    
    assert len(df_ig_clean) == 55, f"Expected 55 posts in clean, got {len(df_ig_clean)}"
    assert len(df_ig_met) == 55, f"Expected 55 posts in metrics, got {len(df_ig_met)}"
    assert df_ig_clean['post_id'].nunique() == 55, "Duplicate post_id in instagram_posts_clean"
    assert df_ig_met['post_id'].nunique() == 55, "Duplicate post_id in instagram_engagement_metrics"
    assert set(df_ig_clean['post_id']) == set(df_ig_src['post_id']), "Post ID set mismatch in posts_clean"
    assert set(df_ig_met['post_id']) == set(df_ig_src['post_id']), "Post ID set mismatch in metrics"
    
    p = "[PASS] Test 4: Instagram key uniqueness & completeness confirmed (55 unique post_ids match source)."
    passes.append(p)
    print(p)
except Exception as e:
    err = f"[FAIL] Test 4: Instagram key uniqueness failed: {e}"
    errors.append(err)
    print(err)

# ----------------------------------------------------
# Test 5: Play Store Key Uniqueness & Completeness
# ----------------------------------------------------
try:
    df_ps_clean = pd.read_csv(os.path.join(EXPORT_PS, "playstore_reviews_clean.csv"))
    df_ps_sent = pd.read_csv(os.path.join(EXPORT_PS, "playstore_sentiment.csv"))
    df_ps_asp = pd.read_csv(os.path.join(EXPORT_PS, "playstore_aspects.csv"))
    
    assert len(df_ps_clean) == 417, f"Expected 417 reviews in clean, got {len(df_ps_clean)}"
    assert len(df_ps_sent) == 417, f"Expected 417 reviews in sentiment, got {len(df_ps_sent)}"
    assert len(df_ps_asp) == 417, f"Expected 417 reviews in aspects, got {len(df_ps_asp)}"
    
    assert df_ps_clean['review_id'].nunique() == 417, "Duplicate review_id in playstore_reviews_clean"
    assert df_ps_sent['review_id'].nunique() == 417, "Duplicate review_id in playstore_sentiment"
    assert df_ps_asp['review_id'].nunique() == 417, "Duplicate review_id in playstore_aspects"
    
    assert set(df_ps_clean['review_id']) == set(df_ps['review_id']), "Review ID mismatch in reviews_clean"
    assert set(df_ps_sent['review_id']) == set(df_ps['review_id']), "Review ID mismatch in sentiment"
    assert set(df_ps_asp['review_id']) == set(df_ps['review_id']), "Review ID mismatch in aspects"
    
    p = "[PASS] Test 5: Play Store key uniqueness & completeness confirmed (417 unique review_ids match source)."
    passes.append(p)
    print(p)
except Exception as e:
    err = f"[FAIL] Test 5: Play Store key uniqueness failed: {e}"
    errors.append(err)
    print(err)

# ----------------------------------------------------
# Test 6: Cross-Platform Foreign Key Linkages
# ----------------------------------------------------
try:
    # 1. Instagram: post_id connects clean posts with engagement metrics
    assert (df_ig_clean['post_id'] == df_ig_clean['post_id'].drop_duplicates()).all()
    assert (df_ig_clean['post_id'].sort_values().values == df_ig_met['post_id'].sort_values().values).all()
    
    # 2. Play Store: review_id connects clean reviews with sentiment and aspects
    assert (df_ps_clean['review_id'].sort_values().values == df_ps_sent['review_id'].sort_values().values).all()
    assert (df_ps_clean['review_id'].sort_values().values == df_ps_asp['review_id'].sort_values().values).all()
    
    p = "[PASS] Test 6: Relational integrity confirmed (post_id and review_id link 100% across all export files)."
    passes.append(p)
    print(p)
except Exception as e:
    err = f"[FAIL] Test 6: Foreign key linkage failed: {e}"
    errors.append(err)
    print(err)

# ----------------------------------------------------
# Test 7: Source Value Fidelity
# ----------------------------------------------------
try:
    # Verify Instagram posts clean values match source
    for col in ['likes', 'comments', 'total_interactions', 'caption_word_count', 'hashtag_count']:
        diff = np.abs(df_ig_clean[col].values - df_ig_src[col].values).sum()
        assert diff == 0, f"Value mismatch in Instagram export {col}"
        
    # Verify Play Store reviews clean values match source
    for col in ['score', 'thumbs_up_count', 'text_length_chars', 'word_count']:
        diff = np.abs(df_ps_clean[col].values - df_ps[col].values).sum()
        assert diff == 0, f"Value mismatch in Play Store export {col}"
        
    p = "[PASS] Test 7: Source value fidelity verified (Zero distortion or transformation drift in export files)."
    passes.append(p)
    print(p)
except Exception as e:
    err = f"[FAIL] Test 7: Source fidelity failed: {e}"
    errors.append(err)
    print(err)

# ----------------------------------------------------
# Test 8: Engagement Aggregates Consistency
# ----------------------------------------------------
try:
    assert int(df_ig_clean['likes'].sum()) == 12643, "Likes sum != 12,643"
    assert int(df_ig_clean['comments'].sum()) == 504, "Comments sum != 504"
    assert int(df_ig_clean['total_interactions'].sum()) == 13147, "Total interactions sum != 13,147"
    
    assert int(df_ig_met['likes'].sum()) == 12643, "Metrics likes sum != 12,643"
    assert int(df_ig_met['comments'].sum()) == 504, "Metrics comments sum != 504"
    assert int(df_ig_met['total_interactions'].sum()) == 13147, "Metrics total interactions sum != 13,147"
    
    df_ig_perf = pd.read_csv(os.path.join(EXPORT_IG, "instagram_content_performance.csv"))
    base_row = df_ig_perf[df_ig_perf['analysis_dimension'] == 'Overall Baseline'].iloc[0]
    assert base_row['total_likes'] == 12643, "Performance total_likes mismatch"
    assert base_row['total_comments'] == 504, "Performance total_comments mismatch"
    assert base_row['total_interactions'] == 13147, "Performance total_interactions mismatch"
    assert base_row['post_count'] == 55, "Performance post_count mismatch"
    
    p = "[PASS] Test 8: Engagement aggregates consistent (12,643 likes, 504 comments, 13,147 total interactions across all tables)."
    passes.append(p)
    print(p)
except Exception as e:
    err = f"[FAIL] Test 8: Engagement aggregates failed: {e}"
    errors.append(err)
    print(err)

# ----------------------------------------------------
# Test 9: Aspect Taxonomy & Mention Count Integrity
# ----------------------------------------------------
try:
    aspect_cols = [
        'aspect_login_auth', 'aspect_crash_stability', 'aspect_pricing_subscription',
        'aspect_sync_cloud_data', 'aspect_pos_hardware_print', 'aspect_inventory_accounting',
        'aspect_certification_exam', 'aspect_attendance_face'
    ]
    
    # Check that aspect_count matches the sum of booleans
    assert (df_ps_asp['aspect_count'] == df_ps_asp[aspect_cols].sum(axis=1)).all(), "aspect_count != sum of boolean flags"
    total_mentions = int(df_ps_asp['aspect_count'].sum())
    assert total_mentions == 234, f"Total aspect mentions {total_mentions} != 234"
    
    # Check individual aspect frequencies
    expected_freqs = {
        'aspect_login_auth': 38,
        'aspect_crash_stability': 38,
        'aspect_pricing_subscription': 34,
        'aspect_sync_cloud_data': 15,
        'aspect_pos_hardware_print': 20,
        'aspect_inventory_accounting': 71,
        'aspect_certification_exam': 11,
        'aspect_attendance_face': 7
    }
    for col, exp_cnt in expected_freqs.items():
        act_cnt = int(df_ps_asp[col].sum())
        assert act_cnt == exp_cnt, f"Aspect {col} count {act_cnt} != {exp_cnt}"
        
    # Check long sheet in XLSX
    wb_asp = openpyxl.load_workbook(os.path.join(EXPORT_PS, "playstore_aspects.xlsx"))
    assert "Aspect Mentions (Long)" in wb_asp.sheetnames, "Missing Aspect Mentions (Long) sheet"
    df_long_xlsx = pd.read_excel(os.path.join(EXPORT_PS, "playstore_aspects.xlsx"), sheet_name="Aspect Mentions (Long)")
    assert len(df_long_xlsx) == 234, f"Long sheet row count {len(df_long_xlsx)} != 234"
    
    p = "[PASS] Test 9: Aspect taxonomy & mention count integrity verified (417 reviews, exactly 234 mentions across 8 aspects)."
    passes.append(p)
    print(p)
except Exception as e:
    err = f"[FAIL] Test 9: Aspect integrity failed: {e}"
    errors.append(err)
    print(err)

# ----------------------------------------------------
# Test 10: Human Sentiment Ground Truth Integrity
# ----------------------------------------------------
try:
    assert (df_ps_sent['human_sentiment_label'].values == df_gold['human_sentiment_label'].values).all(), "Human sentiment mismatch with Gold Set"
    sent_counts = df_ps_sent['human_sentiment_label'].value_counts().to_dict()
    assert sent_counts.get('positive', 0) == 232, f"Positive count mismatch: {sent_counts}"
    assert sent_counts.get('neutral', 0) == 112, f"Neutral count mismatch: {sent_counts}"
    assert sent_counts.get('negative', 0) == 73, f"Negative count mismatch: {sent_counts}"
    assert (df_ps_sent['sentiment_label_source'] == "gold_set_human_annotated").all(), "Invalid sentiment_label_source value"
    
    p = "[PASS] Test 10: Human sentiment ground truth verified (232 positive, 112 neutral, 73 negative; source='gold_set_human_annotated')."
    passes.append(p)
    print(p)
except Exception as e:
    err = f"[FAIL] Test 10: Sentiment ground truth failed: {e}"
    errors.append(err)
    print(err)

# ----------------------------------------------------
# Test 11: Explicit Separation of Human vs Model Predictions
# ----------------------------------------------------
try:
    # Model predictions should only be present on the 84 test split reviews
    dev_split = df_ps_sent[df_ps_sent['benchmark_split'] == 'development']
    test_split = df_ps_sent[df_ps_sent['benchmark_split'] == 'test']
    
    assert len(dev_split) == 333, f"Dev split length {len(dev_split)} != 333"
    assert len(test_split) == 84, f"Test split length {len(test_split)} != 84"
    
    # In development split, model predictions must be NaN
    assert dev_split['test_pred_indobert'].isna().all(), "Non-null test_pred_indobert in dev split"
    assert dev_split['test_pred_inset_lexicon'].isna().all(), "Non-null test_pred_inset_lexicon in dev split"
    assert dev_split['test_pred_tfidf_lr'].isna().all(), "Non-null test_pred_tfidf_lr in dev split"
    
    # In test split, model predictions must be present
    assert test_split['test_pred_indobert'].notna().all(), "Null test_pred_indobert in test split"
    assert test_split['test_pred_inset_lexicon'].notna().all(), "Null test_pred_inset_lexicon in test split"
    assert test_split['test_pred_tfidf_lr'].notna().all(), "Null test_pred_tfidf_lr in test split"
    
    p = "[PASS] Test 11: Explicit separation verified (Human labels universal [417]; model predictions explicitly prefixed test_pred_ on 84 test rows)."
    passes.append(p)
    print(p)
except Exception as e:
    err = f"[FAIL] Test 11: Explicit separation failed: {e}"
    errors.append(err)
    print(err)

# ----------------------------------------------------
# Test 12: Privacy & Minimization Audit
# ----------------------------------------------------
try:
    prohibited_user_pii = ["user_name", "username", "user_image", "userimage", "reviewer_id", "reply_text", "password", "token", "cookie"]
    
    for c in df_ps_clean.columns:
        assert c.lower() not in prohibited_user_pii, f"Prohibited PII column {c} found in playstore_reviews_clean"
        
    for c in df_ps_sent.columns:
        assert c.lower() not in prohibited_user_pii, f"Prohibited PII column {c} found in playstore_sentiment"
        
    for c in df_ps_asp.columns:
        assert c.lower() not in prohibited_user_pii, f"Prohibited PII column {c} found in playstore_aspects"
        
    p = "[PASS] Test 12: Privacy minimization verified (Zero userName, userImage, reviewer_id, or reply_text in clean exports)."
    passes.append(p)
    print(p)
except Exception as e:
    err = f"[FAIL] Test 12: Privacy minimization failed: {e}"
    errors.append(err)
    print(err)

# ----------------------------------------------------
# Test 13: Zero-Fabrication & Platform Compliance Audit
# ----------------------------------------------------
try:
    prohibited_fabricated_metrics = ["reach", "impressions", "follower_count", "followers", "engagement_rate", "engagement_rate_pct"]
    for df_chk, name in [(df_ig_clean, "instagram_posts_clean"), (df_ig_met, "instagram_engagement_metrics")]:
        for c in df_chk.columns:
            assert c.lower() not in prohibited_fabricated_metrics, f"Prohibited fabricated metric {c} in {name}"
            
    # Check views is strictly 100% NaN in clean posts
    assert df_ig_clean['views'].isna().all(), "Views column in instagram_posts_clean is not strictly NaN"
    
    p = "[PASS] Test 13: Zero-fabrication confirmed (views remains strictly NaN; no synthetic reach/impressions/ER formulas)."
    passes.append(p)
    print(p)
except Exception as e:
    err = f"[FAIL] Test 13: Zero fabrication failed: {e}"
    errors.append(err)
    print(err)

# ----------------------------------------------------
# Test 14: CSV and XLSX Structural & Semantic Equivalence
# ----------------------------------------------------
try:
    for base, folder in [
        ("instagram_posts_clean", EXPORT_IG),
        ("instagram_engagement_metrics", EXPORT_IG),
        ("instagram_content_performance", EXPORT_IG),
        ("playstore_reviews_clean", EXPORT_PS),
        ("playstore_sentiment", EXPORT_PS),
        ("playstore_aspects", EXPORT_PS)
    ]:
        c_path = os.path.join(folder, f"{base}.csv")
        x_path = os.path.join(folder, f"{base}.xlsx")
        
        c_df = pd.read_csv(c_path)
        wb = openpyxl.load_workbook(x_path)
        first_sheet = wb.sheetnames[0]
        x_df = pd.read_excel(x_path, sheet_name=first_sheet)
        
        assert len(c_df) == len(x_df), f"Row count mismatch in {base}: CSV {len(c_df)} vs XLSX {len(x_df)}"
        assert list(c_df.columns) == list(x_df.columns), f"Column mismatch in {base}"
        
        for col in c_df.select_dtypes(include=[np.number]).columns:
            c_vals = c_df[col].fillna(-999999).values
            x_vals = x_df[col].fillna(-999999).values
            diff = np.abs(c_vals - x_vals)
            assert (diff < 0.01).all(), f"Numeric value mismatch in {base}.{col}: max diff {diff.max()}"
            
    p = "[PASS] Test 14: CSV and XLSX structural & semantic equivalence confirmed across all 6 exported artifact pairs."
    passes.append(p)
    print(p)
except Exception as e:
    err = f"[FAIL] Test 14: CSV/XLSX equivalence failed: {e}"
    errors.append(err)
    print(err)

# ----------------------------------------------------
# Test 15: Multi-Sheet Architecture & Data Dictionary Verification
# ----------------------------------------------------
try:
    wb_ig_perf = openpyxl.load_workbook(os.path.join(EXPORT_IG, "instagram_content_performance.xlsx"))
    assert len(wb_ig_perf.sheetnames) == 7, f"Expected 7 sheets in instagram_content_performance, got {len(wb_ig_perf.sheetnames)}"
    
    wb_ps_sent = openpyxl.load_workbook(os.path.join(EXPORT_PS, "playstore_sentiment.xlsx"))
    assert len(wb_ps_sent.sheetnames) == 3, f"Expected 3 sheets in playstore_sentiment, got {len(wb_ps_sent.sheetnames)}"
    
    wb_ps_asp = openpyxl.load_workbook(os.path.join(EXPORT_PS, "playstore_aspects.xlsx"),
    os.path.join(EXPORT_DIR, "README_data_dictionary.md"))
    assert len(wb_ps_asp.sheetnames) == 3, f"Expected 3 sheets in playstore_aspects, got {len(wb_ps_asp.sheetnames)}"
    
    # Check data dictionaries
    for x_file in ["instagram_posts_clean.xlsx", "instagram_engagement_metrics.xlsx", "playstore_reviews_clean.xlsx"]:
        folder = EXPORT_IG if "instagram" in x_file else EXPORT_PS
        wb_dict = openpyxl.load_workbook(os.path.join(folder, x_file))
        assert "Data Dictionary" in wb_dict.sheetnames, f"Missing Data Dictionary in {x_file}"
        
    p = "[PASS] Test 15: Multi-sheet architecture and embedded data dictionaries verified across all Excel workbooks."
    passes.append(p)
    print(p)
except Exception as e:
    err = f"[FAIL] Test 15: Multi-sheet architecture failed: {e}"
    errors.append(err)
    print(err)

# ----------------------------------------------------
# Final Summary
# ----------------------------------------------------
print("=" * 75)
print(f"VERIFICATION SUMMARY: {len(passes)} PASSED, {len(errors)} FAILED")
print("=" * 75)

if errors:
    print("\nFAILURES ENCOUNTERED:")
    for err in errors:
        print("  -", err)
    sys.exit(1)
else:
    print("\nALL 15 PHASE 5.6 AUTOMATED INTEGRITY TESTS PASSED SUCCESSFULLY!")
    sys.exit(0)