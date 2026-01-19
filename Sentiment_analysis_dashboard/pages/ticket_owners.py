import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# =====================================================
# SAFE DATA NORMALIZATION (DO NOT REMOVE)
# =====================================================
def normalize_columns(df):
    if "Sentiment Score" in df.columns and "sentiment_score" not in df.columns:
        df["sentiment_score"] = pd.to_numeric(df["Sentiment Score"], errors="coerce")

    if "Sentiment Label" in df.columns and "sentiment_label" not in df.columns:
        df["sentiment_label"] = df["Sentiment Label"].astype(str)

    if "Number of Reopen" in df.columns:
        df["Number of Reopen"] = pd.to_numeric(
            df["Number of Reopen"], errors="coerce"
        ).fillna(0)

    return df

# =====================================================
# MAIN PAGE
# =====================================================
def show(df):
    df = normalize_columns(df)

    st.title("👥 Ticket Owner Statistics")
    st.markdown("Comprehensive analysis of support agent performance and workload distribution")
    st.markdown("---")

    # =====================================================
    # SIDEBAR FILTERS
    # =====================================================
    st.sidebar.markdown("### 🔍 Filters")

    if "created" in df.columns:
        min_date = df["created"].min().date()
        max_date = df["created"].max().date()
        date_range = st.sidebar.date_input(
            "Date Range",
            (min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        if len(date_range) == 2:
            df = df[
                (df["created"].dt.date >= date_range[0]) &
                (df["created"].dt.date <= date_range[1])
            ]

    if "Ticket Owner" in df.columns:
        owners = sorted(df["Ticket Owner"].dropna().unique())
        selected_owners = st.sidebar.multiselect(
            "Ticket Owners",
            owners,
            owners[:20] if len(owners) > 20 else owners
        )
        if selected_owners:
            df = df[df["Ticket Owner"].isin(selected_owners)]

    total_tickets = len(df)
    total_agents = df["Ticket Owner"].nunique()

    # =====================================================
    # TEAM OVERVIEW
    # =====================================================
    st.markdown("### 📊 Team Overview")

    c1, c2, c3, c4 = st.columns(4)

    avg_resolution = df["resolution_hours"].mean() if "resolution_hours" in df.columns else 0
    avg_load = total_tickets / total_agents if total_agents else 0

    c1.metric("Total Agents", total_agents)
    c2.metric("Total Tickets", f"{total_tickets:,}")
    c3.metric("Avg Tickets / Agent", f"{avg_load:.1f}")
    c4.metric("Avg Resolution Time", f"{avg_resolution:.1f}h")

    st.markdown("---")

    # =====================================================
    # TICKET VOLUME BY OWNER
    # =====================================================
    owner_counts = df["Ticket Owner"].value_counts().head(20)

    fig_owner_vol = px.bar(
        x=owner_counts.values,
        y=owner_counts.index,
        orientation="h",
        title="Top 20 Agents by Ticket Volume",
        color=owner_counts.values,
        color_continuous_scale="viridis"
    )
    fig_owner_vol.update_layout(template="plotly_dark", height=600)
    st.plotly_chart(fig_owner_vol, use_container_width=True)

    st.markdown("---")

    # =====================================================
    # PERFORMANCE MATRIX
    # =====================================================
    owner_perf = df.groupby("Ticket Owner").agg(
        Avg_Resolution=("resolution_hours", "mean"),
        Avg_Sentiment=("sentiment_score", "mean"),
        Ticket_Count=("Ticket Id", "count"),
        Positive_Rate=("sentiment_label", lambda x: (x == "Positive").mean() * 100)
    ).reset_index()

    owner_perf = owner_perf.nlargest(30, "Ticket_Count")

    fig_matrix = px.scatter(
        owner_perf,
        x="Avg_Resolution",
        y="Avg_Sentiment",
        size="Ticket_Count",
        color="Positive_Rate",
        hover_name="Ticket Owner",
        title="Agent Performance Matrix (Speed vs Satisfaction)",
        color_continuous_scale="RdYlGn"
    )

    fig_matrix.add_hline(y=owner_perf["Avg_Sentiment"].median(), line_dash="dash")
    fig_matrix.add_vline(x=owner_perf["Avg_Resolution"].median(), line_dash="dash")
    fig_matrix.update_layout(template="plotly_dark", height=550)

    st.plotly_chart(fig_matrix, use_container_width=True)

    st.markdown("---")

    # =====================================================
    # POSITIVE / NEGATIVE DISTRIBUTION
    # =====================================================
    col_l, col_r = st.columns(2)

    with col_l:
        pos_agents = (
            df[df["sentiment_label"] == "Positive"]
            .groupby("Ticket Owner").size()
            .sort_values(ascending=False).head(10)
        )

        fig_pos = px.bar(
            x=pos_agents.values,
            y=pos_agents.index,
            orientation="h",
            title="Top Agents – Positive Tickets",
            color=pos_agents.values,
            color_continuous_scale="Greens"
        )
        fig_pos.update_layout(template="plotly_dark", height=450)
        st.plotly_chart(fig_pos, use_container_width=True)

    with col_r:
        neg_agents = (
            df[df["sentiment_label"] == "Negative"]
            .groupby("Ticket Owner").size()
            .sort_values(ascending=False).head(10)
        )

        fig_neg = px.bar(
            x=neg_agents.values,
            y=neg_agents.index,
            orientation="h",
            title="Agents with Most Negative Tickets",
            color=neg_agents.values,
            color_continuous_scale="Reds"
        )
        fig_neg.update_layout(template="plotly_dark", height=450)
        st.plotly_chart(fig_neg, use_container_width=True)

    st.markdown("---")

    # =====================================================
    # DETAILED AGENT TABLE
    # =====================================================
    agent_table = df.groupby("Ticket Owner").agg(
        Total_Tickets=("Ticket Id", "count"),
        Avg_Resolution=("resolution_hours", "mean"),
        Avg_Sentiment=("sentiment_score", "mean"),
        Reopened=("Number of Reopen", lambda x: (x > 0).sum())
    ).reset_index()

    st.dataframe(agent_table.round(2), use_container_width=True, height=420)

    st.markdown("---")

    # =====================================================
    # 💡 DYNAMIC INSIGHTS
    # =====================================================
    reopen_rate = (df["Number of Reopen"] > 0).mean() * 100
    workload_cv = df["Ticket Owner"].value_counts().std() / df["Ticket Owner"].value_counts().mean() * 100
    avg_sent = df["sentiment_score"].mean()

    i1, i2, i3 = st.columns(3)

    i1.info(f"""
    **⚖️ Workload Balance**
    - CV: {workload_cv:.1f}%
    - {"Balanced distribution" if workload_cv < 30 else "Imbalance detected"}
    """)

    i2.success(f"""
    **⚡ Efficiency**
    - Avg resolution: {avg_resolution:.1f}h
    - Reopen rate: {reopen_rate:.1f}%
    """)

    i3.warning(f"""
    **😊 Satisfaction**
    - Avg sentiment: {avg_sent:.3f}
    - {"Healthy experience" if avg_sent > 0.2 else "Needs improvement"}
    """)

    # =====================================================
    # 📌 EXECUTIVE TAKEAWAY
    # =====================================================
    sentiment_state = (
        "strong" if avg_sent > 0.3 and reopen_rate < 10 else
        "moderate" if avg_sent > 0.1 else
        "at risk"
    )

    worst_agent = (
        owner_perf.sort_values("Avg_Sentiment").iloc[0]["Ticket Owner"]
        if not owner_perf.empty else "specific agents"
    )

    st.caption(
        f"""
        📌 **Executive Takeaway:**  
        Team performance is **{sentiment_state}**. Attention should be focused on
        **{worst_agent}**, where lower sentiment and higher effort signals indicate
        coaching and process optimization opportunities.
        """
    )
