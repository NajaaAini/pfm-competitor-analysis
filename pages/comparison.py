import streamlit as st
import pandas as pd
import altair as alt
import re
from collections import Counter

from data_loader import load_data
from styles import apply_global_styles, render_sidebar, YELLOW


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Competitor Comparison | Penang Ferry Museum",
    page_icon="⚖️",
    layout="wide"
)


# ============================================================
# GLOBAL STYLES
# ============================================================

apply_global_styles()


# ============================================================
# SIDEBAR (standardised)
# ============================================================

render_sidebar(current_page="comparison")

# ============================================================
# LOAD DATA
# ============================================================

df = load_data().copy()


# ============================================================
# CLEAN ATTRACTION LIST
# ============================================================

attractions = sorted(
    df["attraction_name"]
    .dropna()
    .astype(str)
    .str.strip()
    .unique()
    .tolist()
)

competitors = [
    x for x in attractions
    if x != "Penang Ferry Museum"
]


# ============================================================
# PAGE HEADER
# ============================================================

st.markdown("""
<p class="pfm-page-title">
     Competitor Comparison
</p>

<p class="pfm-page-subtitle">
    Penang Ferry Museum vs Penang Attractions
</p>

<p class="pfm-yellow-line">
    ━━━━━
</p>
""", unsafe_allow_html=True)


st.markdown("""
<p class="pfm-description">
    Compare visitor ratings, review volume, sentiment, comments and
    discussion topics to understand how other attractions are perceived.
</p>
""", unsafe_allow_html=True)


# ============================================================
# SELECT COMPETITORS
# ============================================================

st.markdown("""
<p class="pfm-section-title">
     Select Competitors
</p>
""", unsafe_allow_html=True)


selected_competitors = st.multiselect(
    "Select one or more attractions to compare with Penang Ferry Museum:",
    competitors,
    default=competitors[:2] if len(competitors) >= 2 else competitors
)


if not selected_competitors:

    st.info(
        "Please select at least one competitor to begin the comparison."
    )

    st.stop()


# ============================================================
# ATTRACTIONS BEING COMPARED
# ============================================================

comparison_attractions = [
    "Penang Ferry Museum"
] + selected_competitors


# ============================================================
# COLOUR PALETTE
# ============================================================

colour_palette = [
    YELLOW,
    "#2F6B7C",
    "#C75B39",
    "#5B4B8A",
    "#4C8C5A",
    "#B45F8A",
    "#6A6A6A",
    "#D46A1F",
    "#3F7CAC",
    "#8A6F3D"
]


attraction_colors = {
    attraction: colour_palette[i % len(colour_palette)]
    for i, attraction in enumerate(comparison_attractions)
}


# ============================================================
# DATASETS
# ============================================================

pfm_df = df[
    df["attraction_name"] == "Penang Ferry Museum"
].copy()


competitor_dfs = {}

for competitor in selected_competitors:

    competitor_dfs[competitor] = df[
        df["attraction_name"] == competitor
    ].copy()


# ============================================================
# BASIC METRICS
# ============================================================

comparison_rows = []

for attraction in comparison_attractions:

    if attraction == "Penang Ferry Museum":

        attraction_df = pfm_df

    else:

        attraction_df = competitor_dfs[attraction]

    comparison_rows.append({

        "Attraction": attraction,

        "Reviews": len(attraction_df),

        "Average Rating": round(
            attraction_df["rating"].mean(),
            2
        ) if not attraction_df.empty else 0,

        "Positive %": round(
            attraction_df["rating"]
            .apply(
                lambda x:
                "Positive"
                if x >= 4
                else (
                    "Neutral"
                    if x == 3
                    else "Negative"
                )
            )
            .eq("Positive")
            .mean() * 100,
            1
        ) if not attraction_df.empty else 0
    })


comparison_summary = pd.DataFrame(
    comparison_rows
)


# ============================================================
# RATING & REVIEW VOLUME
# ============================================================

st.markdown("---")

st.markdown("""
<p class="pfm-section-title">
     Rating &amp; Review Volume
</p>
""", unsafe_allow_html=True)


# ============================================================
# METRIC CARDS
# ============================================================

metric_columns = st.columns(
    min(len(comparison_attractions), 4)
)


for i, attraction in enumerate(comparison_attractions):

    row = comparison_summary[
        comparison_summary["Attraction"] == attraction
    ].iloc[0]

    with metric_columns[
        i % len(metric_columns)
    ]:

        st.metric(
            f"{attraction} Rating",
            f"{row['Average Rating']:.2f} / 5"
        )

        st.caption(
            f"{int(row['Reviews']):,} reviews"
        )


# ============================================================
# SUMMARY TABLE
# ============================================================

with st.container(border=True):

    display_summary = comparison_summary.copy()

    display_summary["Average Rating"] = (
        display_summary["Average Rating"]
        .map(lambda x: f"{x:.2f}")
    )

    display_summary["Positive %"] = (
        display_summary["Positive %"]
        .map(lambda x: f"{x:.1f}%")
    )

    st.dataframe(
        display_summary,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# RATING COMPARISON CHART
# ============================================================

rating_chart = comparison_summary[
    [
        "Attraction",
        "Average Rating"
    ]
].copy()


chart = (
    alt.Chart(rating_chart)
    .mark_bar()
    .encode(

        x=alt.X(
            "Attraction:N",
            title="",
            sort=None,
            axis=alt.Axis(
                labelAngle=-25
            )
        ),

        y=alt.Y(
            "Average Rating:Q",
            scale=alt.Scale(
                domain=[0, 5]
            ),
            title="Average Rating",
            axis=alt.Axis(
                grid=False
            )
        ),

        color=alt.Color(
            "Attraction:N",
            scale=alt.Scale(
                domain=list(attraction_colors.keys()),
                range=list(attraction_colors.values())
            ),
            legend=None
        ),

        tooltip=[
            alt.Tooltip(
                "Attraction:N",
                title="Attraction"
            ),
            alt.Tooltip(
                "Average Rating:Q",
                title="Average Rating",
                format=".2f"
            )
        ]
    )
    .properties(
        height=320
    )
)


st.altair_chart(
    chart,
    use_container_width=True
)


# ============================================================
# SENTIMENT
# ============================================================

st.markdown("---")

st.markdown("""
<p class="pfm-section-title">
     Sentiment Comparison
</p>
""", unsafe_allow_html=True)


def map_sentiment(rating):

    if rating >= 4:
        return "Positive"

    elif rating == 3:
        return "Neutral"

    return "Negative"


sentiment_rows = []


for attraction in comparison_attractions:

    if attraction == "Penang Ferry Museum":

        attraction_df = pfm_df

    else:

        attraction_df = competitor_dfs[attraction]

    sentiment_counts = (
        attraction_df["rating"]
        .apply(map_sentiment)
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

    for sentiment in [
        "Positive",
        "Neutral",
        "Negative"
    ]:

        sentiment_rows.append({

            "Attraction": attraction,

            "Sentiment": sentiment,

            "Reviews": sentiment_counts[
                sentiment
            ]

        })


sentiment_long = pd.DataFrame(
    sentiment_rows
)


# ============================================================
# SENTIMENT CHART
# ============================================================

sentiment_chart = (
    alt.Chart(sentiment_long)
    .mark_bar()
    .encode(

        x=alt.X(
            "Sentiment:N",
            title=""
        ),

        y=alt.Y(
            "Reviews:Q",
            title="Review Count",
            axis=alt.Axis(
                grid=False
            )
        ),

        xOffset=alt.XOffset(
            "Attraction:N"
        ),

        color=alt.Color(
            "Attraction:N",
            scale=alt.Scale(
                domain=list(attraction_colors.keys()),
                range=list(attraction_colors.values())
            ),
            legend=alt.Legend(
                title="Attraction"
            )
        ),

        tooltip=[
            alt.Tooltip(
                "Attraction:N",
                title="Attraction"
            ),
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
        height=360
    )
)


st.altair_chart(
    sentiment_chart,
    use_container_width=True
)


# ============================================================
# SENTIMENT PERCENTAGES
# ============================================================

st.markdown("### Positive Review Percentage")


positive_rows = []


for attraction in comparison_attractions:

    if attraction == "Penang Ferry Museum":

        attraction_df = pfm_df

    else:

        attraction_df = competitor_dfs[attraction]

    positive_percentage = round(
        (
            attraction_df["rating"]
            .apply(map_sentiment)
            .eq("Positive")
            .mean()
            * 100
        ),
        1
    ) if not attraction_df.empty else 0

    positive_rows.append({

        "Attraction": attraction,

        "Positive %": positive_percentage

    })


positive_df = pd.DataFrame(
    positive_rows
)


positive_chart = (
    alt.Chart(positive_df)
    .mark_bar()
    .encode(

        x=alt.X(
            "Attraction:N",
            title="",
            axis=alt.Axis(
                labelAngle=-25
            )
        ),

        y=alt.Y(
            "Positive %:Q",
            title="Positive Reviews (%)",
            scale=alt.Scale(
                domain=[0, 100]
            ),
            axis=alt.Axis(
                grid=False
            )
        ),

        color=alt.Color(
            "Attraction:N",
            scale=alt.Scale(
                domain=list(attraction_colors.keys()),
                range=list(attraction_colors.values())
            ),
            legend=None
        ),

        tooltip=[
            alt.Tooltip(
                "Attraction:N",
                title="Attraction"
            ),
            alt.Tooltip(
                "Positive %:Q",
                title="Positive Reviews",
                format=".1f"
            )
        ]
    )
    .properties(
        height=320
    )
)


st.altair_chart(
    positive_chart,
    use_container_width=True
)


# ============================================================
# REPRESENTATIVE COMMENTS
# ============================================================

st.markdown("---")

st.markdown("""
<p class="pfm-section-title">
     Visitor Comments
</p>
""", unsafe_allow_html=True)


# ============================================================
# COMMENT FILTER
# ============================================================

comment_filter = st.selectbox(
    "Choose comment type:",
    [
        "Positive",
        "Neutral",
        "Negative",
        "All"
    ],
    index=0
)


# ============================================================
# COMMENT DESCRIPTION
# ============================================================

if comment_filter == "Positive":

    st.caption(
        "Showing reviews rated 4–5 stars."
    )

elif comment_filter == "Neutral":

    st.caption(
        "Showing reviews rated 3 stars."
    )

elif comment_filter == "Negative":

    st.caption(
        "Showing reviews rated 1–2 stars."
    )

else:

    st.caption(
        "Showing reviews across all rating levels."
    )


# ============================================================
# COMMENTS FOR EACH ATTRACTION
# ============================================================

comment_columns = st.columns(
    min(len(comparison_attractions), 3)
)


for i, attraction in enumerate(
    comparison_attractions
):

    if attraction == "Penang Ferry Museum":

        attraction_df = pfm_df

    else:

        attraction_df = competitor_dfs[attraction]


    with comment_columns[
        i % len(comment_columns)
    ]:

        st.markdown(
            f"""
            <p class="pfm-card-title">
                {attraction}
            </p>
            """,
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # FILTER COMMENTS
        # ----------------------------------------------------

        if comment_filter == "Positive":

            filtered_comments = attraction_df[
                attraction_df["rating"] >= 4
            ]

        elif comment_filter == "Neutral":

            filtered_comments = attraction_df[
                attraction_df["rating"] == 3
            ]

        elif comment_filter == "Negative":

            filtered_comments = attraction_df[
                attraction_df["rating"] <= 2
            ]

        else:

            filtered_comments = attraction_df


        filtered_comments = (
            filtered_comments[
                ["rating", "text"]
            ]
            .dropna(
                subset=["text"]
            )
            .head(5)
        )


        # ----------------------------------------------------
        # DISPLAY COMMENTS
        # ----------------------------------------------------

        if not filtered_comments.empty:

            for _, row in filtered_comments.iterrows():

                comment = str(
                    row["text"]
                ).strip()


                if len(comment) > 250:

                    comment = (
                        comment[:250]
                        + "..."
                    )


                rating = row["rating"]


                if comment_filter == "Positive":

                    st.success(
                        f"⭐ {rating} / 5\n\n"
                        f"{comment}"
                    )

                elif comment_filter == "Negative":

                    st.error(
                        f"⭐ {rating} / 5\n\n"
                        f"{comment}"
                    )

                elif comment_filter == "Neutral":

                    st.warning(
                        f"⭐ {rating} / 5\n\n"
                        f"{comment}"
                    )

                else:

                    st.info(
                        f"⭐ {rating} / 5\n\n"
                        f"{comment}"
                    )

        else:

            st.info(
                f"No {comment_filter.lower()} "
                f"comments available."
            )


# ============================================================
# TOPIC MODELLING
# ============================================================

st.markdown("---")

st.markdown("""
<p class="pfm-section-title">
     Visitor Topics
</p>
""", unsafe_allow_html=True)


topic_keywords = {

    "Heritage & History": [
        "history",
        "historic",
        "heritage",
        "old",
        "ferry",
        "boat",
        "museum",
        "culture",
        "colonial"
    ],

    "Exhibits & Displays": [
        "exhibit",
        "exhibits",
        "display",
        "displays",
        "collection",
        "artifact",
        "gallery",
        "information"
    ],

    "Staff & Service": [
        "staff",
        "service",
        "friendly",
        "helpful",
        "guide",
        "welcoming"
    ],

    "Location & Accessibility": [
        "location",
        "located",
        "easy",
        "access",
        "parking",
        "walk",
        "walking",
        "transport"
    ],

    "Family Experience": [
        "family",
        "kids",
        "children",
        "child",
        "fun",
        "activity"
    ],

    "Food & Shopping": [
        "food",
        "restaurant",
        "cafe",
        "shop",
        "shopping",
        "souvenir"
    ],

    "Cleanliness": [
        "clean",
        "cleanliness",
        "dirty",
        "toilet",
        "restroom"
    ],

    "Price & Value": [
        "price",
        "expensive",
        "cheap",
        "value",
        "ticket",
        "tickets",
        "fee",
        "worth"
    ],

    "Photo Experience": [
        "photo",
        "photos",
        "photogenic",
        "instagram",
        "picture",
        "pictures"
    ]
}


def detect_topics(text):

    text = str(text).lower()

    detected = []

    for topic, keywords in topic_keywords.items():

        for keyword in keywords:

            if re.search(
                r"\b"
                + re.escape(keyword)
                + r"\b",
                text
            ):

                detected.append(topic)

                break

    return detected


def topic_counts(data):

    counts = Counter()

    for text in data["text"].fillna("").astype(str):

        topics = detect_topics(text)

        for topic in topics:

            counts[topic] += 1

    return pd.DataFrame(
        counts.items(),
        columns=[
            "Topic",
            "Mentions"
        ]
    ).sort_values(
        "Mentions",
        ascending=False
    )


# ============================================================
# TOPICS FOR ALL ATTRACTIONS
# ============================================================

topic_rows = []


for attraction in comparison_attractions:

    if attraction == "Penang Ferry Museum":

        attraction_df = pfm_df

    else:

        attraction_df = competitor_dfs[attraction]

    counts = topic_counts(
        attraction_df
    )

    for _, row in counts.iterrows():

        topic_rows.append({

            "Attraction": attraction,

            "Topic": row["Topic"],

            "Mentions": row["Mentions"]

        })


topic_long = pd.DataFrame(
    topic_rows
)


# ============================================================
# TOPIC DROPDOWN
# ============================================================

if not topic_long.empty:

    st.markdown(
        "### Explore a Specific Topic"
    )

    selected_topic = st.selectbox(
        "Choose a topic to compare:",
        list(topic_keywords.keys()),
        index=0
    )


    # ========================================================
    # SELECTED TOPIC DATA
    # ========================================================

    selected_topic_df = topic_long[
        topic_long["Topic"] == selected_topic
    ].copy()


    # Add zero values for attractions that have no mentions
    topic_complete_rows = []

    for attraction in comparison_attractions:

        matching = selected_topic_df[
            selected_topic_df["Attraction"] == attraction
        ]

        if matching.empty:

            topic_complete_rows.append({

                "Attraction": attraction,

                "Topic": selected_topic,

                "Mentions": 0

            })

        else:

            topic_complete_rows.append({

                "Attraction": attraction,

                "Topic": selected_topic,

                "Mentions": int(
                    matching["Mentions"].sum()
                )

            })


    selected_topic_df = pd.DataFrame(
        topic_complete_rows
    )


    # ========================================================
    # SELECTED TOPIC CHART
    # ========================================================

    st.markdown(
        f"#### {selected_topic}"
    )

    selected_topic_chart = (
        alt.Chart(selected_topic_df)
        .mark_bar()
        .encode(

            x=alt.X(
                "Attraction:N",
                title="",
                sort=None,
                axis=alt.Axis(
                    labelAngle=-25
                )
            ),

            y=alt.Y(
                "Mentions:Q",
                title="Review Mentions",
                axis=alt.Axis(
                    grid=False
                )
            ),

            color=alt.Color(
                "Attraction:N",
                scale=alt.Scale(
                    domain=list(
                        attraction_colors.keys()
                    ),
                    range=list(
                        attraction_colors.values()
                    )
                ),
                legend=None
            ),

            tooltip=[
                alt.Tooltip(
                    "Attraction:N",
                    title="Attraction"
                ),
                alt.Tooltip(
                    "Mentions:Q",
                    title="Mentions"
                )
            ]
        )
        .properties(
            height=350
        )
    )


    st.altair_chart(
        selected_topic_chart,
        use_container_width=True
    )


    # ========================================================
    # TOPIC DESCRIPTION
    # ========================================================

    topic_descriptions = {

        "Heritage & History":
            "history, heritage and cultural information",

        "Exhibits & Displays":
            "exhibit quality, variety, presentation and information",

        "Staff & Service":
            "staff friendliness, helpfulness and visitor service",

        "Location & Accessibility":
            "location, parking and ease of access",

        "Family Experience":
            "family activities and children's experience",

        "Food & Shopping":
            "food, cafés, shops and souvenir opportunities",

        "Cleanliness":
            "cleanliness, toilets and general upkeep",

        "Price & Value":
            "ticket prices, affordability and value for money",

        "Photo Experience":
            "photography opportunities and photogenic areas"
    }


    st.caption(
        f"**This topic covers:** "
        f"{topic_descriptions.get(selected_topic, '')}."
    )


else:

    st.info(
        "Not enough review text to identify topics."
    )


# ============================================================
# TOPIC SUMMARY TABLE
# ============================================================

if not topic_long.empty:

    st.markdown("### Topic Summary")

    topic_table = (
        topic_long
        .pivot_table(
            index="Topic",
            columns="Attraction",
            values="Mentions",
            aggfunc="sum",
            fill_value=0
        )
        .reset_index()
    )

    # Ensure every selected attraction appears
    for attraction in comparison_attractions:

        if attraction not in topic_table.columns:

            topic_table[attraction] = 0


    # Keep attraction order
    topic_table = topic_table[
        ["Topic"] + comparison_attractions
    ]


    st.dataframe(
        topic_table,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# POTENTIAL OPPORTUNITIES — TOP 5
# ============================================================

st.markdown("---")

st.markdown("""
<p class="pfm-section-title">
     Potential Opportunities for Penang Ferry Museum
</p>
""", unsafe_allow_html=True)


def get_topic_comments(
    data,
    topic,
    limit=3
):

    keywords = topic_keywords.get(
        topic,
        []
    )

    if not keywords:
        return pd.DataFrame()

    pattern = (
        r"\b("
        + "|".join(
            re.escape(keyword)
            for keyword in keywords
        )
        + r")\b"
    )

    topic_reviews = data[
        data["text"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.contains(
            pattern,
            regex=True,
            na=False
        )
    ].copy()

    if topic_reviews.empty:
        return pd.DataFrame()

    return topic_reviews[
        [
            "rating",
            "platform",
            "text"
        ]
    ].dropna(
        subset=["text"]
    ).head(limit)


# ============================================================
# TOPIC DESCRIPTIONS
# ============================================================

topic_descriptions = {

    "Heritage & History":
        "history, heritage and cultural information",

    "Exhibits & Displays":
        "exhibit quality, variety, presentation and information",

    "Staff & Service":
        "staff friendliness, helpfulness and visitor service",

    "Location & Accessibility":
        "location, parking and ease of access",

    "Family Experience":
        "family activities and children's experience",

    "Food & Shopping":
        "food, cafés, shops and souvenir opportunities",

    "Cleanliness":
        "cleanliness, toilets and general upkeep",

    "Price & Value":
        "ticket prices, affordability and value for money",

    "Photo Experience":
        "photography opportunities and photogenic areas"

}


# ============================================================
# OPPORTUNITY TOPIC DROPDOWN
# ============================================================

opportunity_topic_options = [
    "All Topics"
] + list(topic_keywords.keys())


selected_opportunity_topic = st.selectbox(
    "Choose topic for opportunities:",
    opportunity_topic_options,
    index=0
)


if selected_opportunity_topic == "All Topics":

    st.caption(
        "Showing the top 5 opportunities across all visitor topics."
    )

else:

    st.caption(
        f"Showing the top 5 opportunities related to "
        f"**{selected_opportunity_topic}**."
    )


# ============================================================
# FIND TOPIC GAPS
# ============================================================

if not topic_long.empty:

    pfm_topic = (
        topic_long[
            topic_long["Attraction"]
            == "Penang Ferry Museum"
        ]
        .groupby("Topic")["Mentions"]
        .sum()
    )

    opportunities = []


    for competitor in selected_competitors:

        competitor_topic = (
            topic_long[
                topic_long["Attraction"]
                == competitor
            ]
            .groupby("Topic")["Mentions"]
            .sum()
        )


        # ----------------------------------------------------
        # DETERMINE TOPICS
        # ----------------------------------------------------

        if selected_opportunity_topic == "All Topics":

            topics_to_check = sorted(
                set(pfm_topic.index)
                | set(competitor_topic.index)
            )

        else:

            topics_to_check = [
                selected_opportunity_topic
            ]


        # ----------------------------------------------------
        # CALCULATE TOPIC DIFFERENCES
        # ----------------------------------------------------

        for topic in topics_to_check:

            pfm_mentions = int(
                pfm_topic.get(
                    topic,
                    0
                )
            )

            competitor_mentions = int(
                competitor_topic.get(
                    topic,
                    0
                )
            )

            difference = (
                competitor_mentions
                - pfm_mentions
            )


            # Only include opportunities where
            # competitor has more mentions than PFM

            if difference > 0:

                opportunities.append({

                    "Competitor":
                        competitor,

                    "Topic":
                        topic,

                    "PFM Mentions":
                        pfm_mentions,

                    "Competitor Mentions":
                        competitor_mentions,

                    "Difference":
                        difference

                })


    opportunity_df = pd.DataFrame(
        opportunities
    )


    # ========================================================
    # SHOW TOP 5 ONLY
    # ========================================================

    if not opportunity_df.empty:

        opportunity_df = (
            opportunity_df
            .sort_values(
                "Difference",
                ascending=False
            )
            .head(5)
            .reset_index(drop=True)
        )


        # ====================================================
        # DISPLAY TOP 5
        # ====================================================

        for index, opportunity in opportunity_df.iterrows():

            competitor = opportunity[
                "Competitor"
            ]

            topic = opportunity[
                "Topic"
            ]

            pfm_mentions = int(
                opportunity[
                    "PFM Mentions"
                ]
            )

            competitor_mentions = int(
                opportunity[
                    "Competitor Mentions"
                ]
            )

            difference = int(
                opportunity[
                    "Difference"
                ]
            )


            # ------------------------------------------------
            # OVERVIEW
            # ------------------------------------------------

            st.markdown(
                f"""
                **{index + 1}. {topic}**  

                {competitor} has **{competitor_mentions} mentions**
                compared with **{pfm_mentions} mentions**
                for Penang Ferry Museum.

                **Difference: +{difference} mentions**
                """
            )


            # ------------------------------------------------
            # DETAILS
            # ------------------------------------------------

            with st.expander(
                f"View details — {topic} / {competitor}"
            ):

                description = topic_descriptions.get(
                    topic,
                    "visitor experiences related to this topic"
                )


                st.markdown(
                    f"""
                    **What this topic covers:**  
                    {description}.
                    """
                )


                # --------------------------------------------
                # COMPARISON
                # --------------------------------------------

                comparison_col1, comparison_col2 = st.columns(2)


                with comparison_col1:

                    st.metric(
                        "Penang Ferry Museum",
                        f"{pfm_mentions} mentions"
                    )


                with comparison_col2:

                    st.metric(
                        competitor,
                        f"{competitor_mentions} mentions"
                    )


                # --------------------------------------------
                # EXAMPLE COMMENTS
                # --------------------------------------------

                st.markdown(
                    "**Example visitor comments:**"
                )


                competitor_comments = get_topic_comments(
                    competitor_dfs[competitor],
                    topic,
                    limit=3
                )


                if not competitor_comments.empty:

                    for _, comment_row in competitor_comments.iterrows():

                        comment_text = str(
                            comment_row["text"]
                        ).strip()


                        if len(comment_text) > 350:

                            comment_text = (
                                comment_text[:350]
                                + "..."
                            )


                        rating = comment_row[
                            "rating"
                        ]

                        platform = comment_row[
                            "platform"
                        ]


                        st.info(
                            f"⭐ **{rating}/5** · "
                            f"{platform}\n\n"
                            f"{comment_text}"
                        )

                else:

                    st.caption(
                        "No specific comments were found "
                        "for this topic."
                    )


    else:

        if selected_opportunity_topic == "All Topics":

            st.info(
                "The available review data does not show "
                "a clear topic gap across the selected competitors."
            )

        else:

            st.info(
                f"No clear opportunity was identified for "
                f"**{selected_opportunity_topic}** "
                f"in the available review data."
            )


else:

    st.info(
        "Not enough review text is available to identify "
        "potential opportunities."
    )