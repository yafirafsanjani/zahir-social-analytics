import sys
import io
import re
import csv
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def clean_count(val):
    if not val or pd.isna(val):
        return np.nan
    val_str = str(val).strip().replace(',', '')
    if 'k' in val_str.lower():
        return int(float(val_str.lower().replace('k', '')) * 1000)
    if 'm' in val_str.lower():
        return int(float(val_str.lower().replace('m', '')) * 1000000)
    try:
        return int(val_str)
    except:
        return np.nan

def save_styled_excel(df, excel_path, sheet_name="Instagram_Data"):
    """Menyimpan DataFrame ke file Excel (.xlsx) dengan styling rapi dan lebar kolom proporsional."""
    try:
        with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name=sheet_name)
            ws = writer.sheets[sheet_name]
            
            # Style Header (Biru Navy Profesional + Teks Putih Tebal)
            header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
            header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
            thin_border = Border(
                left=Side(style="thin", color="D9D9D9"),
                right=Side(style="thin", color="D9D9D9"),
                top=Side(style="thin", color="D9D9D9"),
                bottom=Side(style="thin", color="D9D9D9")
            )
            
            for col_idx in range(1, len(df.columns) + 1):
                cell = ws.cell(row=1, column=col_idx)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                
            for row in ws.iter_rows(min_row=2, max_row=len(df)+1, min_col=1, max_col=len(df.columns)):
                for cell in row:
                    cell.border = thin_border
                    cell.alignment = Alignment(vertical="top", wrap_text=False)
                    
            # Set column widths agar tampilan Excel sangat rapi dan mudah dibaca
            for col in ws.columns:
                col_letter = col[0].column_letter
                col_name = str(col[0].value)
                if col_name == "caption":
                    ws.column_dimensions[col_letter].width = 50
                elif "url" in col_name:
                    ws.column_dimensions[col_letter].width = 38
                elif col_name in ["post_id", "post_date", "content_type", "original_account"]:
                    ws.column_dimensions[col_letter].width = 22
                elif col_name in ["hashtags"]:
                    ws.column_dimensions[col_letter].width = 30
                else:
                    ws.column_dimensions[col_letter].width = 16
        print(f"Berhasil menyimpan file XLSX rapi ke {excel_path}")
    except PermissionError:
        print(f"Perhatian: File {excel_path} sedang dibuka di Microsoft Excel. Silakan tutup file di Excel jika ingin menimpa langsung.")

def save_safe_csv(df, csv_path):
    """Menyimpan DataFrame ke CSV dengan enkapsulasi aman RFC 4180."""
    try:
        df.to_csv(csv_path, index=False, encoding="utf-8-sig", quoting=csv.QUOTE_ALL, lineterminator="\n")
        print(f"Berhasil menyimpan file CSV rapi ke {csv_path} (quoting=QUOTE_ALL)")
    except PermissionError:
        print(f"Perhatian: File {csv_path} sedang dibuka di Microsoft Excel. Silakan tutup file di Excel jika ingin menimpa langsung.")

def scrape_instagram_posts():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="id-ID"
        )
        page = context.new_page()
        profile_url = "https://www.instagram.com/zahiraccounting/"
        print(f"Mengakses profil publik: {profile_url}...")
        page.goto(profile_url, wait_until="networkidle", timeout=30000)
        
        soup = BeautifulSoup(page.content(), "html.parser")
        anchors = soup.find_all("a")
        discovered = []
        seen_ids = set()
        
        for a in anchors:
            href = a.get("href", "")
            if "/p/" in href or "/reel/" in href:
                match = re.search(r"/(?P<acc>[^/]+)/(?P<ptype>p|reel)/(?P<code>[^/]+)/", href)
                if not match:
                    match = re.search(r"/(?P<ptype>p|reel)/(?P<code>[^/]+)/", href)
                    acc = "zahiraccounting"
                else:
                    acc = match.group("acc")
                
                ptype = match.group("ptype")
                code = match.group("code")
                
                if code in seen_ids:
                    continue
                seen_ids.add(code)
                
                # Content type presisi dari badge grid profil
                a_text = a.get_text().strip().lower()
                svg_labels = [s.get("aria-label", "").lower() for s in a.find_all("svg") if s.get("aria-label")]
                all_labels = a_text + " " + " ".join(svg_labels)
                
                if "clip" in all_labels or ptype == "reel":
                    content_type = "video/reel"
                elif "carousel" in all_labels:
                    content_type = "carousel"
                else:
                    content_type = "image"
                    
                canonical_url = f"https://www.instagram.com/{ptype}/{code}/"
                source_url = f"https://www.instagram.com/{acc}/{ptype}/{code}/"
                
                is_collab = (acc.lower() != "zahiraccounting")
                orig_acc = acc.lower()
                
                discovered.append({
                    "post_id": code,
                    "post_url": canonical_url,
                    "source_url": source_url,
                    "content_type": content_type,
                    "is_collaboration": is_collab,
                    "original_account": orig_acc
                })
                
        print(f"Total postingan publik yang dapat diakses: {len(discovered)}")
        
        records = []
        for idx, item in enumerate(discovered, 1):
            url = item["post_url"]
            print(f"[{idx}/{len(discovered)}] Mengekstrak {url}...")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
                page.wait_for_timeout(1000)
                post_soup = BeautifulSoup(page.content(), "html.parser")
                
                meta_desc = post_soup.find("meta", attrs={"name": "description"})
                og_desc = post_soup.find("meta", attrs={"property": "og:description"})
                desc_text = ""
                if meta_desc and meta_desc.get("content"):
                    desc_text = meta_desc["content"]
                elif og_desc and og_desc.get("content"):
                    desc_text = og_desc["content"]
                    
                # Likes & Comments
                likes = np.nan
                comments = np.nan
                like_m = re.search(r"([0-9,.]+K?M?k?m?)\s+likes?", desc_text, re.IGNORECASE)
                if like_m:
                    likes = clean_count(like_m.group(1))
                comm_m = re.search(r"([0-9,.]+K?M?k?m?)\s+comments?", desc_text, re.IGNORECASE)
                if comm_m:
                    comments = clean_count(comm_m.group(1))
                    
                # Caption Extraction
                caption = None
                cap_m = re.search(r':\s*"(.*)"\s*\.?\s*$', desc_text, re.DOTALL)
                if cap_m:
                    caption = cap_m.group(1).strip()
                elif ': "' in desc_text:
                    parts = desc_text.split(': "', 1)
                    if len(parts) > 1:
                        caption = parts[1].rstrip('". ')
                else:
                    caption = desc_text if desc_text else None
                    
                # Date
                time_el = post_soup.find("time")
                post_date = time_el.get("datetime") if time_el else None
                
                # Views (Tidak tersedia di publik web tanpa login)
                views = np.nan
                
                # Hashtags & Caption Length
                if caption:
                    ht_list = re.findall(r"#(\w+)", caption)
                    hashtags_str = " ".join(["#" + h for h in ht_list]) if ht_list else None
                    ht_count = len(ht_list)
                    caption_len = len(caption)
                else:
                    hashtags_str = None
                    ht_count = 0
                    caption_len = 0
                    
                records.append({
                    "post_id": item["post_id"],
                    "post_url": item["post_url"],
                    "source_url": item["source_url"],
                    "post_date": post_date,
                    "content_type": item["content_type"],
                    "caption": caption,
                    "likes": likes,
                    "comments": comments,
                    "views": views,
                    "hashtags": hashtags_str,
                    "hashtag_count": ht_count,
                    "caption_length": caption_len,
                    "is_collaboration": item["is_collaboration"],
                    "original_account": item["original_account"]
                })
            except Exception as e:
                print(f"Error pada {url}: {e}")
                
        df = pd.DataFrame(records)
        browser.close()
        return df

if __name__ == "__main__":
    df = scrape_instagram_posts()
    
    # 1. Simpan ke CSV
    test_csv_path = "data/raw/instagram_test.csv"
    raw_csv_path = "data/raw/instagram_posts_raw.csv"
    save_safe_csv(df, test_csv_path)
    save_safe_csv(df, raw_csv_path)
    
    # 2. Simpan ke XLSX
    test_xlsx_path = "data/raw/instagram_test.xlsx"
    raw_xlsx_path = "data/raw/instagram_posts_raw.xlsx"
    save_styled_excel(df, test_xlsx_path, sheet_name="Instagram_Test")
    save_styled_excel(df, raw_xlsx_path, sheet_name="Instagram_Posts_Raw")
    
    # 3. Validasi pembacaan ulang DataFrame
    print("\n" + "="*50)
    print("VALIDASI PEMBACAAN ULANG (pd.read_csv / pd.read_excel):")
    # Gunakan file yang berhasil tersimpan
    try:
        test_df = pd.read_csv(raw_csv_path, encoding="utf-8-sig")
    except Exception:
        test_df = pd.read_excel(test_xlsx_path)
        
    print("test_df.shape:", test_df.shape)
    print("test_df.columns:", test_df.columns.tolist())
    print("\ntest_df.head():")
    print(test_df.head())
    
    print("\n" + "="*50)
    print("CEK STRUKTUR:")
    print("Rows:", len(test_df))
    print("Columns:", len(test_df.columns))
    print("\ntest_df.dtypes:\n", test_df.dtypes)
    print("\ntest_df.isna().sum():\n", test_df.isna().sum())
    
    print("\n" + "="*50)
    print("CEK CAPTION (3 CAPTION LENGKAP):")
    for i, caption in enumerate(test_df["caption"].head(3)):
        print(f"\n--- CAPTION {i+1} ---")
        print(caption)
        
    print("\n" + "="*50)
    print("CEK DUPLICATE:")
    print("Duplicate post_id:", test_df["post_id"].duplicated().sum())
    print("Duplicate post_url:", test_df["post_url"].duplicated().sum())
    
    print("\n" + "="*50)
    print("VALIDASI CONTENT_TYPE:")
    print(test_df["content_type"].value_counts(dropna=False))
    
    print("\nValidasi khusus DY0oTVmEgxY dan DWIQL4qAWVe:")
    special_check = test_df[test_df["post_id"].isin(["DY0oTVmEgxY", "DWIQL4qAWVe"])][["post_id", "content_type", "is_collaboration", "original_account"]]
    print(special_check)
