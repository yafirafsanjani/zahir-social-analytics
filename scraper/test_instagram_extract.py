import sys
import io
import re
import json
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def clean_count(val):
    if not val:
        return np.nan
    val = str(val).strip().replace(',', '')
    if 'k' in val.lower():
        return int(float(val.lower().replace('k', '')) * 1000)
    if 'm' in val.lower():
        return int(float(val.lower().replace('m', '')) * 1000000)
    try:
        return int(val)
    except:
        return np.nan

def run_test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="id-ID"
        )
        page = context.new_page()
        
        # 1. Access Public Profile
        profile_url = "https://www.instagram.com/zahiraccounting/"
        print(f"Navigating to {profile_url}...")
        response = page.goto(profile_url, wait_until="networkidle", timeout=30000)
        print(f"Profile Status: {response.status if response else 'Unknown'}")
        print(f"Profile Title: {page.title()}")
        print(f"Current URL: {page.url}")
        
        # 2. Discover Post URLs
        anchors = page.locator("a").all()
        links = []
        for a in anchors:
            href = a.get_attribute("href")
            if href and ("/p/" in href or "/reel/" in href):
                match = re.search(r"/(p|reel)/([^/]+)/", href)
                if match:
                    ptype, scode = match.groups()
                    full_url = f"https://www.instagram.com/{ptype}/{scode}/"
                    if full_url not in links:
                        links.append(full_url)
                        
        print(f"Total Unique Posts Discovered: {len(links)}")
        
        # Pick 8 posts for test extraction (between 5 and 10 posts as instructed)
        test_posts = links[:8]
        print(f"Selected {len(test_posts)} posts for extraction test.")
        
        records = []
        for idx, url in enumerate(test_posts, 1):
            print(f"[{idx}/{len(test_posts)}] Extracting {url}...")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
                page.wait_for_timeout(1000)
                html = page.content()
                soup = BeautifulSoup(html, "html.parser")
                
                # Post ID & Type
                sc_match = re.search(r"/(p|reel)/([^/]+)/", url)
                post_id = sc_match.group(2) if sc_match else None
                is_reel_url = "/reel/" in url
                
                # Meta description & OpenGraph
                meta_desc = soup.find("meta", attrs={"name": "description"})
                og_desc = soup.find("meta", attrs={"property": "og:description"})
                desc_text = ""
                if meta_desc and meta_desc.get("content"):
                    desc_text = meta_desc["content"]
                elif og_desc and og_desc.get("content"):
                    desc_text = og_desc["content"]
                    
                # Likes and Comments
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
                cap_match = re.search(r':\s*"(.*)"\s*\.?\s*$', desc_text, re.DOTALL)
                if cap_match:
                    caption = cap_match.group(1).strip()
                elif ": \"" in desc_text:
                    parts = desc_text.split(': "', 1)
                    if len(parts) > 1:
                        caption = parts[1].rstrip('". ')
                else:
                    caption = desc_text if desc_text else None
                    
                # Date
                time_el = soup.find("time")
                post_date = time_el.get("datetime") if time_el else None
                
                # Content Type determination
                video_el = soup.find("video")
                og_video = soup.find("meta", attrs={"property": "og:video"})
                if is_reel_url or video_el or og_video:
                    content_type = "video/reel"
                else:
                    # Check for carousel items or indicators
                    carousel_indicators = soup.find_all(attrs={"aria-label": re.compile(r"carousel|page|next|next slide", re.I)})
                    if len(carousel_indicators) > 0:
                        content_type = "carousel"
                    else:
                        content_type = "image"
                        
                # Views (publicly not accessible without login for posts/reels)
                views = np.nan
                
                # Hashtags & Caption Length
                if caption:
                    hashtags_list = re.findall(r"#(\w+)", caption)
                    hashtags_str = " ".join(["#" + h for h in hashtags_list]) if hashtags_list else None
                    hashtag_count = len(hashtags_list)
                    caption_length = len(caption)  # Defined as character count of caption
                else:
                    hashtags_str = None
                    hashtag_count = 0
                    caption_length = 0
                    
                records.append({
                    "post_id": post_id,
                    "post_url": url,
                    "post_date": post_date,
                    "content_type": content_type,
                    "caption": caption,
                    "likes": likes,
                    "comments": comments,
                    "views": views,
                    "hashtags": hashtags_str,
                    "hashtag_count": hashtag_count,
                    "caption_length": caption_length
                })
            except Exception as e:
                print(f"Error on {url}: {e}")
                
        df = pd.DataFrame(records)
        browser.close()
        return df

if __name__ == "__main__":
    df = run_test()
    print("\n" + "="*50)
    print("DATAFRAME PREVIEW (head):")
    print(df.head())
    print("\n" + "="*50)
    print("DATAFRAME INFO:")
    print(df.info())
    print("\n" + "="*50)
    print("MISSING VALUES COUNT:")
    print(df.isna().sum())
    print("\n" + "="*50)
    print(f"TOTAL TEST POSTS EXTRACTED: {len(df)}")
    
    # Save temporary test dataset
    df.to_csv("data/raw/instagram_test.csv", index=False, encoding="utf-8-sig")
    print("Saved test output to data/raw/instagram_test.csv (temporary, git-ignored)")
