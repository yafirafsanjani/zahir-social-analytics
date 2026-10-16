import csv
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Load source dataset
src_path = 'data/final/playstore_reviews_final.csv'
df_src = pd.read_csv(src_path)

print(f"Loaded source dataset with {len(df_src)} records.")

# Prepare target columns
cols = [
    'review_id',
    'app_name',
    'review_datetime',
    'review_text_clean',
    'human_sentiment_label',
    'needs_review',
    'annotation_notes'
]

# Create DataFrame for gold set
df_gold = pd.DataFrame()
df_gold['review_id'] = df_src['review_id'].astype(str)
df_gold['app_name'] = df_src['app_name'].astype(str)
df_gold['review_datetime'] = pd.to_datetime(df_src['review_datetime']).dt.strftime('%Y-%m-%d %H:%M:%S')
df_gold['review_text_clean'] = df_src['review_text_clean'].astype(str)

# Ensure annotation columns are explicitly blank
df_gold['human_sentiment_label'] = ""
df_gold['needs_review'] = ""
df_gold['annotation_notes'] = ""

# 1. Save CSV version (RFC 4180 standard, quoting non-numeric/all text)
csv_target = 'data/final/playstore_gold_set_template.csv'
df_gold.to_csv(csv_target, index=False, encoding='utf-8', quoting=csv.QUOTE_ALL)
print(f"Successfully generated CSV: {csv_target} ({len(df_gold)} rows)")

# 2. Save XLSX version with openpyxl
xlsx_target = 'data/final/playstore_gold_set_template.xlsx'
wb = openpyxl.Workbook()

# Primary worksheet: Gold Set
ws_gold = wb.active
ws_gold.title = "Gold Set"

# Write headers
headers = [
    "review_id",
    "app_name",
    "review_datetime",
    "review_text_clean",
    "human_sentiment_label",
    "needs_review",
    "annotation_notes"
]
ws_gold.append(headers)

# Styling definitions
header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")  # Professional navy
header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

# Annotation target header highlight (subtle warm accent to draw annotator's focus)
annot_fill = PatternFill(start_color="244062", end_color="244062", fill_type="solid")

thin_border = Border(
    left=Side(style='thin', color='D9D9D9'),
    right=Side(style='thin', color='D9D9D9'),
    top=Side(style='thin', color='D9D9D9'),
    bottom=Side(style='thin', color='D9D9D9')
)

ws_gold.row_dimensions[1].height = 28

for col_idx, header in enumerate(headers, 1):
    cell = ws_gold.cell(row=1, column=col_idx)
    cell.font = header_font
    cell.fill = annot_fill if col_idx in [5, 6, 7] else header_fill
    cell.alignment = header_align
    cell.border = thin_border

# Write rows
text_font = Font(name="Calibri", size=10)
align_left = Alignment(horizontal="left", vertical="top", wrap_text=False)
align_center = Alignment(horizontal="center", vertical="top", wrap_text=False)
align_wrap = Alignment(horizontal="left", vertical="top", wrap_text=True)

for r_idx, row in df_gold.iterrows():
    row_num = r_idx + 2
    
    ws_gold.cell(row=row_num, column=1, value=row['review_id']).alignment = align_left
    ws_gold.cell(row=row_num, column=2, value=row['app_name']).alignment = align_left
    ws_gold.cell(row=row_num, column=3, value=row['review_datetime']).alignment = align_center
    ws_gold.cell(row=row_num, column=4, value=row['review_text_clean']).alignment = align_wrap
    
    # Blank cells for manual annotation
    ws_gold.cell(row=row_num, column=5, value=None).alignment = align_center
    ws_gold.cell(row=row_num, column=6, value=None).alignment = align_center
    ws_gold.cell(row=row_num, column=7, value=None).alignment = align_wrap
    
    for c_idx in range(1, 8):
        c = ws_gold.cell(row=row_num, column=c_idx)
        c.font = text_font
        c.border = thin_border

# Freeze header row
ws_gold.freeze_panes = "A2"

# Enable filter across data table
ws_gold.auto_filter.ref = f"A1:G{len(df_gold) + 1}"

# Set column widths
col_widths = {
    1: 36,  # review_id
    2: 24,  # app_name
    3: 20,  # review_datetime
    4: 65,  # review_text_clean
    5: 24,  # human_sentiment_label
    6: 16,  # needs_review
    7: 35   # annotation_notes
}
for col_idx, width in col_widths.items():
    col_letter = get_column_letter(col_idx)
    ws_gold.column_dimensions[col_letter].width = width

# -------------------------------------------------------------
# Secondary Worksheet: Annotation Guide
# -------------------------------------------------------------
ws_guide = wb.create_sheet(title="Annotation Guide")

guide_title_font = Font(name="Calibri", size=14, bold=True, color="1F497D")
section_font = Font(name="Calibri", size=11, bold=True, color="1F497D")
table_header_fill = PatternFill(start_color="DCE6F1", end_color="DCE6F1", fill_type="solid")
table_header_font = Font(name="Calibri", size=10, bold=True)
regular_font = Font(name="Calibri", size=10)
italic_font = Font(name="Calibri", size=10, italic=True)

ws_guide.cell(row=1, column=1, value="PANDUAN ANOTASI SENTIMEN GOOGLE PLAY STORE").font = guide_title_font
ws_guide.cell(row=2, column=1, value="Zahir Social Analytics - Human Sentiment Gold Set (417 Ulasan)").font = italic_font

guide_content = [
    (4, "1. TAKSONOMI LABEL SENTIMEN", section_font),
    (5, "Kolom 'human_sentiment_label' diisi dengan salah satu dari 4 opsi nilai berikut:", regular_font),
]
for r, text, fnt in guide_content:
    c = ws_guide.cell(row=r, column=1, value=text)
    c.font = fnt

# Guideline Table Headers
guide_headers = ["Label", "Definisi Operasional", "Kriteria Anotasi", "Contoh Hipotetis (Bukan Data Asli)"]
for c_idx, h in enumerate(guide_headers, 1):
    c = ws_guide.cell(row=7, column=c_idx, value=h)
    c.font = table_header_font
    c.fill = table_header_fill
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    c.border = thin_border
ws_guide.row_dimensions[7].height = 24

guide_rows = [
    (
        "positive",
        "Teks mengekspresikan kepuasan, pujian, kepuasan fitur, atau pengalaman positif.",
        "Pujian langsung, rasa terbantu, rekomendasi kepada orang lain, apresiasi kehandalan.",
        "\"Aplikasi sangat membantu pencatatan toko, simpel dan mudah dipahami.\""
    ),
    (
        "neutral",
        "Teks faktual murni, pertanyaan tanpa keluhan/pujian, atau opini berimbang tanpa polaritas dominan.",
        "Pertanyaan teknis/fitur tanpa emosi, pernyataan status update, masukan seimbang.",
        "\"Apakah ada versi desktop yang bisa langsung sinkron real-time?\""
    ),
    (
        "negative",
        "Teks mengekspresikan ketidakpuasan, komplain, kritik tajam, bug, error, atau kendala teknis.",
        "Laporan crash/force close, gagal login, data hilang, keluhan biaya/kebijakan, sistem lambat.",
        "\"Sering keluar sendiri saat cetak laporan, data transaksi kemarin tidak tersimpan.\""
    ),
    (
        "needs_review",
        "Teks tidak dapat dipahami, sangat ambigu, typo berat, atau konteks tidak memadai.",
        "Karakter acak, bahasa tidak teridentifikasi, teks terpotong ekstrem, atau sarkasme ambigu.",
        "\"asdfghjk\" atau teks tanpa makna opini."
    )
]

for idx, g_row in enumerate(guide_rows, 8):
    ws_guide.row_dimensions[idx].height = 42
    for c_idx, val in enumerate(g_row, 1):
        c = ws_guide.cell(row=idx, column=c_idx, value=val)
        c.font = regular_font
        c.border = thin_border
        c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        if c_idx == 1:
            c.font = Font(name="Calibri", size=10, bold=True)
            c.alignment = Alignment(horizontal="center", vertical="center")

# Key Rules Section
rules_start = 14
ws_guide.cell(row=rules_start, column=1, value="2. ATURAN PENTING ANOTASI").font = section_font
rules = [
    "1. Berdasarkan Teks Saja: Jangan berasumsi sentimen dari rating bintang. Rating rendah bisa memuji, rating tinggi bisa mengeluh.",
    "2. Ulasan Campuran: Jika ada positif dan negatif, pilih sentimen yang dominan. Jika benar-benar seimbang, pilih 'neutral'.",
    "3. Kolom 'needs_review': Isi 'TRUE' jika Anda ragu-ragu dan ingin ulasan tersebut didiskusikan ulang bersama tim.",
    "4. Kolom 'annotation_notes': Gunakan untuk mencatat konteks khusus, misalnya indikasi sarkasme atau slang daerah.",
    "5. Preservasi Teks: Jangan mengubah atau mengedit teks ulasan pada kolom 'review_text_clean'."
]
for idx, rule in enumerate(rules, rules_start + 1):
    c = ws_guide.cell(row=idx, column=1, value=rule)
    c.font = regular_font

# Guide column widths
ws_guide.column_dimensions['A'].width = 16
ws_guide.column_dimensions['B'].width = 38
ws_guide.column_dimensions['C'].width = 42
ws_guide.column_dimensions['D'].width = 45

# Save workbook
wb.save(xlsx_target)
print(f"Successfully generated XLSX: {xlsx_target} ({len(df_gold)} rows across 2 sheets)")
