from __future__ import annotations

import csv
import hashlib
import json
import shutil
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
FINAL = DATA / 'final'
EXPORT = DATA / 'export'

PROTECTED = [
    DATA / 'raw' / 'instagram_posts_raw.csv',
    DATA / 'raw' / 'playstore_reviews_raw.csv',
    FINAL / 'playstore_gold_set_final.csv',
    FINAL / 'topic_analysis' / 'phase_5_3' / 'review_aspect_assignments_remediated.csv',
    DATA / 'raw' / 'instagram_posts_raw_phase1_6_baseline.csv',
]

REGISTRY = [
    ('instagram', 'master', FINAL / 'instagram_posts_final.csv', 'instagram_master', 'post_id', 'Canonical final Instagram post-level dataset.'),
    ('instagram', 'engagement', FINAL / 'instagram_analysis' / 'instagram_engagement_metrics.csv', 'instagram_engagement_metrics', 'post_id', 'Post-level engagement ranking, tiers, and outlier flags.'),
    ('instagram', 'engagement', FINAL / 'instagram_analysis' / 'instagram_engagement_summary.csv', 'instagram_engagement_summary', 'metric', 'Overall engagement descriptive statistics.'),
    ('instagram', 'analysis', FINAL / 'instagram_analysis' / 'instagram_content_type_comparison.csv', 'instagram_content_type_comparison', 'content_type', 'Content format performance comparison.'),
    ('instagram', 'analysis', FINAL / 'instagram_analysis' / 'instagram_collaboration_analysis.csv', 'instagram_collaboration_analysis', 'analysis_dimension + segment', 'Collaboration and original-account performance analysis.'),
    ('instagram', 'analysis', FINAL / 'instagram_analysis' / 'instagram_posting_time_analysis.csv', 'instagram_posting_time_analysis', 'time_dimension + time_category', 'Posting-day, hour, and time-bin analysis.'),
    ('instagram', 'analysis', FINAL / 'instagram_analysis' / 'instagram_caption_hashtag_analysis.csv', 'instagram_caption_hashtag_analysis', 'analysis_dimension + feature_category', 'Caption and hashtag correlation and segment analysis.'),
    ('instagram', 'analysis', FINAL / 'instagram_analysis' / 'instagram_top_posts.csv', 'instagram_top_posts', 'tier + rank', 'Top and bottom Instagram posts.'),
    ('instagram', 'analysis', FINAL / 'instagram_analysis' / 'instagram_data_quality_audit.csv', 'instagram_data_quality_audit', 'metric_dimension + metric_name', 'Instagram preprocessing quality audit.'),
    ('instagram', 'analysis', EXPORT / 'instagram' / 'instagram_content_performance.csv', 'instagram_content_performance', 'analysis_dimension + segment', 'Unified Instagram performance overview.'),
    ('playstore', 'sentiment', EXPORT / 'playstore' / 'playstore_sentiment.csv', 'playstore_sentiment_all', 'review_id', 'Human-annotated Gold Set labels with test-only model predictions.'),
    ('playstore', 'sentiment', FINAL / 'sentiment_benchmark' / 'sentiment_benchmark_metrics.csv', 'sentiment_benchmark_metrics', 'model_name', 'Held-out test benchmark metrics by model.'),
    ('playstore', 'sentiment', FINAL / 'sentiment_benchmark' / 'sentiment_split_manifest.csv', 'sentiment_split_manifest', 'review_id', 'Development/test split membership for the benchmark.'),
    ('playstore', 'sentiment', FINAL / 'sentiment_benchmark' / 'sentiment_test_predictions.csv', 'sentiment_test_predictions', 'review_id', 'Test-only model predictions and confidences.'),
    ('playstore', 'sentiment', FINAL / 'sentiment_benchmark' / 'sentiment_error_analysis.csv', 'sentiment_error_analysis', 'review_id + model_name', 'Model error cases on benchmark evaluation.'),
    ('playstore', 'aspects', FINAL / 'topic_analysis' / 'phase_5_3' / 'review_aspect_assignments_remediated.csv', 'playstore_aspect_assignments_remediated', 'review_id', 'Canonical remediated eight-aspect assignments.'),
    ('playstore', 'aspects', FINAL / 'topic_analysis' / 'aspect_summary_all_reviews.csv', 'aspect_summary_all_reviews', 'aspect_id', 'All-review aspect distribution.'),
    ('playstore', 'aspects', FINAL / 'topic_analysis' / 'aspect_summary_negative_neutral.csv', 'aspect_summary_negative_neutral', 'aspect_id', 'Negative and neutral pain-point aspect summary.'),
    ('playstore', 'aspects', FINAL / 'topic_analysis' / 'aspect_sentiment_comparison.csv', 'aspect_sentiment_comparison', 'aspect_id', 'Aspect-level sentiment contrast.'),
    ('playstore', 'aspects', FINAL / 'topic_analysis' / 'aspect_keyword_audit.csv', 'aspect_keyword_audit', 'keyword_or_pattern + assigned_aspect_id', 'Keyword rule audit for aspect extraction.'),
    ('playstore', 'aspects', FINAL / 'topic_analysis' / 'phase_5_3' / 'aspect_count_reconciliation.csv', 'aspect_count_reconciliation', 'category + metric_name', 'Aspect mention reconciliation audit.'),
    ('playstore', 'aspects', FINAL / 'topic_analysis' / 'phase_5_3' / 'aspect_quality_audit_summary.csv', 'aspect_quality_audit_summary', 'audit_dimension', 'Aspect remediation quality summary.'),
    ('playstore', 'aspects', FINAL / 'topic_analysis' / 'phase_5_3' / 'keyword_remediation_log.csv', 'keyword_remediation_log', 'log_id', 'Applied keyword remediation log.'),
    ('playstore', 'aspects', FINAL / 'topic_analysis' / 'phase_5_3' / 'keyword_rule_audit.csv', 'keyword_rule_audit', 'keyword_or_pattern + assigned_aspect_id', 'Risk and rule audit before remediation.'),
    ('playstore', 'aspects', FINAL / 'topic_analysis' / 'phase_5_3' / 'manual_validation_reconciliation.csv', 'manual_validation_reconciliation', 'metric_category + metric_name', 'Manual validation reconciliation.'),
    ('playstore', 'aspects', FINAL / 'topic_analysis' / 'phase_5_3' / 'manual_validation_results.csv', 'manual_validation_results', 'sample_id', 'Manual validation results; audit-only sample.'),
    ('playstore', 'aspects', FINAL / 'topic_analysis' / 'phase_5_3' / 'quality_audit_summary.csv', 'phase_5_3_quality_audit_summary', 'audit_dimension + metric_or_aspect', 'Phase 5.3 remediation evidence summary.'),
    ('playstore', 'analysis', FINAL / 'playstore_missing_value_report.csv', 'playstore_missing_value_report', 'column', 'Missing-value profile for the processed review dataset.'),
    ('playstore', 'analysis', FINAL / 'topic_analysis_readiness' / 'text_quality_summary.csv', 'text_quality_summary', 'metric_category + metric_name', 'Text-quality indicators for topic-analysis readiness.'),
    ('playstore', 'analysis', FINAL / 'topic_analysis_readiness' / 'topic_readiness_audit.csv', 'topic_readiness_audit', 'evaluation_dimension + dimension_item', 'Topic-analysis readiness assessment.'),
    ('playstore', 'analysis', FINAL / 'topic_analysis_readiness' / 'topic_scope_comparison.csv', 'topic_scope_comparison', 'scope_name', 'Analytical scope comparison.'),
    ('playstore', 'analysis', FINAL / 'topic_analysis' / 'exploratory_clustering_assignments.csv', 'exploratory_clustering_assignments', 'review_id', 'Exploratory clustering assignment for negative and neutral reviews.'),
    ('playstore', 'analysis', FINAL / 'topic_analysis' / 'exploratory_clustering_summary.csv', 'exploratory_clustering_summary', 'num_clusters_k', 'Exploratory clustering diagnostics.'),
]

DESCRIPTIONS = {
    'post_id': 'Unique Instagram post shortcode.',
    'review_id': 'Unique Google Play review identifier.',
    'human_sentiment_label': 'Human-annotated Gold Set sentiment label; not a model prediction.',
    'sentiment_label_source': 'Provenance for the human sentiment label.',
    'benchmark_split': 'Benchmark partition; model predictions are populated only for test.',
    'total_interactions': 'Observed likes plus comments; no synthetic reach, impressions, or rate.',
    'views': 'Unavailable public-web metric and intentionally retained as missing.',
    'review_text': 'Original review text retained without user identity fields.',
    'review_text_clean': 'Conservatively cleaned review text for analysis.',
    'matched_keywords': 'Keyword evidence produced by the aspect-assignment method.',
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest().upper()


def write_workbook(path: Path, sheets: dict[str, pd.DataFrame]) -> None:
    workbook = Workbook()
    workbook.remove(workbook.active)
    for sheet_name, frame in sheets.items():
        worksheet = workbook.create_sheet(sheet_name[:31])
        worksheet.append(list(frame.columns))
        for row in frame.itertuples(index=False, name=None):
            worksheet.append([None if pd.isna(value) else value for value in row])
        worksheet.freeze_panes = 'A2'
        worksheet.auto_filter.ref = worksheet.dimensions
        for cell in worksheet[1]:
            cell.fill = PatternFill('solid', fgColor='0F4C5C')
            cell.font = Font(color='FFFFFF', bold=True)
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        for column_index, column_name in enumerate(frame.columns, start=1):
            sample = [str(column_name)] + [str(value) for value in frame.iloc[:100, column_index - 1].fillna('').tolist()]
            width = min(max(len(value) for value in sample) + 2, 45)
            worksheet.column_dimensions[get_column_letter(column_index)].width = width
        worksheet.sheet_view.showGridLines = False
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(path)


def copy_pair(source: Path, destination_dir: Path, destination_name: str) -> dict:
    destination_dir.mkdir(parents=True, exist_ok=True)
    csv_target = destination_dir / f'{destination_name}.csv'
    xlsx_target = destination_dir / f'{destination_name}.xlsx'
    shutil.copy2(source, csv_target)
    source_xlsx = source.with_suffix('.xlsx')
    frame = pd.read_csv(source)
    if destination_name == 'instagram_data_quality_audit':
        source_sheets = pd.ExcelFile(source_xlsx).sheet_names
        sheets = {'Audit Summary': frame}
        for sheet_name in source_sheets[1:]:
            sheets[sheet_name] = pd.read_excel(source_xlsx, sheet_name=sheet_name)
        write_workbook(xlsx_target, sheets)
    elif source_xlsx.exists():
        shutil.copy2(source_xlsx, xlsx_target)
    else:
        write_workbook(xlsx_target, {'Data': frame})
    return {'export_path': csv_target.relative_to(EXPORT).as_posix(), 'rows': len(frame), 'columns': len(frame.columns), 'columns_list': list(frame.columns)}


def classify(path: Path, source_map: dict[Path, str]) -> tuple[str, str]:
    if path in source_map:
        return 'exported', 'Included in the structured Phase 5.8 handoff package.'
    text = path.as_posix().lower()
    if '/raw/' in text:
        if 'playstore_reviews_raw' in text:
            return 'not_exported', 'Contains raw user identity fields and is replaced by privacy-reduced master data.'
        if 'backup' in text or 'baseline' in text or 'test' in text or 'expansion' in text:
            return 'duplicate', 'Historical backup, baseline, or test artifact; canonical final data is exported instead.'
        return 'not_exported', 'Raw source retained immutable; canonical processed data is exported instead.'
    if 'gold_set_template' in text or 'annotated_validated' in text:
        return 'duplicate', 'Template or duplicate annotation artifact; canonical Gold Set is represented in the master and sentiment exports.'
    if 'review_aspect_assignments.csv' in text and 'remediated' not in text:
        return 'not_exported', 'Superseded by the canonical remediated aspect assignments.'
    if '/data/export/' in text:
        return 'duplicate', 'Legacy flat export superseded by the structured Phase 5.8 handoff package.'
    return 'not_exported', 'Supporting source retained in place; not required for repository handoff.'


def profile_file(path: Path) -> tuple[int | None, int | None, str, str]:
    suffix = path.suffix.lower()
    if suffix == '.csv':
        frame = pd.read_csv(path)
        return len(frame), len(frame.columns), ', '.join(frame.columns[:12]), 'CSV dataset'
    if suffix == '.xlsx':
        workbook = pd.ExcelFile(path)
        frame = pd.read_excel(path, sheet_name=workbook.sheet_names[0])
        return len(frame), len(frame.columns), ', '.join(frame.columns[:12]), f'XLSX workbook ({len(workbook.sheet_names)} sheet(s))'
    if suffix == '.json':
        content = json.loads(path.read_text(encoding='utf-8'))
        return len(content) if isinstance(content, dict) else len(content), None, '', 'JSON configuration/dataset'
    return None, None, '', 'Other'


def build_master() -> pd.DataFrame:
    reviews = pd.read_csv(FINAL / 'playstore_reviews_final.csv')
    gold = pd.read_csv(FINAL / 'playstore_gold_set_final.csv')
    aspects = pd.read_csv(FINAL / 'topic_analysis' / 'phase_5_3' / 'review_aspect_assignments_remediated.csv')
    if len(reviews) != 417 or reviews['review_id'].nunique() != 417:
        raise ValueError('Processed Play Store source must contain 417 unique reviews.')
    if len(gold) != 417 or gold['review_id'].nunique() != 417:
        raise ValueError('Canonical Gold Set must contain 417 unique reviews.')
    if len(aspects) != 417 or aspects['review_id'].nunique() != 417:
        raise ValueError('Canonical remediated aspects must contain 417 unique reviews.')
    sentiment = gold[['review_id', 'human_sentiment_label']].copy()
    sentiment['sentiment_label_source'] = 'gold_set_human_annotated'
    aspect_columns = [column for column in aspects.columns if column.startswith('aspect_') and column != 'aspect_count']
    aspect_columns += ['detected_aspects', 'aspect_count', 'has_aspect', 'matched_keywords']
    master = reviews.drop(columns=['reviewer_id', 'reply_text'], errors='ignore').merge(sentiment, on='review_id', validate='one_to_one')
    master = master.merge(aspects[['review_id', *aspect_columns]], on='review_id', validate='one_to_one')
    if len(master) != 417 or master['review_id'].nunique() != 417:
        raise ValueError('Master Play Store join lost or duplicated reviews.')
    if master['human_sentiment_label'].isna().any() or master['aspect_count'].isna().any():
        raise ValueError('Master Play Store join has missing canonical labels or aspect assignments.')
    forbidden = {'userName', 'userImage', 'reviewer_id', 'reply_text'}
    if forbidden.intersection(master.columns):
        raise ValueError('Master Play Store dataset contains prohibited PII fields.')
    return master


def main() -> None:
    initial_hashes = {path: sha256(path) for path in PROTECTED}
    exported = []
    source_map: dict[Path, str] = {}

    instagram_master = pd.read_csv(FINAL / 'instagram_posts_final.csv')
    if len(instagram_master) != 55 or instagram_master['post_id'].nunique() != 55:
        raise ValueError('Instagram master source must contain 55 unique posts.')
    if {'reach', 'impressions', 'engagement_rate'}.intersection(instagram_master.columns):
        raise ValueError('Instagram master contains prohibited synthetic metrics.')
    instagram_dir = EXPORT / 'instagram' / 'master'
    write_workbook(instagram_dir / 'instagram_master.xlsx', {
        'Instagram Master': instagram_master,
        'Data Dictionary': pd.DataFrame([{'column_name': c, 'description': DESCRIPTIONS.get(c, 'Canonical Instagram master field.'), 'dtype': str(instagram_master[c].dtype)} for c in instagram_master.columns]),
    })
    instagram_master.to_csv(instagram_dir / 'instagram_master.csv', index=False, quoting=csv.QUOTE_ALL)
    exported.append({'platform': 'instagram', 'category': 'master', 'dataset_name': 'instagram_master', 'export_path': 'instagram/master/instagram_master.csv', 'source_path': 'data/final/instagram_posts_final.csv', 'primary_key': 'post_id', 'purpose': 'Canonical final Instagram post-level dataset.', 'rows': len(instagram_master), 'columns': len(instagram_master.columns), 'columns_list': list(instagram_master.columns)})
    source_map[FINAL / 'instagram_posts_final.csv'] = 'instagram/master/instagram_master.csv'
    source_map[FINAL / 'playstore_reviews_final.csv'] = 'playstore/master/playstore_master.csv'
    source_map[FINAL / 'playstore_gold_set_final.csv'] = 'playstore/master/playstore_master.csv'

    master = build_master()
    playstore_master_dir = EXPORT / 'playstore' / 'master'
    playstore_master_dir.mkdir(parents=True, exist_ok=True)
    master.to_csv(playstore_master_dir / 'playstore_master.csv', index=False, quoting=csv.QUOTE_ALL)
    write_workbook(playstore_master_dir / 'playstore_master.xlsx', {
        'Play Store Master': master,
        'Data Dictionary': pd.DataFrame([{'column_name': c, 'description': DESCRIPTIONS.get(c, 'Privacy-reduced canonical Play Store master field.'), 'dtype': str(master[c].dtype)} for c in master.columns]),
    })
    exported.append({'platform': 'playstore', 'category': 'master', 'dataset_name': 'playstore_master', 'export_path': 'playstore/master/playstore_master.csv', 'source_path': 'data/final/playstore_reviews_final.csv + data/final/playstore_gold_set_final.csv + data/final/topic_analysis/phase_5_3/review_aspect_assignments_remediated.csv', 'primary_key': 'review_id', 'purpose': 'Privacy-reduced master with human labels and canonical remediated aspects; excludes model predictions.', 'rows': len(master), 'columns': len(master.columns), 'columns_list': list(master.columns)})

    for platform, category, source, name, primary_key, purpose in REGISTRY[1:]:
        result = copy_pair(source, EXPORT / platform / category, name)
        exported.append({'platform': platform, 'category': category, 'dataset_name': name, 'source_path': source.relative_to(ROOT).as_posix(), 'primary_key': primary_key, 'purpose': purpose, **result})
        source_map[source] = result['export_path']

    taxonomy_path = FINAL / 'topic_analysis' / 'phase_5_3' / 'aspect_taxonomy_remediated.json'
    taxonomy = json.loads(taxonomy_path.read_text(encoding='utf-8'))
    taxonomy_frame = pd.DataFrame([{'aspect_id': value['aspect_id'], 'aspect_name': value['aspect_name'], 'description': value['description'], 'keywords_id': '; '.join(value['keywords_id']), 'keywords_en': '; '.join(value['keywords_en']), 'slang_variants': '; '.join(value['slang_variants']), 'inclusion_rules': value['inclusion_rules'], 'exclusion_and_ambiguity_notes': value['exclusion_and_ambiguity_notes']} for value in taxonomy.values()])
    taxonomy_dir = EXPORT / 'playstore' / 'aspects'
    taxonomy_frame.to_csv(taxonomy_dir / 'aspect_taxonomy_remediated.csv', index=False, quoting=csv.QUOTE_ALL)
    write_workbook(taxonomy_dir / 'aspect_taxonomy_remediated.xlsx', {'Aspect Taxonomy': taxonomy_frame})
    exported.append({'platform': 'playstore', 'category': 'aspects', 'dataset_name': 'aspect_taxonomy_remediated', 'export_path': 'playstore/aspects/aspect_taxonomy_remediated.csv', 'source_path': taxonomy_path.relative_to(ROOT).as_posix(), 'primary_key': 'aspect_id', 'purpose': 'Canonical eight-aspect remediated taxonomy and rules.', 'rows': len(taxonomy_frame), 'columns': len(taxonomy_frame.columns), 'columns_list': list(taxonomy_frame.columns)})
    source_map[taxonomy_path] = 'playstore/aspects/aspect_taxonomy_remediated.csv'

    integrity = pd.DataFrame([{'source_path': path.relative_to(ROOT).as_posix(), 'sha256': digest, 'purpose': 'Protected immutable source used by the analytical pipeline.'} for path, digest in initial_hashes.items()])
    integrity.to_csv(EXPORT / 'source_integrity_manifest.csv', index=False, quoting=csv.QUOTE_ALL)
    write_workbook(EXPORT / 'source_integrity_manifest.xlsx', {'Source Integrity': integrity})

    rows = []
    audit_paths = list((DATA / 'raw').rglob('*')) + list(FINAL.rglob('*')) + list((EXPORT / 'instagram').glob('*')) + list((EXPORT / 'playstore').glob('*'))
    seen = set()
    for path in sorted(audit_paths):
            if not path.is_file() or path.suffix.lower() not in {'.csv', '.xlsx', '.json'} or path in seen:
                continue
            seen.add(path)
            count_rows, count_columns, fields, kind = profile_file(path)
            status, reason = classify(path, source_map)
            rows.append({'file_name': path.name, 'source_path': path.relative_to(ROOT).as_posix(), 'platform': 'instagram' if 'instagram' in path.as_posix().lower() else ('playstore' if 'playstore' in path.as_posix().lower() or 'topic_analysis' in path.as_posix().lower() or 'sentiment_benchmark' in path.as_posix().lower() else 'cross_platform'), 'rows': count_rows, 'columns': count_columns, 'dataset_type': kind, 'period_or_scope': 'See source schema / analysis scope', 'primary_key': next((item['primary_key'] for item in exported if item['source_path'] == path.relative_to(ROOT).as_posix()), 'Not applicable or composite'), 'status': status, 'export_path': source_map.get(path, ''), 'decision_reason': reason, 'leading_columns': fields})
    inventory = pd.DataFrame(rows).sort_values(['platform', 'source_path']).reset_index(drop=True)
    inventory.to_csv(EXPORT / 'dataset_inventory.csv', index=False, quoting=csv.QUOTE_ALL)
    summary = pd.DataFrame(exported)[['platform', 'category', 'dataset_name', 'export_path', 'source_path', 'primary_key', 'purpose', 'rows', 'columns']]
    write_workbook(EXPORT / 'dataset_inventory.xlsx', {'Dataset Inventory': inventory, 'Export Summary': summary, 'Data Dictionary': pd.DataFrame([{'field': column, 'description': DESCRIPTIONS.get(column, 'Inventory metadata field.')} for column in inventory.columns])})

    dictionary_lines = ['# Zahir Social Analytics - Data Dictionary', '', '## Master Datasets', '', '| Dataset | Location | Rows | Columns | Primary Key | Purpose |', '| :--- | :--- | ---: | ---: | :--- | :--- |']
    for item in exported:
        dictionary_lines.append(f"| `{item['dataset_name']}` | `{item['export_path']}` | {item['rows']} | {item['columns']} | `{item['primary_key']}` | {item['purpose']} |")
    dictionary_lines.extend(['', '## Privacy and Modeling Rules', '', '- Play Store master exports exclude `userName`, `userImage`, `reviewer_id`, and developer reply text.', '- `human_sentiment_label` comes only from the human-annotated Gold Set.', '- Model outputs remain isolated in `playstore/sentiment/` and are populated only for benchmark test records.', '- Instagram `views` stays missing where the public web source does not expose it; no reach, impressions, or engagement-rate fields are fabricated.', ''])
    (EXPORT / 'README_data_dictionary.md').write_text('\n'.join(dictionary_lines), encoding='utf-8')

    relationships = '''# Dataset Relationships\n\n## Instagram\n\n- `instagram/master/instagram_master.csv` is the canonical post-level table (`post_id`, 55 unique records).\n- `instagram/engagement/instagram_engagement_metrics.csv` and `instagram/analysis/instagram_top_posts.csv` reference `post_id`.\n- Aggregate Instagram analysis files summarize the same 55-post master and do not add new post-level records.\n\n## Google Play Store\n\n- `playstore/master/playstore_master.csv` is the privacy-reduced review-level master (`review_id`, 417 unique records).\n- Human labels in the master originate from the canonical human-annotated Gold Set.\n- `playstore/aspects/playstore_aspect_assignments_remediated.csv` joins one-to-one on `review_id`; its aspect flags expand into multi-label mentions.\n- `playstore/sentiment/playstore_sentiment_all.csv` preserves the separation between `human_sentiment_label` and test-only `test_pred_*` model fields.\n- `playstore/sentiment/sentiment_test_predictions.csv` has 84 held-out review IDs; `sentiment_split_manifest.csv` records the 333 development and 84 test allocation.\n\n## Integrity\n\n- `source_integrity_manifest.csv` records SHA-256 checksums for immutable project sources.\n- CSV and XLSX pairs in the structured package represent the same table or workbook primary sheet.\n'''
    (EXPORT / 'dataset_relationships.md').write_text(relationships, encoding='utf-8')

    for path, digest in initial_hashes.items():
        if sha256(path) != digest:
            raise RuntimeError(f'Protected source changed during export: {path}')
    print(f'Phase 5.8 export complete: {len(exported)} datasets, {len(inventory)} inventoried source artifacts.')


if __name__ == '__main__':
    main()
