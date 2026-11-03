# Zahir Social Analytics - Data Dictionary

## Master Datasets

| Dataset | Location | Rows | Columns | Primary Key | Purpose |
| :--- | :--- | ---: | ---: | :--- | :--- |
| `instagram_master` | `instagram/master/instagram_master.csv` | 55 | 27 | `post_id` | Canonical final Instagram post-level dataset. |
| `playstore_master` | `playstore/master/playstore_master.csv` | 417 | 33 | `review_id` | Privacy-reduced master with human labels and canonical remediated aspects; excludes model predictions. |
| `instagram_engagement_metrics` | `instagram/engagement/instagram_engagement_metrics.csv` | 55 | 23 | `post_id` | Post-level engagement ranking, tiers, and outlier flags. |
| `instagram_engagement_summary` | `instagram/engagement/instagram_engagement_summary.csv` | 3 | 15 | `metric` | Overall engagement descriptive statistics. |
| `instagram_content_type_comparison` | `instagram/analysis/instagram_content_type_comparison.csv` | 4 | 24 | `content_type` | Content format performance comparison. |
| `instagram_collaboration_analysis` | `instagram/analysis/instagram_collaboration_analysis.csv` | 9 | 19 | `analysis_dimension + segment` | Collaboration and original-account performance analysis. |
| `instagram_posting_time_analysis` | `instagram/analysis/instagram_posting_time_analysis.csv` | 14 | 11 | `time_dimension + time_category` | Posting-day, hour, and time-bin analysis. |
| `instagram_caption_hashtag_analysis` | `instagram/analysis/instagram_caption_hashtag_analysis.csv` | 13 | 13 | `analysis_dimension + feature_category` | Caption and hashtag correlation and segment analysis. |
| `instagram_top_posts` | `instagram/analysis/instagram_top_posts.csv` | 20 | 16 | `tier + rank` | Top and bottom Instagram posts. |
| `instagram_data_quality_audit` | `instagram/analysis/instagram_data_quality_audit.csv` | 22 | 4 | `metric_dimension + metric_name` | Instagram preprocessing quality audit. |
| `instagram_content_performance` | `instagram/analysis/instagram_content_performance.csv` | 28 | 16 | `analysis_dimension + segment` | Unified Instagram performance overview. |
| `playstore_sentiment_all` | `playstore/sentiment/playstore_sentiment_all.csv` | 417 | 14 | `review_id` | Human-annotated Gold Set labels with test-only model predictions. |
| `sentiment_benchmark_metrics` | `playstore/sentiment/sentiment_benchmark_metrics.csv` | 4 | 18 | `model_name` | Held-out test benchmark metrics by model. |
| `sentiment_split_manifest` | `playstore/sentiment/sentiment_split_manifest.csv` | 417 | 5 | `review_id` | Development/test split membership for the benchmark. |
| `sentiment_test_predictions` | `playstore/sentiment/sentiment_test_predictions.csv` | 84 | 12 | `review_id` | Test-only model predictions and confidences. |
| `sentiment_error_analysis` | `playstore/sentiment/sentiment_error_analysis.csv` | 130 | 7 | `review_id + model_name` | Model error cases on benchmark evaluation. |
| `playstore_aspect_assignments_remediated` | `playstore/aspects/playstore_aspect_assignments_remediated.csv` | 417 | 17 | `review_id` | Canonical remediated eight-aspect assignments. |
| `aspect_summary_all_reviews` | `playstore/aspects/aspect_summary_all_reviews.csv` | 8 | 14 | `aspect_id` | All-review aspect distribution. |
| `aspect_summary_negative_neutral` | `playstore/aspects/aspect_summary_negative_neutral.csv` | 8 | 10 | `aspect_id` | Negative and neutral pain-point aspect summary. |
| `aspect_sentiment_comparison` | `playstore/aspects/aspect_sentiment_comparison.csv` | 8 | 9 | `aspect_id` | Aspect-level sentiment contrast. |
| `aspect_keyword_audit` | `playstore/aspects/aspect_keyword_audit.csv` | 193 | 6 | `keyword_or_pattern + assigned_aspect_id` | Keyword rule audit for aspect extraction. |
| `aspect_count_reconciliation` | `playstore/aspects/aspect_count_reconciliation.csv` | 22 | 8 | `category + metric_name` | Aspect mention reconciliation audit. |
| `aspect_quality_audit_summary` | `playstore/aspects/aspect_quality_audit_summary.csv` | 4 | 5 | `audit_dimension` | Aspect remediation quality summary. |
| `keyword_remediation_log` | `playstore/aspects/keyword_remediation_log.csv` | 16 | 12 | `log_id` | Applied keyword remediation log. |
| `keyword_rule_audit` | `playstore/aspects/keyword_rule_audit.csv` | 11 | 11 | `keyword_or_pattern + assigned_aspect_id` | Risk and rule audit before remediation. |
| `manual_validation_reconciliation` | `playstore/aspects/manual_validation_reconciliation.csv` | 16 | 6 | `metric_category + metric_name` | Manual validation reconciliation. |
| `manual_validation_results` | `playstore/aspects/manual_validation_results.csv` | 30 | 17 | `sample_id` | Manual validation results; audit-only sample. |
| `phase_5_3_quality_audit_summary` | `playstore/aspects/phase_5_3_quality_audit_summary.csv` | 15 | 8 | `audit_dimension + metric_or_aspect` | Phase 5.3 remediation evidence summary. |
| `playstore_missing_value_report` | `playstore/analysis/playstore_missing_value_report.csv` | 21 | 5 | `column` | Missing-value profile for the processed review dataset. |
| `text_quality_summary` | `playstore/analysis/text_quality_summary.csv` | 26 | 4 | `metric_category + metric_name` | Text-quality indicators for topic-analysis readiness. |
| `topic_readiness_audit` | `playstore/analysis/topic_readiness_audit.csv` | 6 | 6 | `evaluation_dimension + dimension_item` | Topic-analysis readiness assessment. |
| `topic_scope_comparison` | `playstore/analysis/topic_scope_comparison.csv` | 5 | 14 | `scope_name` | Analytical scope comparison. |
| `exploratory_clustering_assignments` | `playstore/analysis/exploratory_clustering_assignments.csv` | 185 | 7 | `review_id` | Exploratory clustering assignment for negative and neutral reviews. |
| `exploratory_clustering_summary` | `playstore/analysis/exploratory_clustering_summary.csv` | 4 | 6 | `num_clusters_k` | Exploratory clustering diagnostics. |
| `aspect_taxonomy_remediated` | `playstore/aspects/aspect_taxonomy_remediated.csv` | 8 | 8 | `aspect_id` | Canonical eight-aspect remediated taxonomy and rules. |

## Privacy and Modeling Rules

- Play Store master exports exclude `userName`, `userImage`, `reviewer_id`, and developer reply text.
- `human_sentiment_label` comes only from the human-annotated Gold Set.
- Model outputs remain isolated in `playstore/sentiment/` and are populated only for benchmark test records.
- Instagram `views` stays missing where the public web source does not expose it; no reach, impressions, or engagement-rate fields are fabricated.
