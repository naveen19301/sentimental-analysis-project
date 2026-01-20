import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

@st.cache_data(show_spinner=False)
def cache_groupby(df, group_cols, agg_dict):
    return df.groupby(group_cols).agg(agg_dict)

@st.cache_data(show_spinner=False)
def get_daily_performance(df_subset):
    if "created" not in df_subset.columns:
        return None
    daily = df_subset.groupby(df_subset["created"].dt.date).size().reset_index(name="count")
    daily["MA7"] = daily["count"].rolling(7, min_periods=1).mean()
    return daily

@st.cache_data(show_spinner=False)
def get_resolution_dist(df_subset):
    if "resolution_hours" not in df_subset.columns:
        return None
    Q1 = df_subset["resolution_hours"].quantile(0.25)
    Q3 = df_subset["resolution_hours"].quantile(0.75)
    IQR = Q3 - Q1
    
    clean = df_subset[
        (df_subset["resolution_hours"] >= Q1 - 1.5 * IQR) &
        (df_subset["resolution_hours"] <= Q3 + 1.5 * IQR)
    ]
    return clean

@st.cache_data(show_spinner=False)
def get_channel_performance(df_subset):
    if "Channel" not in df_subset.columns or "resolution_hours" not in df_subset.columns:
        return None
    
    agg = {"resolution_hours": ["mean", "median", "count"]}
    if "sentiment_score" in df_subset.columns:
        agg["sentiment_score"] = "mean"

    channel_perf = df_subset.groupby("Channel").agg(agg).reset_index()
    channel_perf.columns = (
        ["Channel", "Avg_Resolution", "Median_Resolution", "Ticket_Count"] +
        (["Avg_Sentiment"] if "sentiment_score" in df_subset.columns else [])
    )
    return channel_perf.sort_values("Ticket_Count", ascending=False)

@st.cache_data(show_spinner=False)
def get_hourly_weekly_stats(df_subset):
    if "created" not in df_subset.columns:
        return None, None
    
    # Hour stats
    temp = df_subset.copy()
    temp["hour"] = temp["created"].dt.hour
    hourly = temp.groupby("hour").size()
    
    # Day stats
    temp["day"] = temp["created"].dt.day_name()
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    daily = temp["day"].value_counts().reindex(order)
    
    return hourly, daily

def show(df):
    st.title("⏱️ Performance Metrics")
    st.markdown("Support team efficiency, resolution times, and operational insights")
    st.markdown("---")

    # =====================================================
    # SAFE COLUMN NORMALIZATION (DO NOT REMOVE)
    # =====================================================
    if "Sentiment Score" in df.columns and "sentiment_score" not in df.columns:
        df["sentiment_score"] = df["Sentiment Score"]

    if "Sentiment Label" in df.columns and "sentiment_label" not in df.columns:
        df["sentiment_label"] = df["Sentiment Label"]

    if "Number of Reopen" in df.columns:
        df["Number of Reopen"] = pd.to_numeric(
            df["Number of Reopen"], errors="coerce"
        ).fillna(0)

    total = len(df)

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

    if "Channel" in df.columns:
        channels = sorted(df["Channel"].dropna().astype(str).unique())
        selected_channels = st.sidebar.multiselect("Channel", channels, channels)
        if selected_channels:
            df = df[df["Channel"].isin(selected_channels)]

    # =====================================================
    # KPI METRICS
    # =====================================================
    st.markdown("### 📊 Key Performance Indicators")

    col1, col2, col3, col4 = st.columns(4)

    if "resolution_hours" in df.columns and total > 0:
        avg_resolution = df["resolution_hours"].mean()
        median_resolution = df["resolution_hours"].median()
        within_24h = (df["resolution_hours"] <= 24).sum()
        sla_compliance = within_24h / total * 100

        with col1:
            st.metric("Avg Resolution", f"{avg_resolution:.1f}h")
        with col2:
            st.metric("Median Resolution", f"{median_resolution:.1f}h")
        with col3:
            st.metric("Resolved ≤24h", f"{within_24h:,}")
        with col4:
            st.metric("SLA Compliance", f"{sla_compliance:.1f}%")

    st.markdown("---")

    # =====================================================
    # DAILY TICKET VOLUME
    # =====================================================
    st.markdown("### 📈 Daily Ticket Volume")

    if "created" in df.columns:
        daily = get_daily_performance(df)

        fig_volume = go.Figure()
        fig_volume.add_trace(go.Scatter(
            x=daily["created"],
            y=daily["count"],
            name="Daily Tickets",
            fill="tozeroy",
            line=dict(color="#667eea")
        ))
        fig_volume.add_trace(go.Scatter(
            x=daily["created"],
            y=daily["MA7"],
            name="7-Day Avg",
            line=dict(color="#f59e0b", dash="dash")
        ))

        fig_volume.update_layout(
            template="plotly_dark",
            height=450,
            hovermode="x unified"
        )
        st.plotly_chart(fig_volume, use_container_width=True)

    st.markdown("---")

    # =====================================================
    # RESOLUTION DISTRIBUTION
    # =====================================================
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### ⏱️ Resolution Time Distribution")

        if "resolution_hours" in df.columns:
            clean = get_resolution_dist(df)

            fig_hist = px.histogram(
                clean,
                x="resolution_hours",
                nbins=40,
                title="Resolution Hours (Outliers Removed)"
            )

            fig_hist.add_vline(
                x=clean["resolution_hours"].median(),
                line_dash="dash",
                line_color="#10b981",
                annotation_text="Median"
            )

            fig_hist.add_vline(
                x=clean["resolution_hours"].mean(),
                line_dash="dash",
                line_color="#f59e0b",
                annotation_text="Mean"
            )

            fig_hist.update_layout(template="plotly_dark", height=400)
            st.plotly_chart(fig_hist, use_container_width=True)

    with col_right:
        st.markdown("### 📊 Resolution by Sentiment")

        if "sentiment_label" in df.columns and "resolution_hours" in df.columns:
            fig_box = px.box(
                df,
                x="sentiment_label",
                y="resolution_hours",
                color="sentiment_label",
                title="Resolution Time by Sentiment",
                color_discrete_map={
                    "Positive": "#10b981",
                    "Neutral": "#6b7280",
                    "Negative": "#ef4444"
                }
            )
            fig_box.update_layout(template="plotly_dark", height=400)
            st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("---")

    # =====================================================
    # CHANNEL PERFORMANCE
    # =====================================================
    st.markdown("### 📱 Performance by Channel")

    if "Channel" in df.columns and "resolution_hours" in df.columns:
        channel_perf = get_channel_performance(df)

        fig_channel = go.Figure()

        fig_channel.add_bar(
            x=channel_perf["Channel"],
            y=channel_perf["Avg_Resolution"],
            name="Avg Resolution (hrs)",
            marker_color="#667eea"
        )

        fig_channel.add_bar(
            x=channel_perf["Channel"],
            y=channel_perf["Ticket_Count"],
            name="Ticket Volume",
            marker_color="#764ba2",
            yaxis="y2"
        )

        fig_channel.update_layout(
            template="plotly_dark",
            height=450,
            yaxis=dict(title="Avg Resolution"),
            yaxis2=dict(title="Ticket Count", overlaying="y", side="right"),
            barmode="group"
        )

        st.plotly_chart(fig_channel, use_container_width=True)

    st.markdown("---")

    # =====================================================
    # HOURLY & WEEKLY PATTERNS
    # =====================================================
    col1, col2 = st.columns(2)

    if "created" in df.columns:
        hourly, daily = get_hourly_weekly_stats(df)
        
        with col1:
            st.markdown("### 🕐 Tickets by Hour")
            fig_hour = px.line(
                x=hourly.index,
                y=hourly.values,
                markers=True,
                title="Hourly Ticket Volume"
            )
            fig_hour.update_layout(template="plotly_dark", height=400)
            st.plotly_chart(fig_hour, use_container_width=True)

        with col2:
            st.markdown("### 📅 Tickets by Day")
            fig_day = px.bar(
                x=daily.index,
                y=daily.values,
                title="Weekly Ticket Distribution"
            )
            fig_day.update_layout(template="plotly_dark", height=400)
            st.plotly_chart(fig_day, use_container_width=True)

    st.markdown("---")

    # =====================================================
    # INSIGHTS
    # =====================================================
    st.markdown("### 💡 Performance Insights")

    fast = (df["resolution_hours"] <= 4).sum() if total > 0 else 0
    reopen_rate = ((df["Number of Reopen"] > 0).sum() / total * 100) if total > 0 else 0
    peak_hour = df["created"].dt.hour.mode()[0] if "created" in df.columns and total > 0 else "N/A"
    worst_channel = channel_perf.iloc[0]["Channel"] if "Channel" in df.columns and total > 0 else "N/A"

    c1, c2, c3 = st.columns(3)

    with c1:
        st.success(f"""
        **⚡ Fast Resolution**
        - {fast:,} tickets ≤4h
        - {(fast/total*100):.1f}% efficiency
        """)

    with c2:
        st.warning(f"""
        **🔄 Reopen Risk**
        - {reopen_rate:.1f}% reopened
        - Indicates resolution quality gaps
        """)

    with c3:
        st.info(f"""
        **📊 Demand Pattern**
        - Peak hour: {peak_hour}:00
        - Highest load channel: {worst_channel}
        """)

    # =====================================================
    # EXECUTIVE TAKEAWAY
    # =====================================================
    state = "strong" if reopen_rate < 10 else "moderate" if reopen_rate < 20 else "at risk"

    st.caption(
        f"""
        📌 **Executive Takeaway:**  
        Operational performance is **{state}**.
        Reopen pressure and resolution delays are most visible in **{worst_channel}**,
        especially during **{peak_hour}:00** hours.
        Improving first-contact resolution and load balancing can significantly lift SLA outcomes.
        """
    )
