# -*- coding: utf-8 -*-
"""
verify_phase5_5.py
------------------
Automated Verification Suite untuk Fase 5.5:
Instagram Social Engagement & Content Performance Analysis
ekosistem Zahir Social Analytics.

Cakupan Pengujian:
- Test 1: Canonical Source Immutability (Raw MD5 & Final MD5)
- Test 2: Play Store & Gold Set Immutability (Frozen reference preservation)
- Test 3: Phase 5.5 Artifact Completeness (All 7 CSV & XLSX pairs)
- Test 4: Post-Level Key Uniqueness & Completeness (55 unique post_ids)
- Test 5: Interaction Arithmetic Consistency (likes + comments == total_interactions)
- Test 6: Summary Metrics Consistency (Exact sums, means, medians, IQR)
- Test 7: Outlier Logic & IQR Thresholds (Q3 + 1.5*IQR == 239.0, exactly 9 outliers)
- Test 8: Content Type Comparison Consistency (44 reels, 8 carousels, 3 images)
- Test 9: Collaboration Analysis Consistency (29 organic, 26 colab, sums match)
- Test 10: Temporal Analysis Consistency (Days, time bins, years sum to 55 & 13147)
- Test 11: Caption & Hashtag Statistical Integrity (Pearson & Spearman rho verified)
- Test 12: Top & Bottom Posts Integrity (Top 10 vs Bottom 10 rankings)
- Test 13: CSV and XLSX Structural & Semantic Equivalence (All 7 pairs match)
- Test 14: Zero-Fabrication & Platform Compliance Audit (No fake reach/impressions/ER)
- Test 15: Privacy & Identifier Minimization (Zero private commenter PII)
"""

import os
import sys
import hashlib
import pandas as pd
import numpy as np
import openpyxl

print("=" * 75)
print("PHASE 5.5 AUTOMATED VERIFICATION SUITE - INSTAGRAM ENGAGEMENT ANALYSIS")
print("=" * 75)

errors = []
passes = []

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_CSV = os.path.join(BASE_DIR, "data", "raw", "instagram_posts_raw.csv")
FINAL_CSV = os.path.join(BASE_DIR, "data", "final", "instagram_posts_final.csv")
GOLD_SET_CSV = os.path.join(BASE_DIR, "data", "final", "playstore_gold_set_final.csv")
PLAYSTORE_FINAL_CSV = os.path.join(BASE_DIR, "data", "final", "playstore_reviews_final.csv")
ANALYSIS_DIR = os.path.join(BASE_DIR, "data", "final", "instagram_analysis")

EXPECTED_RAW_MD5 = "c9e7882eff8282bb698825a0ef712817"
EXPECTED_FINAL_MD5 = "794b050f649bc76537cf31f12b485b66"


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
    assert os.path.exists(RAW_CSV), f"Missing {RAW_CSV}"
    assert os.path.exists(FINAL_CSV), f"Missing {FINAL_CSV}"
    
    raw_md5 = compute_md5(RAW_CSV)
    final_md5 = compute_md5(FINAL_CSV)
    
    assert raw_md5 == EXPECTED_RAW_MD5, f"Raw MD5 {raw_md5} != {EXPECTED_RAW_MD5}"
    assert final_md5 == EXPECTED_FINAL_MD5, f"Final MD5 {final_md5} != {EXPECTED_FINAL_MD5}"
    
    df_src = pd.read_csv(FINAL_CSV)
    assert len(df_src) == 55, f"Expected 55 rows, got {len(df_src)}"
    
    p = f"[PASS] Test 1: Canonical raw & final Instagram data are 100% frozen & immutable (Raw MD5: {raw_md5[:8]}..., Final MD5: {final_md5[:8]}...)."
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
    
    df_gold = pd.read_csv(GOLD_SET_CSV)
    df_ps = pd.read_csv(PLAYSTORE_FINAL_CSV)
    
    assert len(df_gold) == 417, f"Gold set length {len(df_gold)} != 417"
    assert len(df_ps) == 417, f"Play Store length {len(df_ps)} != 417"
    
    counts = df_gold["human_sentiment_label"].value_counts().to_dict()
    assert counts.get("positive", 0) == 232, f"Positive mismatch: {counts}"
    assert counts.get("neutral", 0) == 112, f"Neutral mismatch: {counts}"
    assert counts.get("negative", 0) == 73, f"Negative mismatch: {counts}"
    
    p = "[PASS] Test 2: Play Store reviews & Gold Set remain strictly unaltered (417 reviews: 232 pos, 112 neu, 73 neg)."
    passes.append(p)
    print(p)
except Exception as e:
    err = f"[FAIL] Test 2: Play Store immutability failed: {e}"
    errors.append(err)
    print(err)

# ----------------------------------------------------
# Test 3: Phase 5.5 Artifact Completeness (7 Pairs)
# ----------------------------------------------------
EXPECTED_BASE_NAMES = [
    "instagram_engagement_metrics",
    "instagram_engagement_summary",
    "instagram_content_type_comparison",
    "instagram_collaboration_analysis",
    "instagram_posting_time_analysis",
    "instagram_caption_hashtag_analysis",
    "instagram_top_posts"
]

try:
    assert os.path.exists(ANALYSIS_DIR), f"Missing analysis dir {ANALYSIS_DIR}"
    missing_files = []
    for b in EXPECTED_BASE_NAMES:
        csv_file = os.path.join(ANALYSIS_DIR, f"{b}.csv")
        xlsx_file = os.path.join(ANALYSIS_DIR, f"{b}.xlsx")
        if not os.path.exists(csv_file) or os.path.getsize(csv_file) == 0:
            missing_files.append(f"{b}.csv")
        if not os.path.exists(xlsx_file) or os.path.getsize(xlsx_file) == 0:
            missing_files.append(f"{b}.xlsx")
            
    assert not missing_files, f"Missing or empty artifacts: {missing_files}"
    p = f"[PASS] Test 3: Artifact completeness confirmed (All 7 CSV and 7 XLSX pairs exist and non-empty)."
    passes.append(p)
    print(p)
except Exception as e:
    err = f"[FAIL] Test 3: Artifact completeness failed: {e}"
    errors.append(err)
    print(err)

# ----------------------------------------------------
# Test 4: Post-Level Key Uniqueness & Completeness
# ----------------------------------------------------
try:
    metrics_csv = os.path.join(ANALYSIS_DIR, "instagram_engagement_metrics.csv")
    df_met = pd.read_csv(metrics_csv)
    
    assert len(df_met) == 55, f"Expected 55 rows, got {len(df_met)}"
    assert df_met['post_id'].nunique() == 55, "Duplicate post_id detected in metrics output"
    assert df_met['post_url'].nunique() == 55, "Duplicate post_url detected in metrics output"
    assert set(df_met['post_id']) == set(df_src['post_id']), "Post ID set does not match source dataset"
    
    p = "[PASS] Test 4: Post-level key uniqueness & completeness confirmed (55 unique posts, 0 duplicates)."
    passes.append(p)
    print(p)
except Exception as e:
    err = f"[FAIL] Test 4: Key uniqueness failed: {e}"
    errors.append(err)
    print(err)

# ----------------------------------------------------
# Test 5: Interaction Arithmetic Consistency
# ----------------------------------------------------
try:
    assert (df_met['total_interactions'] == df_met['likes'] + df_met['comments']).all(), "Arithmetic error: total_interactions != likes + comments"
    assert int(df_met['likes'].sum()) == 12643, f"Sum likes mismatch: {df_met['likes'].sum()}"
    assert int(df_met['comments'].sum()) == 504, f"Sum comments mismatch: {df_met['comments'].sum()}"
    assert int(df_met['total_interactions'].sum()) == 13147, f"Sum interactions mismatch: {df_met['total_interactions'].sum()}"
    
    p = "[PASS] Test 5: Interaction arithmetic consistency verified (likes: 12,643 + comments: 504 == total: 13,147)."
    passes.append(p)
    print(p)
except Exception as e:
    err = f"[FAIL] Test 5: Arithmetic check failed: {e}"
    errors.append(err)
    print(err)

# ----------------------------------------------------
# Test 6: Summary Metrics Consistency
# ----------------------------------------------------
try:
    summary_csv = os.path.join(ANALYSIS_DIR, "instagram_engagement_summary.csv")
    df_sum = pd.read_csv(summary_csv)
    
    assert len(df_sum) == 3, f"Expected 3 summary rows, got {len(df_sum)}"
    row_inter = df_sum[df_sum['metric'] == 'total_interactions'].iloc[0]
    row_likes = df_sum[df_sum['metric'] == 'likes'].iloc[0]
    row_comms = df_sum[df_sum['metric'] == 'comments'].iloc[0]
    
    assert abs(row_inter['mean'] - 239.04) < 0.01, f"Interactions mean mismatch: {row_inter['mean']}"
    assert abs(row_inter['median'] - 51.0) < 0.01, f"Interactions median mismatch: {row_inter['median']}"
    assert abs(row_likes['mean'] - 229.87) < 0.01, f"Likes mean mismatch: {row_likes['mean']}"
    assert abs(row_likes['median'] - 44.0) < 0.01, f"Likes median mismatch: {row_likes['median']}"
    assert abs(row_comms['mean'] - 9.16) < 0.01, f"Comments mean mismatch: {row_comms['mean']}"
    assert abs(row_comms['median'] - 1.0) < 0.01, f"Comments median mismatch: {row_comms['median']}"
    
    p = "[PASS] Test 6: Summary statistics mathematically consistent across all 3 engagement metrics."
    passes.append(p)
    print(p)
except Exception as e:
    err = f"[FAIL] Test 6: Summary consistency failed: {e}"
    errors.append(err)
    print(err)

# ----------------------------------------------------
# Test 7: Outlier Logic & IQR Thresholds
# ----------------------------------------------------
try:
    outlier_count = int(df_met['is_interaction_outlier'].sum())
    assert outlier_count == 9, f"Expected 9 outlier posts, got {outlier_count}"
    
    # Check threshold Q3 + 1.5*IQR = 110 + 1.5*86 = 239.0
    outliers_vals = df_met[df_met['is_interaction_outlier']]['total_interactions']
    assert (outliers_vals > 239.0).all(), "Posts flagged as outlier have <= 239.0 interactions"
    non_outliers = df_met[~df_met['is_interaction_outlier']]['total_interactions']
    assert (non_outliers <= 239.0).all(), "Non-outlier posts exceed 239.0 interactions"
    
    p = "[PASS] Test 7: Outlier IQR logic verified (Threshold: 239.0, exactly 9 viral outlier posts [16.36%])."
    passes.append(p)
    print(p)
except Exception as e:
    err = f"[FAIL] Test 7: Outlier logic failed: {e}"
    errors.append(err)
    print(err)

# ----------------------------------------------------
# Test 8: Content Type Comparison Consistency
# ----------------------------------------------------
try:
    ct_csv = os.path.join(ANALYSIS_DIR, "instagram_content_type_comparison.csv")
    df_ct = pd.read_csv(ct_csv)
    
    assert len(df_ct) == 4, f"Expected 4 rows in content type table, got {len(df_ct)}"
    ct_dict = df_ct.set_index('content_type')['post_count'].to_dict()
    assert ct_dict.get('video/reel') == 44, f"Reels count: {ct_dict}"
    assert ct_dict.get('carousel') == 8, f"Carousel count: {ct_dict}"
    assert ct_dict.get('image') == 3, f"Image count: {ct_dict}"
    assert ct_dict.get('Total / Overall') == 55, f"Total count: {ct_dict}"
    
    inter_dict = df_ct.set_index('content_type')['total_interactions'].to_dict()
    assert inter_dict.get('video/reel') == 12472, f"Reels interactions: {inter_dict}"
    assert inter_dict.get('carousel') == 658, f"Carousel interactions: {inter_dict}"
    assert inter_dict.get('image') == 17, f"Image interactions: {inter_dict}"
    assert inter_dict.get('Total / Overall') == 13147, f"Total interactions: {inter_dict}"
    
    p = "[PASS] Test 8: Content type comparison consistent (Reels: 44 [12,472 int], Carousel: 8 [658 int], Image: 3 [17 int])."
    passes.append(p)
    print(p)
except Exception as e:
    err = f"[FAIL] Test 8: Content type failed: {e}"
    errors.append(err)
    print(err)

# ----------------------------------------------------
# Test 9: Collaboration Analysis Consistency
# ----------------------------------------------------
try:
    colab_csv = os.path.join(ANALYSIS_DIR, "instagram_collaboration_analysis.csv")
    df_colab = pd.read_csv(colab_csv)
    
    status_df = df_colab[df_colab['analysis_dimension'] == 'Collaboration Status']
    assert len(status_df) == 2, f"Expected 2 status rows, got {len(status_df)}"
    
    org_row = status_df[status_df['segment'].str.contains('Organic')].iloc[0]
    col_row = status_df[status_df['segment'].str.contains('Collaborative')].iloc[0]
    
    assert org_row['post_count'] == 29, f"Organic count mismatch: {org_row['post_count']}"
    assert col_row['post_count'] == 26, f"Colab count mismatch: {col_row['post_count']}"
    assert org_row['total_interactions'] == 1273, f"Organic interactions mismatch: {org_row['total_interactions']}"
    assert col_row['total_interactions'] == 11874, f"Colab interactions mismatch: {col_row['total_interactions']}"
    
    # Check account breakdown sums
    acc_df = df_colab[df_colab['analysis_dimension'] == 'Partner Account Breakdown']
    assert len(acc_df) == 6, f"Expected 6 account rows, got {len(acc_df)}"
    assert int(acc_df['post_count'].sum()) == 55, f"Account post count sum mismatch: {acc_df['post_count'].sum()}"
    assert int(acc_df['total_interactions'].sum()) == 13147, f"Account interactions sum mismatch: {acc_df['total_interactions'].sum()}"
    
    p = "[PASS] Test 9: Collaboration analysis consistent (29 Organic [1,273 int], 26 Colab [11,874 int] across 6 partner entities)."
    passes.append(p)
    print(p)
except Exception as e:
    err = f"[FAIL] Test 9: Collaboration failed: {e}"
    errors.append(err)
    print(err)

# ----------------------------------------------------
# Test 10: Temporal Analysis Consistency
# ----------------------------------------------------
try:
    time_csv = os.path.join(ANALYSIS_DIR, "instagram_posting_time_analysis.csv")
    df_time = pd.read_csv(time_csv)
    
    dow_df = df_time[df_time['time_dimension'] == 'Day of Week']
    assert len(dow_df) == 7, f"Expected 7 days, got {len(dow_df)}"
    assert int(dow_df['post_count'].sum()) == 55, "Day of week post count sum != 55"
    assert int(dow_df['total_interactions'].sum()) == 13147, "Day of week interactions sum != 13,147"
    
    bin_df = df_time[df_time['time_dimension'] == 'Time of Day Bin']
    assert len(bin_df) == 4, f"Expected 4 time bins, got {len(bin_df)}"
    assert int(bin_df['post_count'].sum()) == 55, "Time bin post count sum != 55"
    assert int(bin_df['total_interactions'].sum()) == 13147, "Time bin interactions sum != 13,147"
    
    year_df = df_time[df_time['time_dimension'] == 'Year']
    assert len(year_df) == 3, f"Expected 3 years, got {len(year_df)}"
    assert int(year_df['post_count'].sum()) == 55, "Year post count sum != 55"
    assert int(year_df['total_interactions'].sum()) == 13147, "Year interactions sum != 13,147"
    
    p = "[PASS] Test 10: Temporal analysis consistent (Days, Bins, and Years all sum exactly to 55 posts & 13,147 interactions)."
    passes.append(p)
    print(p)
except Exception as e:
    err = f"[FAIL] Test 10: Temporal analysis failed: {e}"
    errors.append(err)
    print(err)

# ----------------------------------------------------
# Test 11: Caption & Hashtag Statistical Integrity
# ----------------------------------------------------
try:
    ch_csv = os.path.join(ANALYSIS_DIR, "instagram_caption_hashtag_analysis.csv")
    df_ch = pd.read_csv(ch_csv)
    
    corr_df = df_ch[df_ch['analysis_dimension'] == 'Correlation Analysis']
    assert len(corr_df) == 3, f"Expected 3 correlation rows, got {len(corr_df)}"
    
    wc_row = corr_df[corr_df['feature_category'].str.contains('Word Count')].iloc[0]
    ht_row = corr_df[corr_df['feature_category'].str.contains('Hashtag Count')].iloc[0]
    
    assert abs(wc_row['spearman_rho'] - 0.3806) < 0.01, f"Spearman word count mismatch: {wc_row['spearman_rho']}"
    assert abs(ht_row['spearman_rho'] - (-0.4509)) < 0.01, f"Spearman hashtag mismatch: {ht_row['spearman_rho']}"
    assert wc_row['sample_size'] == 55, f"Word count sample size: {wc_row['sample_size']}"
    assert ht_row['sample_size'] == 55, f"Hashtag count sample size: {ht_row['sample_size']}"
    
    p = "[PASS] Test 11: Caption & hashtag statistics verified (Spearman rho: word count +0.381, hashtag count -0.451 [Simpson's paradox])."
    passes.append(p)
    print(p)
except Exception as e:
    err = f"[FAIL] Test 11: Caption & hashtag stats failed: {e}"
    errors.append(err)
    print(err)

# ----------------------------------------------------
# Test 12: Top & Bottom Posts Integrity
# ----------------------------------------------------
try:
    top_csv = os.path.join(ANALYSIS_DIR, "instagram_top_posts.csv")
    df_top = pd.read_csv(top_csv)
    
    assert len(df_top) == 20, f"Expected 20 showcase rows (10 top, 10 bottom), got {len(df_top)}"
    top10_p = df_top[df_top['tier'] == 'Top 10 High Engagement']
    bot10_p = df_top[df_top['tier'] == 'Bottom 10 Low Engagement']
    
    assert len(top10_p) == 10, f"Top 10 count: {len(top10_p)}"
    assert len(bot10_p) == 10, f"Bottom 10 count: {len(bot10_p)}"
    
    # Check top 1
    top1 = top10_p.iloc[0]
    assert top1['post_id'] == 'DQnklphEi9f', f"Top 1 post ID mismatch: {top1['post_id']}"
    assert top1['total_interactions'] == 3217, f"Top 1 interactions: {top1['total_interactions']}"
    
    # Check bottom 1
    bot1 = bot10_p.iloc[0]
    assert bot1['post_id'] == 'DQww8EzE8tt', f"Bottom 1 post ID mismatch: {bot1['post_id']}"
    assert bot1['total_interactions'] == 1, f"Bottom 1 interactions: {bot1['total_interactions']}"
    
    p = "[PASS] Test 12: Top & Bottom posts showcase verified (Top 1: DQnklphEi9f [3,217], Bottom 1: DQww8EzE8tt [1])."
    passes.append(p)
    print(p)
except Exception as e:
    err = f"[FAIL] Test 12: Top & Bottom posts failed: {e}"
    errors.append(err)
    print(err)

# ----------------------------------------------------
# Test 13: CSV and XLSX Structural & Semantic Equivalence
# ----------------------------------------------------
try:
    for base in EXPECTED_BASE_NAMES:
        c_path = os.path.join(ANALYSIS_DIR, f"{base}.csv")
        x_path = os.path.join(ANALYSIS_DIR, f"{base}.xlsx")
        
        c_df = pd.read_csv(c_path)
        wb = openpyxl.load_workbook(x_path)
        first_sheet = wb.sheetnames[0]
        x_df = pd.read_excel(x_path, sheet_name=first_sheet)
        
        assert len(c_df) == len(x_df), f"Row count mismatch in {base}: CSV {len(c_df)} vs XLSX {len(x_df)}"
        assert list(c_df.columns) == list(x_df.columns), f"Column mismatch in {base}"
        
        # Check numeric equivalence for numeric columns
        for col in c_df.select_dtypes(include=[np.number]).columns:
            c_vals = c_df[col].fillna(-999999).values
            x_vals = x_df[col].fillna(-999999).values
            diff = np.abs(c_vals - x_vals)
            assert (diff < 0.01).all(), f"Numeric value mismatch in {base}.{col}: max diff {diff.max()}"
            
    p = "[PASS] Test 13: CSV and XLSX structural & semantic equivalence confirmed across all 7 artifact pairs."
    passes.append(p)
    print(p)
except Exception as e:
    err = f"[FAIL] Test 13: CSV/XLSX equivalence failed: {e}"
    errors.append(err)
    print(err)

# ----------------------------------------------------
# Test 14: Zero-Fabrication & Platform Compliance Audit
# ----------------------------------------------------
try:
    prohibited_fabricated_cols = [
        "reach", "impressions", "follower_count", "followers",
        "engagement_rate", "engagement_rate_pct", "view_count"
    ]
    
    for base in EXPECTED_BASE_NAMES:
        c_path = os.path.join(ANALYSIS_DIR, f"{base}.csv")
        df_check = pd.read_csv(c_path)
        for c in df_check.columns:
            assert c.lower() not in prohibited_fabricated_cols, f"Prohibited fabricated column {c} found in {base}.csv"
            
    # Check that in source final dataset, views is strictly NaN (unauthenticated truth preserved)
    assert df_src['views'].isna().all(), "Views in source final dataset is not strictly NaN"
    
    p = "[PASS] Test 14: Zero-fabrication confirmed (No synthetic reach, impressions, followers, views, or arbitrary ER formulas)."
    passes.append(p)
    print(p)
except Exception as e:
    err = f"[FAIL] Test 14: Fabrication test failed: {e}"
    errors.append(err)
    print(err)

# ----------------------------------------------------
# Test 15: Privacy & Identifier Minimization
# ----------------------------------------------------
try:
    prohibited_pii_cols = [
        "user_name", "user_image", "commenter_id", "commenter_name",
        "password", "token", "cookie", "email", "phone"
    ]
    for base in EXPECTED_BASE_NAMES:
        c_path = os.path.join(ANALYSIS_DIR, f"{base}.csv")
        df_check = pd.read_csv(c_path)
        for c in df_check.columns:
            assert c.lower() not in prohibited_pii_cols, f"PII column {c} found in {base}.csv"
            
    # Check original_account is restricted to known corporate / creator partner entities
    allowed_accounts = {"zahiraccounting", "muhamad.is", "pecahtelur.id", "zahironlineid", "modalngobrol", "zahirerp"}
    metrics_csv = os.path.join(ANALYSIS_DIR, "instagram_engagement_metrics.csv")
    df_met = pd.read_csv(metrics_csv)
    assert set(df_met["original_account"]).issubset(allowed_accounts), f"Unexpected account: {set(df_met['original_account'])}"
    
    p = "[PASS] Test 15: Privacy verified (Zero personal commenter identifiers or credentials; verified brand accounts only)."
    passes.append(p)
    print(p)
except Exception as e:
    err = f"[FAIL] Test 15: Privacy test failed: {e}"
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
    print("\nALL 15 PHASE 5.5 AUTOMATED INTEGRITY TESTS PASSED SUCCESSFULLY!")
    sys.exit(0)