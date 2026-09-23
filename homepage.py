import streamlit as st
import pandas as pd
from pathlib import Path
from streamlit_geolocation import streamlit_geolocation

from styles import apply_global_styles, render_sidebar


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Penang Ferry Museum & Attractions Dashboard",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# GLOBAL STYLES
# ============================================================

apply_global_styles()


# ============================================================
# GEOLOCATION
# ============================================================

def get_geolocation():
    return streamlit_geolocation()


# ============================================================
# CLEAN ATTRACTION NAME
# ============================================================

def clean_attraction_name(raw_name):

    if pd.isna(raw_name):
        return "Unknown"

    name = str(raw_name).strip().title()

    mapping = {

        "Penang Ferry Museum": [
            "Penang Ferry Museum",
            "The Penang Ferry Museum",
            "Ferry Museum Penang"
        ],

        "Pinang Peranakan Mansion": [
            "Pinang Peranakan Mansion",
            "Peranakan Mansion"
        ],

        "Khoo Kongsi": [
            "Khoo Kongsi",
            "Leong San Tong Khoo Kongsi"
        ],

        "Wonderfood Museum": [
            "Wonderfood Museum",
            "Wonderfood Museum Penang"
        ],

        "The Habitat Penang Hill": [
            "The Habitat Penang Hill",
            "The Habitat"
        ],

        "Entopia by Penang Butterfly Farm": [
            "Entopia",
            "Entopia By Penang Butterfly Farm",
            "Penang Butterfly Farm"
        ],

        "Penang Hill": [
            "Penang Hill",
            "Bukit Bendera"
        ],

        "Fort Cornwallis": [
            "Fort Cornwallis"
        ],

        "Penang History Gallery": [
            "Penang History Gallery"
        ],

        "Colonial Penang Museum": [
            "Colonial Penang Museum"
        ],

        "Asia Camera Museum": [
            "Asia Camera Museum"
        ],

        "Upside Down Museum": [
            "Upside Down Museum"
        ],

        "Ghost Museum": [
            "Ghost Museum"
        ],

        "The TOP Penang, Theme Park Penang": [
            "The Top Penang",
            "The TOP Penang, Theme Park Penang",
            "The Top"
        ],

        "Tech Dome Penang": [
            "Tech Dome Penang"
        ],

        "ESCAPE Penang": [
            "Escape Penang",
            "ESCAPE Penang",
            "Escape Theme Park"
        ],

        "Botanical Gardens Penang": [
            "Botanical Gardens Penang",
            "Penang Botanical Gardens"
        ],

        "Chew Jetty": [
            "Chew Jetty",
            "Clan Jetties Of Penang",
            "Chew Thean Yeang Jetty"
        ]

    }

    for canonical_name, variants in mapping.items():

        for v in variants:

            if v.lower() in name.lower():
                return canonical_name

    return name


# ============================================================
# LOAD AND CLEAN DATA
# ============================================================

@st.cache_data
def load_data():

    google_file = (
        "dataset_Google-Maps-Reviews-Scraper_2026-09-21_03-47-05-709.xlsx"
    )

    trip_file = (
        "dataset_tripadvisor-reviews_2026-09-21_03-27-44-975.xlsx"
    )

    # Read Google Maps data
    google_df = pd.read_excel(
        google_file,
        sheet_name="Data"
    )

    # Read TripAdvisor data
    trip_df = pd.read_excel(
        trip_file,
        sheet_name="Data"
    )

    # Clean Google data
    google_clean = pd.DataFrame({

        "attraction_name":
            google_df["title"],

        "platform":
            "Google Maps",

        "rating":
            google_df["stars"],

        "text":
            google_df["text"],

        "date":
            google_df["publishedAtDate"]

    })

    # Clean TripAdvisor data
    trip_clean = pd.DataFrame({

        "attraction_name":
            trip_df["placeInfo/name"],

        "platform":
            "TripAdvisor",

        "rating":
            trip_df["rating"],

        "text":
            trip_df["text"],

        "date":
            trip_df["publishedDate"]

    })

    # Combine datasets
    master = pd.concat(
        [
            google_clean,
            trip_clean
        ],
        ignore_index=True
    )

    # Remove missing reviews and ratings
    master = master.dropna(
        subset=[
            "text",
            "rating"
        ]
    )

    # Standardize attraction names
    master["attraction_name"] = (
        master["attraction_name"]
        .apply(clean_attraction_name)
    )

    return master


# ============================================================
# LOAD DATA
# ============================================================

df = load_data()


# ============================================================
# SIDEBAR (standardised)
# ============================================================

render_sidebar(current_page="homepage")


# ============================================================
# DASHBOARD HEADER
# ============================================================

import base64

BASE_DIR = Path(__file__).resolve().parent
IMAGE_PATH = BASE_DIR / "images (1).jpg"

# ---------- LOGO (centered via base64) ----------
if IMAGE_PATH.exists():
    with open(IMAGE_PATH, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <div style="text-align: center; margin-top: 10px;">
            <img src="data:image/jpeg;base64,{img_b64}"
                 width="220"
                 style="display: inline-block;"/>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        "<div style='text-align:center;font-size:80px;'>🚢</div>",
        unsafe_allow_html=True,
    )

# ---------- TITLE ----------
st.markdown("""
<h1 style="
    text-align: center;
    color: #292929;
    font-family: 'Poppins', Arial, sans-serif;
    font-size: 38px;
    font-weight: 800;
    margin: 15px 0 0 0;
    padding: 0;
">
    Penang Ferry Museum
</h1>
""", unsafe_allow_html=True)

# ---------- SUBTITLE ----------
st.markdown("""
<h3 style="
    text-align: center;
    color: #666666;
    font-family: 'Lato', Arial, sans-serif;
    font-size: 19px;
    font-weight: 500;
    margin: 5px 0 0 0;
    padding: 0;
">
    Competitor Analysis
</h3>
""", unsafe_allow_html=True)

# ---------- YELLOW DIVIDER ----------
st.markdown("""
<p style="
    text-align: center;
    color: #F2B705;
    font-size: 18px;
    margin: 5px 0 20px 0;
    padding: 0;
">
    ━━━━━
</p>
""", unsafe_allow_html=True)

# ============================================================
# MAIN DATA OVERVIEW
# ============================================================

st.markdown("## Dataset Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Reviews",
        f"{len(df):,}"
    )

with col2:
    st.metric(
        "Attractions",
        f"{df['attraction_name'].nunique():,}"
    )

with col3:
    st.metric(
        "Google Maps Reviews",
        f"{(df['platform'] == 'Google Maps').sum():,}"
    )

with col4:
    st.metric(
        "TripAdvisor Reviews",
        f"{(df['platform'] == 'TripAdvisor').sum():,}"
    )


# ============================================================
# DATASET INFORMATION
# ============================================================

st.markdown("---")

st.markdown("## Dataset Information")

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("""
        <h3 style="
            color:#292929;
            font-family:Poppins,Arial,sans-serif;
            font-size:20px;
            font-weight:700;
            margin:0 0 8px 0;
        ">
            🗺️ Google Maps
        </h3>
        """, unsafe_allow_html=True)

        st.markdown("""
        <p style="
            color:#666666;
            font-family:Lato,Arial,sans-serif;
            font-size:14px;
            line-height:1.6;
            margin:0;
        ">
            Reviews collected from Google Maps,
            including attraction names, ratings,
            review text and publication dates.
        </p>
        """, unsafe_allow_html=True)

with col2:
    with st.container(border=True):
        st.markdown("""
        <h3 style="
            color:#292929;
            font-family:Poppins,Arial,sans-serif;
            font-size:20px;
            font-weight:700;
            margin:0 0 8px 0;
        ">
            ⭐ TripAdvisor
        </h3>
        """, unsafe_allow_html=True)

        st.markdown("""
        <p style="
            color:#666666;
            font-family:Lato,Arial,sans-serif;
            font-size:14px;
            line-height:1.6;
            margin:0;
        ">
            Reviews collected from TripAdvisor,
            including attraction names, ratings,
            review text and publication dates.
        </p>
        """, unsafe_allow_html=True)


# ============================================================
# ATTRACTION SUMMARY
# ============================================================

st.markdown("## Attraction Summary")

summary = (
    df.groupby("attraction_name")
    .agg(
        Reviews=("rating", "count"),
        Average_Rating=("rating", "mean")
    )
    .reset_index()
)

summary["Average_Rating"] = (
    summary["Average_Rating"]
    .round(2)
)

summary = summary.sort_values(
    "Reviews",
    ascending=False
)

st.dataframe(
    summary,
    use_container_width=True,
    hide_index=True
)