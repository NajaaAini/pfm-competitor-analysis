import pandas as pd
import streamlit as st
from streamlit_geolocation import streamlit_geolocation


# ============================================================
# GET USER GEOLOCATION
# ============================================================

def get_geolocation():
    return streamlit_geolocation()


# ============================================================
# CLEAN ATTRACTION NAMES
# ============================================================

def clean_attraction_name(name):

    if pd.isna(name):
        return name

    name = str(name).strip()

    name_mapping = {

        "Penang Ferry Museum":
            "Penang Ferry Museum",

        "The Penang Ferry Museum":
            "Penang Ferry Museum",

        "Ferry Museum Penang":
            "Penang Ferry Museum",

        "Pinang Peranakan Mansion":
            "Pinang Peranakan Mansion",

        "Peranakan Mansion":
            "Pinang Peranakan Mansion",

        "Khoo Kongsi":
            "Khoo Kongsi",

        "Leong San Tong Khoo Kongsi":
            "Khoo Kongsi",

        "Wonderfood Museum":
            "Wonderfood Museum",

        "The Habitat Penang Hill":
            "The Habitat Penang Hill",

        "Entopia by Penang Butterfly Farm":
            "Entopia by Penang Butterfly Farm",

        "Penang Hill":
            "Penang Hill",

        "Fort Cornwallis":
            "Fort Cornwallis",

        "Penang History Gallery":
            "Penang History Gallery",

        "Colonial Penang Museum":
            "Colonial Penang Museum",

        "Asia Camera Museum":
            "Asia Camera Museum",

        "Upside Down Museum":
            "Upside Down Museum",

        "Ghost Museum":
            "Ghost Museum",

        "The TOP Penang":
            "The TOP Penang, Theme Park Penang",

        "Theme Park Penang":
            "The TOP Penang, Theme Park Penang",

        "The TOP Penang, Theme Park Penang":
            "The TOP Penang, Theme Park Penang",

        "Tech Dome Penang":
            "Tech Dome Penang",

        "ESCAPE Penang":
            "ESCAPE Penang",

        "Botanical Gardens Penang":
            "Botanical Gardens Penang",

        "Chew Jetty":
            "Chew Jetty"
    }

    return name_mapping.get(
        name,
        name.title()
    )


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    google_file = (
        "dataset_Google-Maps-Reviews-Scraper_2026-09-21_03-47-05-709.xlsx"
    )

    trip_file = (
        "dataset_tripadvisor-reviews_2026-09-21_03-27-44-975.xlsx"
    )


    # --------------------------------------------------------
    # GOOGLE MAPS
    # --------------------------------------------------------

    google_df = pd.read_excel(
        google_file,
        sheet_name="Data"
    )

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


    # --------------------------------------------------------
    # TRIPADVISOR
    # --------------------------------------------------------

    trip_df = pd.read_excel(
        trip_file,
        sheet_name="Data"
    )

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


    # --------------------------------------------------------
    # COMBINE DATA
    # --------------------------------------------------------

    master = pd.concat(
        [
            google_clean,
            trip_clean
        ],
        ignore_index=True
    )


    # --------------------------------------------------------
    # CLEAN DATA
    # --------------------------------------------------------

    master = master.dropna(
        subset=[
            "text",
            "rating"
        ]
    )

    master["attraction_name"] = (
        master["attraction_name"]
        .apply(clean_attraction_name)
    )


    return master