import sys
import subprocess
import hashlib
from pathlib import Path
import nbformat
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
print("=" * 70)
print("ZAHIR SOCIAL ANALYTICS - COMPREHENSIVE REFACTORING TEST SUITE")
print("=" * 70)
print(f"Repository Root: {ROOT}")

test_results = []

def record(name, status, details=""):
    test_results.append({"suite": name, "status": status, "details": details})
    tag = "[PASS]" if status else "[FAIL]"
    print(f"{tag} {name} - {details}")

# 1. Structural nbformat Validation of 8 Canonical Notebooks
notebooks = [
    "01_data_acquisition.ipynb",
    "02_playstore_preprocessing_eda.ipynb",
    "03_playstore_goldset.ipynb",
    "04_sentiment_benchmark.ipynb",
    "05_aspect_analysis.ipynb",
    "06_instagram_preprocessing.ipynb",
    "07_instagram_engagement_analysis.ipynb",
    "08_dataset_validation_export.ipynb"
]

all_nb_valid = True
for nb_name in notebooks:
    nb_path = ROOT / "notebooks" / nb_name
    if not nb_path.exists():
        record(f"Notebook Exists: {nb_name}", False, "File not found")
        all_nb_valid = False
        continue
    try:
        nb = nbformat.read(str(nb_path), as_version=4)
        nbformat.validate(nb)
    except Exception as e:
        record(f"nbformat Validate: {nb_name}", False, str(e))
        all_nb_valid = False
record("Notebook Structural Validity", all_nb_valid, f"All {len(notebooks)} canonical notebooks conform to nbformat v4 schema")

# 2. SHA-256 Checksum Validation of Protected Sources
manifest_path = ROOT / "data" / "export" / "source_integrity_manifest.csv"
if manifest_path.exists():
    m_df = pd.read_csv(manifest_path)
    all_matched = True
    for _, row in m_df.iterrows():
        p = ROOT / row["source_path"]
        if not p.exists():
            all_matched = False
            break
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        if h.hexdigest().upper() != row["sha256"].upper():
            all_matched = False
            break
    record("Source Integrity Checksums", all_matched, f"{len(m_df)} protected source datasets match SHA-256 manifest")
else:
    record("Source Integrity Checksums", False, "Manifest file missing")

# 3. Canonical Master Datasets Validation
ig_master_path = ROOT / "data" / "export" / "instagram" / "master" / "instagram_master.csv"
ps_master_path = ROOT / "data" / "export" / "playstore" / "master" / "playstore_master.csv"

if ig_master_path.exists() and ps_master_path.exists():
    ig_df = pd.read_csv(ig_master_path)
    ps_df = pd.read_csv(ps_master_path)
    ig_ok = (len(ig_df) == 55 and ig_df["post_id"].nunique() == 55 and ig_df["views"].isna().all() and ig_df["total_interactions"].sum() == 13147)
    ps_ok = (len(ps_df) == 417 and ps_df["review_id"].nunique() == 417 and ps_df["aspect_count"].sum() == 234 and ps_df["human_sentiment_label"].notna().all())
    record("Instagram Master Validation", ig_ok, f"55 rows, 55 unique IDs, zero fabrication (views 100% NaN), sum interactions = 13,147")
    record("Play Store Master Validation", ps_ok, f"417 rows, 417 unique IDs, Gold Set universal, 234 remediated aspect mentions")
else:
    record("Master Datasets Check", False, "One or more master datasets missing")

# 4. Regression Verification Suites Execution
python_exe = sys.executable
scripts_to_run = [
    ("Phase 5.3 Quality Suite", "archive/legacy_code/scripts/verify_phase5_3.py"),
    ("Phase 5.4 Quality Suite", "archive/legacy_code/scripts/verify_phase5_4.py"),
    ("Phase 5.5 Quality Suite", "archive/legacy_code/scripts/verify_phase5_5.py"),
    ("Phase 5.6 Quality Suite", "archive/legacy_code/scripts/verify_phase5_6.py"),
    ("Phase 5.8 Quality Suite", "archive/legacy_code/scripts/verify_phase5_8.py"),
]

for name, script_rel in scripts_to_run:
    script_path = ROOT / script_rel
    res = subprocess.run([python_exe, str(script_path)], capture_output=True, text=True, cwd=str(ROOT))
    success = (res.returncode == 0) and ("FAILED" not in res.stdout or "0 FAILED" in res.stdout)
    record(name, success, "100% assertions passed" if success else f"Return code {res.returncode}")

# 5. Summary
print("=" * 70)
total_pass = sum(1 for r in test_results if r["status"])
total_fail = sum(1 for r in test_results if not r["status"])
print(f"OVERALL SUMMARY: {total_pass} SUITES PASSED, {total_fail} FAILED")
print("=" * 70)
