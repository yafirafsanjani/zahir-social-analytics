"""
playstore_preprocessing.py
--------------------------
Modul preprocessing terstandar dan reproducible untuk dataset ulasan
Google Play Store ekosistem Zahir (Zahir Accounting).

Aturan pembersihan:
- Pembersihan teks konservatif (tidak menghapus negasi, emoji, stopwords, atau stemming).
- Privacy-reduced: URL avatar dan nama akun mentah dihilangkan, reviewer_id di-hash.
- Datetime processing: standardisasi ISO-8601, ekstraksi year/month/date, perhitungan response_time_days.
- Rating categorical mapping (1-2 critical, 3 neutral, 4-5 positive) tanpa mengasumsikan rating sebagai teks sentimen.
"""

import os
import re
import hashlib
import unicodedata
import pandas as pd
import numpy as np


def generate_reviewer_id(user_name: str, review_id: str) -> str:
    """
    Menghasilkan identifier reviewer anonim berbobot hash SHA-256 (16 karakter awal)
    untuk privasi data pengguna tanpa menghilangkan traceabilty.
    """
    combined = f"{str(user_name).strip()}::{str(review_id).strip()}".encode("utf-8")
    return hashlib.sha256(combined).hexdigest()[:16]


def clean_review_text(text: str) -> str:
    """
    Membersihkan teks ulasan secara konservatif:
    - Normalisasi unicode (NFKC)
    - Normalisasi whitespace berlebih dan baris baru
    - Menghilangkan URL dan karakter kontrol tak kasat mata
    - Menjaga emoji, tanda baca, huruf kapital, dan kata negasi (tidak, gak, dll.)
    """
    if not isinstance(text, str) or pd.isna(text):
        return ""

    # Normalisasi unicode (misal karakter gabungan atau varian ekspresi)
    cleaned = unicodedata.normalize("NFKC", text)

    # Menghapus karakter kontrol (ASCII 0-31 kecuali newline/tab yang akan dirapikan)
    cleaned = "".join(ch for ch in cleaned if unicodedata.category(ch)[0] != "C" or ch in "\n\t")

    # Menghapus URL jika ada
    cleaned = re.sub(r"https?://\S+|www\.\S+", "", cleaned)

    # Mengubah baris baru dan tab menjadi spasi tunggal
    cleaned = re.sub(r"[\r\n\t]+", " ", cleaned)

    # Normalisasi spasi ganda berturut-turut menjadi satu spasi
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned


def map_rating_category(score: int) -> str:
    """
    Mengelompokkan rating bintang menjadi kategori auxiliary berbasis skor:
    - 1-2: critical
    - 3: neutral
    - 4-5: positive

    Catatan metodologi: Variabel ini adalah kategori rating numerik,
    bukan klasifikasi sentimen berbasis teks ulasan.
    """
    try:
        val = int(score)
        if val in [1, 2]:
            return "critical"
        elif val == 3:
            return "neutral"
        elif val in [4, 5]:
            return "positive"
        else:
            return "unknown"
    except (ValueError, TypeError):
        return "unknown"


def preprocess_playstore_dataset(
    raw_path: str = "data/raw/playstore_reviews_raw.csv",
    output_path: str = "data/final/playstore_reviews_final.csv",
    save_output: bool = True
) -> pd.DataFrame:
    """
    Mengeksekusi pipeline preprocessing data ulasan Google Play Store.

    Parameters:
    -----------
    raw_path : str
        Path lokasi file mentah playstore_reviews_raw.csv.
    output_path : str
        Path target penyimpanan playstore_reviews_final.csv.
    save_output : bool
        Opsi penyimpanan otomatis ke CSV dengan standar encoding utf-8-sig.

    Returns:
    --------
    pd.DataFrame : Dataset hasil olahan siap analisis analitik.
    """
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"File raw dataset tidak ditemukan di: {raw_path}")

    df_raw = pd.read_csv(raw_path)
    df = df_raw.copy()

    # 1. Privacy-reduced Identifier
    df["reviewer_id"] = [
        generate_reviewer_id(un, rid)
        for un, rid in zip(df["userName"], df["reviewId"])
    ]

    # 2. Text Cleaning & Text-Quality Features
    df["review_text"] = df["content"].astype(str)
    df["review_text_clean"] = df["content"].apply(clean_review_text)

    # Fitur kualitas teks
    df["text_length_chars"] = df["review_text_clean"].str.len()
    df["word_count"] = df["review_text_clean"].apply(
        lambda x: len(x.split()) if len(x.strip()) > 0 else 0
    )

    # 3. Rating & Thumbs Up Features
    df["score"] = df["score"].astype(int)
    df["rating_category"] = df["score"].apply(map_rating_category)
    df["thumbs_up_count"] = df["thumbsUpCount"].fillna(0).astype(int)

    # 4. Datetime Transformations & Response Calculation
    df["review_datetime"] = pd.to_datetime(df["at"])
    df["review_date"] = df["review_datetime"].dt.strftime("%Y-%m-%d")
    df["review_year"] = df["review_datetime"].dt.year
    df["review_month"] = df["review_datetime"].dt.month

    # Developer response
    df["has_developer_reply"] = df["replyContent"].notna() & (
        df["replyContent"].astype(str).str.strip() != ""
    )
    df["reply_text"] = df["replyContent"]

    # Replied datetime parsing
    df["replied_datetime"] = pd.to_datetime(df["repliedAt"])

    # Response time calculation (dalam hari, desimal float)
    # Formula: (replied_datetime - review_datetime).total_seconds() / 86400
    time_diff_days = (
        (df["replied_datetime"] - df["review_datetime"]).dt.total_seconds() / 86400.0
    )
    df["response_time_days"] = np.where(df["has_developer_reply"], time_diff_days, np.nan)

    # 5. Application & Version Metadata
    # appVersion dan reviewCreatedVersion memiliki isi yang identik saat non-null (105 missing)
    # Kami mendokumentasikan kedua kolom agar data lineage versi aplikasi tetap lengkap
    df["app_name"] = df["app_name"].astype(str)
    df["package_name"] = df["package_name"].astype(str)
    df["app_version"] = df["appVersion"]
    df["review_created_version"] = df["reviewCreatedVersion"]

    # 6. Susun Skema Final yang Rapi & Terstandar (20 Kolom Analitik)
    final_cols = [
        "review_id",
        "reviewer_id",
        "review_datetime",
        "review_date",
        "review_year",
        "review_month",
        "review_text",
        "review_text_clean",
        "score",
        "rating_category",
        "thumbs_up_count",
        "has_developer_reply",
        "reply_text",
        "replied_datetime",
        "response_time_days",
        "app_name",
        "package_name",
        "review_created_version",
        "app_version",
        "text_length_chars",
        "word_count"
    ]

    # Mapping nama reviewId -> review_id
    df["review_id"] = df["reviewId"].astype(str)

    df_final = df[final_cols].copy()

    if save_output:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df_final.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"Dataset hasil preprocessing berhasil disimpan ke: {output_path}")

    return df_final


if __name__ == "__main__":
    df_result = preprocess_playstore_dataset()
    print("Shape hasil olahan:", df_result.shape)
    print("Kolom hasil olahan:", df_result.columns.tolist())
