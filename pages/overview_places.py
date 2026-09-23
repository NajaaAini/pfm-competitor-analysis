import streamlit as st
import pandas as pd
import altair as alt
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
import re
import nltk

from wordcloud import STOPWORDS
from nltk.sentiment import SentimentIntensityAnalyzer

from data_loader import load_data, get_geolocation
from styles import apply_global_styles, render_sidebar, YELLOW


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Overview | Penang Ferry Museum",
    page_icon="🚢",
    layout="wide"
)


# ============================================================
# GLOBAL STYLES
# ============================================================

apply_global_styles()


# ============================================================
# LOAD DATA
# ============================================================

df = load_data().copy()


# ============================================================
# BASIC CLEANING
# ============================================================

df["text"] = (
    df["text"]
    .fillna("")
    .astype(str)
)

df["rating"] = pd.to_numeric(
    df["rating"],
    errors="coerce"
)

df = df.dropna(
    subset=["rating"]
).copy()

df["date"] = pd.to_datetime(
    df["date"],
    errors="coerce"
)

df["month"] = (
    df["date"]
    .dt.to_period("M")
    .astype(str)
)


# ============================================================
# SENTIMENT
# ============================================================

def map_sentiment(rating):

    if rating >= 4:
        return "Positive"

    elif rating == 3:
        return "Neutral"

    return "Negative"


df["sentiment"] = df["rating"].apply(
    map_sentiment
)


# ============================================================
# SIDEBAR (standardised)
# ============================================================

render_sidebar(current_page="overview_places")


# ============================================================
# PAGE HEADER
# ============================================================

st.markdown("""
<p class="pfm-page-title">
     Executive Overview
</p>

<p class="pfm-page-subtitle">
    Penang Ferry Museum &amp; Attractions Analytics
</p>

<p class="pfm-yellow-line">
    ━━━━━
</p>
""", unsafe_allow_html=True)


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_reviews = len(df)

total_attractions = (
    df["attraction_name"]
    .nunique()
)

overall_avg_rating = round(
    df["rating"].mean(),
    2
)

positive_percentage = (
    df["sentiment"]
    .eq("Positive")
    .mean()
    * 100
)

negative_percentage = (
    df["sentiment"]
    .eq("Negative")
    .mean()
    * 100
)


# ============================================================
# PFM METRICS
# ============================================================

pfm_df = df[
    df["attraction_name"]
    .eq("Penang Ferry Museum")
].copy()

pfm_reviews = len(pfm_df)

pfm_rating = (
    round(
        pfm_df["rating"].mean(),
        2
    )
    if not pfm_df.empty
    else 0
)

pfm_positive = (
    pfm_df["sentiment"]
    .eq("Positive")
    .mean() * 100
    if not pfm_df.empty
    else 0
)


# ============================================================
# KPI CARDS
# ============================================================

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Total Reviews",
        f"{total_reviews:,}"
    )

with col2:
    st.metric(
        "Average Rating",
        f"{overall_avg_rating} / 5"
    )

with col3:
    st.metric(
        "Positive Reviews",
        f"{positive_percentage:.1f}%"
    )

with col4:
    st.metric(
        "Attractions Tracked",
        f"{total_attractions}"
    )

with col5:
    st.metric(
        "PFM Rating",
        f"{pfm_rating} / 5"
    )


# ============================================================
# PFM SNAPSHOT
# ============================================================

st.markdown("---")

st.markdown("""
<p class="pfm-section-title">
     Penang Ferry Museum Snapshot
</p>
""", unsafe_allow_html=True)

snapshot_col1, snapshot_col2, snapshot_col3, snapshot_col4 = st.columns(4)

with snapshot_col1:
    st.metric(
        "PFM Reviews",
        f"{pfm_reviews:,}"
    )

with snapshot_col2:
    st.metric(
        "PFM Rating",
        f"{pfm_rating} / 5"
    )

with snapshot_col3:
    st.metric(
        "Positive Reviews",
        f"{pfm_positive:.1f}%"
    )

with snapshot_col4:

    if not pfm_df.empty:

        latest_pfm_date = pfm_df["date"].max()

        if pd.notna(latest_pfm_date):
            latest_text = latest_pfm_date.strftime(
                "%d %b %Y"
            )
        else:
            latest_text = "N/A"

    else:
        latest_text = "N/A"

    st.metric(
        "Latest Review",
        latest_text
    )


# ============================================================
# VISITOR SATISFACTION
# ============================================================

st.markdown("---")

st.markdown("""
<p class="pfm-section-title">
     Visitor Satisfaction
</p>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)


# ============================================================
# RATING DISTRIBUTION
# ============================================================

with col1:

    st.markdown("""
    <p class="pfm-card-title">
         Rating Distribution
    </p>
    """, unsafe_allow_html=True)

    rating_df = (
        df["rating"]
        .value_counts()
        .sort_index()
        .reset_index()
    )

    rating_df.columns = [
        "Rating",
        "Reviews"
    ]

    chart = (
        alt.Chart(rating_df)
        .mark_bar(
            color=YELLOW,
            cornerRadiusTopLeft=4,
            cornerRadiusTopRight=4
        )
        .encode(
            x=alt.X(
                "Rating:O",
                title="Rating",
                axis=alt.Axis(
                    grid=False
                )
            ),
            y=alt.Y(
                "Reviews:Q",
                title="Reviews",
                axis=alt.Axis(
                    grid=False
                )
            ),
            tooltip=[
                alt.Tooltip(
                    "Rating:O",
                    title="Rating"
                ),
                alt.Tooltip(
                    "Reviews:Q",
                    title="Reviews"
                )
            ]
        )
        .properties(
            height=300
        )
    )

    st.altair_chart(
        chart,
        use_container_width=True
    )


# ============================================================
# SENTIMENT DISTRIBUTION
# ============================================================

with col2:

    st.markdown("""
    <p class="pfm-card-title">
         Visitor Sentiment
    </p>
    """, unsafe_allow_html=True)

    sentiment_df = (
        df["sentiment"]
        .value_counts()
        .reindex(
            [
                "Positive",
                "Neutral",
                "Negative"
            ],
            fill_value=0
        )
        .reset_index()
    )

    sentiment_df.columns = [
        "Sentiment",
        "Reviews"
    ]

    sentiment_colors = {
        "Positive": "#4C8C5A",
        "Neutral": YELLOW,
        "Negative": "#C75B39"
    }

    chart = (
        alt.Chart(sentiment_df)
        .mark_bar(
            cornerRadiusTopLeft=4,
            cornerRadiusTopRight=4
        )
        .encode(
            x=alt.X(
                "Sentiment:N",
                title="",
                axis=alt.Axis(
                    grid=False
                )
            ),
            y=alt.Y(
                "Reviews:Q",
                title="Reviews",
                axis=alt.Axis(
                    grid=False
                )
            ),
            color=alt.Color(
                "Sentiment:N",
                scale=alt.Scale(
                    domain=[
                        "Positive",
                        "Neutral",
                        "Negative"
                    ],
                    range=[
                        sentiment_colors["Positive"],
                        sentiment_colors["Neutral"],
                        sentiment_colors["Negative"]
                    ]
                ),
                legend=None
            ),
            tooltip=[
                alt.Tooltip(
                    "Sentiment:N",
                    title="Sentiment"
                ),
                alt.Tooltip(
                    "Reviews:Q",
                    title="Reviews"
                )
            ]
        )
        .properties(
            height=300
        )
    )

    st.altair_chart(
        chart,
        use_container_width=True
    )


# ============================================================
# ATTRACTION PERFORMANCE
# ============================================================

st.markdown("---")

st.markdown("""
<p class="pfm-section-title">
     Attraction Performance
</p>
""", unsafe_allow_html=True)


attraction_table = (
    df.groupby("attraction_name")
    .agg(
        Reviews=("rating", "count"),
        Rating=("rating", "mean"),
        Positive=("sentiment",
                  lambda x: (
                      x == "Positive"
                  ).mean() * 100),
        Negative=("sentiment",
                  lambda x: (
                      x == "Negative"
                  ).mean() * 100),
        Latest_Review=("date", "max")
    )
    .reset_index()
)


attraction_table["Rating"] = (
    attraction_table["Rating"]
    .round(2)
)

attraction_table["Positive"] = (
    attraction_table["Positive"]
    .round(1)
)

attraction_table["Negative"] = (
    attraction_table["Negative"]
    .round(1)
)

attraction_table["Latest_Review"] = (
    attraction_table["Latest_Review"]
    .dt.strftime("%d %b %Y")
)


attraction_table = (
    attraction_table
    .sort_values(
        "Reviews",
        ascending=False
    )
)


attraction_table = (
    attraction_table.rename(
        columns={
            "attraction_name": "Attraction",
            "Reviews": "Reviews",
            "Rating": "Rating",
            "Positive": "Positive %",
            "Negative": "Negative %",
            "Latest_Review": "Latest Review"
        }
    )
)


st.dataframe(
    attraction_table,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Rating": st.column_config.NumberColumn(
            "Rating ⭐",
            format="%.2f"
        ),
        "Positive %": st.column_config.NumberColumn(
            "Positive %",
            format="%.1f%%"
        ),
        "Negative %": st.column_config.NumberColumn(
            "Negative %",
            format="%.1f%%"
        )
    }
)


# ============================================================
# REVIEW VOLUME
# ============================================================

st.markdown("""
<p class="pfm-card-title">
     Review Activity by Attraction
</p>
""", unsafe_allow_html=True)


volume_df = (
    df["attraction_name"]
    .value_counts()
    .head(15)
    .reset_index()
)

volume_df.columns = [
    "Attraction",
    "Reviews"
]

volume_df = (
    volume_df
    .sort_values(
        "Reviews",
        ascending=True
    )
)


chart = (
    alt.Chart(volume_df)
    .mark_bar(
        color=YELLOW,
        cornerRadiusEnd=4
    )
    .encode(
        x=alt.X(
            "Reviews:Q",
            title="Review Count",
            axis=alt.Axis(
                grid=False
            )
        ),
        y=alt.Y(
            "Attraction:N",
            sort=None,
            title=""
        ),
        tooltip=[
            alt.Tooltip(
                "Attraction:N",
                title="Attraction"
            ),
            alt.Tooltip(
                "Reviews:Q",
                title="Reviews"
            )
        ]
    )
    .properties(
        height=420
    )
)

st.altair_chart(
    chart,
    use_container_width=True
)


# ============================================================
# REVIEW TRENDS
# ============================================================

st.markdown("---")

st.markdown("""
<p class="pfm-section-title">
     Review Trends
</p>
""", unsafe_allow_html=True)


trend_col1, trend_col2 = st.columns(2)


# ============================================================
# REVIEW VOLUME TREND
# ============================================================

with trend_col1:

    st.markdown("""
    <p class="pfm-card-title">
         Monthly Review Volume
    </p>
    """, unsafe_allow_html=True)

    monthly_reviews = (
        df.dropna(
            subset=["date"]
        )
        .groupby("month")
        .size()
        .reset_index(
            name="Reviews"
        )
    )

    monthly_reviews = monthly_reviews[
        monthly_reviews["month"] != "NaT"
    ]

    chart = (
        alt.Chart(monthly_reviews)
        .mark_line(
            color=YELLOW,
            strokeWidth=3,
            point=alt.OverlayMarkDef(
                color=YELLOW,
                size=55
            )
        )
        .encode(
            x=alt.X(
                "month:N",
                title="Month",
                sort=None,
                axis=alt.Axis(
                    grid=False
                )
            ),
            y=alt.Y(
                "Reviews:Q",
                title="Reviews",
                axis=alt.Axis(
                    grid=False
                )
            ),
            tooltip=[
                alt.Tooltip(
                    "month:N",
                    title="Month"
                ),
                alt.Tooltip(
                    "Reviews:Q",
                    title="Reviews"
                )
            ]
        )
        .properties(
            height=300
        )
    )

    st.altair_chart(
        chart,
        use_container_width=True
    )


# ============================================================
# RATING TREND
# ============================================================

with trend_col2:

    st.markdown("""
    <p class="pfm-card-title">
         Monthly Average Rating
    </p>
    """, unsafe_allow_html=True)

    monthly_rating = (
        df.dropna(
            subset=["date"]
        )
        .groupby("month")["rating"]
        .mean()
        .reset_index()
    )

    monthly_rating.columns = [
        "Month",
        "Average Rating"
    ]

    monthly_rating["Average Rating"] = (
        monthly_rating["Average Rating"]
        .round(2)
    )

    chart = (
        alt.Chart(monthly_rating)
        .mark_line(
            color=YELLOW,
            strokeWidth=3,
            point=alt.OverlayMarkDef(
                color=YELLOW,
                size=55
            )
        )
        .encode(
            x=alt.X(
                "Month:N",
                title="Month",
                sort=None,
                axis=alt.Axis(
                    grid=False
                )
            ),
            y=alt.Y(
                "Average Rating:Q",
                title="Average Rating",
                scale=alt.Scale(
                    domain=[1, 5]
                ),
                axis=alt.Axis(
                    grid=False
                )
            ),
            tooltip=[
                alt.Tooltip(
                    "Month:N",
                    title="Month"
                ),
                alt.Tooltip(
                    "Average Rating:Q",
                    title="Rating"
                )
            ]
        )
        .properties(
            height=300
        )
    )

    st.altair_chart(
        chart,
        use_container_width=True
    )


# ============================================================
# PLATFORM COMPARISON
# ============================================================

st.markdown("---")

st.markdown("""
<p class="pfm-section-title">
     Platform Comparison
</p>
""", unsafe_allow_html=True)


platform_summary = (
    df.groupby("platform")
    .agg(
        Reviews=("rating", "count"),
        Average_Rating=("rating", "mean"),
        Positive=("sentiment",
                  lambda x: (
                      x == "Positive"
                  ).mean() * 100),
        Neutral=("sentiment",
                 lambda x: (
                     x == "Neutral"
                 ).mean() * 100),
        Negative=("sentiment",
                  lambda x: (
                      x == "Negative"
                  ).mean() * 100)
    )
    .reset_index()
)


platform_summary["Average_Rating"] = (
    platform_summary["Average_Rating"]
    .round(2)
)

platform_summary["Positive"] = (
    platform_summary["Positive"]
    .round(1)
)

platform_summary["Neutral"] = (
    platform_summary["Neutral"]
    .round(1)
)

platform_summary["Negative"] = (
    platform_summary["Negative"]
    .round(1)
)


platform_summary = (
    platform_summary.rename(
        columns={
            "platform": "Platform",
            "Reviews": "Reviews",
            "Average_Rating": "Rating",
            "Positive": "Positive %",
            "Neutral": "Neutral %",
            "Negative": "Negative %"
        }
    )
)


st.dataframe(
    platform_summary,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Rating": st.column_config.NumberColumn(
            "Rating ⭐",
            format="%.2f"
        ),
        "Positive %": st.column_config.NumberColumn(
            "Positive %",
            format="%.1f%%"
        ),
        "Neutral %": st.column_config.NumberColumn(
            "Neutral %",
            format="%.1f%%"
        ),
        "Negative %": st.column_config.NumberColumn(
            "Negative %",
            format="%.1f%%"
        )
    }
)


# ============================================================
# GEOGRAPHIC ANALYSIS
# ============================================================

st.markdown("---")

st.markdown("""
<p class="pfm-section-title">
     Attraction Locations
</p>
""", unsafe_allow_html=True)


st.markdown("""
<p class="pfm-description">
    Explore attraction locations and view the approximate distance
    from your current location when location access is available.
</p>
""", unsafe_allow_html=True)


# ============================================================
# USER LOCATION
# ============================================================

user_location = get_geolocation()


if (
    user_location
    and user_location.get("coords")
):

    u_lat = user_location["coords"]["latitude"]
    u_lon = user_location["coords"]["longitude"]

    location_available = True

else:

    u_lat = 5.4164
    u_lon = 100.3400

    location_available = False

    st.caption(
        "ℹ️ Location access was unavailable. "
        "Distances are based on central George Town."
    )


# ============================================================
# ATTRACTION COORDINATES
# ============================================================

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


# ============================================================
# ATTRACTION SELECTOR
# ============================================================

selected_attraction = st.selectbox(
    "Select an attraction",
    [
        "All"
    ] + sorted(
        df["attraction_name"]
        .dropna()
        .unique()
        .tolist()
    )
)


# ============================================================
# SELECTED ATTRACTION
# ============================================================

if selected_attraction != "All":

    specific_df = df[
        df["attraction_name"]
        .str.strip()
        == selected_attraction.strip()
    ].copy()


    if not specific_df.empty:

        col_info, col_map = st.columns(
            [1, 1]
        )


        # ====================================================
        # ATTRACTION INFORMATION
        # ====================================================

        with col_info:

            st.markdown("""
            <p class="pfm-card-title">
                🏛️ Attraction Overview
            </p>
            """, unsafe_allow_html=True)

            total_revs = len(
                specific_df
            )

            avg_rating = round(
                specific_df["rating"].mean(),
                2
            )

            positive_rate = (
                specific_df["sentiment"]
                .eq("Positive")
                .mean()
                * 100
            )

            negative_rate = (
                specific_df["sentiment"]
                .eq("Negative")
                .mean()
                * 100
            )

            platforms_used = ", ".join(
                specific_df["platform"]
                .dropna()
                .unique()
            )

            latest_date = (
                specific_df["date"].max()
            )

            if pd.notna(latest_date):
                latest_date_text = (
                    latest_date.strftime(
                        "%d %b %Y"
                    )
                )
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
                {total_revs:,}<br><br>

                <b>Average Rating:</b>
                {avg_rating} / 5.0 ⭐<br><br>

                <b>Positive Reviews:</b>
                {positive_rate:.1f}%<br><br>

                <b>Negative Reviews:</b>
                {negative_rate:.1f}%<br><br>

                <b>Latest Review:</b>
                {latest_date_text}<br><br>

                <b>Platforms:</b>
                {platforms_used}

                </div>
                """,
                unsafe_allow_html=True
            )


        # ====================================================
        # MAP
        # ====================================================

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


            dist = geodesic(
                (u_lat, u_lon),
                (lat, lon)
            ).km


            if location_available:

                st.success(
                    f"📍 Approximately "
                    f"**{dist:.2f} km** from your current location"
                )

            else:

                st.info(
                    f"📍 Approximately "
                    f"**{dist:.2f} km** from central George Town"
                )


            m = folium.Map(
                location=[
                    lat,
                    lon
                ],
                zoom_start=15,
                control_scale=True
            )


            folium.Marker(
                [lat, lon],
                popup=selected_attraction,
                tooltip=selected_attraction,
                icon=folium.Icon(
                    color="orange",
                    icon="ship",
                    prefix="fa"
                )
            ).add_to(m)


            folium.Marker(
                [u_lat, u_lon],
                popup=(
                    "Your approximate location"
                    if location_available
                    else "Central George Town"
                ),
                tooltip=(
                    "You"
                    if location_available
                    else "Central George Town"
                ),
                icon=folium.Icon(
                    color="blue",
                    icon="user",
                    prefix="fa"
                )
            ).add_to(m)


            st_folium(
                m,
                height=350,
                use_container_width=True
            )


# ============================================================
# ALL ATTRACTIONS MAP
# ============================================================

else:

    st.success(
        "📍 Displaying all tracked attractions across Penang."
    )


    m = folium.Map(
        location=[
            5.4164,
            100.3400
        ],
        zoom_start=13,
        control_scale=True
    )


    folium.Marker(
        [u_lat, u_lon],
        popup=(
            "Your approximate location"
            if location_available
            else "Central George Town"
        ),
        tooltip=(
            "You"
            if location_available
            else "Central George Town"
        ),
        icon=folium.Icon(
            color="blue",
            icon="user",
            prefix="fa"
        )
    ).add_to(m)


    for name, coords in attraction_coords.items():

        folium.Marker(
            [
                coords[0],
                coords[1]
            ],
            popup=name,
            tooltip=name,
            icon=folium.Icon(
                color="orange",
                icon="ship",
                prefix="fa"
            )
        ).add_to(m)


    st_folium(
        m,
        height=450,
        use_container_width=True
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown("""
<p style="
    text-align:center;
    color:#777777;
    font-size:12px;
    margin-top:20px;
">
    Penang Ferry Museum &amp; Attractions Analytics
    <br>
    Review data from Google Maps and TripAdvisor
</p>
""", unsafe_allow_html=True)