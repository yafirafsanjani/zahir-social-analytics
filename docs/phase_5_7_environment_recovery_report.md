# Fase 5.7 - Environment Recovery & Regression Verification

Tanggal: 2026-11-03

## 1. Kondisi Sebelum Recovery

- Virtual environment `.venv_social` tidak dapat dijalankan. File `.venv_social/pyvenv.cfg` mengikat environment ke `C:\Users\Yafi Rafsanjani H\AppData\Local\Programs\Python\Python311\python.exe` versi 3.11.9, sementara interpreter tersebut tidak tersedia pada saat audit awal.
- Tidak ditemukan `pyproject.toml`, `Pipfile`, `environment.yml`, atau manifest dependency lain. `requirements.txt` adalah manifest resmi proyek.
- Instalasi package lama masih ada di `.venv_social`, tetapi tidak dapat digunakan tanpa base interpreter.
- Sebelum perubahan environment, checksum file sumber terlindungi dicatat. Tidak ada data raw, Gold Set, assignment remediated, baseline Instagram, maupun ekspor yang dimodifikasi selama recovery.

## 2. Recovery yang Dilakukan

1. Memasang ulang Python **3.11.9** user-level dari installer resmi Python.org agar persis sesuai dengan konfigurasi `pyvenv.cfg`.
2. Memverifikasi `.venv_social\Scripts\python.exe`: Python 3.11.9 dan pip 24.0 kembali dapat dijalankan.
3. Menjalankan `pip install --upgrade-strategy only-if-needed -r requirements.txt`; paket yang telah memenuhi batas minimum dipertahankan.
4. Dependency langsung yang sebelumnya belum tersedia dipenuhi: `plotly 7.1.0`, `streamlit 1.66.1`, `jupyterlab 4.6.5`, dan `python-dotenv 1.2.4`, beserta dependency transitif yang diperlukan pip.
5. Menjalankan `pip check`, import semua dependency utama, dan `python -m jupyter --version`.

## 3. Environment Akhir

- Python: 3.11.9
- pandas: 3.0.6; numpy: 2.4.6; openpyxl: 3.1.5; scipy: 1.17.1; scikit-learn: 1.9.1.
- matplotlib: 3.11.2; seaborn: 0.13.2; plotly: 7.1.0; streamlit: 1.66.1; playwright terpasang.
- ipykernel: 7.4.0; jupyterlab: 4.6.5; nbclient: 0.11.0; nbformat: 5.11.1.
- `pip check`: **No broken requirements found**. Import semua dependency pada `requirements.txt` berhasil. Jupyter, ipykernel, dan JupyterLab tersedia untuk notebook proyek.

## 4. Hasil Regression Verification

| Suite | Target | Hasil Aktual | Status |
| :--- | ---: | ---: | :--- |
| Fase 5.3 Aspect Analysis Remediation | 15 PASS | 15 PASS, 0 FAIL | PASS |
| Fase 5.4 Instagram Preprocessing | 13 PASS | 13 PASS, 0 FAIL | PASS |
| Fase 5.5 Instagram Engagement Analysis | 15 PASS | 15 PASS, 0 FAIL | PASS |
| Fase 5.6 Final Data Packaging | 15 PASS | 15 PASS, 0 FAIL | PASS |
| Consistency Audit Fase 5.6 | 10 PASS | 10 PASS, 0 FAIL | PASS |
| **Total** | **68 PASS** | **68 PASS, 0 FAIL** | **PASS** |

Tidak ada assertion dinonaktifkan atau dihapus. Tidak ditemukan kegagalan logika, dependency, maupun integritas data setelah environment dipulihkan.

## 5. Integritas Data

Checksum SHA-256 pasca-recovery:

| File | SHA-256 |
| :--- | :--- |
| `data/raw/instagram_posts_raw.csv` | `71DDC5101396E29876F319C08F9E5FC0E4408AE62F5F66B4535CF8E2B18AB192` |
| `data/raw/playstore_reviews_raw.csv` | `5A649ADCE76098531A7BE93405189242F13B19ED498059AD5F2C13EDA52A3B0B` |
| `data/final/playstore_gold_set_final.csv` | `9CEBFC47B0426FBDAAFBB91E1313D5DBF164E301F3DEF4F244856384FAE14240` |
| `data/final/topic_analysis/phase_5_3/review_aspect_assignments_remediated.csv` | `EA2C13A01B888AFF35C445B87710A9D05F1DAA12FD90F2ABFBEFBF4ED1F4237E` |
| `data/raw/instagram_posts_raw_phase1_6_baseline.csv` | `71DDC5101396E29876F319C08F9E5FC0E4408AE62F5F66B4535CF8E2B18AB192` |

Checksum sumber direkam sebelum dan sesudah recovery; tidak ada perubahan pada file sumber terlindungi. Suite Fase 5.3--5.6 juga memverifikasi immutability, relasi, dan nilai sumber secara otomatis.

## 6. Status Akhir

`.venv_social` kembali dapat digunakan dengan Python 3.11.9 dan dependency project yang tervalidasi. Environment siap menjalankan skrip analisis dan notebook yang menggunakan Jupyter/IPython. Recovery berhenti pada Fase 5.7; tidak ada pekerjaan Fase 6, scraping, dashboard, staging, commit, atau push yang dilakukan.