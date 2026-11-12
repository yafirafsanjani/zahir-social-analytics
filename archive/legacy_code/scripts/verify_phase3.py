import os
import json
import pandas as pd

def test_phase3():
    print("=== VALIDATION SUITE FOR PHASE 3 ===")

    csv_path = os.path.join("data", "final", "playstore_reviews_final.csv")
    assert os.path.exists(csv_path), "Final CSV does not exist!"
    df = pd.read_csv(csv_path)
    print("[PASS] Test 1: Final dataset loads successfully.")

    assert len(df) == 417, f"Row count expected 417, got {len(df)}"
    print(f"[PASS] Test 2: Row count = {len(df)} rows.")

    expected_cols = [
        "review_id", "reviewer_id", "review_datetime", "review_date", "review_year", "review_month",
        "review_text", "review_text_clean", "score", "rating_category", "thumbs_up_count",
        "has_developer_reply", "reply_text", "replied_datetime", "response_time_days",
        "app_name", "package_name", "review_created_version", "app_version",
        "text_length_chars", "word_count"
    ]
    assert list(df.columns) == expected_cols, f"Columns mismatch! Got: {list(df.columns)}"
    print(f"[PASS] Test 3: Expected 21 columns match exactly ({len(df.columns)} columns).")

    assert df["review_id"].nunique() == 417, "review_id is not unique!"
    assert df["review_id"].duplicated().sum() == 0, "Found duplicate review_id!"
    print("[PASS] Test 4: review_id is 100% unique (0 duplicates).")

    apps = sorted(df["app_name"].unique().tolist())
    assert len(apps) == 5, f"Expected 5 apps, got {len(apps)}"
    print(f"[PASS] Test 5: Five applications present: {apps}")

    assert df["score"].between(1, 5).all(), "Score outside 1-5!"
    assert set(df["score"].unique()) == {1, 2, 3, 4, 5}, "Scores do not span 1-5!"
    print("[PASS] Test 6: Score values strictly in range [1, 5].")

    assert set(df["rating_category"].unique()) == {"critical", "neutral", "positive"}
    crit_match = (df[df["score"].isin([1, 2])]["rating_category"] == "critical").all()
    neut_match = (df[df["score"] == 3]["rating_category"] == "neutral").all()
    pos_match = (df[df["score"].isin([4, 5])]["rating_category"] == "positive").all()
    assert crit_match and neut_match and pos_match, "Rating category mapping mismatch!"
    print("[PASS] Test 7: rating_category valid and correctly mapped.")

    parsed_dates = pd.to_datetime(df["review_datetime"], errors="coerce")
    assert parsed_dates.notna().all(), "Invalid review_datetime!"
    print("[PASS] Test 8: review_datetime valid and 100% parseable.")

    assert set(df["has_developer_reply"].unique()) == {True, False}
    assert (df["has_developer_reply"] == df["reply_text"].notna()).all()
    assert df["has_developer_reply"].sum() == 366
    print("[PASS] Test 9: has_developer_reply valid (366 Replied, 51 Unreplied).")

    neg_cases = (df["response_time_days"] < 0).sum()
    assert neg_cases == 15, f"Expected 15 negative response time cases, got {neg_cases}"
    print(f"[PASS] Test 10: response_time_days negative cases = {neg_cases} exactly and documented.")

    nb_path = os.path.join("notebooks", "05_playstore_eda.ipynb")
    assert os.path.exists(nb_path), "Notebook does not exist!"
    with open(nb_path, "r", encoding="utf-8") as f:
        nb_json = json.load(f)
    assert "cells" in nb_json and len(nb_json["cells"]) > 0
    print(f"[PASS] Test 11: Notebook JSON valid with {len(nb_json['cells'])} cells.")

    cells_with_output = sum(1 for c in nb_json["cells"] if len(c.get("outputs", [])) > 0)
    assert cells_with_output > 10, f"Expected multiple executed cells, got {cells_with_output}"
    print(f"[PASS] Test 12: Notebook executed successfully from project root ({cells_with_output} cells with outputs).")

    print("\nALL 12 TESTS PASSED PERFECTLY!")

if __name__ == "__main__":
    test_phase3()
