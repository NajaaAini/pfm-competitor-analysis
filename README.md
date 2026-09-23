# 🚢 PFM Competitor Analysis

A Streamlit dashboard that benchmarks **Penang Ferry Museum** against 13 competing Penang attractions using 6,400+ reviews from **Google Maps** and **TripAdvisor**.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red?logo=streamlit&logoColor=white)

---

## ✨ Features

- **Executive Overview** — KPIs, rating distribution, platform comparison
- **Competitor Comparison** — side-by-side ratings, sentiment, comments
- **Topic Analysis** — 9 visitor themes mapped across attractions
- **Opportunity Finder** — where competitors outperform PFM
- **Geographic Map** — Folium map with attraction distances
- **Detail Explorer** — filter by attraction, rating, sentiment + word clouds
- **PFM Deep Dive** — PFM's own reviews and management insights

---

## 🛠 Tech Stack

Streamlit · Pandas · Altair · Folium · NLTK · scikit-learn · WordCloud · Geopy

---

## 🚀 Run Locally

```bash
git clone https://github.com/NajaaAini/pfm-competitor-analysis.git
cd pfm-competitor-analysis
pip install -r requirements.txt
streamlit run homepage.py
