import streamlit as st
import pandas as pd
import numpy as np
import re
from collections import Counter
from pathlib import Path

from data_loader import load_data
from styles import apply_global_styles, render_sidebar, YELLOW, POSITIVE, NEGATIVE


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Penang Ferry Museum | PFM Analytics",
    page_icon="🚢",
    layout="wide"
)


# =========================================================
# GLOBAL STYLES
# =========================================================

apply_global_styles()


# =========================================================
# SIDEBAR (standardised)
# =========================================================

render_sidebar(current_page="pfm_analysis")

# =========================================================
# LOAD DATA
# =========================================================

df = load_data().copy()

pfm = df[
    df["attraction_name"]
    .astype(str)
    .str.strip()
    .str.lower()
    == "penang ferry museum"
].copy()

if pfm.empty:
    st.error(
        "No Penang Ferry Museum data was found. "
        "Please check the attraction name in data_loader.py."
    )
    st.stop()


# =========================================================
# CLEAN DATA
# =========================================================

pfm["rating"] = pd.to_numeric(
    pfm["rating"],
    errors="coerce"
)

pfm["rating"] = pfm["rating"].clip(1, 5)

pfm["date"] = pd.to_datetime(
    pfm["date"],
    errors="coerce"
)

pfm["text"] = (
    pfm["text"]
    .fillna("")
    .astype(str)
)


# =========================================================
# SENTIMENT
# =========================================================

def map_sentiment(rating):
    if rating >= 4:
        return "Positive"
    elif rating == 3:
        return "Neutral"
    else:
        return "Negative"


pfm["sentiment"] = pfm["rating"].apply(
    map_sentiment
)


# =========================================================
# PAGE HEADER
# =========================================================

IMAGE_PATH = Path(__file__).resolve().parent / "images (1).jpg"

st.markdown("""
<p class="pfm-page-title">
     Penang Ferry Museum
</p>

<p class="pfm-page-subtitle">
    Dedicated visitor review, satisfaction and feedback analysis
</p>

<p class="pfm-yellow-line">
    ━━━━━
</p>
""", unsafe_allow_html=True)


# =========================================================
# KPI CALCULATIONS
# =========================================================

total_reviews = len(pfm)

avg_rating = pfm["rating"].mean()

positive_pct = (
    pfm["sentiment"].eq("Positive").mean() * 100
)

negative_pct = (
    pfm["sentiment"].eq("Negative").mean() * 100
)

neutral_pct = (
    pfm["sentiment"].eq("Neutral").mean() * 100
)

google = pfm[
    pfm["platform"] == "Google Maps"
]

tripadvisor = pfm[
    pfm["platform"] == "TripAdvisor"
]


# =========================================================
# PERFORMANCE OVERVIEW
# =========================================================

st.markdown("""
<p class="pfm-section-title">
     Performance Overview
</p>
""", unsafe_allow_html=True)

st.caption(
    "Key indicators based on available online visitor reviews."
)

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.metric(
        "Total Reviews",
        f"{total_reviews:,}"
    )

with k2:
    st.metric(
        "Average Rating",
        f"{avg_rating:.2f} / 5"
    )

with k3:
    st.metric(
        "Positive Reviews",
        f"{positive_pct:.1f}%"
    )

with k4:
    st.metric(
        "Negative Reviews",
        f"{negative_pct:.1f}%"
    )

with k5:
    st.metric(
        "Platforms",
        f"{pfm['platform'].nunique()}"
    )


# =========================================================
# PLATFORM PERFORMANCE
# =========================================================

st.markdown("""
<p class="pfm-section-title">
    Platform Performance
</p>
""", unsafe_allow_html=True)

st.caption(
    "Comparison of review activity and visitor ratings across platforms."
)

platform_rows = []

for platform in ["Google Maps", "TripAdvisor"]:

    platform_df = pfm[
        pfm["platform"] == platform
    ]

    if not platform_df.empty:

        platform_rows.append({
            "Platform": platform,
            "Reviews": len(platform_df),
            "Average Rating": round(
                platform_df["rating"].mean(),
                2
            ),
            "Positive %": round(
                platform_df["sentiment"]
                .eq("Positive")
                .mean() * 100,
                1
            ),
            "Negative %": round(
                platform_df["sentiment"]
                .eq("Negative")
                .mean() * 100,
                1
            )
        })

platform_summary = pd.DataFrame(platform_rows)

if not platform_summary.empty:

    with st.container(border=True):

        st.dataframe(
            platform_summary,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# VISITOR SATISFACTION
# =========================================================

st.markdown("""
<p class="pfm-section-title">
     Visitor Satisfaction
</p>
""", unsafe_allow_html=True)

st.caption(
    "Distribution of visitor ratings and rating-based sentiment."
)

col1, col2 = st.columns(2)


with col1:

    with st.container(border=True):

        st.markdown("###  Rating Distribution")

        rating_counts = (
            pfm["rating"]
            .round()
            .value_counts()
            .reindex(
                [1, 2, 3, 4, 5],
                fill_value=0
            )
        )

        rating_chart = pd.DataFrame({
            "Rating": [
                "1 Star",
                "2 Stars",
                "3 Stars",
                "4 Stars",
                "5 Stars"
            ],
            "Reviews": rating_counts.values
        })

        st.bar_chart(
            rating_chart.set_index("Rating"),
            height=300
        )


with col2:

    with st.container(border=True):

        st.markdown("###  Visitor Sentiment")

        sentiment_counts = (
            pfm["sentiment"]
            .value_counts()
            .reindex(
                [
                    "Positive",
                    "Neutral",
                    "Negative"
                ],
                fill_value=0
            )
        )

        sentiment_chart = pd.DataFrame({
            "Sentiment": sentiment_counts.index,
            "Reviews": sentiment_counts.values
        })

        st.bar_chart(
            sentiment_chart.set_index("Sentiment"),
            height=300
        )


# =========================================================
# SATISFACTION SUMMARY
# =========================================================

if avg_rating >= 4:

    rating_message = (
        f"PFM has an average online rating of "
        f"{avg_rating:.2f}/5, with most reviews "
        f"falling within the positive rating range."
    )

elif avg_rating >= 3:

    rating_message = (
        f"PFM has an average online rating of "
        f"{avg_rating:.2f}/5, showing a mixed-to-positive "
        f"rating pattern."
    )

else:

    rating_message = (
        f"PFM has an average online rating of "
        f"{avg_rating:.2f}/5, with a relatively larger "
        f"share of lower ratings."
    )


with st.container(border=True):

    st.markdown("### Satisfaction Summary")

    st.write(rating_message)


# =========================================================
# REVIEW TRENDS
# =========================================================

st.markdown("""
<p class="pfm-section-title">
     Review Trends
</p>
""", unsafe_allow_html=True)

st.caption(
    "Changes in online review activity and average rating over time."
)

monthly = (
    pfm
    .dropna(subset=["date"])
    .groupby(
        pfm["date"].dt.to_period("M")
    )
    .agg(
        Reviews=("rating", "count"),
        Average_Rating=("rating", "mean")
    )
    .reset_index()
)

if not monthly.empty:

    monthly["Month"] = (
        monthly["date"]
        .astype(str)
    )

    trend1, trend2 = st.columns(2)

    with trend1:

        with st.container(border=True):

            st.markdown("### Review Volume")

            review_volume = (
                monthly[
                    ["Month", "Reviews"]
                ]
                .set_index("Month")
            )

            st.bar_chart(
                review_volume,
                height=300
            )

    with trend2:

        with st.container(border=True):

            st.markdown("###  Average Rating")

            rating_trend = (
                monthly[
                    [
                        "Month",
                        "Average_Rating"
                    ]
                ]
                .set_index("Month")
            )

            rating_trend.columns = [
                "Average Rating"
            ]

            st.line_chart(
                rating_trend,
                height=300
            )


# =========================================================
# KEYWORD ANALYSIS
# =========================================================

STOPWORDS = {
    "the", "and", "for", "that", "this",
    "with", "was", "were", "are", "but",
    "not", "you", "your", "from", "have",
    "has", "had", "very", "really", "about",
    "there", "their", "they", "them", "its",
    "our", "out", "all", "one", "two", "too",
    "also", "can", "just", "been", "more",
    "much", "into", "than", "then", "when",
    "what", "where", "which", "who", "would",
    "could", "should", "will", "get", "got",
    "we", "i", "it", "a", "an", "to", "of",
    "in", "on", "at", "is", "as", "be", "or",
    "by", "so", "my", "me", "he", "she",
    "his", "her", "do", "did", "no", "yes",
    "if", "up", "down", "over", "after",
    "before", "during", "through", "visit",
    "visited", "place", "museum"
}


def extract_words(texts):

    words = []

    for text in texts:

        text = text.lower()

        text_words = re.findall(
            r"\b[a-zA-Z]{3,}\b",
            text
        )

        for word in text_words:

            if word not in STOPWORDS:
                words.append(word)

    return Counter(words)


positive_words = extract_words(
    pfm[
        pfm["sentiment"] == "Positive"
    ]["text"]
)

negative_words = extract_words(
    pfm[
        pfm["sentiment"] == "Negative"
    ]["text"]
)

positive_common = positive_words.most_common(10)

negative_common = negative_words.most_common(10)


# =========================================================
# REPRESENTATIVE REVIEWS
# =========================================================

st.markdown("""
<p class="pfm-section-title">
     Representative Visitor Reviews
</p>
""", unsafe_allow_html=True)

st.caption(
    "Examples of visitor feedback from the available dataset."
)

reviews1, reviews2 = st.columns(2)


with reviews1:

    st.markdown("###  Positive Feedback")

    positive_examples = (
        pfm[
            (
                pfm["sentiment"] == "Positive"
            )
            &
            (
                pfm["text"].str.len() > 40
            )
        ]
        .sort_values(
            "rating",
            ascending=False
        )
        .head(5)
    )

    if positive_examples.empty:

        st.info(
            "No suitable positive reviews found."
        )

    else:

        for _, row in positive_examples.iterrows():

            review_text = row["text"].strip()

            if len(review_text) > 300:

                review_text = (
                    review_text[:300]
                    + "..."
                )

            with st.container(border=True):

                st.markdown(
                    f"**⭐ {row['rating']:.0f}/5**"
                )

                st.write(
                    review_text
                )

                st.caption(
                    row["platform"]
                )


with reviews2:

    st.markdown("###  Critical Feedback")

    negative_examples = (
        pfm[
            (
                pfm["sentiment"] == "Negative"
            )
            &
            (
                pfm["text"].str.len() > 40
            )
        ]
        .sort_values(
            "rating",
            ascending=True
        )
        .head(5)
    )

    if negative_examples.empty:

        st.info(
            "No suitable negative reviews found."
        )

    else:

        for _, row in negative_examples.iterrows():

            review_text = row["text"].strip()

            if len(review_text) > 300:

                review_text = (
                    review_text[:300]
                    + "..."
                )

            with st.container(border=True):

                st.markdown(
                    f"**⭐ {row['rating']:.0f}/5**"
                )

                st.write(
                    review_text
                )

                st.caption(
                    row["platform"]
                )


# =========================================================
# MANAGEMENT INSIGHTS
# =========================================================

st.markdown("""
<p class="pfm-section-title">
     Management Insights
</p>
""", unsafe_allow_html=True)

st.caption(
    "Key points derived from the available visitor review data."
)

insight1, insight2 = st.columns(2)


with insight1:

    with st.container(border=True):

        st.markdown("###  Visitor Strengths")

        strengths = []

        if avg_rating >= 4:

            strengths.append(
                f"Average online rating is "
                f"{avg_rating:.2f}/5."
            )

        if positive_pct >= 70:

            strengths.append(
                f"{positive_pct:.1f}% of reviews "
                f"are in the positive rating category."
            )

        if positive_common:

            top_positive = (
                positive_common[0][0]
                .title()
            )

            strengths.append(
                f"'{top_positive}' is among the "
                f"most frequently mentioned "
                f"positive terms."
            )

        if not strengths:

            strengths.append(
                "Continue monitoring reviews to "
                "identify recurring visitor strengths."
            )

        for item in strengths:

            st.write(
                f"• {item}"
            )


with insight2:

    with st.container(border=True):

        st.markdown("###  Areas to Monitor")

        improvements = []

        if negative_pct > 20:

            improvements.append(
                f"Negative reviews represent "
                f"{negative_pct:.1f}% of available reviews."
            )

        if negative_common:

            top_negative = (
                negative_common[0][0]
                .title()
            )

            improvements.append(
                f"'{top_negative}' appears frequently "
                f"in negative reviews and can be monitored."
            )

        if not improvements:

            improvements.append(
                "Continue monitoring negative reviews "
                "for emerging visitor concerns."
            )

        for item in improvements:

            st.write(
                f"• {item}"
            )


# =========================================================
# DATA COVERAGE
# =========================================================

st.markdown("""
<p class="pfm-section-title">
     Data Coverage
</p>
""", unsafe_allow_html=True)

d1, d2, d3 = st.columns(3)


with d1:

    st.metric(
        "Google Maps Reviews",
        f"{len(google):,}"
    )


with d2:

    st.metric(
        "TripAdvisor Reviews",
        f"{len(tripadvisor):,}"
    )


with d3:

    date_min = pfm["date"].min()
    date_max = pfm["date"].max()

    if (
        pd.notna(date_min)
        and pd.notna(date_max)
    ):

        date_range = (
            f"{date_min.strftime('%b %Y')} – "
            f"{date_max.strftime('%b %Y')}"
        )

    else:

        date_range = "Not available"

    st.metric(
        "Review Period",
        date_range
    )


# =========================================================
# FOOTNOTE
# =========================================================

st.markdown("---")

st.caption(
    "Note: Sentiment is classified using review ratings "
    "(4–5 = Positive, 3 = Neutral, 1–2 = Negative). "
    "Review volume represents online review activity and "
    "should not be interpreted as actual visitor numbers."
)