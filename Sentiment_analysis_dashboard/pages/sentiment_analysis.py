import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

@st.cache_data(show_spinner=False)
def cache_groupby(df, group_cols, agg_dict):
    return df.groupby(group_cols).agg(agg_dict)

@st.cache_data(show_spinner=False)
def get_sentiment_trend(df_subset):
    if "created" not in df_subset.columns or "Sentiment Label" not in df_subset.columns:
        return None
    trend_df = (
        df_subset.groupby([df_subset["created"].dt.date, "Sentiment Label"])
        .size()
        .reset_index(name="count")
    )
    trend_df.columns = ["date", "sentiment", "count"]
    return trend_df

@st.cache_data(show_spinner=False)
def get_channel_sentiment(df_subset):
    if "Channel" not in df_subset.columns or "Sentiment Label" not in df_subset.columns:
        return None
    return pd.crosstab(df_subset["Channel"], df_subset["Sentiment Label"])

@st.cache_data(show_spinner=False)
def get_category_counts(df_subset, sentiment_label):
    if "Major Categories" not in df_subset.columns:
        return None
    sub = df_subset[df_subset["Sentiment Label"] == sentiment_label]
    return sub["Major Categories"].value_counts().head(10)

@st.cache_data(show_spinner=False)
def get_sentiment_heatmap(df_subset):
    if "created" not in df_subset.columns or "Sentiment Score" not in df_subset.columns:
        return None
    
    # Create local copy to avoid modifying the original dataframe in cache
    temp = df_subset.copy()
    temp["day_of_week"] = temp["created"].dt.day_name()
    temp["hour"] = temp["created"].dt.hour

    heat = (
        temp.groupby(["day_of_week", "hour"])["Sentiment Score"]
        .mean()
        .reset_index()
    )

    pivot = heat.pivot(
        index="day_of_week",
        columns="hour",
        values="Sentiment Score"
    )

    day_order = [
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"
    ]
    return pivot.reindex(day_order)

def show(df):
    st.title("💬 Sentiment Analysis")
    st.markdown("Deep dive into customer sentiment patterns and trends")
    st.markdown("---")

    # =====================================================
    # FILTER TO MEASURABLE TICKETS (Completed)
    # =====================================================
    if "processing_status" in df.columns:
        df = df[df["processing_status"].astype(str).str.strip() == "Completed"]

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

    if "Sentiment Label" in df.columns:
        sentiments = df["Sentiment Label"].dropna().unique().tolist()
        selected = st.sidebar.multiselect("Sentiment", sentiments, sentiments)
        if selected:
            df = df[df["Sentiment Label"].isin(selected)]

    # =====================================================
    # SENTIMENT METRICS
    # =====================================================
    st.markdown("### 📊 Sentiment Overview")

    col1, col2, col3, col4 = st.columns(4)

    if "Sentiment Score" in df.columns:
        avg_score = df["Sentiment Score"].mean()
        median_score = df["Sentiment Score"].median()
        std_score = df["Sentiment Score"].std()

        with col1:
            st.metric("Average Score", f"{avg_score:.3f}", delta=f"±{std_score:.3f}")
        with col2:
            st.metric("Median Score", f"{median_score:.3f}")
        with col3:
            positive_pct = (df["Sentiment Label"] == "Positive").sum() / len(df) * 100
            st.metric("Positive Rate", f"{positive_pct:.1f}%")
        with col4:
            negative_pct = (df["Sentiment Label"] == "Negative").sum() / len(df) * 100
            st.metric("Negative Rate", f"{negative_pct:.1f}%")

    st.markdown("---")

    # =====================================================
    # SENTIMENT TREND OVER TIME
    # =====================================================
    if "created" in df.columns and "Sentiment Label" in df.columns:
        trend_df = get_sentiment_trend(df)

        fig_trend = px.line(
            trend_df,
            x="date",
            y="count",
            color="sentiment",
            title="Daily Sentiment Distribution",
            color_discrete_map={
                "Positive": "#10b981",
                "Neutral": "#6b7280",
                "Negative": "#ef4444"
            }
        )
        fig_trend.update_layout(template="plotly_dark", height=450)
        st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown("---")

    # =====================================================
    # SCORE DISTRIBUTION + CHANNEL STACK
    # =====================================================
    col_left, col_right = st.columns(2)

    with col_left:
        if "Sentiment Score" in df.columns:
            fig_hist = px.histogram(
                df,
                x="Sentiment Score",
                nbins=50,
                title="Distribution of Sentiment Scores",
                color_discrete_sequence=["#667eea"]
            )
            fig_hist.add_vline(x=avg_score, line_dash="dash", line_color="#f59e0b")
            fig_hist.add_vline(x=median_score, line_dash="dash", line_color="#10b981")
            fig_hist.update_layout(template="plotly_dark", height=400)
            st.plotly_chart(fig_hist, use_container_width=True)

    with col_right:
        if "Channel" in df.columns and "Sentiment Label" in df.columns:
            channel_sent = get_channel_sentiment(df)

            fig_channel = go.Figure()
            for s, c in {
                "Positive": "#10b981",
                "Neutral": "#6b7280",
                "Negative": "#ef4444"
            }.items():
                if s in channel_sent.columns:
                    fig_channel.add_bar(
                        name=s,
                        x=channel_sent.index,
                        y=channel_sent[s],
                        marker_color=c
                    )

            fig_channel.update_layout(
                barmode="stack",
                template="plotly_dark",
                height=400,
                title="Sentiment Distribution by Channel"
            )
            st.plotly_chart(fig_channel, use_container_width=True)

    st.markdown("---")

    # =====================================================
    # CATEGORY ANALYSIS
    # =====================================================
    col1, col2 = st.columns(2)

    with col1:
        if "Major Categories" in df.columns:
            top_pos = get_category_counts(df, "Positive")

            fig_pos = px.bar(
                x=top_pos.values,
                y=top_pos.index,
                orientation="h",
                title="Top Positive Categories",
                color_continuous_scale="Greens"
            )
            fig_pos.update_layout(template="plotly_dark", height=400)
            st.plotly_chart(fig_pos, use_container_width=True)

    with col2:
        if "Major Categories" in df.columns:
            top_neg = get_category_counts(df, "Negative")

            fig_neg = px.bar(
                x=top_neg.values,
                y=top_neg.index,
                orientation="h",
                title="Top Negative Categories",
                color_continuous_scale="Reds"
            )
            fig_neg.update_layout(template="plotly_dark", height=400)
            st.plotly_chart(fig_neg, use_container_width=True)

    st.markdown("---")

    # =====================================================
    # HEATMAP
    # =====================================================
    if "created" in df.columns and "Sentiment Score" in df.columns:
        pivot = get_sentiment_heatmap(df)

        fig_heat = px.imshow(
            pivot,
            title="Average Sentiment Score by Day & Hour",
            color_continuous_scale="RdYlGn",
            labels=dict(x="Hour of Day", y="Day of Week", color="Avg Sentiment"),
            aspect="auto"
        )
        fig_heat.update_layout(
            template="plotly_dark",
            height=400,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_heat, use_container_width=True)


        # =====================================================
    # === SMART SENTIMENT INSIGHTS (DYNAMIC)
    # =====================================================
    st.markdown("### 💡 Key Sentiment Insights")

    total_records = len(df)

    avg_sent = df["Sentiment Score"].mean()
    neg_pct = (df["Sentiment Label"] == "Negative").mean() * 100
    pos_pct = (df["Sentiment Label"] == "Positive").mean() * 100

    worst_lob = None
    top_lob = None

    if "LOB" in df.columns and total_records > 0:
        lob_stats = (
            df.groupby("LOB")
            .agg(
                avg_sentiment=("Sentiment Score", "mean"),
                ticket_count=("Sentiment Score", "count"),
                negative_rate=("Sentiment Label", lambda x: (x == "Negative").mean() * 100)
            )
            .reset_index()
        )

        worst_lob = lob_stats.sort_values("avg_sentiment").iloc[0]
        top_lob = lob_stats.sort_values("avg_sentiment", ascending=False).iloc[0]

    # Time-based insight
    peak_negative_hour = None
    if "created" in df.columns:
        df["_hour"] = df["created"].dt.hour
        hour_neg = (
            df[df["Sentiment Label"] == "Negative"]
            .groupby("_hour")
            .size()
            .sort_values(ascending=False)
        )
        if not hour_neg.empty:
            peak_negative_hour = hour_neg.index[0]

    # =====================================================
    # INSIGHT CARDS
    # =====================================================
    col1, col2, col3 = st.columns(3)

    with col1:
        st.success(f"""
        **😊 Overall Sentiment Health**
        
        • Avg sentiment score: **{avg_sent:.2f}**  
        • Positive tickets: **{pos_pct:.1f}%**  
        • Sentiment trend is **{"healthy" if avg_sent > 0.15 else "mixed" if avg_sent > -0.1 else "concerning"}**
        
        👉 Indicates how customers *feel overall*
        """)

    with col2:
        if worst_lob is not None:
            st.warning(f"""
            **⚠️ Risk Concentration**
            
            • Weakest LOB: **{worst_lob['LOB']}**  
            • Avg sentiment: **{worst_lob['avg_sentiment']:.2f}**  
            • Negative rate: **{worst_lob['negative_rate']:.1f}%**
            
            👉 Priority area for **service improvement**
            """)
        else:
            st.warning("Not enough LOB data for risk analysis.")

    with col3:
        insight_msg = (
            f"Peak negative sentiment occurs around **{peak_negative_hour}:00 hrs**"
            if peak_negative_hour is not None
            else "No strong time-based negativity detected"
        )

        st.info(f"""
        **⏰ Behavioral Pattern**
        
        • {insight_msg}  
        • Monitor staffing & response quality during this window  
        • Consider proactive communication
        
        👉 Helps **optimize operations timing**
        """)

    # =====================================================
    # OPTIONAL EXECUTIVE SUMMARY LINE
    # =====================================================
    st.markdown("---")
    st.caption(
        f"""
        📌 **Executive takeaway:**  
        Customer sentiment is **{'strong' if avg_sent > 0.2 else 'moderate' if avg_sent > -0.05 else 'at risk'}**, 
        with improvement opportunities concentrated in **{worst_lob['LOB'] if worst_lob is not None else 'specific segments'}**.
        """
    )
