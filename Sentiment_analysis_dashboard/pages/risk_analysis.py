import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# CACHED HELPERS
# =====================================================
@st.cache_data(show_spinner=False)
def cache_groupby(df, group_cols, agg_dict):
    return df.groupby(group_cols).agg(agg_dict)

@st.cache_data(show_spinner=False)
def cache_filter(df, col, values):
    return df[df[col].isin(values)]

# =====================================================
# MAIN PAGE
# =====================================================
def show(df):
    st.title("🚨 Risk Analysis")
    st.markdown("Identify and manage high-risk tickets and complaint patterns")
    st.markdown("---")

    RISK_COL = "Complaint Risk Level"

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

    if RISK_COL in df.columns:
        risk_levels = ["Low", "Medium", "High", "Critical"]
        available = [r for r in risk_levels if r in df[RISK_COL].unique()]
        selected = st.sidebar.multiselect("Risk Level", available, available)
        if selected:
            df = df[df[RISK_COL].isin(selected)]

    total = len(df)

    # =====================================================
    # RISK OVERVIEW KPIs
    # =====================================================
    st.markdown("### 📊 Risk Overview")

    def cnt(level):
        return (df[RISK_COL] == level).sum() if RISK_COL in df.columns else 0

    low = cnt("Low")
    medium = cnt("Medium")
    high = cnt("High")
    critical = cnt("Critical")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("🟢 Low", f"{low:,}", f"{low/total*100:.1f}%" if total else "0%")
    with col2:
        st.metric("🟡 Medium", f"{medium:,}", f"{medium/total*100:.1f}%" if total else "0%")
    with col3:
        st.metric("🟠 High", f"{high:,}", f"{high/total*100:.1f}%" if total else "0%")
    with col4:
        st.metric("🔴 Critical", f"{critical:,}", f"{critical/total*100:.1f}%" if total else "0%")

    st.markdown("---")

    # =====================================================
    # RISK DISTRIBUTION
    # =====================================================
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("### 🎯 Risk Level Distribution")
        risk_counts = df[RISK_COL].value_counts()

        fig_pie = px.pie(
            values=risk_counts.values,
            names=risk_counts.index,
            hole=0.4,
            color=risk_counts.index,
            color_discrete_map={
                "Low": "#10b981",
                "Medium": "#f59e0b",
                "High": "#fb923c",
                "Critical": "#ef4444"
            }
        )
        fig_pie.update_layout(template="plotly_dark", height=420)
        st.plotly_chart(fig_pie, width="stretch")

    with col_r:
        st.markdown("### 📈 Risk Trend Over Time")
        if "created" in df.columns:
            trend = df.groupby([df["created"].dt.date, RISK_COL]).size().reset_index(name="count")
            trend.columns = ["date", "risk", "count"]

            fig_trend = px.line(
                trend,
                x="date",
                y="count",
                color="risk",
                color_discrete_map={
                    "Low": "#10b981",
                    "Medium": "#f59e0b",
                    "High": "#fb923c",
                    "Critical": "#ef4444"
                }
            )
            fig_trend.update_layout(template="plotly_dark", height=420)
            st.plotly_chart(fig_trend, width="stretch")

    st.markdown("---")

    # =====================================================
    # RISK VS SENTIMENT
    # =====================================================
    st.markdown("### 🔥 Risk vs Sentiment Correlation")

    if "Sentiment Label" in df.columns:
        heat = pd.crosstab(df[RISK_COL], df["Sentiment Label"])

        fig_heat = px.imshow(
            heat,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="Reds",
            labels=dict(x="Sentiment", y="Risk Level", color="Tickets")
        )
        fig_heat.update_layout(template="plotly_dark", height=460)
        st.plotly_chart(fig_heat, width="stretch")

    st.markdown("---")

    # =====================================================
    # HIGH & CRITICAL RISK CATEGORIES
    # =====================================================
    st.markdown("### 📋 High & Critical Risk Drivers")

    risk_df = df[df[RISK_COL].isin(["High", "Critical"])]

    if not risk_df.empty:
        col1, col2 = st.columns(2)

        with col1:
            if "Major Categories" in risk_df.columns:
                cats = risk_df["Major Categories"].value_counts().head(15)
                fig_cat = px.bar(
                    x=cats.values,
                    y=cats.index,
                    orientation="h",
                    color=cats.values,
                    color_continuous_scale="Reds"
                )
                fig_cat.update_layout(template="plotly_dark", height=520)
                st.plotly_chart(fig_cat, width="stretch")

        with col2:
            if "Channel" in risk_df.columns:
                ch = risk_df["Channel"].value_counts()
                fig_ch = px.bar(
                    x=ch.index,
                    y=ch.values,
                    color=ch.values,
                    color_continuous_scale="Reds"
                )
                fig_ch.update_layout(template="plotly_dark", height=520)
                st.plotly_chart(fig_ch, width="stretch")

    st.markdown("---")

    # =====================================================
    # HIGH RISK TICKETS TABLE
    # =====================================================
    st.markdown("### 🚨 High & Critical Risk Tickets")

    if not risk_df.empty:
        display_cols = [
            "Ticket Id", "Contact Name (Ticket)", "Sentiment Label",
            "emotion", "Channel", "LOB", RISK_COL, "created"
        ]
        display_cols = [c for c in display_cols if c in risk_df.columns]

        st.dataframe(
            risk_df.sort_values("created", ascending=False)[display_cols].head(50),
            width="stretch",
            height=420
        )

        csv = risk_df[display_cols].to_csv(index=False)
        st.download_button(
            "📥 Download High Risk Tickets",
            csv,
            "high_risk_tickets.csv",
            "text/csv"
        )

    st.markdown("---")

    # =====================================================
    # ENHANCED INSIGHTS
    # =====================================================
    st.markdown("### 💡 Risk Insights")

    neg = high + critical
    neg_pct = (neg / total * 100) if total else 0

    worst_lob = (
        risk_df["LOB"].value_counts().idxmax()
        if "LOB" in risk_df.columns and not risk_df.empty
        else "N/A"
    )

    worst_cat = (
        risk_df["Major Categories"].value_counts().idxmax()
        if "Major Categories" in risk_df.columns and not risk_df.empty
        else "key categories"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.error(
            f"""
            **🚨 Risk Exposure**
            - {neg:,} high / critical tickets
            - {neg_pct:.1f}% of workload
            - Escalation pressure is {"high" if neg_pct > 25 else "moderate"}
            """
        )

    with col2:
        st.warning(
            f"""
            **📌 Concentration Risk**
            - LOB most affected: **{worst_lob}**
            - Dominant issue: **{worst_cat}**
            - Targeted fixes will yield fastest impact
            """
        )

    with col3:
        st.info(
            f"""
            **🛡️ Preventive Actions**
            - Strengthen first-response quality
            - Reduce reopen loops
            - Improve SOP adherence for risky categories
            """
        )

    st.markdown("---")

    # =====================================================
    # EXECUTIVE TAKEAWAY
    # =====================================================
    risk_state = (
        "healthy" if neg_pct < 10 else
        "moderate" if neg_pct < 25 else
        "at risk"
    )

    st.caption(
        f"""
        📌 **Executive Takeaway:**  
        Complaint risk is **{risk_state}**, with elevated exposure concentrated in
        **{worst_lob}**.  
        Addressing **{worst_cat.lower()}-driven escalations** and improving early resolution
        quality will materially reduce customer dissatisfaction and operational risk.
        """
    )
