import pandas as pd
import re

df_rev = pd.read_csv('data/final/playstore_reviews_final.csv')
df_gold = pd.read_csv('data/final/playstore_gold_set_final.csv')
df = df_rev.merge(df_gold[['review_id', 'human_sentiment_label']], on='review_id')

taxonomy_enriched = {
    'login_auth': [
        r'\blogin\b', r'\blog\s*in\b', r'\blog\s*out\b', r'\bmasuk\b', r'\bsign\s*in\b',
        r'\bsign\s*up\b', r'\bpassword\b', r'\bsandi\b', r'\botp\b', r'\bregistrasi\b',
        r'\bregister\b', r'\bdaftar\b', r'\bbuat\s*akun\b', r'\bbikin\s*akun\b',
        r'\bverifikasi\b', r'\blupa\s*(?:kata\s*)?sandi\b', r'\blupa\s*password\b',
        r'\bgagal\s*masuk\b', r'\btidak\s*bisa\s*masuk\b', r'\bsusah\s*masuk\b',
        r'\bsulit\s*masuk\b', r'\bnot\s*to\s*allowed\b', r'\buser\s*id\b',
        r'\bemail\s*sudah\s*terdaftar\b', r'\bakun\b'
    ],
    'crash_stability': [
        r'\bforce\s*close\b', r'\bfc\b', r'\bcrash\b', r'\bkeluar\s*sendiri\b',
        r'\bclose\s*sendiri\b', r'\bauto\s*close\b', r'\bmental\b', r'\blet?mot\b',
        r'\blambat\b', r'\blelet\b', r'\bngelag\b', r'\blag\b', r'\bhang\b',
        r'\bfreeze\b', r'\bmacet\b', r'\ber+or\b', r'\bbug\b', r'\bstuck\b',
        r'\bloading\s*(?:lama|terus)?\b', r'\bkeluar\s*terus\b'
    ],
    'pricing_subscription': [
        r'\bberbayar\b', r'\bbayar\b', r'\blangganan\b', r'\bberlangganan\b',
        r'\bsubscription\b', r'\btarif\b', r'\bharga\b', r'\bmahal\b',
        r'\bgratis+\b', r'\bfree\b', r'\btagihan\b', r'\bperpanjang(?:an)?\b',
        r'\bexpired\b', r'\bkadaluarsa\b', r'\btrial\b', r'\bmasa\s*aktif\b',
        r'\bbeli\b', r'\bbiaya\b'
    ],
    'sync_cloud_data': [
        r'\bsinkron(?:isasi)?\b', r'\bsync\b', r'\bcloud\b', r'\bdatabase\b',
        r'\bserver\b', r'\bdata\s*hilang\b', r'\bhilang\s*data(?:nya)?\b',
        r'\bdata\s*terhapus\b', r'\bdata\s*(?:tidak|gak|nggak)\s*tersimpan\b',
        r'\bgagal\s*simpan\b', r'\btidak\s*tersimpan\b', r'\bbackup\b',
        r'\brestore\b', r'\breal\s*time\b', r'\bsambung(?:an)?\s*server\b'
    ],
    'pos_hardware_print': [
        r'\bcetak\b', r'\bprint(?:er)?\b', r'\bstruk\b', r'\bnota\b', r'\bthermal\b',
        r'\bbluetooth\b', r'\bkasir\b', r'\bpos\b', r'\bbarcode\b', r'\bscanner\b',
        r'\blaci\b', r'\bdrawer\b', r'\breceipt\b'
    ],
    'inventory_accounting': [
        r'\bstok\b', r'\bstock\b', r'\bbarang\b', r'\bproduk\b', r'\binventory\b',
        r'\btransaksi\b', r'\blaporan\b', r'\binvoice\b', r'\bfaktur\b', r'\bhutang\b',
        r'\bpiutang\b', r'\bjurnal\b', r'\bneraca\b', r'\blaba\s*rugi\b', r'\bkeuangan\b',
        r'\bpembukuan\b', r'\bakuntansi\b', r'\baccounting\b', r'\bpenjualan\b',
        r'\bpembelian\b', r'\bpo\b'
    ],
    'certification_exam': [
        r'\bujian\b', r'\bsoal\b', r'\bsertifikasi\b', r'\bsertifikat\b',
        r'\bnilai\b', r'\bskor\b', r'\btes\b', r'\bexam\b', r'\bwaktu\s*ujian\b',
        r'\bujikom\b'
    ],
    'attendance_face': [
        r'\babsen(?:si)?\b', r'\bpresensi\b', r'\bwajah\b', r'\bface\b',
        r'\bselfie\b', r'\bfoto\b', r'\bkamera\b', r'\bgps\b', r'\blokasi\b',
        r'\bcheck\s*in\b', r'\bcheck\s*out\b', r'\bclock\s*in\b', r'\bjam\s*kerja\b'
    ]
}

aspect_matrix = pd.DataFrame(index=df.index)
for asp, pats in taxonomy_enriched.items():
    combined = '|'.join(pats)
    aspect_matrix[asp] = df['review_text_clean'].str.contains(combined, case=False, regex=True)

df['has_aspect'] = aspect_matrix.any(axis=1)

print('Enriched Aspect Coverage by Sentiment:')
for sent in ['negative', 'neutral', 'positive']:
    sub = df[df['human_sentiment_label'] == sent]
    has_asp = sub['has_aspect'].sum()
    pct = has_asp / len(sub) * 100
    print(f'{sent:<8}: {has_asp:>3} / {len(sub):>3} ({pct:5.2f}%)')

sub_b = df[df['human_sentiment_label'].isin(['negative', 'neutral'])]
pct_b = sub_b['has_aspect'].sum() / len(sub_b) * 100
print(f'Scope B (Negative + Neutral): {sub_b["has_aspect"].sum()} / {len(sub_b)} ({pct_b:.2f}%)')
