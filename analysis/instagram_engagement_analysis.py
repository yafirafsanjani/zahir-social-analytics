# -*- coding: utf-8 -*-
"""
instagram_engagement_analysis.py
---------------------------------
Modul Analisis Performa Postingan dan Engagement Media Sosial Instagram Zahir
(Fase 5.5 - Zahir Social Analytics).

Dataset Sumber: data/final/instagram_posts_final.csv (55 postingan unik)
"""

import os
import sys
import pandas as pd
import numpy as np
from scipy import stats
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Path Konfigurasi
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FINAL_DIR = os.path.join(BASE_DIR, "data", "final")
OUTPUT_DIR = os.path.join(DATA_FINAL_DIR, "instagram_analysis")
SOURCE_CSV = os.path.join(DATA_FINAL_DIR, "instagram_posts_final.csv")


def style_worksheet(ws, header_bg="1F4E78"):
    """
    Menerapkan styling openpyxl profesional pada worksheet:
    - Header pada baris 1 (Navy blue, font putih tebal)
    - Zebra striping baris selang-seling
    - Border tipis pada seluruh sel data
    - Penyesuaian otomatis lebar kolom
    """
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
        
    # Format baris data (baris 2 onward)
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

    # Auto-adjust column widths
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


def save_dual_format(df_primary, base_name, additional_sheets=None):
    """Menyimpan DataFrame ke berkas CSV (RFC 4180) dan berkas Excel XLSX."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    csv_path = os.path.join(OUTPUT_DIR, f"{base_name}.csv")
    xlsx_path = os.path.join(OUTPUT_DIR, f"{base_name}.xlsx")
    
    df_primary.to_csv(csv_path, index=False, encoding="utf-8-sig")
    
    wb = openpyxl.Workbook()
    ws_primary = wb.active
    ws_primary.title = "Summary" if base_name == "instagram_engagement_summary" else "Main Data"
    
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


def classify_time_bin(hour):
    """Mengelompokkan jam publikasi (WIB) ke segmen waktu standar."""
    if 6 <= hour <= 11:
        return 'Morning (06:00-11:59)'
    elif 12 <= hour <= 14:
        return 'Afternoon (12:00-14:59)'
    elif 15 <= hour <= 17:
        return 'Late Afternoon (15:00-17:59)'
    elif 18 <= hour <= 23:
        return 'Evening/Night (18:00-23:59)'
    else:
        return 'Early Morning (00:00-05:59)'

def run_analysis():
    print("=" * 75)
    print("ZAHIR SOCIAL ANALYTICS - PHASE 5.5 INSTAGRAM ENGAGEMENT ANALYSIS")
    print("=" * 75)
    
    assert os.path.exists(SOURCE_CSV), f"Dataset sumber tidak ditemukan: {SOURCE_CSV}"
    df = pd.read_csv(SOURCE_CSV)
    assert len(df) == 55, f"Ukuran dataset tidak valid: {len(df)} (diharapkan 55)"
    print(f"[OK] Ingested {len(df)} posts from {SOURCE_CSV}")
    
    # -------------------------------------------------------------------------
    # TABEL 1: Per-Post Engagement Metrics (instagram_engagement_metrics)
    # -------------------------------------------------------------------------
    print("\n[1/7] Menghasilkan instagram_engagement_metrics...")
    df_metrics = df.copy()
    assert (df_metrics['total_interactions'] == df_metrics['likes'] + df_metrics['comments']).all()
    
    df_metrics['interaction_rank'] = df_metrics['total_interactions'].rank(ascending=False, method='min').astype(int)
    df_metrics['percentile_rank'] = (df_metrics['total_interactions'].rank(pct=True, ascending=True) * 100).round(2)
    
    q1_inter = df_metrics['total_interactions'].quantile(0.25)
    q3_inter = df_metrics['total_interactions'].quantile(0.75)
    iqr_inter = q3_inter - q1_inter
    outlier_thresh_inter = q3_inter + 1.5 * iqr_inter
    
    df_metrics['is_interaction_outlier'] = df_metrics['total_interactions'] > outlier_thresh_inter
    
    def get_tier(row):
        val = row['total_interactions']
        if val > outlier_thresh_inter:
            return 'Viral Outlier (>239)'
        elif val >= q3_inter:
            return 'High (110-239)'
        elif val >= q1_inter:
            return 'Moderate (24-109)'
        else:
            return 'Low (<24)'
            
    df_metrics['interaction_tier'] = df_metrics.apply(get_tier, axis=1)
    df_metrics['time_bin'] = df_metrics['post_hour_wib'].apply(classify_time_bin)
    
    metrics_cols = [
        'post_id', 'interaction_rank', 'percentile_rank', 'likes', 'comments',
        'total_interactions', 'interaction_tier', 'is_interaction_outlier',
        'content_type', 'is_collaboration', 'original_account',
        'post_date', 'post_datetime_wib', 'post_year', 'post_month',
        'post_day_of_week', 'post_hour_wib', 'time_bin',
        'caption_word_count', 'hashtag_count', 'has_hashtags',
        'post_url', 'source_url'
    ]
    df_metrics_export = df_metrics[metrics_cols].sort_values(by='interaction_rank', ascending=True)
    
    dict_rows = [
        {"column_name": "post_id", "data_type": "string", "description": "Shortcode unik identifier postingan Instagram"},
        {"column_name": "interaction_rank", "data_type": "integer", "description": "Peringkat postingan (1 = interaksi tertinggi)"},
        {"column_name": "percentile_rank", "data_type": "float", "description": "Persentil interaksi postingan terhadap seluruh 55 postingan"},
        {"column_name": "likes", "data_type": "integer", "description": "Jumlah suka yang diperoleh postingan"},
        {"column_name": "comments", "data_type": "integer", "description": "Jumlah komentar publik pada postingan"},
        {"column_name": "total_interactions", "data_type": "integer", "description": "Total keterlibatan riil (likes + comments)"},
        {"column_name": "interaction_tier", "data_type": "string", "description": "Klasifikasi tingkat performa: Viral Outlier, High, Moderate, Low"},
        {"column_name": "is_interaction_outlier", "data_type": "boolean", "description": "Flag outlier IQR (True jika total_interactions > Q3 + 1.5*IQR)"},
        {"column_name": "content_type", "data_type": "string", "description": "Format konten: video/reel, carousel, image"},
        {"column_name": "is_collaboration", "data_type": "boolean", "description": "Status co-author / kemitraan akun"},
        {"column_name": "original_account", "data_type": "string", "description": "Akun kreator / inisiator postingan"},
        {"column_name": "post_date", "data_type": "string", "description": "Tanggal posting lokal WIB (YYYY-MM-DD)"},
        {"column_name": "post_datetime_wib", "data_type": "string", "description": "Timestamp lengkap terstandarisasi Asia/Jakarta (+07:00)"},
        {"column_name": "post_year", "data_type": "integer", "description": "Tahun publikasi (2024, 2025, 2026)"},
        {"column_name": "post_month", "data_type": "integer", "description": "Bulan publikasi (1 - 12)"},
        {"column_name": "post_day_of_week", "data_type": "string", "description": "Hari publikasi (Monday - Sunday)"},
        {"column_name": "post_hour_wib", "data_type": "integer", "description": "Jam publikasi dalam WIB (0 - 23)"},
        {"column_name": "time_bin", "data_type": "string", "description": "Segmen waktu penayangan (Morning, Afternoon, dll)"},
        {"column_name": "caption_word_count", "data_type": "integer", "description": "Jumlah kata caption setelah pembersihan"},
        {"column_name": "hashtag_count", "data_type": "integer", "description": "Jumlah tagar (#) yang disertakan"},
        {"column_name": "has_hashtags", "data_type": "boolean", "description": "Indikator kehadiran tagar"},
        {"column_name": "post_url", "data_type": "string", "description": "Tautan publik postingan Instagram untuk audit keaslian"},
        {"column_name": "source_url", "data_type": "string", "description": "URL sumber navigasi penjelajahan publik"}
    ]
    df_dict = pd.DataFrame(dict_rows)
    
    save_dual_format(
        df_metrics_export,
        "instagram_engagement_metrics",
        additional_sheets={"Data Dictionary": df_dict}
    )
    print(f"  -> Generated metrics for {len(df_metrics_export)} posts")

    # -------------------------------------------------------------------------
    # TABEL 2: Engagement Distribution Summary (instagram_engagement_summary)
    # -------------------------------------------------------------------------
    print("\n[2/7] Menghasilkan instagram_engagement_summary...")
    summary_rows = []
    for col in ['likes', 'comments', 'total_interactions']:
        s = df_metrics[col]
        q1 = float(s.quantile(0.25))
        q3 = float(s.quantile(0.75))
        iqr = float(q3 - q1)
        thresh = float(q3 + 1.5 * iqr)
        outliers = s[s > thresh]
        
        summary_rows.append({
            'metric': col,
            'count': int(len(s)),
            'sum': int(s.sum()),
            'mean': round(float(s.mean()), 2),
            'std': round(float(s.std()), 2),
            'median': round(float(s.median()), 2),
            'min': int(s.min()),
            'max': int(s.max()),
            'q1': round(q1, 2),
            'q3': round(q3, 2),
            'iqr': round(iqr, 2),
            'skewness': round(float(s.skew()), 2),
            'outlier_threshold': round(thresh, 2),
            'outlier_count': int(len(outliers)),
            'outlier_pct': round(float(len(outliers) / len(s) * 100), 2)
        })
    df_summary = pd.DataFrame(summary_rows)
    
    outliers_detail = df_metrics_export[df_metrics_export['is_interaction_outlier'] == True][
        ['interaction_rank', 'post_id', 'content_type', 'is_collaboration', 'original_account', 'post_date', 'likes', 'comments', 'total_interactions', 'post_url']
    ].copy()
    
    save_dual_format(
        df_summary,
        "instagram_engagement_summary",
        additional_sheets={"Outliers Detail": outliers_detail}
    )
    print(f"  -> Generated summary for {len(df_summary)} metrics")
    # -------------------------------------------------------------------------
    # TABEL 3: Content Type Comparison (instagram_content_type_comparison)
    # -------------------------------------------------------------------------
    print("\n[3/7] Menghasilkan instagram_content_type_comparison...")
    ct_rows = []
    content_types = ['video/reel', 'carousel', 'image']
    
    for ct in content_types:
        sub = df_metrics[df_metrics['content_type'] == ct]
        cnt = len(sub)
        q1_sub = sub['total_interactions'].quantile(0.25)
        q3_sub = sub['total_interactions'].quantile(0.75)
        iqr_sub = q3_sub - q1_sub
        
        colab_count = int((sub['is_collaboration'] == True).sum())
        organic_count = int((sub['is_collaboration'] == False).sum())
        
        ct_rows.append({
            'content_type': ct,
            'post_count': cnt,
            'post_share_pct': round(cnt / len(df_metrics) * 100, 2),
            'total_likes': int(sub['likes'].sum()),
            'mean_likes': round(float(sub['likes'].mean()), 2),
            'median_likes': round(float(sub['likes'].median()), 2),
            'std_likes': round(float(sub['likes'].std()), 2) if cnt > 1 else 0.0,
            'min_likes': int(sub['likes'].min()),
            'max_likes': int(sub['likes'].max()),
            'total_comments': int(sub['comments'].sum()),
            'mean_comments': round(float(sub['comments'].mean()), 2),
            'median_comments': round(float(sub['comments'].median()), 2),
            'std_comments': round(float(sub['comments'].std()), 2) if cnt > 1 else 0.0,
            'min_comments': int(sub['comments'].min()),
            'max_comments': int(sub['comments'].max()),
            'total_interactions': int(sub['total_interactions'].sum()),
            'mean_interactions': round(float(sub['total_interactions'].mean()), 2),
            'median_interactions': round(float(sub['total_interactions'].median()), 2),
            'std_interactions': round(float(sub['total_interactions'].std()), 2) if cnt > 1 else 0.0,
            'iqr_interactions': round(float(iqr_sub), 2),
            'min_interactions': int(sub['total_interactions'].min()),
            'max_interactions': int(sub['total_interactions'].max()),
            'colab_posts_count': colab_count,
            'organic_posts_count': organic_count
        })
        
    total_q1 = df_metrics['total_interactions'].quantile(0.25)
    total_q3 = df_metrics['total_interactions'].quantile(0.75)
    ct_rows.append({
        'content_type': 'Total / Overall',
        'post_count': len(df_metrics),
        'post_share_pct': 100.0,
        'total_likes': int(df_metrics['likes'].sum()),
        'mean_likes': round(float(df_metrics['likes'].mean()), 2),
        'median_likes': round(float(df_metrics['likes'].median()), 2),
        'std_likes': round(float(df_metrics['likes'].std()), 2),
        'min_likes': int(df_metrics['likes'].min()),
        'max_likes': int(df_metrics['likes'].max()),
        'total_comments': int(df_metrics['comments'].sum()),
        'mean_comments': round(float(df_metrics['comments'].mean()), 2),
        'median_comments': round(float(df_metrics['comments'].median()), 2),
        'std_comments': round(float(df_metrics['comments'].std()), 2),
        'min_comments': int(df_metrics['comments'].min()),
        'max_comments': int(df_metrics['comments'].max()),
        'total_interactions': int(df_metrics['total_interactions'].sum()),
        'mean_interactions': round(float(df_metrics['total_interactions'].mean()), 2),
        'median_interactions': round(float(df_metrics['total_interactions'].median()), 2),
        'std_interactions': round(float(df_metrics['total_interactions'].std()), 2),
        'iqr_interactions': round(float(total_q3 - total_q1), 2),
        'min_interactions': int(df_metrics['total_interactions'].min()),
        'max_interactions': int(df_metrics['total_interactions'].max()),
        'colab_posts_count': int((df_metrics['is_collaboration'] == True).sum()),
        'organic_posts_count': int((df_metrics['is_collaboration'] == False).sum())
    })
    df_ct = pd.DataFrame(ct_rows)
    
    crosstab_df = pd.crosstab(
        df_metrics['content_type'],
        df_metrics['is_collaboration'],
        margins=True,
        margins_name='Total'
    ).reset_index()
    crosstab_df.columns = ['content_type', 'organic_count', 'collaboration_count', 'total_count']
    
    save_dual_format(
        df_ct,
        "instagram_content_type_comparison",
        additional_sheets={"Format by Collaboration": crosstab_df}
    )
    print("  -> Generated content type comparison")

    # -------------------------------------------------------------------------
    # TABEL 4: Collaboration Analysis (instagram_collaboration_analysis)
    # -------------------------------------------------------------------------
    print("\n[4/7] Menghasilkan instagram_collaboration_analysis...")
    colab_rows = []
    
    org = df_metrics[df_metrics['is_collaboration'] == False]
    col = df_metrics[df_metrics['is_collaboration'] == True]
    
    org_q1 = org['total_interactions'].quantile(0.25)
    org_q3 = org['total_interactions'].quantile(0.75)
    col_q1 = col['total_interactions'].quantile(0.25)
    col_q3 = col['total_interactions'].quantile(0.75)
    
    colab_rows.append({
        'analysis_dimension': 'Collaboration Status',
        'segment': 'Organic Content (@zahiraccounting)',
        'is_collaboration': False,
        'post_count': len(org),
        'post_share_pct': round(len(org) / len(df_metrics) * 100, 2),
        'total_likes': int(org['likes'].sum()),
        'mean_likes': round(float(org['likes'].mean()), 2),
        'median_likes': round(float(org['likes'].median()), 2),
        'total_comments': int(org['comments'].sum()),
        'mean_comments': round(float(org['comments'].mean()), 2),
        'median_comments': round(float(org['comments'].median()), 2),
        'total_interactions': int(org['total_interactions'].sum()),
        'mean_interactions': round(float(org['total_interactions'].mean()), 2),
        'median_interactions': round(float(org['total_interactions'].median()), 2),
        'std_interactions': round(float(org['total_interactions'].std()), 2),
        'iqr_interactions': round(float(org_q3 - org_q1), 2),
        'min_interactions': int(org['total_interactions'].min()),
        'max_interactions': int(org['total_interactions'].max()),
        'notes': 'Postingan tunggal internal Zahir Accounting'
    })
    
    colab_rows.append({
        'analysis_dimension': 'Collaboration Status',
        'segment': 'Collaborative Content (Partners & Creators)',
        'is_collaboration': True,
        'post_count': len(col),
        'post_share_pct': round(len(col) / len(df_metrics) * 100, 2),
        'total_likes': int(col['likes'].sum()),
        'mean_likes': round(float(col['likes'].mean()), 2),
        'median_likes': round(float(col['likes'].median()), 2),
        'total_comments': int(col['comments'].sum()),
        'mean_comments': round(float(col['comments'].mean()), 2),
        'median_comments': round(float(col['comments'].median()), 2),
        'total_interactions': int(col['total_interactions'].sum()),
        'mean_interactions': round(float(col['total_interactions'].mean()), 2),
        'median_interactions': round(float(col['total_interactions'].median()), 2),
        'std_interactions': round(float(col['total_interactions'].std()), 2),
        'iqr_interactions': round(float(col_q3 - col_q1), 2),
        'min_interactions': int(col['total_interactions'].min()),
        'max_interactions': int(col['total_interactions'].max()),
        'notes': 'Postingan co-author dengan akun mitra / founder'
    })
    
    abs_diff_mean = round(float(col['total_interactions'].mean() - org['total_interactions'].mean()), 2)
    abs_diff_median = round(float(col['total_interactions'].median() - org['total_interactions'].median()), 2)
    
    colab_rows.append({
        'analysis_dimension': 'Comparison Delta',
        'segment': 'Absolute Difference (Colab vs Organic)',
        'is_collaboration': None,
        'post_count': len(col) - len(org),
        'post_share_pct': round((len(col) - len(org)) / len(df_metrics) * 100, 2),
        'total_likes': int(col['likes'].sum() - org['likes'].sum()),
        'mean_likes': round(float(col['likes'].mean() - org['likes'].mean()), 2),
        'median_likes': round(float(col['likes'].median() - org['likes'].median()), 2),
        'total_comments': int(col['comments'].sum() - org['comments'].sum()),
        'mean_comments': round(float(col['comments'].mean() - org['comments'].mean()), 2),
        'median_comments': round(float(col['comments'].median() - org['comments'].median()), 2),
        'total_interactions': int(col['total_interactions'].sum() - org['total_interactions'].sum()),
        'mean_interactions': abs_diff_mean,
        'median_interactions': abs_diff_median,
        'std_interactions': None,
        'iqr_interactions': None,
        'min_interactions': None,
        'max_interactions': None,
        'notes': f'Delta Absolut: Mean +{abs_diff_mean}, Median +{abs_diff_median}'
    })
    
    acc_summary = df_metrics.groupby(['original_account', 'is_collaboration']).agg(
        post_count=('post_id', 'count'),
        total_likes=('likes', 'sum'),
        mean_likes=('likes', 'mean'),
        median_likes=('likes', 'median'),
        total_comments=('comments', 'sum'),
        mean_comments=('comments', 'mean'),
        median_comments=('comments', 'median'),
        total_interactions=('total_interactions', 'sum'),
        mean_interactions=('total_interactions', 'mean'),
        median_interactions=('total_interactions', 'median'),
        std_interactions=('total_interactions', 'std'),
        min_interactions=('total_interactions', 'min'),
        max_interactions=('total_interactions', 'max')
    ).reset_index().sort_values(by='total_interactions', ascending=False)
    
    for row in acc_summary.itertuples():
        q1_a = df_metrics[df_metrics['original_account'] == row.original_account]['total_interactions'].quantile(0.25)
        q3_a = df_metrics[df_metrics['original_account'] == row.original_account]['total_interactions'].quantile(0.75)
        iqr_a = q3_a - q1_a
        colab_rows.append({
            'analysis_dimension': 'Partner Account Breakdown',
            'segment': f"@{row.original_account}",
            'is_collaboration': row.is_collaboration,
            'post_count': row.post_count,
            'post_share_pct': round(row.post_count / len(df_metrics) * 100, 2),
            'total_likes': int(row.total_likes),
            'mean_likes': round(float(row.mean_likes), 2),
            'median_likes': round(float(row.median_likes), 2),
            'total_comments': int(row.total_comments),
            'mean_comments': round(float(row.mean_comments), 2),
            'median_comments': round(float(row.median_comments), 2),
            'total_interactions': int(row.total_interactions),
            'mean_interactions': round(float(row.mean_interactions), 2),
            'median_interactions': round(float(row.median_interactions), 2),
            'std_interactions': round(float(row.std_interactions), 2) if not np.isnan(row.std_interactions) else 0.0,
            'iqr_interactions': round(float(iqr_a), 2),
            'min_interactions': int(row.min_interactions),
            'max_interactions': int(row.max_interactions),
            'notes': f"Format dominant: {df_metrics[df_metrics['original_account']==row.original_account]['content_type'].mode().iloc[0]}"
        })
        
    df_colab = pd.DataFrame(colab_rows)
    df_colab_overview = df_colab[df_colab['analysis_dimension'].isin(['Collaboration Status', 'Comparison Delta'])].copy()
    df_colab_accounts = df_colab[df_colab['analysis_dimension'] == 'Partner Account Breakdown'].copy()
    
    save_dual_format(
        df_colab,
        "instagram_collaboration_analysis",
        additional_sheets={
            "Collaboration Overview": df_colab_overview,
            "Partner Accounts": df_colab_accounts
        }
    )
    print("  -> Generated collaboration analysis")

    # -------------------------------------------------------------------------
    # TABEL 5: Posting Time Analysis (instagram_posting_time_analysis)
    # -------------------------------------------------------------------------
    print("\n[5/7] Menghasilkan instagram_posting_time_analysis...")
    time_rows = []
    
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for day in day_order:
        sub = df_metrics[df_metrics['post_day_of_week'] == day]
        cnt = len(sub)
        if cnt > 0:
            q1_d = sub['total_interactions'].quantile(0.25)
            q3_d = sub['total_interactions'].quantile(0.75)
            time_rows.append({
                'time_dimension': 'Day of Week',
                'time_category': day,
                'post_count': cnt,
                'post_share_pct': round(cnt / len(df_metrics) * 100, 2),
                'total_interactions': int(sub['total_interactions'].sum()),
                'mean_interactions': round(float(sub['total_interactions'].mean()), 2),
                'median_interactions': round(float(sub['total_interactions'].median()), 2),
                'min_interactions': int(sub['total_interactions'].min()),
                'max_interactions': int(sub['total_interactions'].max()),
                'std_interactions': round(float(sub['total_interactions'].std()), 2) if cnt > 1 else 0.0,
                'iqr_interactions': round(float(q3_d - q1_d), 2)
            })
            
    bin_order = [
        'Morning (06:00-11:59)',
        'Afternoon (12:00-14:59)',
        'Late Afternoon (15:00-17:59)',
        'Evening/Night (18:00-23:59)'
    ]
    for tb in bin_order:
        sub = df_metrics[df_metrics['time_bin'] == tb]
        cnt = len(sub)
        if cnt > 0:
            q1_tb = sub['total_interactions'].quantile(0.25)
            q3_tb = sub['total_interactions'].quantile(0.75)
            time_rows.append({
                'time_dimension': 'Time of Day Bin',
                'time_category': tb,
                'post_count': cnt,
                'post_share_pct': round(cnt / len(df_metrics) * 100, 2),
                'total_interactions': int(sub['total_interactions'].sum()),
                'mean_interactions': round(float(sub['total_interactions'].mean()), 2),
                'median_interactions': round(float(sub['total_interactions'].median()), 2),
                'min_interactions': int(sub['total_interactions'].min()),
                'max_interactions': int(sub['total_interactions'].max()),
                'std_interactions': round(float(sub['total_interactions'].std()), 2) if cnt > 1 else 0.0,
                'iqr_interactions': round(float(q3_tb - q1_tb), 2)
            })
            
    for yr in sorted(df_metrics['post_year'].unique()):
        sub = df_metrics[df_metrics['post_year'] == yr]
        cnt = len(sub)
        q1_y = sub['total_interactions'].quantile(0.25)
        q3_y = sub['total_interactions'].quantile(0.75)
        time_rows.append({
            'time_dimension': 'Year',
            'time_category': str(yr),
            'post_count': cnt,
            'post_share_pct': round(cnt / len(df_metrics) * 100, 2),
            'total_interactions': int(sub['total_interactions'].sum()),
            'mean_interactions': round(float(sub['total_interactions'].mean()), 2),
            'median_interactions': round(float(sub['total_interactions'].median()), 2),
            'min_interactions': int(sub['total_interactions'].min()),
            'max_interactions': int(sub['total_interactions'].max()),
            'std_interactions': round(float(sub['total_interactions'].std()), 2) if cnt > 1 else 0.0,
            'iqr_interactions': round(float(q3_y - q1_y), 2)
        })
        
    df_time = pd.DataFrame(time_rows)
    hourly_df = df_metrics.groupby('post_hour_wib').agg(
        post_count=('post_id', 'count'),
        total_interactions=('total_interactions', 'sum'),
        mean_interactions=('total_interactions', 'mean'),
        median_interactions=('total_interactions', 'median'),
        min_interactions=('total_interactions', 'min'),
        max_interactions=('total_interactions', 'max')
    ).reset_index()
    hourly_df['hour_label'] = hourly_df['post_hour_wib'].apply(lambda h: f"{h:02d}:00 WIB")
    hourly_df = hourly_df[['post_hour_wib', 'hour_label', 'post_count', 'total_interactions', 'mean_interactions', 'median_interactions', 'min_interactions', 'max_interactions']]
    
    save_dual_format(
        df_time,
        "instagram_posting_time_analysis",
        additional_sheets={"Hourly Detail": hourly_df}
    )
    print("  -> Generated temporal analysis")
    # -------------------------------------------------------------------------
    # TABEL 6: Caption & Hashtag Analysis (instagram_caption_hashtag_analysis)
    # -------------------------------------------------------------------------
    print("\n[6/7] Menghasilkan instagram_caption_hashtag_analysis...")
    ch_rows = []
    
    features = [
        ('caption_word_count', 'Jumlah Kata Caption (Word Count)'),
        ('caption_length_clean', 'Panjang Karakter Caption Bersih'),
        ('hashtag_count', 'Jumlah Tagar (Hashtag Count)')
    ]
    for feat, label in features:
        p_r, p_p = stats.pearsonr(df_metrics[feat], df_metrics['total_interactions'])
        s_rho, s_p = stats.spearmanr(df_metrics[feat], df_metrics['total_interactions'])
        
        sig_flag = "Statistically Significant (p < 0.05)" if s_p < 0.05 else "Not Significant (p >= 0.05)"
        ch_rows.append({
            'analysis_dimension': 'Correlation Analysis',
            'feature_category': label,
            'sample_size': len(df_metrics),
            'missing_count': 0,
            'pearson_r': round(float(p_r), 4),
            'pearson_p_value': round(float(p_p), 4),
            'spearman_rho': round(float(s_rho), 4),
            'spearman_p_value': round(float(s_p), 4),
            'mean_interactions': None,
            'median_interactions': None,
            'min_interactions': None,
            'max_interactions': None,
            'notes': f"{sig_flag}; Spearman rho={s_rho:.3f} (Pearson r={p_r:.3f})"
        })
        
    u_stat, u_p = stats.mannwhitneyu(
        df_metrics[df_metrics['has_hashtags'] == True]['total_interactions'],
        df_metrics[df_metrics['has_hashtags'] == False]['total_interactions']
    )
    for flag in [False, True]:
        sub = df_metrics[df_metrics['has_hashtags'] == flag]
        status_label = "Tanpa Tagar (0 Hashtags / False)" if not flag else "Menggunakan Tagar (>=1 Hashtags / True)"
        ch_rows.append({
            'analysis_dimension': 'Hashtag Presence (has_hashtags)',
            'feature_category': status_label,
            'sample_size': len(sub),
            'missing_count': 0,
            'pearson_r': None,
            'pearson_p_value': None,
            'spearman_rho': None,
            'spearman_p_value': None,
            'mean_interactions': round(float(sub['total_interactions'].mean()), 2),
            'median_interactions': round(float(sub['total_interactions'].median()), 2),
            'min_interactions': int(sub['total_interactions'].min()),
            'max_interactions': int(sub['total_interactions'].max()),
            'notes': f"Mann-Whitney U={u_stat:.1f}, p={u_p:.4f} (Perbedaan terdistorsi kolaborasi pecahtelur.id)"
        })
        
    def classify_ht_bracket(h):
        if h == 0:
            return '0 hashtags (None)'
        elif 1 <= h <= 3:
            return '1-3 hashtags'
        elif 4 <= h <= 7:
            return '4-7 hashtags'
        else:
            return '8+ hashtags'
            
    df_metrics['ht_bracket'] = df_metrics['hashtag_count'].apply(classify_ht_bracket)
    for brk in ['0 hashtags (None)', '1-3 hashtags', '4-7 hashtags', '8+ hashtags']:
        sub = df_metrics[df_metrics['ht_bracket'] == brk]
        ch_rows.append({
            'analysis_dimension': 'Hashtag Count Brackets',
            'feature_category': brk,
            'sample_size': len(sub),
            'missing_count': 0,
            'pearson_r': None,
            'pearson_p_value': None,
            'spearman_rho': None,
            'spearman_p_value': None,
            'mean_interactions': round(float(sub['total_interactions'].mean()), 2),
            'median_interactions': round(float(sub['total_interactions'].median()), 2),
            'min_interactions': int(sub['total_interactions'].min()),
            'max_interactions': int(sub['total_interactions'].max()),
            'notes': f"Total interaksi: {sub['total_interactions'].sum()}"
        })
        
    def classify_wc_bracket(w):
        if w <= 20:
            return 'Short (<=20 words)'
        elif w <= 50:
            return 'Medium (21-50 words)'
        elif w <= 100:
            return 'Long (51-100 words)'
        else:
            return 'Very Long (>100 words)'
            
    df_metrics['wc_bracket'] = df_metrics['caption_word_count'].apply(classify_wc_bracket)
    for brk in ['Short (<=20 words)', 'Medium (21-50 words)', 'Long (51-100 words)', 'Very Long (>100 words)']:
        sub = df_metrics[df_metrics['wc_bracket'] == brk]
        ch_rows.append({
            'analysis_dimension': 'Caption Length Brackets',
            'feature_category': brk,
            'sample_size': len(sub),
            'missing_count': 0,
            'pearson_r': None,
            'pearson_p_value': None,
            'spearman_rho': None,
            'spearman_p_value': None,
            'mean_interactions': round(float(sub['total_interactions'].mean()), 2),
            'median_interactions': round(float(sub['total_interactions'].median()), 2),
            'min_interactions': int(sub['total_interactions'].min()),
            'max_interactions': int(sub['total_interactions'].max()),
            'notes': f"Total interaksi: {sub['total_interactions'].sum()}"
        })
        
    df_ch = pd.DataFrame(ch_rows)
    corr_df = df_ch[df_ch['analysis_dimension'] == 'Correlation Analysis'].copy()
    ht_df = df_ch[df_ch['analysis_dimension'].isin(['Hashtag Presence (has_hashtags)', 'Hashtag Count Brackets'])].copy()
    cap_df = df_ch[df_ch['analysis_dimension'] == 'Caption Length Brackets'].copy()
    
    save_dual_format(
        df_ch,
        "instagram_caption_hashtag_analysis",
        additional_sheets={
            "Correlations": corr_df,
            "Hashtag Groups": ht_df,
            "Caption Groups": cap_df
        }
    )
    print("  -> Generated caption & hashtag analysis")

    # -------------------------------------------------------------------------
    # TABEL 7: Top and Bottom Posts (instagram_top_posts)
    # -------------------------------------------------------------------------
    print("\n[7/7] Menghasilkan instagram_top_posts...")
    
    top10 = df_metrics_export.head(10).copy()
    top10['tier'] = 'Top 10 High Engagement'
    top10['rank'] = range(1, 11)
    
    bot10 = df_metrics_export.tail(10).copy().sort_values(by='total_interactions', ascending=True)
    bot10['tier'] = 'Bottom 10 Low Engagement'
    bot10['rank'] = range(55, 45, -1)
    
    combined_posts = pd.concat([top10, bot10], ignore_index=True)
    
    def snippet(text):
        if pd.isna(text):
            return ""
        s = str(text).replace("\n", " ").strip()
        return s[:80] + "..." if len(s) > 80 else s
        
    combined_posts['caption_snippet'] = combined_posts['post_id'].apply(
        lambda pid: snippet(df[df['post_id'] == pid]['caption_clean'].iloc[0])
    )
    
    top_cols = [
        'tier', 'rank', 'post_id', 'content_type', 'is_collaboration',
        'original_account', 'post_date', 'post_day_of_week', 'post_hour_wib',
        'likes', 'comments', 'total_interactions', 'caption_word_count',
        'hashtag_count', 'caption_snippet', 'post_url'
    ]
    df_top_posts = combined_posts[top_cols]
    
    top10_detailed = df_top_posts[df_top_posts['tier'] == 'Top 10 High Engagement']
    bot10_detailed = df_top_posts[df_top_posts['tier'] == 'Bottom 10 Low Engagement']
    
    save_dual_format(
        df_top_posts,
        "instagram_top_posts",
        additional_sheets={
            "Top 10 High Engagement": top10_detailed,
            "Bottom 10 Low Engagement": bot10_detailed
        }
    )
    print(f"  -> Generated top posts table (Top 1: {df_top_posts.iloc[0]['post_id']}, Bottom 1: {df_top_posts.iloc[10]['post_id']})")
    
    print("\n" + "=" * 75)
    print("ALL 7 INSTAGRAM ANALYSIS ARTIFACT PAIRS SUCCESSFULLY GENERATED!")
    print(f"Output directory: {OUTPUT_DIR}")
    print("=" * 75)
    return True


if __name__ == "__main__":
    success = run_analysis()
    if not success:
        sys.exit(1)