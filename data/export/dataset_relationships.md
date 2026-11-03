# Dataset Relationships

## Instagram

- `instagram/master/instagram_master.csv` is the canonical post-level table (`post_id`, 55 unique records).
- `instagram/engagement/instagram_engagement_metrics.csv` and `instagram/analysis/instagram_top_posts.csv` reference `post_id`.
- Aggregate Instagram analysis files summarize the same 55-post master and do not add new post-level records.

## Google Play Store

- `playstore/master/playstore_master.csv` is the privacy-reduced review-level master (`review_id`, 417 unique records).
- Human labels in the master originate from the canonical human-annotated Gold Set.
- `playstore/aspects/playstore_aspect_assignments_remediated.csv` joins one-to-one on `review_id`; its aspect flags expand into multi-label mentions.
- `playstore/sentiment/playstore_sentiment_all.csv` preserves the separation between `human_sentiment_label` and test-only `test_pred_*` model fields.
- `playstore/sentiment/sentiment_test_predictions.csv` has 84 held-out review IDs; `sentiment_split_manifest.csv` records the 333 development and 84 test allocation.

## Integrity

- `source_integrity_manifest.csv` records SHA-256 checksums for immutable project sources.
- CSV and XLSX pairs in the structured package represent the same table or workbook primary sheet.
