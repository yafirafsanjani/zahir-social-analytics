import pandas as pd
import re

df = pd.read_csv('data/final/topic_analysis/review_aspect_assignments.csv')

print('=== 1. ALL REVIEWS MATCHING login_auth WITH "akun" ===')
m_akun = df[df['matched_keywords'].str.contains(r'login_auth:\[[^\]]*\bakun\b', regex=True)]
for _, r in m_akun.iterrows():
    print(r['review_id'], '|', r['app_name'], '|', r['human_sentiment_label'])
    print(' ', r['review_text_clean'])
    print(' ', r['matched_keywords'])

print('\n=== 2. ALL REVIEWS MATCHING certification_exam WITH "nilai" ===')
m_nilai = df[df['matched_keywords'].str.contains(r'certification_exam:\[[^\]]*\bnilai\b', regex=True)]
for _, r in m_nilai.iterrows():
    print(r['review_id'], '|', r['app_name'], '|', r['human_sentiment_label'])
    print(' ', r['review_text_clean'])
    print(' ', r['matched_keywords'])

print('\n=== 3. ALL REVIEWS MATCHING attendance_face WITH "lokasi" or "jam kerja" or "foto" ===')
m_att = df[df['matched_keywords'].str.contains(r'attendance_face:\[[^\]]*\b(lokasi|jam kerja|foto)\b', regex=True)]
for _, r in m_att.iterrows():
    print(r['review_id'], '|', r['app_name'], '|', r['human_sentiment_label'])
    print(' ', r['review_text_clean'])
    print(' ', r['matched_keywords'])

print('\n=== 4. ALL REVIEWS MATCHING pos_hardware_print WITH "pos" ===')
m_pos = df[df['matched_keywords'].str.contains(r'pos_hardware_print:\[[^\]]*\bpos\b', regex=True)]
for _, r in m_pos.iterrows():
    print(r['review_id'], '|', r['app_name'], '|', r['human_sentiment_label'])
    print(' ', r['review_text_clean'])
    print(' ', r['matched_keywords'])

print('\n=== 5. ALL REVIEWS MATCHING inventory_accounting WITH "po" ===')
m_po = df[df['matched_keywords'].str.contains(r'inventory_accounting:\[[^\]]*\bpo\b', regex=True)]
for _, r in m_po.iterrows():
    print(r['review_id'], '|', r['app_name'], '|', r['human_sentiment_label'])
    print(' ', r['review_text_clean'])
    print(' ', r['matched_keywords'])
