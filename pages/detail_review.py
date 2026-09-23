import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer

from data_loader import load_data
from styles import apply_global_styles, render_sidebar


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Attraction Detail | Penang Ferry Museum",
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

df = load_data()


# ============================================================
# SIDEBAR (standardised — sentiment filter enabled here only)
# ============================================================

sidebar = render_sidebar(
    current_page="detail_review",
    show_attraction_selector=True,
    attraction_options=sorted(
        df["attraction_name"]
        .dropna()
        .unique()
    ),
    show_extra_filters=True,
    show_sentiment_filter=True,
)

selected_attraction = sidebar["attraction"]
rating_filter = sidebar["rating_filter"]
sentiment_filter = sidebar["sentiment_filter"]
min_words_limit = sidebar["min_words"]
max_words_limit = sidebar["max_words"]


# ============================================================
# FILTER DATA
# ============================================================

filtered_df = df[
    df["attraction_name"] == selected_attraction
].copy()

analysis_df = filtered_df.copy()


# ---------- Rating filter ----------
if rating_filter != "All Ratings":

    star_val = int(rating_filter[0])

    analysis_df = analysis_df[
        analysis_df["rating"] == star_val
    ]


# ---------- Sentiment filter ----------
def map_sentiment(rating):
    if rating >= 4:
        return "Positive"
    elif rating == 3:
        return "Neutral"
    return "Negative"


analysis_df["sentiment"] = analysis_df["rating"].apply(map_sentiment)


if sentiment_filter != "All Sentiments":

    analysis_df = analysis_df[
        analysis_df["sentiment"] == sentiment_filter
    ]


# ============================================================
# PAGE HEADER
# ============================================================

st.markdown("""
<p class="pfm-page-title">
    Detailed Attraction Analysis
</p>

<p class="pfm-page-subtitle">
    Review insights and visitor feedback
</p>

<p class="pfm-yellow-line">
    ━━━━━
</p>
""", unsafe_allow_html=True)


# ============================================================
# SELECTED ATTRACTION
# ============================================================

st.markdown(
    f"""
    <p class="pfm-section-title">
        {selected_attraction}
    </p>
    """,
    unsafe_allow_html=True
)


# ============================================================
# METRICS
# ============================================================

col1, col2, col3 = st.columns(3)


with col1:
    st.metric(
        "Filtered Reviews",
        len(analysis_df)
    )


with col2:
    st.metric(
        "Average Rating",
        round(
            analysis_df["rating"].mean(),
            2
        ) if not analysis_df.empty else 0
    )


with col3:
    st.metric(
        "Platforms",
        ", ".join(
            analysis_df["platform"].unique()
        ) if not analysis_df.empty else "N/A"
    )


# ============================================================
# REVIEWS
# ============================================================

st.markdown("---")

st.markdown("""
<p class="pfm-section-title">
    Recent Reviews
</p>
""", unsafe_allow_html=True)

st.caption(
    f"{len(analysis_df)} review(s) available for {selected_attraction}"
)


if not analysis_df.empty:

    # ---------- Format the table for display ----------
    display_df = analysis_df[
        [
            "platform",
            "rating",
            "sentiment",
            "date",
            "text"
        ]
    ].copy()

    # Convert date to readable format (e.g., "21 Sep 2026")
    display_df["date"] = pd.to_datetime(
        display_df["date"],
        errors="coerce"
    ).dt.strftime("%d %b %Y")

    # Rename for cleaner column headers
    display_df = display_df.rename(
        columns={
            "platform": "Platform",
            "rating": "Rating",
            "sentiment": "Sentiment",
            "date": "Date",
            "text": "Review",
        }
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rating": st.column_config.NumberColumn(
                "Rating",
                format="%.0f"
            ),
            "Review": st.column_config.TextColumn(
                "Review",
                width="large"
            ),
        }
    )

else:

    st.info(
        "No reviews match the selected filters."
    )


# ============================================================
# WORD CLOUD ANALYSIS
# ============================================================

st.markdown("---")

st.markdown("""
<p class="pfm-section-title">
    Review Text Analysis
</p>
""", unsafe_allow_html=True)

st.caption(
    f"Word clouds based on the filtered reviews • "
    f"Maximum {max_words_limit} words"
)


corpus_text = " ".join(
    analysis_df["text"]
    .dropna()
    .astype(str)
    .tolist()
)


if corpus_text.strip():

    wc_col1, wc_col2 = st.columns(2)


    # ========================================================
    # UNIGRAM
    # ========================================================

    with wc_col1:

        st.markdown("""
        <p class="pfm-card-title">
            Unigram Word Cloud
        </p>
        """, unsafe_allow_html=True)

        wc_uni = WordCloud(
            width=500,
            height=350,
            background_color="white",
            colormap="Wistia",
            min_word_length=min_words_limit,
            max_words=max_words_limit
        ).generate(corpus_text)

        fig1, ax1 = plt.subplots(
            figsize=(5, 3.5)
        )

        ax1.imshow(
            wc_uni,
            interpolation="bilinear"
        )

        ax1.axis("off")

        st.pyplot(
            fig1,
            use_container_width=True
        )

        plt.close(fig1)


    # ========================================================
    # BIGRAM
    # ========================================================

    with wc_col2:

        st.markdown("""
        <p class="pfm-card-title">
            Bigram Word Cloud
        </p>
        """, unsafe_allow_html=True)

        vectorizer = CountVectorizer(
            ngram_range=(2, 2),
            stop_words="english"
        )

        try:

            X = vectorizer.fit_transform(
                [corpus_text]
            )

            bigrams_freq = dict(
                zip(
                    vectorizer.get_feature_names_out(),
                    X.toarray()[0]
                )
            )

        except ValueError:

            bigrams_freq = {}


        if bigrams_freq:

            wc_bi = WordCloud(
                width=500,
                height=350,
                background_color="white",
                colormap="YlOrBr",
                max_words=max_words_limit
            ).generate_from_frequencies(
                bigrams_freq
            )

            fig2, ax2 = plt.subplots(
                figsize=(5, 3.5)
            )

            ax2.imshow(
                wc_bi,
                interpolation="bilinear"
            )

            ax2.axis("off")

            st.pyplot(
                fig2,
                use_container_width=True
            )

            plt.close(fig2)

        else:

            st.info(
                "Not enough text data for bigram word cloud."
            )


else:

    st.info(
        "No text data available for the selected filters."
    )