import pandas as pd
import numpy as np

df = pd.read_csv('data/final/playstore_reviews_final.csv')

print('=== 1. TEMPORAL METRICS ===')
yearly = df.groupby('review_year').agg(
    count=('score', 'count'),
    mean_score=('score', 'mean'),
    median_score=('score', 'median'),
    critical=('rating_category', lambda s: (s=='critical').sum()),
    neutral=('rating_category', lambda s: (s=='neutral').sum()),
    positive=('rating_category', lambda s: (s=='positive').sum()),
    pct_critical=('rating_category', lambda s: (s=='critical').mean()*100),
    pct_neutral=('rating_category', lambda s: (s=='neutral').mean()*100),
    pct_positive=('rating_category', lambda s: (s=='positive').mean()*100)
).reset_index()
print(yearly.to_string(index=False))

print('\n=== 2. APPLICATION STATISTICS ===')
app_stats = []
for app in sorted(df['app_name'].unique()):
    sub = df[df['app_name'] == app]
    n = len(sub)
    crit = (sub['rating_category'] == 'critical').sum()
    neut = (sub['rating_category'] == 'neutral').sum()
    pos = (sub['rating_category'] == 'positive').sum()
    rep = sub['has_developer_reply'].sum()
    app_stats.append({
        'app_name': app,
        'review_count': n,
        'mean_score': round(sub['score'].mean(), 4),
        'median_score': sub['score'].median(),
        'critical_count': crit,
        'neutral_count': neut,
        'positive_count': pos,
        'critical_pct': round(crit / n * 100, 2),
        'neutral_pct': round(neut / n * 100, 2),
        'positive_pct': round(pos / n * 100, 2),
        'reply_count': rep,
        'reply_pct': round(rep / n * 100, 2)
    })
df_apps = pd.DataFrame(app_stats)
print(df_apps.to_string(index=False))

print('\n=== 3. RESPONSE RATE VALIDATION ===')
total_rev = len(df)
rep_total = df['has_developer_reply'].sum()
unrep_total = total_rev - rep_total
print(f'Overall: total={total_rev}, replied={rep_total} ({rep_total/total_rev*100:.2f}%), unreplied={unrep_total} ({unrep_total/total_rev*100:.2f}%)')

print('By rating category:')
for cat in ['critical', 'neutral', 'positive']:
    sub = df[df['rating_category'] == cat]
    n = len(sub)
    rep = sub['has_developer_reply'].sum()
    unrep = n - rep
    print(f'  {cat}: total={n}, replied={rep} ({rep/n*100:.2f}%), unreplied={unrep} ({unrep/n*100:.2f}%)')

print('By application:')
for app in sorted(df['app_name'].unique()):
    sub = df[df['app_name'] == app]
    n = len(sub)
    rep = sub['has_developer_reply'].sum()
    print(f'  {app}: total={n}, replied={rep} ({rep/n*100:.2f}%)')

print('\n=== 4. RESPONSE TIME VALIDATION ===')
rt_all = df['response_time_days'].dropna()
print(f'Total non-null: {len(rt_all)}')
neg = rt_all[rt_all < 0]
pos = rt_all[rt_all >= 0]
print(f'Negative count: {len(neg)}')
print(f'Non-negative count: {len(pos)}')
print('All response times:')
print(f'  min={rt_all.min():.6f}, max={rt_all.max():.6f}, mean={rt_all.mean():.6f}, median={rt_all.median():.6f}')
print('Non-negative subset (valid analysis subset):')
print(f'  min={pos.min():.6f}, max={pos.max():.6f}, mean={pos.mean():.6f}, median={pos.median():.6f}')
print(f'  Q1 (25%)={pos.quantile(0.25):.6f}, Q3 (75%)={pos.quantile(0.75):.6f}')

print('\n=== 5. REVIEW TEXT & ENGAGEMENT VALIDATION ===')
for cat in ['critical', 'neutral', 'positive']:
    sub = df[df['rating_category'] == cat]
    print(f'{cat}:')
    print('  text_length_chars: mean=' + str(round(sub['text_length_chars'].mean(), 2)) + ', median=' + str(round(sub['text_length_chars'].median(), 2)))
    print('  word_count: mean=' + str(round(sub['word_count'].mean(), 2)) + ', median=' + str(round(sub['word_count'].median(), 2)))
    print('  thumbs_up: mean=' + str(round(sub['thumbs_up_count'].mean(), 2)) + ', median=' + str(round(sub['thumbs_up_count'].median(), 2)) + ', max=' + str(sub['thumbs_up_count'].max()))

r_score = df['score'].rank()
r_text = df['text_length_chars'].rank()
r_word = df['word_count'].rank()
rho_text = r_score.corr(r_text)
rho_word = r_score.corr(r_word)
print(f'Spearman rho (score vs text_length_chars): {rho_text:.4f}')
print(f'Spearman rho (score vs word_count): {rho_word:.4f}')
