import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from pathlib import Path

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
        <div style="text-align: center; margin-top: 0;">
            <img src="data:image/jpeg;base64,{img_b64}"
                width="220"
                style="display: inline-block; vertical-align: middle; margin-bottom: -40px;"/>
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
    margin: 0;
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


# ============================================================
# ATTRACTION LOCATIONS MAP
# ============================================================

st.markdown("---")

st.markdown("## Attraction Locations")

st.markdown("""
<p class="pfm-description">
    Explore the locations of Penang Ferry Museum and its competitors across Penang.
</p>
""", unsafe_allow_html=True)


# ---------- ATTRACTION COORDINATES ----------
attraction_coords = {

    "Penang Ferry Museum":
        (5.415545698678018, 100.34328173033566),

    "Pinang Peranakan Mansion":
        (5.418681884875115, 100.34146202239594),

    "Khoo Kongsi":
        (5.415727156015716, 100.33886362872535),

    "Wonderfood Museum":
        (5.417123363369828, 100.341871175829),

    "The Habitat Penang Hill":
        (5.426160535647011, 100.27157025039966),

    "Entopia by Penang Butterfly Farm":
        (5.448518563592429, 100.21520880705607),

    "Penang Hill":
        (5.409997882396369, 100.27561397161718),

    "Fort Cornwallis":
        (5.421268681174111, 100.34648002078593),

    "Penang History Gallery":
        (5.420484829297916, 100.33972388430617),

    "Colonial Penang Museum":
        (5.430396696213923, 100.30643358430729),

    "Asia Camera Museum":
        (5.4159403983369385, 100.33706702239564),

    "Upside Down Museum":
        (5.416445369192765, 100.33357244567907),

    "Ghost Museum":
        (5.4150170291131925, 100.33473298430552),

    "The TOP Penang, Theme Park Penang":
        (5.414881551517756, 100.3294207843056),

    "Tech Dome Penang":
        (5.415041413965149, 100.3306715223955),

    "ESCAPE Penang":
        (5.451022051948458, 100.21360877690643),

    "Botanical Gardens Penang":
        (5.438928533486615, 100.29065521499493),

    "Chew Jetty":
        (5.4141273029603925, 100.34002972239536)
}


# ---------- ATTRACTION SELECTOR ----------
selected_attraction = st.selectbox(
    "Select an attraction",
    ["All"] + sorted(
        df["attraction_name"]
        .dropna()
        .unique()
        .tolist()
    )
)


# ---------- VIEW: SELECTED ATTRACTION ----------
if selected_attraction != "All":

    specific_df = df[
        df["attraction_name"]
        .str.strip()
        == selected_attraction.strip()
    ].copy()

    if not specific_df.empty:

        col_info, col_map = st.columns([1, 1])

        # ---------- ATTRACTION INFORMATION ----------
        with col_info:

            st.markdown("""
            <p class="pfm-card-title">
                🏛️ Attraction Overview
            </p>
            """, unsafe_allow_html=True)

            total_revs = len(specific_df)

            avg_rating = round(
                specific_df["rating"].mean(),
                2
            )

            # Sentiment from rating
            specific_df["sentiment"] = specific_df["rating"].apply(
                lambda x: "Positive" if x >= 4
                else ("Neutral" if x == 3 else "Negative")
            )

            positive_rate = (
                specific_df["sentiment"]
                .eq("Positive")
                .mean() * 100
            )

            negative_rate = (
                specific_df["sentiment"]
                .eq("Negative")
                .mean() * 100
            )

            platforms_used = ", ".join(
                specific_df["platform"]
                .dropna()
                .unique()
            )

            specific_df["date"] = pd.to_datetime(
                specific_df["date"],
                errors="coerce"
            )

            latest_date = specific_df["date"].max()

            if pd.notna(latest_date):
                latest_date_text = latest_date.strftime("%d %b %Y")
            else:
                latest_date_text = "N/A"

            st.markdown(
                f"""
                <div class="pfm-card">

                <p class="pfm-card-title">
                    {selected_attraction}
                </p>

                <p class="pfm-description">
                    Performance summary based on the available
                    Google Maps and TripAdvisor reviews.
                </p>

                <b>Reviews Tracked:</b>
                {total_revs:,}<br>

                <b>Average Rating:</b>
                {avg_rating} / 5.0 ⭐<br>

                <b>Positive Reviews:</b>
                {positive_rate:.1f}%<br>

                <b>Negative Reviews:</b>
                {negative_rate:.1f}%<br>

                <b>Latest Review:</b>
                {latest_date_text}<br>

                <b>Platforms:</b>
                {platforms_used}

                </div>
                """,
                unsafe_allow_html=True
            )

        # ---------- MAP ----------
        with col_map:

            st.markdown("""
            <p class="pfm-card-title">
                🗺️ Location
            </p>
            """, unsafe_allow_html=True)

            coords = attraction_coords.get(
                selected_attraction,
                (5.4164, 100.3400)
            )

            lat, lon = coords

            m = folium.Map(
                location=[lat, lon],
                zoom_start=15,
                control_scale=True
            )

            folium.Marker(
                [lat, lon],
                popup=selected_attraction,
                tooltip=selected_attraction,
                icon=folium.Icon(
                    color="red",
                    icon="ship",
                    prefix="fa"
                )
            ).add_to(m)

            st_folium(
                m,
                height=350,
                use_container_width=True
            )


# ---------- VIEW: ALL ATTRACTIONS ----------
else:

    m = folium.Map(
        location=[5.4164, 100.3400],
        zoom_start=13,
        control_scale=True
    )

    for name, coords in attraction_coords.items():

        folium.Marker(
            [coords[0], coords[1]],
            popup=name,
            tooltip=name,
            icon=folium.Icon(
                color="red",
                icon="ship",
                prefix="fa"
            )
        ).add_to(m)

    st_folium(
        m,
        height=500,
        use_container_width=True
    )
