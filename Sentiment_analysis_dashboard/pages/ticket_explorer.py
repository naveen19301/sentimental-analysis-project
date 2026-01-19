import streamlit as st
import pandas as pd
from io import BytesIO

@st.cache_data(show_spinner=False)
def cache_groupby(df, group_cols, agg_dict):
    return df.groupby(group_cols).agg(agg_dict)

@st.cache_data(show_spinner=False)
def cache_filter(df, col, values):
    return df[df[col].isin(values)]

def show(df):
    st.title("📄 Ticket Explorer")
    st.markdown("Search, filter, and export detailed ticket information")
    st.markdown("---")

    # =====================================================
    # SEARCH & FILTERS
    # =====================================================
    st.markdown("### 🔍 Search & Filter")

    col1, col2 = st.columns([2, 1])

    with col1:
        search_query = st.text_input(
            "🔎 Search Tickets",
            placeholder="Search by ID, Subject, Description, Contact Name, or Message..."
        )

    with col2:
        search_fields = st.multiselect(
            "Search In",
            [
                "Ticket Id",
                "Subject",
                "Ticket Description",
                "Contact Name (Ticket)",
                "Inbound Thread"
            ],
            default=["Subject", "Ticket Description"]
        )

    # =====================================================
    # ADVANCED FILTERS
    # =====================================================
    with st.expander("🎯 Advanced Filters", expanded=True):
        f1, f2, f3 = st.columns(3)

        with f1:
            sentiments = (
                ["All"]
                + sorted(df["Sentiment Label"].dropna().astype(str).unique().tolist())
                if "Sentiment Label" in df.columns
                else ["All"]
            )
            selected_sentiment = st.selectbox("Sentiment", sentiments)

        with f2:
            risks = (
                ["All"]
                + sorted(df["Complaint Risk Level"].dropna().astype(str).unique().tolist())
                if "Complaint Risk Level" in df.columns
                else ["All"]
            )
            selected_risk = st.selectbox("Risk Level", risks)

        with f3:
            channels = (
                ["All"]
                + sorted(df["Channel"].dropna().astype(str).unique().tolist())
                if "Channel" in df.columns
                else ["All"]
            )
            selected_channel = st.selectbox("Channel", channels)

        f4, f5, f6 = st.columns(3)

        with f4:
            emotions = (
                ["All"]
                + sorted(df["Emotion"].dropna().astype(str).str.title().unique().tolist())
                if "Emotion" in df.columns
                else ["All"]
            )
            selected_emotion = st.selectbox("Emotion", emotions)

        with f5:
            lobs = (
                ["All"]
                + sorted(df["LOB"].dropna().astype(str).unique().tolist())
                if "LOB" in df.columns
                else ["All"]
            )
            selected_lob = st.selectbox("Line of Business", lobs)

        with f6:
            categories = (
                ["All"]
                + sorted(df["Ticket Category"].dropna().astype(str).unique().tolist())
                if "Ticket Category" in df.columns
                else ["All"]
            )
            selected_category = st.selectbox("Ticket Category", categories)

        if "created" in df.columns:
            d1, d2 = st.columns(2)
            with d1:
                start_date = st.date_input("From Date", df["created"].min().date())
            with d2:
                end_date = st.date_input("To Date", df["created"].max().date())

    # =====================================================
    # APPLY FILTERS
    # =====================================================
    filtered_df = df.copy()

    # ---------- REMOVE BLANK ROWS (CRITICAL FIX) ----------
    filter_columns = [
        "Sentiment Label",
        "Complaint Risk Level",
        "Channel",
        "Emotion",
        "LOB",
        "Ticket Category",
        "created"
    ]

    for col in filter_columns:
        if col in filtered_df.columns:
            filtered_df = filtered_df[
                filtered_df[col].notna() &
                (filtered_df[col].astype(str).str.strip() != "")
            ]

    # ---------- SEARCH ----------
    if search_query and search_fields:
        mask = pd.Series(False, index=filtered_df.index)
        for field in search_fields:
            if field in filtered_df.columns:
                mask |= filtered_df[field].astype(str).str.contains(
                    search_query, case=False, na=False
                )
        filtered_df = filtered_df[mask]

    # ---------- FILTERS ----------
    if selected_sentiment != "All":
        filtered_df = filtered_df[
            filtered_df["Sentiment Label"] == selected_sentiment
        ]

    if selected_risk != "All":
        filtered_df = filtered_df[
            filtered_df["Complaint Risk Level"] == selected_risk
        ]

    if selected_channel != "All":
        filtered_df = filtered_df[
            filtered_df["Channel"] == selected_channel
        ]

    if selected_emotion != "All":
        filtered_df = filtered_df[
            filtered_df["Emotion"].astype(str).str.title() == selected_emotion
        ]

    if selected_lob != "All":
        filtered_df = filtered_df[
            filtered_df["LOB"] == selected_lob
        ]

    if selected_category != "All":
        filtered_df = filtered_df[
            filtered_df["Ticket Category"] == selected_category
        ]

    if "created" in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df["created"].dt.date >= start_date) &
            (filtered_df["created"].dt.date <= end_date)
        ]

    st.markdown("---")

    # =====================================================
    # RESULTS SUMMARY
    # =====================================================
    st.markdown("### 📊 Results Summary")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Tickets Found", f"{len(filtered_df):,}")

    with c2:
        if "Sentiment Label" in filtered_df.columns:
            pos_rate = (
                (filtered_df["Sentiment Label"] == "Positive").sum()
                / len(filtered_df) * 100
                if len(filtered_df) else 0
            )
            st.metric("Positive Rate", f"{pos_rate:.1f}%")

    with c3:
        if "Complaint Risk Level" in filtered_df.columns:
            high_risk = (filtered_df["Complaint Risk Level"] == "High").sum()
            st.metric("High Risk", f"{high_risk:,}")

    with c4:
        if "resolution_hours" in filtered_df.columns:
            st.metric(
                "Avg Resolution",
                f"{filtered_df['resolution_hours'].mean():.1f}h"
            )

    st.markdown("---")

    # =====================================================
    # TABLE
    # =====================================================
    st.markdown(f"### 📑 Tickets ({len(filtered_df):,})")

    st.dataframe(
        filtered_df,
        width="stretch",
        height=600
    )

    st.caption(
        f"Dashboard generated on {pd.Timestamp.now():%Y-%m-%d %H:%M:%S} "
        f"| Showing {len(filtered_df):,} tickets"
    )
