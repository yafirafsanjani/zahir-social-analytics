import pandas as pd
df = pd.read_csv('data/final/topic_analysis/review_aspect_assignments.csv')

print('=== REVIEWS MATCHING pricing_subscription WITH "beli" ===')
m_beli = df[df['matched_keywords'].str.contains(r'pricing_subscription:\[[^\]]*\bbeli\b', regex=True)]
print('Count:', len(m_beli))
for _, r in m_beli.iterrows():
    print(r['review_id'], '|', r['app_name'], '|', r['human_sentiment_label'])
    print('  Text:', r['review_text_clean'][:100])
    print('  Matched:', r['matched_keywords'])
