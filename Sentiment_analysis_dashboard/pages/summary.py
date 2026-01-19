import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

@st.cache_data(show_spinner=False)
def cache_groupby(df, group_cols, agg_dict):
    return df.groupby(group_cols).agg(agg_dict)

@st.cache_data(show_spinner=False)
def cache_filter(df, col, values):
    return df[df[col].isin(values)]

def premium_kpi_card(title, value, subtitle="", icon=""):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">{icon} {title}</div>
        <div class="kpi-value">{value}</div>
        <div style="font-size:12px;color:rgba(255,255,255,0.5);margin-top:4px;">
            {subtitle}
        </div>
    </div>
    """, unsafe_allow_html=True)

def show(df):
    st.title("📌 Executive Summary")
    st.markdown("Quick insights into overall support health and performance")
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

    if "Major Categories" in df.columns:
        cats = sorted(df["Major Categories"].dropna().astype(str).unique())
        selected_cats = st.sidebar.multiselect("Major Categories", cats, cats)
        if selected_cats:
            df = df[df["Major Categories"].isin(selected_cats)]

    # =====================================================
    # TICKET CLASSIFICATION (UI LABELS ONLY)
    # =====================================================
    st.markdown("### 📋 Ticket Classification")

    total_tickets = len(df)

    measurable = (
        df[df["processing_status"].astype(str).str.strip() == "Completed"].shape[0]
        if "processing_status" in df.columns else 0
    )

    immeasurable = (
        df[df["processing_status"].astype(str).str.strip() == "Completed - No Inbound"].shape[0]
        if "processing_status" in df.columns else 0
    )

    measurable_rate = (measurable / total_tickets * 100) if total_tickets else 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        premium_kpi_card("Total Tickets", f"{total_tickets:,}", "All tickets", "📊")

    with col2:
        premium_kpi_card(
            "Measurable Tickets",
            f"{measurable:,}",
            f"{measurable_rate:.1f}% of total",
            "✔️"
        )

    with col3:
        premium_kpi_card(
            "Immeasurable Tickets",
            f"{immeasurable:,}",
            f"{(immeasurable/total_tickets*100):.1f}%" if total_tickets else "0%",
            "⛔"
        )

    with col4:
        icon = "🟢" if measurable_rate >= 90 else "🟡" if measurable_rate >= 70 else "🔴"
        premium_kpi_card(
            "Coverage",
            f"{icon} {measurable_rate:.1f}%",
            "Measurable tickets",
            "📈"
        )

    st.markdown("---")

    # =====================================================
    # MEASURABLE DATA FOR SENTIMENT
    # =====================================================
    df_measurable = (
        df[df["processing_status"].astype(str).str.strip() == "Completed"]
        if "processing_status" in df.columns else df
    )

    # =====================================================
    # KPI METRICS
    # =====================================================
    st.markdown("### 📊 Key Performance Indicators")

    positive = (df_measurable["Sentiment Label"] == "Positive").sum()
    neutral = (df_measurable["Sentiment Label"] == "Neutral").sum()
    negative = (df_measurable["Sentiment Label"] == "Negative").sum()

    avg_resolution = df_measurable["resolution_hours"].mean()
    avg_sentiment = df_measurable["Sentiment Score"].mean()

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        premium_kpi_card("Positive", f"{positive:,}", "😊", "😊")
    with c2:
        premium_kpi_card("Neutral", f"{neutral:,}", "😐", "😐")
    with c3:
        premium_kpi_card("Negative", f"{negative:,}", "😞", "😞")
    with c4:
        premium_kpi_card("Avg Resolution", f"{avg_resolution:.1f}h", "Hours", "⏱️")
    with c5:
        icon = "🟢" if avg_sentiment > 0.3 else "🟡" if avg_sentiment > -0.1 else "🔴"
        premium_kpi_card("Sentiment Score", f"{icon} {avg_sentiment:.3f}", "Overall", "📊")

    st.markdown("---")

    # =====================================================
    # TICKET VOLUME TREND
    # =====================================================
    if "created" in df.columns:
        daily = df.groupby(df["created"].dt.date).size().reset_index(name="count")
        fig = px.line(
            daily,
            x="created",
            y="count",
            title="Daily Ticket Volume",
            labels={"created": "Date", "count": "Tickets"}
        )
        fig.update_traces(fill="tozeroy", line_color="#667eea", line_width=3)
        fig.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig, width="stretch")

    st.markdown("---")

    # =====================================================
    # SENTIMENT PIE + FUNNEL
    # =====================================================
    col_l, col_r = st.columns(2)

    with col_l:
        sentiment_counts = df_measurable["Sentiment Label"].value_counts()
        fig_pie = px.pie(
            values=sentiment_counts.values,
            names=sentiment_counts.index,
            hole=0.4,
            title="Sentiment Distribution (Measurable Tickets)",
            color=sentiment_counts.index,
            color_discrete_map={
                "Positive": "#10b981",
                "Neutral": "#6b7280",
                "Negative": "#ef4444"
            }
        )
        fig_pie.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig_pie, width="stretch")

    with col_r:
        funnel_df = pd.DataFrame([
            {"Stage": "Total Tickets", "Count": total_tickets},
            {"Stage": "Measurable Tickets", "Count": measurable},
            {"Stage": "Positive", "Count": positive},
            {"Stage": "Actionable", "Count": positive + negative}
        ])

        fig_funnel = go.Figure(go.Funnel(
            y=funnel_df["Stage"],
            x=funnel_df["Count"],
            textinfo="value+percent initial",
            marker=dict(color=["#667eea", "#764ba2", "#10b981", "#f59e0b"])
        ))
        fig_funnel.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig_funnel, width="stretch")

    st.markdown("---")

    # =====================================================
    # LOB + SLA GAUGE
    # =====================================================
    col_l2, col_r2 = st.columns(2)

    with col_l2:
        if "LOB" in df.columns:
            lob_counts = df["LOB"].value_counts().head(10)
            fig_lob = px.bar(
                x=lob_counts.values,
                y=lob_counts.index,
                orientation="h",
                title="Top 10 Lines of Business",
                labels={"x": "Tickets", "y": "LOB"}
            )
            fig_lob.update_layout(template="plotly_dark", height=400)
            st.plotly_chart(fig_lob, width="stretch")

    with col_r2:
        if "resolution_hours" in df.columns:
            within_sla = (df["resolution_hours"] <= 24).sum()
            sla_pct = (within_sla / len(df) * 100) if len(df) else 0

            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=sla_pct,
                title={"text": "% Resolved within 24h"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#667eea"},
                    "steps": [
                        {"range": [0, 50], "color": "rgba(239,68,68,0.3)"},
                        {"range": [50, 80], "color": "rgba(245,158,11,0.3)"},
                        {"range": [80, 100], "color": "rgba(16,185,129,0.3)"}
                    ],
                    "threshold": {"line": {"color": "white", "width": 4}, "value": 80}
                }
            ))
            fig_gauge.update_layout(template="plotly_dark", height=400)
            st.plotly_chart(fig_gauge, width="stretch")

    st.markdown("---")

    # =====================================================
    # 🔥 KEY INSIGHTS (ENHANCED & DYNAMIC)
    # =====================================================
    st.markdown("### 💡 Executive Insights")

    total_measured = len(df_measurable)

    # Safety checks
    if total_measured > 0:
        pos_rate = (positive / total_measured) * 100
        neg_rate = (negative / total_measured) * 100
    else:
        pos_rate = neg_rate = 0

    # Best & Worst LOB
    best_lob = worst_lob = None
    if "LOB" in df_measurable.columns and total_measured > 0:
        lob_perf = (
            df_measurable.groupby("LOB")
            .agg(
                avg_sentiment=("Sentiment Score", "mean"),
                ticket_count=("Sentiment Score", "count")
            )
            .reset_index()
            .sort_values("avg_sentiment")
        )
        worst_lob = lob_perf.iloc[0]
        best_lob = lob_perf.iloc[-1]

    # Peak negative day
    peak_neg_day = None
    if "created" in df_measurable.columns and negative > 0:
        df_measurable["_day"] = df_measurable["created"].dt.day_name()
        neg_by_day = (
            df_measurable[df_measurable["Sentiment Label"] == "Negative"]
            .groupby("_day")
            .size()
            .sort_values(ascending=False)
        )
        if not neg_by_day.empty:
            peak_neg_day = neg_by_day.index[0]

    i1, i2, i3 = st.columns(3)

    # -----------------------------------------------------
    with i1:
        st.info(f"""
        **📊 Data Coverage & Quality**
        
        • **{measurable_rate:.1f}%** tickets are measurable  
        • **{immeasurable:,}** tickets excluded from sentiment  
        • Insights reflect **actual customer conversations**
        
        👉 High coverage ensures reliable analysis
        """)

    # -----------------------------------------------------
    with i2:
        st.success(f"""
        **😊 Customer Sentiment Health**
        
        • **{pos_rate:.1f}%** positive sentiment  
        • **{neg_rate:.1f}%** negative sentiment  
        • Overall mood: **{"Healthy" if pos_rate > 60 else "Mixed" if pos_rate > 40 else "At Risk"}**
        
        👉 Indicates customer satisfaction trend
        """)

    # -----------------------------------------------------
    with i3:
        risk_msg = (
            f"Weakest LOB: **{worst_lob['LOB']}** (avg sentiment {worst_lob['avg_sentiment']:.2f})"
            if worst_lob is not None else
            "LOB-level risk not significant"
        )

        time_msg = (
            f"Negativity peaks on **{peak_neg_day}**"
            if peak_neg_day else
            "No strong day-wise negativity pattern"
        )

        st.warning(f"""
        **⚠️ Operational Risk Signals**
        
        • {risk_msg}  
        • {time_msg}  
        • SLA compliance: **{sla_pct:.1f}%**
        
        👉 Focus areas for service improvement
        """)

    # -----------------------------------------------------
    st.markdown("---")

    # Executive takeaway
    st.caption(
        f"""
        📌 **Executive Takeaway:**  
        Customer sentiment is **{"strong" if pos_rate > 60 else "moderate" if pos_rate > 40 else "concerning"}**.
        Priority attention should be given to **{worst_lob['LOB'] if worst_lob is not None else "specific segments"}**
        to improve satisfaction and reduce negative experiences.
        """
    )
