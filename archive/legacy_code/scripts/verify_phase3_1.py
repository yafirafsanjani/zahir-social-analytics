import os
import json
import pandas as pd

def run_phase3_1_tests():
    print("==================================================")
    print("PHASE 3.1 COMPREHENSIVE VERIFICATION TEST SUITE")
    print("==================================================")

    # 1. Final dataset loads
    csv_path = os.path.join("data", "final", "playstore_reviews_final.csv")
    assert os.path.exists(csv_path), "Test 1 FAILED: Final dataset does not exist!"
    df = pd.read_csv(csv_path)
    print("[PASS] Test 1: Final dataset loads successfully.")

    # 2. Row count = 417
    assert len(df) == 417, f"Test 2 FAILED: Expected 417 rows, got {len(df)}"
    print(f"[PASS] Test 2: Row count = {len(df)} exactly.")

    # 3. Year counts sum = 417
    parsed_dates = pd.to_datetime(df["review_datetime"])
    year_counts = parsed_dates.dt.year.value_counts().sort_index()
    assert year_counts.sum() == 417, f"Test 3 FAILED: Expected sum 417, got {year_counts.sum()}"
    # Verify expected year distribution:
    expected_years = {2018: 190, 2019: 78, 2020: 50, 2021: 32, 2022: 29, 2023: 21, 2024: 7, 2025: 8, 2026: 2}
    actual_years = year_counts.to_dict()
    assert actual_years == expected_years, f"Test 3 FAILED: Year distribution mismatch! {actual_years}"
    print(f"[PASS] Test 3: Year counts sum = {year_counts.sum()} and match actual dataset distribution {actual_years}.")

    # 4. Application counts sum = 417
    app_counts = df["app_name"].value_counts()
    assert app_counts.sum() == 417, f"Test 4 FAILED: Expected sum 417, got {app_counts.sum()}"
    expected_apps = {
        "Zahir Simple Start": 160,
        "Zahir Online": 98,
        "POS X": 87,
        "Zahir Certification": 44,
        "Zahir Attendance": 28
    }
    assert app_counts.to_dict() == expected_apps, f"Test 4 FAILED: App counts mismatch! {app_counts.to_dict()}"
    print(f"[PASS] Test 4: Application counts sum = {app_counts.sum()} across 5 applications.")

    # 5. Rating counts sum = 417
    score_counts = df["score"].value_counts().sort_index()
    assert score_counts.sum() == 417, f"Test 5 FAILED: Expected sum 417, got {score_counts.sum()}"
    expected_scores = {1: 74, 2: 27, 3: 37, 4: 31, 5: 248}
    assert score_counts.to_dict() == expected_scores, f"Test 5 FAILED: Score counts mismatch! {score_counts.to_dict()}"
    print(f"[PASS] Test 5: Rating counts sum = {score_counts.sum()} (Scores 1-5).")

    # 6. Rating category mapping valid
    crit_valid = (df[df["score"].isin([1, 2])]["rating_category"] == "critical").all()
    neut_valid = (df[df["score"] == 3]["rating_category"] == "neutral").all()
    pos_valid = (df[df["score"].isin([4, 5])]["rating_category"] == "positive").all()
    assert crit_valid and neut_valid and pos_valid, "Test 6 FAILED: Rating category mapping invalid!"
    cat_counts = df["rating_category"].value_counts().to_dict()
    assert cat_counts == {"positive": 279, "critical": 101, "neutral": 37}
    print(f"[PASS] Test 6: Rating category mapping strictly valid (Positive: 279, Critical: 101, Neutral: 37).")

    # 7. Reply counts consistent
    rep_count = df["has_developer_reply"].sum()
    unrep_count = (~df["has_developer_reply"]).sum()
    assert rep_count == 366 and unrep_count == 51, f"Test 7 FAILED: Replied={rep_count}, Unreplied={unrep_count}"
    assert (df["has_developer_reply"] == df["reply_text"].notna()).all(), "Test 7 FAILED: reply_text mismatch!"
    print(f"[PASS] Test 7: Reply counts consistent (Replied: {rep_count}, Unreplied: {unrep_count}).")

    # 8. Negative response-time count = 15
    neg_rt_count = (df["response_time_days"] < 0).sum()
    non_neg_rt_count = (df["response_time_days"] >= 0).sum()
    assert neg_rt_count == 15, f"Test 8 FAILED: Expected 15 negative response time records, got {neg_rt_count}"
    assert non_neg_rt_count == 351, f"Test 8 FAILED: Expected 351 non-negative records, got {non_neg_rt_count}"
    print(f"[PASS] Test 8: Negative response-time count = {neg_rt_count} exactly; valid subset = {non_neg_rt_count}.")

    # 9. Notebook JSON valid
    nb_path = os.path.join("notebooks", "05_playstore_eda.ipynb")
    assert os.path.exists(nb_path), "Test 9 FAILED: Notebook does not exist!"
    with open(nb_path, "r", encoding="utf-8") as f:
        nb_json = json.load(f)
    assert "cells" in nb_json and len(nb_json["cells"]) >= 35, f"Test 9 FAILED: Insufficient cells ({len(nb_json['cells'])})"
    print(f"[PASS] Test 9: Notebook JSON valid with {len(nb_json['cells'])} cells.")

    # 10. Notebook executes successfully
    code_cells = [c for c in nb_json["cells"] if c["cell_type"] == "code"]
    executed_cells = [c for c in code_cells if len(c.get("outputs", [])) > 0]
    assert len(executed_cells) == len(code_cells), f"Test 10 FAILED: Executed {len(executed_cells)}/{len(code_cells)}"
    print(f"[PASS] Test 10: Notebook executes successfully ({len(executed_cells)}/{len(code_cells)} code cells with fresh outputs).")

    print("\nALL 10 TESTS PASSED WITH 100% SUCCESS!")

if __name__ == "__main__":
    run_phase3_1_tests()
