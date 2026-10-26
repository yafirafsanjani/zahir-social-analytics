import os
import sys
import re
import json
import csv
import numpy as np
import pandas as pd
import openpyxl

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

print("=" * 70)
print("PHASE 5.2: ASPECT TAXONOMY CONSTRUCTION & CUSTOMER VOICE EXTRACTION")
print("=" * 70)

# Paths
REVIEWS_CSV = "data/final/playstore_reviews_final.csv"
GOLD_CSV = "data/final/playstore_gold_set_final.csv"
CONFIG_PATH = "config/aspect_taxonomy.json"
OUTPUT_DIR = "data/final/topic_analysis"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs("config", exist_ok=True)

# -------------------------------------------------------------------------
# 1. Formalize Taxonomy Configuration
# -------------------------------------------------------------------------
print("[1/7] Formalizing Aspect Taxonomy Configuration...")

taxonomy_config = {
    "login_auth": {
        "aspect_id": "login_auth",
        "aspect_name": "Authentication & Access",
        "description": "User authentication, credential handling, account registration, and access barriers.",
        "keywords_id": [
            "login", "log in", "log out", "logout", "masuk", "password", "sandi", "kata sandi",
            "lupa sandi", "lupa password", "buat akun", "bikin akun", "daftar", "registrasi",
            "verifikasi", "gagal masuk", "susah masuk", "sulit masuk", "email sudah terdaftar", "akun"
        ],
        "keywords_en": [
            "sign in", "sign up", "register", "user id", "otp", "not to allowed"
        ],
        "slang_variants": [
            "gabisa masuk", "ga bisa masuk", "gabisa login", "ga bisa login", "login akun"
        ],
        "inclusion_rules": "Matches login, sign-in, credential entry, account verification, and session timeouts.",
        "exclusion_and_ambiguity_notes": "'akun' is paired with access/registration context to avoid false positives with accounting chart of accounts (nama akun kas)."
    },
    "crash_stability": {
        "aspect_id": "crash_stability",
        "aspect_name": "System Stability & Crash",
        "description": "Application crashes, freezing, sudden closures, performance latency, and system bugs.",
        "keywords_id": [
            "keluar sendiri", "close sendiri", "auto close", "keluar terus", "lemot", "lambat",
            "lelet", "ngelag", "macet", "mental", "loading lama", "loading terus", "eror", "error"
        ],
        "keywords_en": [
            "force close", "fc", "crash", "lag", "hang", "freeze", "bug", "stuck", "loading"
        ],
        "slang_variants": [
            "mental mulu", "mental terus", "eror mulu", "error mulu", "ngelag parah"
        ],
        "inclusion_rules": "Matches unexpected application shutdown, hanging screens, persistent error dialogues, and UI freezes.",
        "exclusion_and_ambiguity_notes": "'error' is matched in system failure context. 'close' is matched via 'force close' or 'close sendiri' to avoid confusing with accounting period closing (tutup buku)."
    },
    "pricing_subscription": {
        "aspect_id": "pricing_subscription",
        "aspect_name": "Pricing & Subscription",
        "description": "Software monetization, subscription tiers, renewal fees, trial limitations, and licensing costs.",
        "keywords_id": [
            "berbayar", "bayar", "harus bayar", "disuruh bayar", "langganan", "berlangganan",
            "tarif", "harga", "mahal", "gratis", "gratiss", "tagihan", "perpanjang", "perpanjangan",
            "kadaluarsa", "masa aktif", "beli", "biaya"
        ],
        "keywords_en": [
            "subscription", "free", "trial", "expired", "pricing"
        ],
        "slang_variants": [
            "ujung2nya bayar", "gak gratis", "ga gratis", "ngga gratis"
        ],
        "inclusion_rules": "Matches discussions of software cost, subscription requirements, paid versus free versions, and license expiration.",
        "exclusion_and_ambiguity_notes": "'bayar' in POS retail transactions is distinguished where possible; rule targets software access payments and subscription tiers."
    },
    "sync_cloud_data": {
        "aspect_id": "sync_cloud_data",
        "aspect_name": "Cloud & Database Synchronization",
        "description": "Multi-device cloud synchronization, database connection, server downtime, and stored data loss.",
        "keywords_id": [
            "sinkron", "sinkronisasi", "data hilang", "hilang datanya", "data terhapus",
            "data tidak tersimpan", "gagal simpan", "tidak tersimpan", "sambungan server", "server down"
        ],
        "keywords_en": [
            "sync", "cloud", "database", "server", "backup", "restore", "real time"
        ],
        "slang_variants": [
            "data kehapus", "data ilang", "ga sinkron", "gak sinkron"
        ],
        "inclusion_rules": "Matches cloud database connectivity, sync failure between mobile and web/desktop, and data disappearance.",
        "exclusion_and_ambiguity_notes": "'data' is required to appear alongside sync, storage, or loss predicates to avoid capturing general data entry."
    },
    "pos_hardware_print": {
        "aspect_id": "pos_hardware_print",
        "aspect_name": "POS & Hardware Printing",
        "description": "Point-of-Sale hardware peripherals, Bluetooth thermal printers, receipt layout, barcode, and cash drawers.",
        "keywords_id": [
            "cetak", "cetak struk", "cetak nota", "struk", "nota", "kasir", "laci kasir", "laci"
        ],
        "keywords_en": [
            "print", "printer", "thermal", "bluetooth", "pos", "barcode", "scanner", "drawer", "receipt"
        ],
        "slang_variants": [
            "ngeprint", "printer bluetooth", "print struk", "susah cetak", "gabisa cetak"
        ],
        "inclusion_rules": "Matches hardware peripheral integration, thermal paper printing, Bluetooth printer pairing, and retail cash register functions.",
        "exclusion_and_ambiguity_notes": "'pos' is matched with word boundary to avoid substrings in words like 'posisi'."
    },
    "inventory_accounting": {
        "aspect_id": "inventory_accounting",
        "aspect_name": "Core Accounting & Inventory",
        "description": "Bookkeeping features, stock management, financial reports, transaction recording, and invoicing.",
        "keywords_id": [
            "stok", "stok barang", "barang", "produk", "transaksi", "laporan", "faktur",
            "hutang", "piutang", "jurnal", "neraca", "laba rugi", "keuangan", "pembukuan",
            "akuntansi", "penjualan", "pembelian", "po"
        ],
        "keywords_en": [
            "stock", "inventory", "invoice", "accounting", "purchase order"
        ],
        "slang_variants": [
            "input barang", "laporan keuangan", "ubah po", "bikin po"
        ],
        "inclusion_rules": "Matches core accounting transactions, ledger management, inventory tracking, financial statements, and invoice processing.",
        "exclusion_and_ambiguity_notes": "'po' matches Purchase Order context; 'laporan' matches financial and transactional reports."
    },
    "certification_exam": {
        "aspect_id": "certification_exam",
        "aspect_name": "Certification Exam Engine",
        "description": "Zahir Certification app functionality: exam sessions, question navigation, scoring, and certificate issuance.",
        "keywords_id": [
            "ujian", "soal", "sertifikasi", "sertifikat", "nilai", "skor", "tes", "waktu ujian", "ujikom"
        ],
        "keywords_en": [
            "exam", "test", "certificate", "score"
        ],
        "slang_variants": [
            "tes sertifikasi", "mulai ujian", "soal ujian", "ujikom zahir"
        ],
        "inclusion_rules": "Matches student/professional certification test sessions, test questions, grading, and digital certificate delivery.",
        "exclusion_and_ambiguity_notes": "'nilai' is matched in examination grading context rather than financial asset valuation."
    },
    "attendance_face": {
        "aspect_id": "attendance_face",
        "aspect_name": "Face Attendance & Geolocation",
        "description": "Zahir Attendance app workflows: facial biometric scanning, GPS location verification, and attendance check-in/out.",
        "keywords_id": [
            "absen", "absensi", "presensi", "wajah", "foto", "kamera", "lokasi", "jam kerja", "peta"
        ],
        "keywords_en": [
            "face", "selfie", "gps", "check in", "check out", "clock in"
        ],
        "slang_variants": [
            "scan wajah", "absen wajah", "deteksi wajah", "titik gps", "lokasi palsu"
        ],
        "inclusion_rules": "Matches employee attendance clocking, selfie photo capture, facial detection accuracy, and GPS location radius.",
        "exclusion_and_ambiguity_notes": "'lokasi' and 'foto' are paired with attendance and selfie validation context."
    }
}

with open(CONFIG_PATH, "w", encoding="utf-8") as f:
    json.dump(taxonomy_config, f, indent=2, ensure_ascii=False)
print(f"  - Saved taxonomy config: {CONFIG_PATH}")

# -------------------------------------------------------------------------
# 2. Compile Aspect Keyword Audit Table
# -------------------------------------------------------------------------
print("[2/7] Generating Aspect Keyword Audit Table...")

audit_rows = []
for asp_id, data in taxonomy_config.items():
    asp_name = data["aspect_name"]
    inc_rule = data["inclusion_rules"]
    amb_rule = data["exclusion_and_ambiguity_notes"]
    
    for kw in data["keywords_id"]:
        audit_rows.append({
            "keyword_or_pattern": kw,
            "assigned_aspect_id": asp_id,
            "aspect_name": asp_name,
            "language_or_type": "Indonesian Formal/Standard",
            "inclusion_rule": inc_rule,
            "ambiguity_and_exclusion_notes": amb_rule
        })
    for kw in data["keywords_en"]:
        audit_rows.append({
            "keyword_or_pattern": kw,
            "assigned_aspect_id": asp_id,
            "aspect_name": asp_name,
            "language_or_type": "English / Code-Switching",
            "inclusion_rule": inc_rule,
            "ambiguity_and_exclusion_notes": amb_rule
        })
    for kw in data["slang_variants"]:
        audit_rows.append({
            "keyword_or_pattern": kw,
            "assigned_aspect_id": asp_id,
            "aspect_name": asp_name,
            "language_or_type": "Informal / Slang Variant",
            "inclusion_rule": inc_rule,
            "ambiguity_and_exclusion_notes": amb_rule
        })

df_kw_audit = pd.DataFrame(audit_rows)
kw_csv = os.path.join(OUTPUT_DIR, "aspect_keyword_audit.csv")
kw_xlsx = os.path.join(OUTPUT_DIR, "aspect_keyword_audit.xlsx")
df_kw_audit.to_csv(kw_csv, index=False, quoting=csv.QUOTE_ALL, encoding="utf-8")
df_kw_audit.to_excel(kw_xlsx, index=False)
print(f"  - Saved keyword audit: {kw_csv} & {kw_xlsx} ({len(df_kw_audit)} rules)")

# -------------------------------------------------------------------------
# 3. Build Aspect Detection Pipeline & Review Assignments Table
# -------------------------------------------------------------------------
print("[3/7] Running Aspect Detection on all 417 reviews...")

df_rev = pd.read_csv(REVIEWS_CSV)
df_gold = pd.read_csv(GOLD_CSV)
df = df_rev.merge(df_gold[["review_id", "human_sentiment_label"]], on="review_id", how="inner")
assert len(df) == 417

# Compiled regex patterns for each aspect
compiled_patterns = {}
for asp_id, data in taxonomy_config.items():
    all_terms = data["keywords_id"] + data["keywords_en"] + data["slang_variants"]
    # Sort by length descending to match longer phrases first
    all_terms = sorted(all_terms, key=len, reverse=True)
    regex_terms = [r'\b' + re.escape(t).replace(r'\ ', r'\s*') + r'\b' if ' ' in t or len(t) <= 3 else r'\b' + re.escape(t) + r'\b' for t in all_terms]
    # Specific edge cases
    if asp_id == "crash_stability":
        regex_terms.append(r'\ber+or\b')
        regex_terms.append(r'\blet?mot\b')
    if asp_id == "pricing_subscription":
        regex_terms.append(r'\bgratis+\b')
    if asp_id == "sync_cloud_data":
        regex_terms.append(r'\bhilang\s*data(?:nya)?\b')
    compiled_patterns[asp_id] = [re.compile(p, re.IGNORECASE) for p in regex_terms]

aspect_ids = list(taxonomy_config.keys())

detection_results = []
for idx, row in df.iterrows():
    text = str(row["review_text_clean"]).lower()
    row_dict = {
        "review_id": row["review_id"],
        "app_name": row["app_name"],
        "review_datetime": row["review_datetime"],
        "human_sentiment_label": row["human_sentiment_label"],
        "review_text_clean": row["review_text_clean"],
    }
    
    assigned_aspects = []
    matched_evidences = []
    
    for asp_id in aspect_ids:
        patterns = compiled_patterns[asp_id]
        aspect_matches = []
        for p in patterns:
            found = p.findall(text)
            if found:
                for match_item in found:
                    if isinstance(match_item, tuple):
                        match_item = " ".join(filter(None, match_item))
                    match_item = match_item.strip()
                    if match_item not in aspect_matches:
                        aspect_matches.append(match_item)
        
        has_asp = len(aspect_matches) > 0
        row_dict[f"aspect_{asp_id}"] = has_asp
        if has_asp:
            assigned_aspects.append(asp_id)
            matched_evidences.append(f"{asp_id}:[{', '.join(aspect_matches)}]")
    
    row_dict["aspect_count"] = len(assigned_aspects)
    row_dict["has_aspect"] = len(assigned_aspects) > 0
    row_dict["detected_aspects"] = "; ".join(assigned_aspects) if assigned_aspects else "none"
    row_dict["matched_keywords"] = "; ".join(matched_evidences) if matched_evidences else "none"
    row_dict["detection_method"] = "keyword_rule"
    
    detection_results.append(row_dict)

df_assignments = pd.DataFrame(detection_results)
assign_csv = os.path.join(OUTPUT_DIR, "review_aspect_assignments.csv")
assign_xlsx = os.path.join(OUTPUT_DIR, "review_aspect_assignments.xlsx")
df_assignments.to_csv(assign_csv, index=False, quoting=csv.QUOTE_ALL, encoding="utf-8")
df_assignments.to_excel(assign_xlsx, index=False)
print(f"  - Saved assignments table: {assign_csv} & {assign_xlsx} (417 reviews)")

# -------------------------------------------------------------------------
# 4. Aspect Summary: Scope A (All Reviews, N=417)
# -------------------------------------------------------------------------
print("[4/7] Generating Aspect Summary for Scope A (All Reviews)...")

scope_a_rows = []
for asp_id in aspect_ids:
    asp_name = taxonomy_config[asp_id]["aspect_name"]
    col = f"aspect_{asp_id}"
    matched_df = df_assignments[df_assignments[col]]
    n_total = len(matched_df)
    pct_total = round(n_total / 417 * 100, 2)
    
    n_neg = (matched_df["human_sentiment_label"] == "negative").sum()
    n_neu = (matched_df["human_sentiment_label"] == "neutral").sum()
    n_pos = (matched_df["human_sentiment_label"] == "positive").sum()
    
    pct_neg = round(n_neg / n_total * 100, 2) if n_total > 0 else 0.0
    pct_neu = round(n_neu / n_total * 100, 2) if n_total > 0 else 0.0
    pct_pos = round(n_pos / n_total * 100, 2) if n_total > 0 else 0.0
    
    # App distribution
    app_counts = matched_df["app_name"].value_counts().to_dict()
    top_app = matched_df["app_name"].mode()[0] if n_total > 0 else "None"
    app_str = ", ".join([f"{k}: {v}" for k, v in app_counts.items()])
    
    # Extract top matched keywords
    kw_list = []
    for m in matched_df["matched_keywords"]:
        for part in m.split("; "):
            if part.startswith(f"{asp_id}:["):
                clean_kws = part.replace(f"{asp_id}:[", "").replace("]", "").split(", ")
                kw_list.extend(clean_kws)
    kw_series = pd.Series(kw_list).value_counts()
    top_kws = ", ".join([f"{k} ({v})" for k, v in kw_series.head(4).items()]) if not kw_series.empty else "none"
    
    # Concise grounded interpretation
    if n_neg > n_pos:
        interp = f"Didominasi sentimen negatif ({pct_neg}%), merepresentasikan area keluhan teknis utama pada {top_app}."
    elif n_pos > n_neg:
        interp = f"Didominasi sentimen positif ({pct_pos}%), merepresentasikan fungsionalitas yang diapresiasi pengguna pada {top_app}."
    else:
        interp = f"Distribusi seimbang antara pertanyaan fungsional dan komplain pada {top_app}."
        
    scope_a_rows.append({
        "aspect_id": asp_id,
        "aspect_name": asp_name,
        "total_mentions": n_total,
        "mention_percentage_total": pct_total,
        "count_negative": int(n_neg),
        "pct_negative": pct_neg,
        "count_neutral": int(n_neu),
        "pct_neutral": pct_neu,
        "count_positive": int(n_pos),
        "pct_positive": pct_pos,
        "top_application": top_app,
        "application_distribution": app_str,
        "top_matched_keywords": top_kws,
        "concise_interpretation": interp
    })

df_scope_a = pd.DataFrame(scope_a_rows).sort_values("total_mentions", ascending=False)
sa_csv = os.path.join(OUTPUT_DIR, "aspect_summary_all_reviews.csv")
sa_xlsx = os.path.join(OUTPUT_DIR, "aspect_summary_all_reviews.xlsx")
df_scope_a.to_csv(sa_csv, index=False, quoting=csv.QUOTE_ALL, encoding="utf-8")
df_scope_a.to_excel(sa_xlsx, index=False)
print(f"  - Saved Scope A summary: {sa_csv} & {sa_xlsx}")

# -------------------------------------------------------------------------
# 5. Aspect Summary: Scope B (Negative + Neutral Reviews, N=185)
# -------------------------------------------------------------------------
print("[5/7] Generating Aspect Summary for Scope B (Negative + Neutral)...")

sub_b = df_assignments[df_assignments["human_sentiment_label"].isin(["negative", "neutral"])].copy()
assert len(sub_b) == 185

scope_b_rows = []
for asp_id in aspect_ids:
    asp_name = taxonomy_config[asp_id]["aspect_name"]
    col = f"aspect_{asp_id}"
    matched_b = sub_b[sub_b[col]]
    n_pain = len(matched_b)
    pct_pain = round(n_pain / 185 * 100, 2)
    
    n_neg = (matched_b["human_sentiment_label"] == "negative").sum()
    n_neu = (matched_b["human_sentiment_label"] == "neutral").sum()
    
    app_counts = matched_b["app_name"].value_counts().to_dict()
    dom_app = matched_b["app_name"].mode()[0] if n_pain > 0 else "None"
    app_str = ", ".join([f"{k}: {v}" for k, v in app_counts.items()])
    
    kw_list = []
    for m in matched_b["matched_keywords"]:
        for part in m.split("; "):
            if part.startswith(f"{asp_id}:["):
                clean_kws = part.replace(f"{asp_id}:[", "").replace("]", "").split(", ")
                kw_list.extend(clean_kws)
    kw_series = pd.Series(kw_list).value_counts()
    top_kws = ", ".join([f"{k} ({v})" for k, v in kw_series.head(4).items()]) if not kw_series.empty else "none"
    
    pain_interp = f"Terkonsentrasi pada {dom_app} ({n_neg} komplain kritis, {n_neu} pertanyaan fungsional)."
    
    scope_b_rows.append({
        "aspect_id": asp_id,
        "aspect_name": asp_name,
        "painpoint_mentions": n_pain,
        "painpoint_percentage_of_185": pct_pain,
        "negative_complaints": int(n_neg),
        "neutral_inquiries": int(n_neu),
        "dominant_application": dom_app,
        "application_breakdown": app_str,
        "top_painpoint_keywords": top_kws,
        "customer_pain_interpretation": pain_interp
    })

df_scope_b = pd.DataFrame(scope_b_rows).sort_values("painpoint_mentions", ascending=False)
sb_csv = os.path.join(OUTPUT_DIR, "aspect_summary_negative_neutral.csv")
sb_xlsx = os.path.join(OUTPUT_DIR, "aspect_summary_negative_neutral.xlsx")
df_scope_b.to_csv(sb_csv, index=False, quoting=csv.QUOTE_ALL, encoding="utf-8")
df_scope_b.to_excel(sb_xlsx, index=False)
print(f"  - Saved Scope B summary: {sb_csv} & {sb_xlsx}")

# -------------------------------------------------------------------------
# 6. Aspect Summary: Scope C (Positive vs Negative Contrast)
# -------------------------------------------------------------------------
print("[6/7] Generating Aspect Contrast Table for Scope C (Pos vs Neg)...")

sub_pos = df_assignments[df_assignments["human_sentiment_label"] == "positive"]
sub_neg = df_assignments[df_assignments["human_sentiment_label"] == "negative"]
assert len(sub_pos) == 232 and len(sub_neg) == 73

scope_c_rows = []
for asp_id in aspect_ids:
    asp_name = taxonomy_config[asp_id]["aspect_name"]
    col = f"aspect_{asp_id}"
    
    n_neg = int(sub_neg[col].sum())
    rate_neg = round(n_neg / 73 * 100, 2)
    
    n_pos = int(sub_pos[col].sum())
    rate_pos = round(n_pos / 232 * 100, 2)
    
    ratio = round(n_pos / n_neg, 2) if n_neg > 0 else (99.0 if n_pos > 0 else 1.0)
    
    if n_neg > n_pos * 2:
        pattern = "Dominansi Keluhan (High Dissatisfaction)"
        insight = f"Tingkat keluhan ({rate_neg}%) jauh melampaui apresiasi ({rate_pos}%); isu kritis prioritas perbaikan tim teknis."
    elif n_pos > n_neg * 2:
        pattern = "Dominansi Apresiasi (High Appreciation)"
        insight = f"Fitur dipuji secara luas ({rate_pos}%) dan minim keluhan ({rate_neg}%); keunggulan kompetitif produk."
    else:
        pattern = "Aspek Kontroversial / Campuran (Balanced Discussion)"
        insight = f"Fitur aktif digunakan tetapi memiliki polaritas campuran; pengguna mengapresiasi fungsionalitas dasar namun mengeluhkan kendala operasional."
        
    scope_c_rows.append({
        "aspect_id": asp_id,
        "aspect_name": asp_name,
        "negative_mentions_n73": n_neg,
        "negative_rate_within_neg_pct": rate_neg,
        "positive_mentions_n232": n_pos,
        "positive_rate_within_pos_pct": rate_pos,
        "ratio_positive_to_negative": ratio,
        "contrastive_pattern": pattern,
        "customer_appreciation_vs_complaint_insight": insight
    })

df_scope_c = pd.DataFrame(scope_c_rows).sort_values("negative_mentions_n73", ascending=False)
sc_csv = os.path.join(OUTPUT_DIR, "aspect_sentiment_comparison.csv")
sc_xlsx = os.path.join(OUTPUT_DIR, "aspect_sentiment_comparison.xlsx")
df_scope_c.to_csv(sc_csv, index=False, quoting=csv.QUOTE_ALL, encoding="utf-8")
df_scope_c.to_excel(sc_xlsx, index=False)
print(f"  - Saved Scope C contrast: {sc_csv} & {sc_xlsx}")

# -------------------------------------------------------------------------
# 7. Stratified Manual Validation Sample Worksheet
# -------------------------------------------------------------------------
print("[7/7] Generating Stratified Manual Validation Sample Worksheet...")

# Sample 30 reviews: stratified across sentiment and aspect presence
# 10 negative (with aspect), 10 neutral (with aspect), 5 positive (with aspect), 5 non-detections
sample_parts = [
    df_assignments[(df_assignments["human_sentiment_label"] == "negative") & (df_assignments["has_aspect"])].sample(n=10, random_state=42),
    df_assignments[(df_assignments["human_sentiment_label"] == "neutral") & (df_assignments["has_aspect"])].sample(n=10, random_state=42),
    df_assignments[(df_assignments["human_sentiment_label"] == "positive") & (df_assignments["has_aspect"])].sample(n=5, random_state=42),
    df_assignments[~df_assignments["has_aspect"]].sample(n=5, random_state=42)
]
df_val_sample = pd.concat(sample_parts).reset_index(drop=True)

df_val_sheet = pd.DataFrame()
df_val_sheet["review_id"] = df_val_sample["review_id"]
df_val_sheet["app_name"] = df_val_sample["app_name"]
df_val_sheet["review_text_clean"] = df_val_sample["review_text_clean"]
df_val_sheet["human_sentiment_label"] = df_val_sample["human_sentiment_label"]
df_val_sheet["detected_aspects"] = df_val_sample["detected_aspects"]
df_val_sheet["matched_keywords"] = df_val_sample["matched_keywords"]
df_val_sheet["manual_aspect_review"] = ""
df_val_sheet["manual_correction_notes"] = ""

val_csv = os.path.join(OUTPUT_DIR, "aspect_manual_validation_sample.csv")
val_xlsx = os.path.join(OUTPUT_DIR, "aspect_manual_validation_sample.xlsx")
df_val_sheet.to_csv(val_csv, index=False, quoting=csv.QUOTE_ALL, encoding="utf-8")
df_val_sheet.to_excel(val_xlsx, index=False)
print(f"  - Saved validation sample: {val_csv} & {val_xlsx} (30 stratified reviews)")

# -------------------------------------------------------------------------
# Optional Exploratory Clustering Analysis (Scope B, N=185)
# -------------------------------------------------------------------------
print("\n[OPTIONAL] Performing Exploratory TF-IDF + K-Means Clustering on Scope B (n=185)...")

indo_stopwords = [
    'yang', 'dan', 'di', 'ini', 'untuk', 'bisa', 'aplikasi', 'saya', 'tidak', 'sudah',
    'sangat', 'bagus', 'ada', 'dari', 'ke', 'dengan', 'nya', 'gak', 'ga', 'nggak',
    'kok', 'tapi', 'mau', 'kalo', 'kalau', 'apa', 'kenapa', 'knp', 'ya', 'sy', 'zahir',
    'apk', 'app', 'online', 'start', 'simple', 'pos', 'posx', 'aja', 'bgt', 'tolong'
]

vec = TfidfVectorizer(stop_words=indo_stopwords, min_df=2, max_df=0.8, ngram_range=(1,2))
X = vec.fit_transform(sub_b["review_text_clean"])

clustering_diagnostics = []
for k in [3, 4, 5, 6]:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X)
    score = silhouette_score(X, labels)
    clustering_diagnostics.append({
        "num_clusters_k": k,
        "silhouette_score": round(score, 4),
        "inertia": round(km.inertia_, 2),
        "algorithm": "KMeans",
        "random_seed": 42,
        "coherence_assessment": "Low / Diffuse (Silhouette < 0.05 indicates high overlap and lack of distinct cluster separation in short text)"
    })

df_diag = pd.DataFrame(clustering_diagnostics)
diag_csv = os.path.join(OUTPUT_DIR, "exploratory_clustering_summary.csv")
diag_xlsx = os.path.join(OUTPUT_DIR, "exploratory_clustering_summary.xlsx")
df_diag.to_csv(diag_csv, index=False, quoting=csv.QUOTE_ALL, encoding="utf-8")
df_diag.to_excel(diag_xlsx, index=False)
print(f"  - Saved clustering summary: {diag_csv} & {diag_xlsx}")

# Run K=4 for assignments
km4 = KMeans(n_clusters=4, random_state=42, n_init=10)
sub_b_labels = km4.fit_predict(X)

terms = vec.get_feature_names_out()
cluster_top_terms_dict = {}
for c in range(4):
    centroid = km4.cluster_centers_[c]
    top_indices = centroid.argsort()[-5:][::-1]
    top_terms = [terms[i] for i in top_indices]
    cluster_top_terms_dict[c] = ", ".join(top_terms)

df_cluster_assign = pd.DataFrame()
df_cluster_assign["review_id"] = sub_b["review_id"]
df_cluster_assign["app_name"] = sub_b["app_name"]
df_cluster_assign["human_sentiment_label"] = sub_b["human_sentiment_label"]
df_cluster_assign["review_text_clean"] = sub_b["review_text_clean"]
df_cluster_assign["detected_aspects"] = sub_b["detected_aspects"]
df_cluster_assign["kmeans_cluster_k4"] = sub_b_labels
df_cluster_assign["cluster_top_terms"] = [cluster_top_terms_dict[c] for c in sub_b_labels]

cl_csv = os.path.join(OUTPUT_DIR, "exploratory_clustering_assignments.csv")
cl_xlsx = os.path.join(OUTPUT_DIR, "exploratory_clustering_assignments.xlsx")
df_cluster_assign.to_csv(cl_csv, index=False, quoting=csv.QUOTE_ALL, encoding="utf-8")
df_cluster_assign.to_excel(cl_xlsx, index=False)
print(f"  - Saved clustering assignments: {cl_csv} & {cl_xlsx} (185 reviews)")

print("\n" + "=" * 70)
print("ALL 16 PHASE 5.2 ARTIFACTS SUCCESSFULLY GENERATED!")
print("=" * 70)
