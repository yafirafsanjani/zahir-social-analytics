# Zahir Social Analytics

Social Media Analytics pipeline and interactive dashboard designed to evaluate brand performance, user engagement, customer sentiments, and cross-platform insights for **Zahir** using public Instagram content and Google Play Store user reviews.

---

## 📌 Project Overview & Objectives

**Zahir Social Analytics** is an academic and portfolio project that integrates multi-source social listening data into a unified business intelligence pipeline. The primary goals are:
- **Instagram Performance & Content Strategy**: Evaluate public post engagement, content formats, reach proxies, and hashtag efficacy on the official `@zahiraccounting` page.
- **Customer Voice on Google Play Store**: Uncover user experience themes, rating distributions, and pain points from real mobile application reviews.
- **Sentiment & Aspect-Based Analysis**: Dissect opinions into distinct aspects (e.g., usability, customer service, performance, pricing/features) across both platforms.
- **Cross-Platform Synthesis**: Bridge public marketing engagement with actual user satisfaction feedback in an interactive Streamlit dashboard.

---

## 📂 Project Structure

```text
zahir_social_analytics/
├── .venv_social/               # Isolated virtual environment (Python 3.11)
├── data/
│   ├── raw/                   # Raw data files (Git-ignored)
│   │   ├── instagram_posts_raw.csv    # Accessible public Instagram posts (CSV RFC 4180)
│   │   ├── instagram_posts_raw.xlsx   # Styled Excel spreadsheet (OpenPyXL)
│   │   └── playstore_reviews_raw.csv  # Authentic Play Store reviews
│   └── final/                 # Cleaned and processed datasets (Git-ignored)
│       ├── instagram_final.csv
│       └── playstore_final.csv
├── notebooks/                 # Core analysis notebooks (sequential pipeline)
│   ├── 01_instagram_scraping.ipynb
│   ├── 02_instagram_preprocessing.ipynb
│   ├── 03_instagram_eda.ipynb
│   ├── 04_playstore_preprocessing.ipynb
│   ├── 05_playstore_eda.ipynb
│   ├── 06_sentiment_analysis.ipynb
│   ├── 07_topic_analysis.ipynb
│   └── 08_cross_platform_analysis.ipynb
├── dashboard/                 # Interactive Streamlit application
│   └── app.py
├── config/                    # Configuration files and schemas
├── scraper/                   # Public data extraction utilities
│   └── instagram_scraper.py
├── preprocessing/             # Text cleaning and preprocessing modules
├── analysis/                  # Modeling and analytical utilities
├── .gitignore                 # Exclusion rules for secrets, venv, and datasets
├── requirements.txt           # Project dependencies
└── README.md                  # Public project documentation
```

---

## 🛠️ Tools & Technologies

- **Language & Runtime**: Python 3.11 (`.venv_social`)
- **Data Wrangling & Computing**: Pandas, NumPy, OpenPyXL
- **Visual Analytics**: Matplotlib, Seaborn, Plotly
- **Natural Language Processing**: NLTK, Scikit-learn
- **Automation / Web Ingestion**: Playwright (Async API for unauthenticated public extraction)
- **Application Interface**: Streamlit
- **Reproducibility**: Jupyter Notebooks, nbclient, nbformat

---

## 🚀 Pipeline & Methodology

1. **Ingestion & Data Preparation**:
   - Extract public post metadata from `@zahiraccounting` using Playwright without authentication.
   - Accurately categorize content types (`carousel`, `image`, `video/reel`) using profile grid badges.
   - Capture collaborative posts via `is_collaboration`, `original_account`, and `source_url`.
   - Export dual standardized raw data: **RFC 4180 CSV** (for programmatic pipelines) and **Styled XLSX** (for human spreadsheet viewing).
   - Ingest authentic user review records from the Google Play Store dataset.
2. **Preprocessing & Text Normalization**:
   - Cleaning captions and reviews (punctuation removal, lowercase conversion, slang normalization, Indonesian stopword filtering).
3. **Exploratory Data Analysis (EDA)**:
   - Instagram: engagement rate patterns, post types, hashtag distributions, temporal posting trends.
   - Play Store: rating trends over time, version comparisons, thumbs-up impact.
4. **Sentiment & Aspect / Topic Modeling**:
   - Polarity labeling and topic modeling to extract core customer themes.
5. **Interactive Executive Dashboard**:
   - Streamlit dashboard combining KPI summaries, sentiment charts, and strategic recommendations.

---

## 🔒 Data Ethics, Platform Limitations, and Responsible Usage

This project strictly follows ethical research and platform compliance guidelines:
- **Strict Public Access**: Extraction applies exclusively to publicly accessible web information. No CAPTCHAs, login walls, or anti-bot mechanisms are bypassed.
- **Accessible Session Limitation**: Without login, Instagram restricts grid viewing to the initial 12 public posts. In strict adherence to ethics, no attempt is made to bypass this restriction. The collected raw dataset represents **"seluruh postingan yang dapat diakses secara publik dalam sesi pengambilan data"**.
- **Dual Format Output**: Data raw disimpan dalam format CSV terenkapsulasi penuh (`QUOTE_ALL`) dan format Excel XLSX dengan penyesuaian lebar kolom agar tidak terpotong saat dibuka di spreadsheet.
- **Unavailable Public Metrics (`views`)**: Play counts/views are not exposed on unauthenticated Instagram web endpoints; these remain recorded as `NaN` without speculation.
- **Collaborative Posts**: Collaborative posts shown on `@zahiraccounting`'s public feed are tracked with complete provenance to distinguish internal content from co-authored posts.
- **Zero Credentials Policy**: No passwords, cookies, session IDs, or private tokens are requested, used, or stored.
- **Repository Safety**: Datasets (`data/raw/`, `data/final/`) and internal logs (`AGENTS.md`) are completely excluded via `.gitignore`.

---

## ⚙️ Getting Started

### 1. Prerequisites
- Python 3.11.x installed.
- Git.

### 2. Setting Up the Environment
```bash
# Clone the repository
git clone https://github.com/<your-username>/zahir-social-analytics.git
cd zahir-social-analytics

# Activate the virtual environment
# Windows PowerShell:
.\.venv_social\Scripts\Activate.ps1

# Install required dependencies
pip install -r requirements.txt
```

### 3. Data Ingestion
- Instagram: Run `python scraper/instagram_scraper.py` or execute `notebooks/01_instagram_scraping.ipynb`.
- Google Play Store: Place the authentic raw dataset at `data/raw/playstore_reviews_raw.csv`.

### 4. Running the Dashboard
```bash
streamlit run dashboard/app.py
```

---

## 📊 Project Milestones & Progress

- [x] **Fase 0: Setup Lingkungan & Tata Kelola Proyek**
- [x] **Fase 1: Scraping Data Publik Instagram & Standarisasi Output Ganda (CSV & XLSX)**
- [ ] **Fase 2: Ingestion & Verifikasi Dataset Play Store**
- [ ] **Fase 3: Preprocessing & Pembersihan Teks**
- [ ] **Fase 4: Exploratory Data Analysis (EDA)**
- [ ] **Fase 5: Analisis Sentimen & Topik**
- [ ] **Fase 6: Sintesis Cross-Platform & Dashboard Streamlit**
