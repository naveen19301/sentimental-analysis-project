import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import matplotlib
import re

matplotlib.use("Agg")

# =====================================================
# BUSINESS EMOTION TAXONOMY
# =====================================================
POSITIVE_EMOTIONS = ["joy", "satisfied"]
NEGATIVE_EMOTIONS = ["angry", "frustrated", "disappointed", "concerned"]
NEUTRAL_EMOTION = "neutral"

# =====================================================
# CACHED COMPUTATIONS
# =====================================================
@st.cache_data(show_spinner=False)
def get_emotion_counts(df_subset):
    return df_subset["Emotion"].value_counts()

@st.cache_data(show_spinner=False)
def get_emotion_trends(df_subset):
    if "created" not in df_subset.columns:
        return None
    trend = (
        df_subset.groupby([df_subset["created"].dt.date, "Emotion"])
        .size()
        .reset_index(name="count")
    )
    return trend

@st.cache_data(show_spinner=False)
def get_emotion_heat(df_subset):
    return pd.crosstab(df_subset["Emotion"], df_subset["Sentiment Label"])

@st.cache_data(show_spinner=False)
def generate_wordcloud(texts_series, colormap="Oranges"):
    # Convert to list or hashable if needed, but Series usually works if index is stable
    # To be safest with caching, we'll join text first and cache that or use the series directly
    text = " ".join(texts_series.dropna().astype(str))

    if not text.strip():
        return None

    # Remove Thread markers
    text = re.sub(r"\bthread\d+\b", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return None

    return WordCloud(
        width=1000,
        height=450,
        background_color="black",
        colormap=colormap,
        max_words=120,
        stopwords={"thread", "threads"},
        relative_scaling=0.5,
        min_font_size=10
    ).generate(text)

# =====================================================
# MAIN PAGE
# =====================================================
def show(df):
    st.title("📊 Emotions & Word Clouds")
    st.markdown("Understanding customer emotions through conversation patterns")
    st.markdown("---")

    # =====================================================
    # NORMALIZE EMOTION
    # =====================================================
    df["Emotion_norm"] = df["Emotion"].astype(str).str.lower().str.strip()

    # =====================================================
    # SIDEBAR FILTERS
    # =====================================================
    st.sidebar.markdown("### 🔍 Filters")

    if "created" in df.columns:
        min_date = df["created"].min().date()
        max_date = df["created"].max().date()
        date_range = st.sidebar.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        if len(date_range) == 2:
            df = df[
                (df["created"].dt.date >= date_range[0]) &
                (df["created"].dt.date <= date_range[1])
            ]

    # =====================================================
    # EMOTION DISTRIBUTION
    # =====================================================
    st.markdown("### 🎭 Emotion Distribution")

    emotion_counts = get_emotion_counts(df)

    col1, col2 = st.columns([2, 1])

    with col1:
        fig_emo = px.bar(
            x=emotion_counts.values,
            y=emotion_counts.index,
            orientation="h",
            color=emotion_counts.values,
            color_continuous_scale="viridis",
            labels={"x": "Tickets", "y": "Emotion"},
            title="Emotion Frequency"
        )
        fig_emo.update_layout(template="plotly_dark", height=480)
        st.plotly_chart(fig_emo, use_container_width=True)

    with col2:
        st.markdown("#### 📊 Top Emotions")
        for emo, cnt in emotion_counts.head(5).items():
            st.metric(emo, f"{cnt:,}", f"{cnt/len(df)*100:.1f}%")

    st.markdown("---")

    # =====================================================
    # EMOTION TRENDS
    # =====================================================
    if "created" in df.columns:
        trend = get_emotion_trends(df)

        fig_trend = px.line(
            trend,
            x="created",
            y="count",
            color="Emotion",
            title="Daily Emotion Trends"
        )
        fig_trend.update_layout(template="plotly_dark", height=450)
        st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown("---")

    # =====================================================
    # WORD CLOUD CONTROLS
    # =====================================================
    st.markdown("### ☁️ Word Cloud Analysis")

    wc_emotion = st.selectbox(
        "Filter by Emotion",
        ["All"] + sorted(df["Emotion"].dropna().astype(str).unique().tolist())
    )

    # =====================================================
    # WORD CLOUDS
    # =====================================================
    col_wc1, col_wc2 = st.columns(2)

    with col_wc1:
        st.markdown("### 👍 Positive Sentiment")
        pos_df = df[df["Emotion_norm"].isin(POSITIVE_EMOTIONS)]
        if wc_emotion != "All":
            pos_df = pos_df[pos_df["Emotion"] == wc_emotion]

        wc = generate_wordcloud(pos_df["Inbound Thread"], "Greens")
        if wc:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wc)
            ax.axis("off")
            st.pyplot(fig)
            plt.close()
        else:
            st.info("No positive text available")

    with col_wc2:
        st.markdown("### 👎 Negative Sentiment")
        neg_df = df[df["Emotion_norm"].isin(NEGATIVE_EMOTIONS)]
        if wc_emotion != "All":
            neg_df = neg_df[neg_df["Emotion"] == wc_emotion]

        wc = generate_wordcloud(neg_df["Inbound Thread"], "Reds")
        if wc:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wc)
            ax.axis("off")
            st.pyplot(fig)
            plt.close()
        else:
            st.info("No negative text available")

    st.markdown("---")

    # =====================================================
    # NEUTRAL WORD CLOUD
    # =====================================================
    st.markdown("### 😐 Neutral Sentiment")

    neu_df = df[df["Emotion_norm"] == NEUTRAL_EMOTION]
    wc = generate_wordcloud(neu_df["Inbound Thread"], "Blues")

    if wc:
        fig, ax = plt.subplots(figsize=(16, 6))
        ax.imshow(wc)
        ax.axis("off")
        st.pyplot(fig)
        plt.close()
    else:
        st.info("No neutral text available")

    st.markdown("---")

    # =====================================================
    # EMOTION vs SENTIMENT HEATMAP (FIXED SIZE)
    # =====================================================
    st.markdown("### 🔥 Emotion vs Sentiment Heatmap")

    heat = get_emotion_heat(df)

    fig_heat = px.imshow(
        heat,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="YlOrRd",
        labels=dict(x="Sentiment", y="Emotion", color="Tickets"),
        title="Emotion vs Sentiment Relationship"
    )
    fig_heat.update_layout(
        template="plotly_dark",
        height=520,
        margin=dict(l=60, r=60, t=80, b=60)
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("---")

    # =====================================================
    # EXECUTIVE INSIGHTS
    # =====================================================
    total = len(df)
    pos_cnt = df[df["Emotion_norm"].isin(POSITIVE_EMOTIONS)].shape[0]
    neg_cnt = df[df["Emotion_norm"].isin(NEGATIVE_EMOTIONS)].shape[0]
    neu_cnt = df[df["Emotion_norm"] == NEUTRAL_EMOTION].shape[0]

    pos_pct = pos_cnt / total * 100
    neg_pct = neg_cnt / total * 100
    neu_pct = neu_cnt / total * 100

    top_neg = (
        df[df["Emotion_norm"].isin(NEGATIVE_EMOTIONS)]["Emotion"]
        .value_counts()
        .idxmax()
        if neg_cnt else "N/A"
    )

    worst_lob = (
        df[df["Emotion_norm"].isin(NEGATIVE_EMOTIONS)]
        .groupby("LOB")
        .size()
        .sort_values(ascending=False)
        .index[0]
        if "LOB" in df.columns and neg_cnt else "N/A"
    )

    st.markdown("### 💡 Executive Insights")

    i1, i2, i3 = st.columns(3)

    with i1:
        st.success(f"""
        **😊 Positive Experience**
        - {pos_cnt:,} tickets ({pos_pct:.1f}%)
        - Driven by **Joy & Satisfaction**
        - Indicates successful resolutions
        """)

    with i2:
        st.error(f"""
        **😠 Negative Experience**
        - {neg_cnt:,} tickets ({neg_pct:.1f}%)
        - Dominated by **{top_neg}**
        - High risk of dissatisfaction
        """)

    with i3:
        st.warning(f"""
        **⚠️ Operational Risk**
        - Most impacted LOB: **{worst_lob}**
        - Neutral interactions: {neu_pct:.1f}%
        - Improvement opportunity exists
        """)

    # =====================================================
    # EXECUTIVE TAKEAWAY
    # =====================================================
    sentiment_state = (
        "strong" if neg_pct < 25 else
        "moderate" if neg_pct < 40 else
        "concerning"
    )

    st.caption(
        f"""
        📌 **Executive Takeaway:**  
        Customer sentiment is **{sentiment_state}**, with improvement opportunities concentrated in
        **{worst_lob if worst_lob != "N/A" else "specific segments"}**.
        Reducing **{top_neg.lower()}-driven interactions** and improving response effectiveness
        can significantly lift customer satisfaction.
        """
    )

