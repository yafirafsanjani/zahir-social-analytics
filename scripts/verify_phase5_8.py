from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EXPORT = ROOT / 'data' / 'export'


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest().upper()


def check(condition: bool, message: str, failures: list[str], passes: list[str]) -> None:
    if condition:
        passes.append(message)
        print(f'[PASS] {message}')
    else:
        failures.append(message)
        print(f'[FAIL] {message}')


def main() -> None:
    failures: list[str] = []
    passes: list[str] = []
    instagram = pd.read_csv(EXPORT / 'instagram' / 'master' / 'instagram_master.csv')
    required_ig = {'post_id', 'post_url', 'post_date', 'content_type', 'caption', 'hashtags', 'likes', 'comments', 'total_interactions', 'is_collaboration', 'original_account'}
    check(len(instagram) == 55 and instagram.post_id.nunique() == 55 and required_ig.issubset(instagram.columns), 'Instagram master preserves 55 unique canonical posts and required fields.', failures, passes)
    check(not {'reach', 'impressions', 'engagement_rate', 'engagement_rate_pct'}.intersection(instagram.columns) and instagram['views'].isna().all(), 'Instagram master preserves the zero-fabrication policy for unavailable metrics.', failures, passes)
    master = pd.read_csv(EXPORT / 'playstore' / 'master' / 'playstore_master.csv')
    aspects = pd.read_csv(EXPORT / 'playstore' / 'aspects' / 'playstore_aspect_assignments_remediated.csv')
    flags = [column for column in aspects.columns if column.startswith('aspect_') and column != 'aspect_count']
    forbidden = {'userName', 'userImage', 'reviewer_id', 'reply_text'}
    check(len(master) == 417 and master.review_id.nunique() == 417 and not forbidden.intersection(master.columns), 'Play Store master preserves 417 unique privacy-reduced reviews.', failures, passes)
    check(master.human_sentiment_label.notna().all() and (master.sentiment_label_source == 'gold_set_human_annotated').all(), 'Play Store master preserves universal human-annotated Gold Set labels.', failures, passes)
    check(int(master.aspect_count.sum()) == 234 and (master.aspect_count == master[flags].sum(axis=1)).all(), 'Play Store master preserves 234 remediated aspect mentions across eight flags.', failures, passes)
    sentiment = pd.read_csv(EXPORT / 'playstore' / 'sentiment' / 'playstore_sentiment_all.csv')
    test = sentiment[sentiment.benchmark_split == 'test']
    development = sentiment[sentiment.benchmark_split == 'development']
    check(len(test) == 84 and len(development) == 333 and test.test_pred_indobert.notna().all() and development.test_pred_indobert.isna().all(), 'Model predictions remain separated to the 84 held-out test reviews.', failures, passes)
    manifest = pd.read_csv(EXPORT / 'source_integrity_manifest.csv')
    check(all((ROOT / row.source_path).exists() and digest(ROOT / row.source_path) == row.sha256 for row in manifest.itertuples()), 'Protected source checksums match the export integrity manifest.', failures, passes)
    inventory = pd.read_csv(EXPORT / 'dataset_inventory.csv')
    check(len(inventory) >= 90 and {'exported', 'not_exported', 'duplicate'}.issubset(set(inventory.status)), 'Dataset inventory documents exported, withheld, and duplicate source artifacts.', failures, passes)
    summary = pd.read_excel(EXPORT / 'dataset_inventory.xlsx', sheet_name='Export Summary')
    check(len(summary) == 35 and (EXPORT / 'README_data_dictionary.md').exists() and (EXPORT / 'dataset_relationships.md').exists(), 'Dictionary, relationship documentation, and 35-dataset export summary are present.', failures, passes)
    pairs = []
    for row in summary.itertuples():
        csv_path = EXPORT / row.export_path
        pairs.append((csv_path, csv_path.with_suffix('.xlsx')))
    pairs += [(EXPORT / 'dataset_inventory.csv', EXPORT / 'dataset_inventory.xlsx'), (EXPORT / 'source_integrity_manifest.csv', EXPORT / 'source_integrity_manifest.xlsx')]
    pair_ok = True
    for csv_path, xlsx_path in pairs:
        csv_frame = pd.read_csv(csv_path)
        xlsx_frame = pd.read_excel(xlsx_path, sheet_name=0)
        csv_columns = [re.sub(r'[^a-z0-9]', '', column.lower()) for column in csv_frame.columns]
        xlsx_columns = [re.sub(r'[^a-z0-9]', '', column.lower()) for column in xlsx_frame.columns]
        if len(csv_frame) != len(xlsx_frame) or csv_columns != xlsx_columns:
            pair_ok = False
            print(f'Pair mismatch: {csv_path}')
            break
    check(pair_ok, 'All structured CSV/XLSX pairs have matching primary-sheet schemas and row counts.', failures, passes)
    print(f'PHASE 5.8 VERIFICATION SUMMARY: {len(passes)} PASSED, {len(failures)} FAILED')
    if failures:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
