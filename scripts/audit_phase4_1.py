import re
from collections import Counter
import pandas as pd

df = pd.read_csv('data/final/playstore_reviews_final.csv')

print("="*60)
print("PHASE 4.1 DATASET AUDIT REPORT")
print("="*60)

# 1. Row and column counts
print(f"1. Total Rows: {len(df)}")
print(f"   Total Columns: {df.shape[1]}")
print(f"   Columns: {list(df.columns)}")

# 2. review_id uniqueness and completeness
null_ids = df['review_id'].isnull().sum()
unique_ids = df['review_id'].nunique()
print(f"\n2. review_id nulls: {null_ids}, unique IDs: {unique_ids} (Matches row count: {unique_ids == len(df)})")

# 3. review_text_clean missing/empty
null_text = df['review_text_clean'].isnull().sum()
empty_text = (df['review_text_clean'].astype(str).str.strip() == '').sum()
print(f"\n3. review_text_clean null count: {null_text}")
print(f"   review_text_clean empty/whitespace count: {empty_text}")

# 4. Distinct applications
apps = df['app_name'].value_counts()
print(f"\n4. Distinct Applications ({len(apps)} apps):")
for app, cnt in apps.items():
    print(f"   - {app}: {cnt} reviews ({cnt/len(df)*100:.2f}%)")

# 5. Rating distribution
ratings = df['score'].value_counts().sort_index()
print(f"\n5. Rating Score Distribution (1-5):")
for score, cnt in ratings.items():
    print(f"   - Score {score}: {cnt} reviews ({cnt/len(df)*100:.2f}%)")

# 6. Languages and Language Mixtures
# Lexicon based language audit
id_lexicon = {
    'yang', 'dan', 'di', 'ini', 'untuk', 'bisa', 'aplikasi', 'tidak', 'gak', 'nggak',
    'sangat', 'bagus', 'sudah', 'saya', 'ke', 'dengan', 'ada', 'mohon', 'update',
    'tolong', 'susah', 'bantu', 'masuk', 'error', 'bintang', 'terus', 'kenapa',
    'pas', 'login', 'nya', 'banget', 'mantap', 'keren', 'bermanfaat', 'makasih',
    'terima', 'kasih', 'baik', 'kecewa', 'sulit', 'rusak', 'lemot', 'ribet', 'gagal'
}
en_lexicon = {
    'the', 'and', 'is', 'for', 'to', 'good', 'very', 'nice', 'great', 'app',
    'not', 'it', 'easy', 'use', 'best', 'bad', 'please', 'help', 'awesome',
    'simple', 'helpful', 'useful', 'service', 'thanks', 'thank', 'you', 'fast',
    'cant', 'cannot', 'work', 'working', 'excellent', 'slow', 'fix', 'problem'
}

lang_class = []
for text in df['review_text_clean'].astype(str):
    tokens = set(re.findall(r'\b[a-zA-Z]{2,}\b', text.lower()))
    id_matches = tokens.intersection(id_lexicon)
    en_matches = tokens.intersection(en_lexicon)
    
    if len(id_matches) > 0 and len(en_matches) > 0:
        lang_class.append('mixed_id_en')
    elif len(id_matches) > 0:
        lang_class.append('indonesian')
    elif len(en_matches) > 0:
        lang_class.append('english')
    else:
        # short slang or single words like 'Sip', 'Top', 'Ok'
        lang_class.append('short_or_ambiguous')

df['lang_audit'] = lang_class
lang_counts = Counter(lang_class)
print(f"\n6. Language Classification Audit:")
for k, v in lang_counts.most_common():
    print(f"   - {k}: {v} reviews ({v/len(df)*100:.2f}%)")

# Inspect short/ambiguous
print("\n   Sample of short_or_ambiguous reviews:")
for t in df[df['lang_audit'] == 'short_or_ambiguous']['review_text_clean'].unique()[:10]:
    print(f"     * \"{t}\"")

# 7. Exact duplicates and near-duplicates
text_counts = df['review_text_clean'].value_counts()
exact_dups = text_counts[text_counts > 1]
print(f"\n7. Text Duplication Audit:")
print(f"   - Total unique text strings: {df['review_text_clean'].nunique()} out of {len(df)}")
print(f"   - Number of text strings appearing > 1 time: {len(exact_dups)} (covering {exact_dups.sum()} rows)")
for txt, cnt in exact_dups.items():
    print(f"     * \"{txt}\" : {cnt} occurrences")

# Check normalized text near-duplicates (lowercase, stripped punctuation)
df['norm_text'] = df['review_text_clean'].astype(str).str.lower().str.replace(r'[^\w\s]', '', regex=True).str.strip()
norm_counts = df['norm_text'].value_counts()
norm_dups = norm_counts[norm_counts > 1]
print(f"   - Normalized (lowercased, punctuation-removed) unique texts: {df['norm_text'].nunique()}")
print(f"   - Top normalized recurring texts:")
for txt, cnt in norm_dups.head(8).items():
    print(f"     * \"{txt}\" : {cnt} occurrences")

# 8. Privacy & Data Quality
print("\n8. Privacy & Data Quality Audit:")
print(f"   - Any userImage in final dataset? {'userImage' in df.columns}")
print(f"   - Any userName in final dataset? {'userName' in df.columns}")
print(f"   - Reviewer identity in final dataset: 'reviewer_id' (SHA-256 anonymized hash)")
print(f"   - Will gold set exclude 'reviewer_id'? Yes (as required).")
print(f"   - Min text length: {df['text_length_chars'].min()} chars")
print(f"   - Max text length: {df['text_length_chars'].max()} chars")
print(f"   - Median text length: {df['text_length_chars'].median()} chars")
print("="*60)
