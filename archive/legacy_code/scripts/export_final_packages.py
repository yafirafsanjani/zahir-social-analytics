# -*- coding: utf-8 -*-
"""
export_final_packages.py
-------------------------
Pipeline Ekspor & Pengemasan Dataset Final Zahir Social Analytics (Fase 5.6).

Tujuan:
Menyiapkan paket dataset final Play Store dan Instagram yang bersih, terstruktur,
terdokumentasi, serta siap digunakan pada repository dashboard terpisah.

Folder Output:
- data/export/instagram/
- data/export/playstore/
"""

import os
import sys
import pandas as pd
import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FINAL_DIR = os.path.join(BASE_DIR, "data", "final")
EXPORT_DIR = os.path.join(BASE_DIR, "data", "export")
EXPORT_IG_DIR = os.path.join(EXPORT_DIR, "instagram")
EXPORT_PS_DIR = os.path.join(EXPORT_DIR, "playstore")


def style_worksheet(ws, header_bg="1F4E78"):
    """Menerapkan styling openpyxl profesional pada worksheet."""
    header_fill = PatternFill(start_color=header_bg, end_color=header_bg, fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    zebra_fill = PatternFill(start_color="F9FAFB", end_color="F9FAFB", fill_type="solid")
    regular_font = Font(name="Calibri", size=10)
    
    thin_border = Border(
        left=Side(style='thin', color='E5E7EB'),
        right=Side(style='thin', color='E5E7EB'),
        top=Side(style='thin', color='E5E7EB'),
        bottom=Side(style='thin', color='E5E7EB')
    )
    
    ws.row_dimensions[1].height = 24
    
    # Format header baris 1
    for col_idx in range(1, ws.max_column + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border
        
    # Format data
    for row_idx in range(2, ws.max_row + 1):
        ws.row_dimensions[row_idx].height = 20
        is_even = (row_idx % 2 == 0)
        for col_idx in range(1, ws.max_column + 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.font = regular_font
            cell.border = thin_border
            if is_even:
                cell.fill = zebra_fill
                
            val = cell.value
            if isinstance(val, (int, np.integer)):
                cell.alignment = Alignment(horizontal="right", vertical="center")
                cell.number_format = '#,##0'
            elif isinstance(val, (float, np.floating)):
                cell.alignment = Alignment(horizontal="right", vertical="center")
                if abs(val) < 0.01 and val != 0:
                    cell.number_format = '0.0000'
                elif abs(val) >= 1000:
                    cell.number_format = '#,##0.00'
                else:
                    cell.number_format = '0.00'
            elif isinstance(val, bool):
                cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")

    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            if cell.value is not None:
                val_str = str(cell.value)
                if len(val_str) > max_len:
                    max_len = len(val_str)
        adjusted_width = max(max_len + 4, 12)
        ws.column_dimensions[col_letter].width = min(adjusted_width, 60)


def save_dual_export(df_primary, target_dir, base_name, primary_sheet_name="Main Data", additional_sheets=None):
    """Menyimpan DataFrame ke CSV (RFC 4180 / UTF-8-sig) dan XLSX multi-sheet terformat."""
    os.makedirs(target_dir, exist_ok=True)
    csv_path = os.path.join(target_dir, f"{base_name}.csv")
    xlsx_path = os.path.join(target_dir, f"{base_name}.xlsx")
    
    df_primary.to_csv(csv_path, index=False, encoding="utf-8-sig")
    
    wb = openpyxl.Workbook()
    ws_primary = wb.active
    ws_primary.title = primary_sheet_name
    
    ws_primary.append(list(df_primary.columns))
    for row in df_primary.itertuples(index=False):
        ws_primary.append(list(row))
    style_worksheet(ws_primary)
    
    if additional_sheets:
        for sheet_title, sheet_df in additional_sheets.items():
            ws_extra = wb.create_sheet(title=sheet_title)
            ws_extra.append(list(sheet_df.columns))
            for row in sheet_df.itertuples(index=False):
                ws_extra.append(list(row))
            style_worksheet(ws_extra, header_bg="2C3E50")
            
    wb.save(xlsx_path)
    return csv_path, xlsx_path

def export_instagram_package():
    print("\n" + "=" * 65)
    print("1. MEMPROSES PAKET EKSPOR INSTAGRAM (data/export/instagram/)")
    print("=" * 65)
    os.makedirs(EXPORT_IG_DIR, exist_ok=True)
    
    # -------------------------------------------------------------
    # 1.1 instagram_posts_clean (55 rows, 27 cols)
    # -------------------------------------------------------------
    src_posts = os.path.join(DATA_FINAL_DIR, "instagram_posts_final.csv")
    df_posts = pd.read_csv(src_posts)
    assert len(df_posts) == 55, f"Post count mismatch: {len(df_posts)}"
    assert len(df_posts.columns) == 27, f"Post columns mismatch: {len(df_posts.columns)}"
    
    dict_posts = [
        {"column_name": "post_id", "data_type": "string", "description": "Shortcode unik identifier postingan Instagram publik"},
        {"column_name": "post_url", "data_type": "string", "description": "Tautan URL postingan Instagram (/p/... atau /reel/...)"},
        {"column_name": "source_url", "data_type": "string", "description": "URL sumber navigasi penjelajahan publik"},
        {"column_name": "post_date_raw", "data_type": "string", "description": "Timestamp ISO-8601 UTC asli dari platform"},
        {"column_name": "post_datetime_utc", "data_type": "string", "description": "Timestamp UTC terstandarisasi (+00:00)"},
        {"column_name": "post_datetime_wib", "data_type": "string", "description": "Timestamp lokal terstandarisasi Asia/Jakarta (+07:00)"},
        {"column_name": "post_date", "data_type": "string", "description": "Tanggal publikasi lokal WIB (YYYY-MM-DD)"},
        {"column_name": "post_year", "data_type": "integer", "description": "Tahun publikasi (2024, 2025, 2026)"},
        {"column_name": "post_month", "data_type": "integer", "description": "Bulan publikasi (1 - 12)"},
        {"column_name": "post_day", "data_type": "integer", "description": "Hari dalam bulan (1 - 31)"},
        {"column_name": "post_day_of_week", "data_type": "string", "description": "Hari dalam seminggu (Monday - Sunday)"},
        {"column_name": "post_hour_wib", "data_type": "integer", "description": "Jam penayangan dalam WIB (0 - 23)"},
        {"column_name": "content_type", "data_type": "string", "description": "Format konten: video/reel, carousel, image"},
        {"column_name": "caption", "data_type": "string", "description": "Teks caption mentah asli"},
        {"column_name": "caption_clean", "data_type": "string", "description": "Teks caption bersih konservatif"},
        {"column_name": "caption_length_raw", "data_type": "integer", "description": "Jumlah karakter caption mentah"},
        {"column_name": "caption_length_clean", "data_type": "integer", "description": "Jumlah karakter caption bersih"},
        {"column_name": "caption_word_count", "data_type": "integer", "description": "Jumlah kata caption bersih"},
        {"column_name": "hashtags", "data_type": "string", "description": "Daftar tagar dipisahkan spasi (null jika tidak ada)"},
        {"column_name": "hashtag_count", "data_type": "integer", "description": "Jumlah tagar yang digunakan (0 - 16)"},
        {"column_name": "has_hashtags", "data_type": "boolean", "description": "Indikator kehadiran tagar (True/False)"},
        {"column_name": "likes", "data_type": "integer", "description": "Jumlah suka publik riil"},
        {"column_name": "comments", "data_type": "integer", "description": "Jumlah komentar publik riil"},
        {"column_name": "views", "data_type": "float", "description": "Penayangan (strictly NaN, tidak terekspos di web unauthenticated)"},
        {"column_name": "total_interactions", "data_type": "integer", "description": "Total interaksi riil (likes + comments)"},
        {"column_name": "is_collaboration", "data_type": "boolean", "description": "Status co-author / kemitraan akun"},
        {"column_name": "original_account", "data_type": "string", "description": "Akun inisiator / mitra kreator postingan"}
    ]
    df_dict_posts = pd.DataFrame(dict_posts)
    
    save_dual_export(
        df_posts,
        EXPORT_IG_DIR,
        "instagram_posts_clean",
        primary_sheet_name="Instagram Posts Clean",
        additional_sheets={"Data Dictionary": df_dict_posts}
    )
    print("  -> Diekspor: instagram_posts_clean (.csv & .xlsx) [55 rows, 27 cols]")

    # -------------------------------------------------------------
    # 1.2 instagram_engagement_metrics (55 rows, 23 cols)
    # -------------------------------------------------------------
    src_metrics = os.path.join(DATA_FINAL_DIR, "instagram_analysis", "instagram_engagement_metrics.csv")
    df_metrics = pd.read_csv(src_metrics)
    assert len(df_metrics) == 55, f"Metrics count mismatch: {len(df_metrics)}"
    assert len(df_metrics.columns) == 23, f"Metrics cols mismatch: {len(df_metrics.columns)}"
    
    dict_metrics = [
        {"column_name": "post_id", "data_type": "string", "description": "Shortcode unik identifier postingan Instagram (Foreign Key)"},
        {"column_name": "interaction_rank", "data_type": "integer", "description": "Peringkat performa (1 = total_interactions tertinggi)"},
        {"column_name": "percentile_rank", "data_type": "float", "description": "Persentil interaksi (0.00 - 100.00%)"},
        {"column_name": "likes", "data_type": "integer", "description": "Jumlah likes"},
        {"column_name": "comments", "data_type": "integer", "description": "Jumlah comments"},
        {"column_name": "total_interactions", "data_type": "integer", "description": "likes + comments"},
        {"column_name": "interaction_tier", "data_type": "string", "description": "Tier: Viral Outlier (>239), High (110-239), Moderate (24-109), Low (<24)"},
        {"column_name": "is_interaction_outlier", "data_type": "boolean", "description": "Flag pencilan IQR (True jika total_interactions > 239.0)"},
        {"column_name": "content_type", "data_type": "string", "description": "video/reel, carousel, image"},
        {"column_name": "is_collaboration", "data_type": "boolean", "description": "Status postingan kolaborasi"},
        {"column_name": "original_account", "data_type": "string", "description": "Akun inisiator (@zahiraccounting, @pecahtelur.id, dll)"},
        {"column_name": "post_date", "data_type": "string", "description": "Tanggal publikasi WIB (YYYY-MM-DD)"},
        {"column_name": "post_datetime_wib", "data_type": "string", "description": "Timestamp lengkap WIB (+07:00)"},
        {"column_name": "post_year", "data_type": "integer", "description": "Tahun publikasi"},
        {"column_name": "post_month", "data_type": "integer", "description": "Bulan publikasi"},
        {"column_name": "post_day_of_week", "data_type": "string", "description": "Nama hari publikasi"},
        {"column_name": "post_hour_wib", "data_type": "integer", "description": "Jam publikasi WIB (0-23)"},
        {"column_name": "time_bin", "data_type": "string", "description": "Segmen waktu (Morning, Afternoon, Late Afternoon, Evening/Night)"},
        {"column_name": "caption_word_count", "data_type": "integer", "description": "Jumlah kata caption"},
        {"column_name": "hashtag_count", "data_type": "integer", "description": "Jumlah tagar"},
        {"column_name": "has_hashtags", "data_type": "boolean", "description": "Kehadiran tagar"},
        {"column_name": "post_url", "data_type": "string", "description": "Tautan URL postingan Instagram"},
        {"column_name": "source_url", "data_type": "string", "description": "URL sumber navigasi penjelajahan publik"}
    ]
    df_dict_metrics = pd.DataFrame(dict_metrics)
    
    save_dual_export(
        df_metrics,
        EXPORT_IG_DIR,
        "instagram_engagement_metrics",
        primary_sheet_name="Engagement Metrics",
        additional_sheets={"Data Dictionary": df_dict_metrics}
    )
    print("  -> Diekspor: instagram_engagement_metrics (.csv & .xlsx) [55 rows, 23 cols]")

    # -------------------------------------------------------------
    # 1.3 instagram_content_performance (Unified Overview & Multi-Sheet)
    # -------------------------------------------------------------
    # Bangun unified performance table
    perf_rows = []
    
    # Dimension 1: Content Type
    for ct in ['video/reel', 'carousel', 'image']:
        sub = df_metrics[df_metrics['content_type'] == ct]
        perf_rows.append({
            'analysis_dimension': 'Content Type',
            'segment': ct,
            'post_count': len(sub),
            'post_share_pct': round(len(sub) / 55 * 100, 2),
            'total_likes': int(sub['likes'].sum()),
            'mean_likes': round(float(sub['likes'].mean()), 2),
            'median_likes': round(float(sub['likes'].median()), 2),
            'total_comments': int(sub['comments'].sum()),
            'mean_comments': round(float(sub['comments'].mean()), 2),
            'median_comments': round(float(sub['comments'].median()), 2),
            'total_interactions': int(sub['total_interactions'].sum()),
            'mean_interactions': round(float(sub['total_interactions'].mean()), 2),
            'median_interactions': round(float(sub['total_interactions'].median()), 2),
            'min_interactions': int(sub['total_interactions'].min()),
            'max_interactions': int(sub['total_interactions'].max()),
            'notes': f'Format {ct}; n={len(sub)}'
        })
        
    # Baseline Overall
    perf_rows.append({
        'analysis_dimension': 'Overall Baseline',
        'segment': 'Total / All 55 Posts',
        'post_count': len(df_metrics),
        'post_share_pct': 100.0,
        'total_likes': int(df_metrics['likes'].sum()),
        'mean_likes': round(float(df_metrics['likes'].mean()), 2),
        'median_likes': round(float(df_metrics['likes'].median()), 2),
        'total_comments': int(df_metrics['comments'].sum()),
        'mean_comments': round(float(df_metrics['comments'].mean()), 2),
        'median_comments': round(float(df_metrics['comments'].median()), 2),
        'total_interactions': int(df_metrics['total_interactions'].sum()),
        'mean_interactions': round(float(df_metrics['total_interactions'].mean()), 2),
        'median_interactions': round(float(df_metrics['total_interactions'].median()), 2),
        'min_interactions': int(df_metrics['total_interactions'].min()),
        'max_interactions': int(df_metrics['total_interactions'].max()),
        'notes': 'Populasi lengkap 55 postingan Instagram publik Zahir'
    })
    
    # Dimension 2: Collaboration Status
    for flag, lbl in [(False, 'Organic Content (@zahiraccounting)'), (True, 'Collaborative Content (Partners & Creators)')]:
        sub = df_metrics[df_metrics['is_collaboration'] == flag]
        perf_rows.append({
            'analysis_dimension': 'Collaboration Status',
            'segment': lbl,
            'post_count': len(sub),
            'post_share_pct': round(len(sub) / 55 * 100, 2),
            'total_likes': int(sub['likes'].sum()),
            'mean_likes': round(float(sub['likes'].mean()), 2),
            'median_likes': round(float(sub['likes'].median()), 2),
            'total_comments': int(sub['comments'].sum()),
            'mean_comments': round(float(sub['comments'].mean()), 2),
            'median_comments': round(float(sub['comments'].median()), 2),
            'total_interactions': int(sub['total_interactions'].sum()),
            'mean_interactions': round(float(sub['total_interactions'].mean()), 2),
            'median_interactions': round(float(sub['total_interactions'].median()), 2),
            'min_interactions': int(sub['total_interactions'].min()),
            'max_interactions': int(sub['total_interactions'].max()),
            'notes': 'Postingan tunggal internal' if not flag else 'Co-authored dengan akun mitra / founder'
        })
        
    # Dimension 3: Partner Accounts
    for acc in ['pecahtelur.id', 'muhamad.is', 'zahirerp', 'zahironlineid', 'modalngobrol', 'zahiraccounting']:
        sub = df_metrics[df_metrics['original_account'] == acc]
        perf_rows.append({
            'analysis_dimension': 'Partner Accounts',
            'segment': f'@{acc}',
            'post_count': len(sub),
            'post_share_pct': round(len(sub) / 55 * 100, 2),
            'total_likes': int(sub['likes'].sum()),
            'mean_likes': round(float(sub['likes'].mean()), 2),
            'median_likes': round(float(sub['likes'].median()), 2),
            'total_comments': int(sub['comments'].sum()),
            'mean_comments': round(float(sub['comments'].mean()), 2),
            'median_comments': round(float(sub['comments'].median()), 2),
            'total_interactions': int(sub['total_interactions'].sum()),
            'mean_interactions': round(float(sub['total_interactions'].mean()), 2),
            'median_interactions': round(float(sub['total_interactions'].median()), 2),
            'min_interactions': int(sub['total_interactions'].min()),
            'max_interactions': int(sub['total_interactions'].max()),
            'notes': f'Entitas akun kreator/mitra @{acc}'
        })
        
    # Dimension 4: Day of Week
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        sub = df_metrics[df_metrics['post_day_of_week'] == day]
        perf_rows.append({
            'analysis_dimension': 'Day of Week',
            'segment': day,
            'post_count': len(sub),
            'post_share_pct': round(len(sub) / 55 * 100, 2),
            'total_likes': int(sub['likes'].sum()),
            'mean_likes': round(float(sub['likes'].mean()), 2),
            'median_likes': round(float(sub['likes'].median()), 2),
            'total_comments': int(sub['comments'].sum()),
            'mean_comments': round(float(sub['comments'].mean()), 2),
            'median_comments': round(float(sub['comments'].median()), 2),
            'total_interactions': int(sub['total_interactions'].sum()),
            'mean_interactions': round(float(sub['total_interactions'].mean()), 2),
            'median_interactions': round(float(sub['total_interactions'].median()), 2),
            'min_interactions': int(sub['total_interactions'].min()),
            'max_interactions': int(sub['total_interactions'].max()),
            'notes': f'Hari penayangan {day}'
        })
        
    # Dimension 5: Time of Day Bins
    for tb in ['Morning (06:00-11:59)', 'Afternoon (12:00-14:59)', 'Late Afternoon (15:00-17:59)', 'Evening/Night (18:00-23:59)']:
        sub = df_metrics[df_metrics['time_bin'] == tb]
        perf_rows.append({
            'analysis_dimension': 'Time of Day Bin',
            'segment': tb,
            'post_count': len(sub),
            'post_share_pct': round(len(sub) / 55 * 100, 2),
            'total_likes': int(sub['likes'].sum()),
            'mean_likes': round(float(sub['likes'].mean()), 2),
            'median_likes': round(float(sub['likes'].median()), 2),
            'total_comments': int(sub['comments'].sum()),
            'mean_comments': round(float(sub['comments'].mean()), 2),
            'median_comments': round(float(sub['comments'].median()), 2),
            'total_interactions': int(sub['total_interactions'].sum()),
            'mean_interactions': round(float(sub['total_interactions'].mean()), 2),
            'median_interactions': round(float(sub['total_interactions'].median()), 2),
            'min_interactions': int(sub['total_interactions'].min()),
            'max_interactions': int(sub['total_interactions'].max()),
            'notes': f'Segmen jam WIB {tb}'
        })
        
    # Dimension 6: Publication Year
    for yr in [2024, 2025, 2026]:
        sub = df_metrics[df_metrics['post_year'] == yr]
        perf_rows.append({
            'analysis_dimension': 'Publication Year',
            'segment': str(yr),
            'post_count': len(sub),
            'post_share_pct': round(len(sub) / 55 * 100, 2),
            'total_likes': int(sub['likes'].sum()),
            'mean_likes': round(float(sub['likes'].mean()), 2),
            'median_likes': round(float(sub['likes'].median()), 2),
            'total_comments': int(sub['comments'].sum()),
            'mean_comments': round(float(sub['comments'].mean()), 2),
            'median_comments': round(float(sub['comments'].median()), 2),
            'total_interactions': int(sub['total_interactions'].sum()),
            'mean_interactions': round(float(sub['total_interactions'].mean()), 2),
            'median_interactions': round(float(sub['total_interactions'].median()), 2),
            'min_interactions': int(sub['total_interactions'].min()),
            'max_interactions': int(sub['total_interactions'].max()),
            'notes': f'Tahun publikasi {yr}'
        })
        
    # Dimension 7: Hashtag Presence
    for flag, lbl in [(False, 'Tanpa Tagar (0 Hashtags)'), (True, 'Menggunakan Tagar (>=1 Hashtags)')]:
        sub = df_metrics[df_metrics['has_hashtags'] == flag]
        perf_rows.append({
            'analysis_dimension': 'Hashtag Presence',
            'segment': lbl,
            'post_count': len(sub),
            'post_share_pct': round(len(sub) / 55 * 100, 2),
            'total_likes': int(sub['likes'].sum()),
            'mean_likes': round(float(sub['likes'].mean()), 2),
            'median_likes': round(float(sub['likes'].median()), 2),
            'total_comments': int(sub['comments'].sum()),
            'mean_comments': round(float(sub['comments'].mean()), 2),
            'median_comments': round(float(sub['comments'].median()), 2),
            'total_interactions': int(sub['total_interactions'].sum()),
            'mean_interactions': round(float(sub['total_interactions'].mean()), 2),
            'median_interactions': round(float(sub['total_interactions'].median()), 2),
            'min_interactions': int(sub['total_interactions'].min()),
            'max_interactions': int(sub['total_interactions'].max()),
            'notes': 'Simpson paradox: 0 tagar terdistorsi @pecahtelur.id' if not flag else 'Postingan dengan 1-16 tagar'
        })
        
    df_perf_unified = pd.DataFrame(perf_rows)
    
    # Load detailed sheets from Phase 5.5 analysis
    df_ct_detail = pd.read_csv(os.path.join(DATA_FINAL_DIR, "instagram_analysis", "instagram_content_type_comparison.csv"))
    df_col_detail = pd.read_csv(os.path.join(DATA_FINAL_DIR, "instagram_analysis", "instagram_collaboration_analysis.csv"))
    df_time_detail = pd.read_csv(os.path.join(DATA_FINAL_DIR, "instagram_analysis", "instagram_posting_time_analysis.csv"))
    df_ch_detail = pd.read_csv(os.path.join(DATA_FINAL_DIR, "instagram_analysis", "instagram_caption_hashtag_analysis.csv"))
    df_sum_detail = pd.read_csv(os.path.join(DATA_FINAL_DIR, "instagram_analysis", "instagram_engagement_summary.csv"))
    df_top_detail = pd.read_csv(os.path.join(DATA_FINAL_DIR, "instagram_analysis", "instagram_top_posts.csv"))
    
    save_dual_export(
        df_perf_unified,
        EXPORT_IG_DIR,
        "instagram_content_performance",
        primary_sheet_name="Performance Overview",
        additional_sheets={
            "Content Type Breakdown": df_ct_detail,
            "Collaboration Breakdown": df_col_detail,
            "Posting Time Breakdown": df_time_detail,
            "Caption & Hashtags": df_ch_detail,
            "Engagement Distribution": df_sum_detail,
            "Top & Bottom Showcase": df_top_detail
        }
    )
    print(f"  -> Diekspor: instagram_content_performance (.csv & .xlsx) [{len(df_perf_unified)} rows, 16 cols; 7 sheets]")

def export_playstore_package():
    print("\n" + "=" * 65)
    print("2. MEMPROSES PAKET EKSPOR PLAY STORE (data/export/playstore/)")
    print("=" * 65)
    os.makedirs(EXPORT_PS_DIR, exist_ok=True)
    
    # -------------------------------------------------------------
    # 2.1 playstore_reviews_clean (417 rows, 19 cols)
    # -------------------------------------------------------------
    src_reviews = os.path.join(DATA_FINAL_DIR, "playstore_reviews_final.csv")
    df_reviews = pd.read_csv(src_reviews)
    assert len(df_reviews) == 417, f"Play Store review count mismatch: {len(df_reviews)}"
    
    # Strictly exclude userName, userImage, reviewer_id, reply_text
    prohibited_to_exclude = ['reviewer_id', 'reply_text']
    clean_cols = [c for c in df_reviews.columns if c not in prohibited_to_exclude]
    
    # Expected clean_cols (19 columns):
    # ['review_id', 'review_datetime', 'review_date', 'review_year', 'review_month',
    #  'review_text', 'review_text_clean', 'score', 'rating_category', 'thumbs_up_count',
    #  'has_developer_reply', 'replied_datetime', 'response_time_days', 'app_name',
    #  'package_name', 'review_created_version', 'app_version', 'text_length_chars', 'word_count']
    
    # Susun kolom teratur
    ordered_clean_cols = [
        'review_id', 'app_name', 'package_name', 'review_datetime', 'review_date',
        'review_year', 'review_month', 'score', 'rating_category', 'thumbs_up_count',
        'review_text', 'review_text_clean', 'text_length_chars', 'word_count',
        'review_created_version', 'app_version', 'has_developer_reply',
        'replied_datetime', 'response_time_days'
    ]
    df_reviews_clean = df_reviews[ordered_clean_cols].copy()
    assert len(df_reviews_clean.columns) == 19, f"Cols mismatch: {len(df_reviews_clean.columns)}"
    
    dict_reviews = [
        {"column_name": "review_id", "data_type": "string", "description": "Identifier UUID unik ulasan Google Play Store (Primary Key)"},
        {"column_name": "app_name", "data_type": "string", "description": "Nama aplikasi ekosistem Zahir (5 aplikasi)"},
        {"column_name": "package_name", "data_type": "string", "description": "Package identifier Android aplikasi"},
        {"column_name": "review_datetime", "data_type": "string", "description": "Timestamp ulasan lengkap ISO-8601"},
        {"column_name": "review_date", "data_type": "string", "description": "Tanggal ulasan (YYYY-MM-DD)"},
        {"column_name": "review_year", "data_type": "integer", "description": "Tahun ulasan (2018 - 2026)"},
        {"column_name": "review_month", "data_type": "integer", "description": "Bulan ulasan (1 - 12)"},
        {"column_name": "score", "data_type": "integer", "description": "Rating bintang ulasan (1 - 5)"},
        {"column_name": "rating_category", "data_type": "string", "description": "Kategori rating: critical (1-2), neutral (3), positive (4-5)"},
        {"column_name": "thumbs_up_count", "data_type": "integer", "description": "Jumlah upvote/likes ulasan dari pengguna lain"},
        {"column_name": "review_text", "data_type": "string", "description": "Teks ulasan asli"},
        {"column_name": "review_text_clean", "data_type": "string", "description": "Teks ulasan bersih konservatif (tanpa URL/spasi berlebih)"},
        {"column_name": "text_length_chars", "data_type": "integer", "description": "Panjang karakter teks ulasan bersih"},
        {"column_name": "word_count", "data_type": "integer", "description": "Jumlah kata teks ulasan bersih"},
        {"column_name": "review_created_version", "data_type": "string", "description": "Versi aplikasi saat ulasan dibuat (null jika tidak tercatat)"},
        {"column_name": "app_version", "data_type": "string", "description": "Versi aplikasi terpasang saat ulasan (null jika tidak tercatat)"},
        {"column_name": "has_developer_reply", "data_type": "boolean", "description": "Status balasan developer (True jika dibalas)"},
        {"column_name": "replied_datetime", "data_type": "string", "description": "Timestamp tanggapan developer (null jika tidak dibalas)"},
        {"column_name": "response_time_days", "data_type": "float", "description": "Waktu respon developer dalam hari (null jika tidak dibalas)"}
    ]
    df_dict_reviews = pd.DataFrame(dict_reviews)
    
    save_dual_export(
        df_reviews_clean,
        EXPORT_PS_DIR,
        "playstore_reviews_clean",
        primary_sheet_name="Play Store Reviews Clean",
        additional_sheets={"Data Dictionary": df_dict_reviews}
    )
    print("  -> Diekspor: playstore_reviews_clean (.csv & .xlsx) [417 rows, 19 cols]")

    # -------------------------------------------------------------
    # 2.2 playstore_sentiment (417 rows, 14 cols)
    # -------------------------------------------------------------
    src_gold = os.path.join(DATA_FINAL_DIR, "playstore_gold_set_final.csv")
    df_gold = pd.read_csv(src_gold)
    assert len(df_gold) == 417, f"Gold set count mismatch: {len(df_gold)}"
    
    src_split = os.path.join(DATA_FINAL_DIR, "sentiment_benchmark", "sentiment_split_manifest.csv")
    df_split = pd.read_csv(src_split)
    
    src_test_pred = os.path.join(DATA_FINAL_DIR, "sentiment_benchmark", "sentiment_test_predictions.csv")
    df_test_pred = pd.read_csv(src_test_pred)
    
    # Merge gold set with split manifest
    df_sent = df_gold[['review_id', 'app_name', 'human_sentiment_label']].merge(
        df_reviews[['review_id', 'review_date', 'score', 'rating_category']],
        on='review_id',
        how='left'
    )
    df_sent = df_sent.merge(df_split[['review_id', 'split']], on='review_id', how='left')
    df_sent.rename(columns={'split': 'benchmark_split'}, inplace=True)
    df_sent['sentiment_label_source'] = "gold_set_human_annotated"
    
    # Merge test predictions explicitly
    test_cols_to_merge = [
        'review_id', 'pred_indobert', 'indobert_confidence',
        'pred_inset_lexicon', 'inset_score',
        'pred_tfidf_lr', 'tfidf_lr_confidence'
    ]
    df_sent = df_sent.merge(df_test_pred[test_cols_to_merge], on='review_id', how='left')
    df_sent.rename(columns={
        'pred_indobert': 'test_pred_indobert',
        'indobert_confidence': 'test_indobert_confidence',
        'pred_inset_lexicon': 'test_pred_inset_lexicon',
        'inset_score': 'test_inset_score',
        'pred_tfidf_lr': 'test_pred_tfidf_lr',
        'tfidf_lr_confidence': 'test_tfidf_lr_confidence'
    }, inplace=True)
    
    ordered_sent_cols = [
        'review_id', 'app_name', 'review_date', 'score', 'rating_category',
        'human_sentiment_label', 'sentiment_label_source', 'benchmark_split',
        'test_pred_indobert', 'test_indobert_confidence',
        'test_pred_inset_lexicon', 'test_inset_score',
        'test_pred_tfidf_lr', 'test_tfidf_lr_confidence'
    ]
    df_sent_export = df_sent[ordered_sent_cols].copy()
    assert len(df_sent_export) == 417, f"Sentiment rows mismatch: {len(df_sent_export)}"
    assert len(df_sent_export.columns) == 14, f"Sentiment cols mismatch: {len(df_sent_export.columns)}"
    
    # Detailed benchmark test predictions & benchmark metrics for XLSX sheets
    df_bench_metrics = pd.read_csv(os.path.join(DATA_FINAL_DIR, "sentiment_benchmark", "sentiment_benchmark_metrics.csv"))
    df_test_only = df_sent_export[df_sent_export['benchmark_split'] == 'test'].copy()
    
    save_dual_export(
        df_sent_export,
        EXPORT_PS_DIR,
        "playstore_sentiment",
        primary_sheet_name="Sentiment Full Dataset",
        additional_sheets={
            "Benchmark Test Predictions": df_test_only,
            "Benchmark Metrics Summary": df_bench_metrics
        }
    )
    print("  -> Diekspor: playstore_sentiment (.csv & .xlsx) [417 rows, 14 cols; 3 sheets]")

    # -------------------------------------------------------------
    # 2.3 playstore_aspects (417 rows, 17 cols, 234 mentions)
    # -------------------------------------------------------------
    src_aspects = os.path.join(DATA_FINAL_DIR, "topic_analysis", "phase_5_3", "review_aspect_assignments_remediated.csv")
    df_aspects = pd.read_csv(src_aspects)
    assert len(df_aspects) == 417, f"Aspect count mismatch: {len(df_aspects)}"
    assert int(df_aspects['aspect_count'].sum()) == 234, f"Aspect mentions mismatch: {df_aspects['aspect_count'].sum()}"
    
    # Build long format for Excel Sheet 2
    aspect_map = {
        'aspect_login_auth': ('login_auth', 'Login, Otentikasi & Akses Akun'),
        'aspect_crash_stability': ('crash_stability', 'Stabilitas Aplikasi, Bug & Crash'),
        'aspect_pricing_subscription': ('pricing_subscription', 'Harga, Langganan & Lisensi'),
        'aspect_sync_cloud_data': ('sync_cloud_data', 'Sinkronisasi Cloud & Integritas Data'),
        'aspect_pos_hardware_print': ('pos_hardware_print', 'POS, Kasir & Integrasi Hardware Printer'),
        'aspect_inventory_accounting': ('inventory_accounting', 'Fitur Akuntansi, Laporan & Inventori'),
        'aspect_certification_exam': ('certification_exam', 'Sertifikasi & Ujian Online Zahir'),
        'aspect_attendance_face': ('attendance_face', 'Presensi & Deteksi Wajah (Attendance)')
    }
    
    long_records = []
    for _, row in df_aspects.iterrows():
        if row['has_aspect']:
            for col, (asp_id, asp_name) in aspect_map.items():
                if row[col]:
                    long_records.append({
                        'review_id': row['review_id'],
                        'app_name': row['app_name'],
                        'review_datetime': row['review_datetime'],
                        'human_sentiment_label': row['human_sentiment_label'],
                        'aspect_id': asp_id,
                        'aspect_name': asp_name,
                        'matched_keywords': row['matched_keywords']
                    })
    df_aspects_long = pd.DataFrame(long_records)
    assert len(df_aspects_long) == 234, f"Long aspects count mismatch: {len(df_aspects_long)}"
    
    # Build aspect summary table for Excel Sheet 3
    summary_aspect_records = []
    for col, (asp_id, asp_name) in aspect_map.items():
        sub_asp = df_aspects[df_aspects[col] == True]
        pos_cnt = int((sub_asp['human_sentiment_label'] == 'positive').sum())
        neu_cnt = int((sub_asp['human_sentiment_label'] == 'neutral').sum())
        neg_cnt = int((sub_asp['human_sentiment_label'] == 'negative').sum())
        tot_cnt = len(sub_asp)
        crit_rate = round((neg_cnt + neu_cnt) / tot_cnt * 100, 2) if tot_cnt > 0 else 0.0
        
        summary_aspect_records.append({
            'aspect_id': asp_id,
            'aspect_name': asp_name,
            'total_mentions': tot_cnt,
            'mentions_share_pct': round(tot_cnt / 234 * 100, 2),
            'reviews_affected_pct': round(tot_cnt / 417 * 100, 2),
            'positive_mentions': pos_cnt,
            'neutral_mentions': neu_cnt,
            'negative_mentions': neg_cnt,
            'critical_proportion_pct': crit_rate
        })
    df_aspect_summary = pd.DataFrame(summary_aspect_records).sort_values(by='total_mentions', ascending=False)
    
    save_dual_export(
        df_aspects,
        EXPORT_PS_DIR,
        "playstore_aspects",
        primary_sheet_name="Aspect Reviews (Wide)",
        additional_sheets={
            "Aspect Mentions (Long)": df_aspects_long,
            "Aspect Summary (8 Aspects)": df_aspect_summary
        }
    )
    print(f"  -> Diekspor: playstore_aspects (.csv & .xlsx) [417 rows, 17 cols, 234 mentions; 3 sheets]")

def main():
    print("=" * 75)
    print("ZAHIR SOCIAL ANALYTICS - PHASE 5.6 FINAL DATA PACKAGING PIPELINE")
    print("=" * 75)
    
    export_instagram_package()
    export_playstore_package()
    
    print("\n" + "=" * 75)
    print("SELURUH PAKET DATA BERHASIL DIEKSPOR KE data/export/")
    print(f"1. Instagram Export: {EXPORT_IG_DIR}")
    print(f"2. Play Store Export: {EXPORT_PS_DIR}")
    print("=" * 75)
    return True


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)