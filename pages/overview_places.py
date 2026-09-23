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
