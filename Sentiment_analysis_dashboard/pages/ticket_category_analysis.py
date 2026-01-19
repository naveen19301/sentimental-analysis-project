import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def show(df):
    st.title("📂 Issue Classification Analysis")
    st.markdown("Clear visibility into customer issue types, risk exposure, and resolution effectiveness")
    st.markdown("---")

    # Store original dataframe for sentiment heatmap
    df_original = df.copy()

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

    if "Ticket Category" in df.columns:
        categories = sorted(df["Ticket Category"].dropna().unique())
        selected_categories = st.sidebar.multiselect(
            "Ticket Category",
            categories,
            default=categories
        )
        if selected_categories:
            df = df[df["Ticket Category"].isin(selected_categories)]

    st.markdown("---")

    # =====================================================
    # OVERVIEW METRICS
    # =====================================================
    st.markdown("### 📊 Category Overview")

    total_tickets = len(df)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Tickets", f"{total_tickets:,}")

    with col2:
        st.metric(
            "Active Categories",
            df["Ticket Category"].nunique()
        )

    if "Sentiment Label" in df.columns:
        neg_pct = (df["Sentiment Label"] == "Negative").mean() * 100
        with col3:
            st.metric("Negative Sentiment", f"{neg_pct:.1f}%")

    if "resolution_hours" in df.columns:
        with col4:
            st.metric("Avg Resolution", f"{df['resolution_hours'].mean():.1f}h")

    st.markdown("---")

    # =====================================================
    # CATEGORY DISTRIBUTION - BAR CHART
    # =====================================================
    st.markdown("### 🎯 Category Distribution")

    if "Ticket Category" in df.columns:
        cat_counts = df["Ticket Category"].value_counts().reset_index()
        cat_counts.columns = ["Category", "Count"]
        cat_counts["Percentage"] = (cat_counts["Count"] / cat_counts["Count"].sum() * 100).round(1)
        
        fig_dist = px.bar(
            cat_counts,
            x="Category",
            y="Count",
            title="Issue Distribution Across Categories",
            color="Count",
            color_continuous_scale="Viridis",
            text="Count",
            hover_data={"Percentage": True}
        )
        
        fig_dist.update_traces(
            texttemplate='%{text}',
            textposition='outside',
            hovertemplate="<b>%{x}</b><br>Tickets: %{y}<br>Percentage: %{customdata[0]}%<extra></extra>"
        )
        
        fig_dist.update_layout(
            template="plotly_dark",
            height=500,
            xaxis_tickangle=-45,
            xaxis_title="Category",
            yaxis_title="Number of Tickets",
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0.2)"
        )
        
        st.plotly_chart(fig_dist, use_container_width=True)

    st.markdown("---")

    # =====================================================
    # CATEGORY VOLUME - ENHANCED BAR WITH GRADIENT
    # =====================================================
    st.markdown("### 📊 Ticket Volume by Category")

    cat_counts = df["Ticket Category"].value_counts().sort_values(ascending=True)
    
    # Create gradient colors
    colors = px.colors.sequential.Viridis
    color_idx = [int(i * (len(colors) - 1) / (len(cat_counts) - 1)) for i in range(len(cat_counts))]
    bar_colors = [colors[idx] for idx in color_idx]

    fig_cat = go.Figure()
    
    fig_cat.add_trace(go.Bar(
        x=cat_counts.values,
        y=cat_counts.index,
        orientation="h",
        marker=dict(
            color=cat_counts.values,
            colorscale="Viridis",
            showscale=False,
            line=dict(color='rgba(255,255,255,0.3)', width=1)
        ),
        text=cat_counts.values,
        textposition="outside",
        textfont=dict(size=12, color="white"),
        hovertemplate="<b>%{y}</b><br>Tickets: %{x}<extra></extra>"
    ))

    fig_cat.update_layout(
        template="plotly_dark",
        height=500,
        title="Where customer issues are concentrated",
        xaxis_title="Number of Tickets",
        yaxis_title="",
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0.2)",
        margin=dict(l=20, r=100, t=60, b=40)
    )

    st.plotly_chart(fig_cat, use_container_width=True)

    st.markdown("---")

    # =====================================================
    # SENTIMENT HEATMAP BY CATEGORY (COUNTS - ONLY COMPLETED)
    # =====================================================
    st.markdown("### 🌡️ Sentiment Heatmap by Category")

    if "Sentiment Label" in df_original.columns:
        # Filter only completed tickets for sentiment analysis
        df_completed = df_original.copy()
        if "processing_status" in df_completed.columns:
            df_completed = df_completed[df_completed["processing_status"] == "Completed"]
        
        # Create sentiment matrix with counts
        sentiment_matrix = pd.crosstab(
            df_completed["Ticket Category"],
            df_completed["Sentiment Label"]
        )
        
        # Reorder columns if they exist
        col_order = [col for col in ["Negative", "Neutral", "Positive"] if col in sentiment_matrix.columns]
        sentiment_matrix = sentiment_matrix[col_order]
        
        fig_heat = go.Figure(data=go.Heatmap(
            z=sentiment_matrix.values,
            x=sentiment_matrix.columns,
            y=sentiment_matrix.index,
            colorscale="RdYlGn",
            text=sentiment_matrix.values,
            texttemplate="%{text}",
            textfont={"size": 11},
            hovertemplate="<b>%{y}</b><br>%{x}: %{z} tickets<extra></extra>",
            colorbar=dict(title="Ticket Count")
        ))
        
        fig_heat.update_layout(
            template="plotly_dark",
            height=500,
            title="Sentiment distribution across categories (Completed Tickets Only)",
            xaxis_title="Sentiment",
            yaxis_title="Category",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        
        st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("---")    

    # =====================================================
    # RESOLUTION TIME - BOX PLOT
    # =====================================================
    st.markdown("### ⏱️ Resolution Time Distribution")

    if "resolution_hours" in df.columns:
        fig_box = px.box(
            df,
            x="Ticket Category",
            y="resolution_hours",
            title="Resolution time spread shows consistency and outliers",
            labels={
                "resolution_hours": "Resolution Time (Hours)",
                "Ticket Category": "Category"
            },
            color="Ticket Category",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig_box.update_layout(
            template="plotly_dark",
            height=500,
            showlegend=False,
            xaxis_tickangle=-45,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0.2)"
        )
        
        fig_box.update_traces(
            marker=dict(opacity=0.6),
            line=dict(width=2)
        )
        
        st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("---")

    # =====================================================
    # RISK GAUGE CHART
    # =====================================================
    if "Complaint Risk Level" in df.columns:
        st.markdown("### 🎯 Risk Level Distribution")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            risk_by_cat = pd.crosstab(
                df["Ticket Category"],
                df["Complaint Risk Level"]
            )
            
            # Reorder risk levels
            risk_order = ["Low", "Medium", "High", "Critical"]
            risk_cols = [col for col in risk_order if col in risk_by_cat.columns]
            risk_by_cat = risk_by_cat[risk_cols]
            
            fig_risk_stack = go.Figure()
            
            colors_risk = {
                "Low": "#10b981",
                "Medium": "#f59e0b",
                "High": "#ef4444",
                "Critical": "#7f1d1d"
            }
            
            for col in risk_by_cat.columns:
                fig_risk_stack.add_trace(go.Bar(
                    name=col,
                    x=risk_by_cat.index,
                    y=risk_by_cat[col],
                    marker_color=colors_risk.get(col, "#6b7280"),
                    text=risk_by_cat[col],
                    textposition="inside",
                    hovertemplate="<b>%{x}</b><br>" + col + ": %{y}<extra></extra>"
                ))
            
            fig_risk_stack.update_layout(
                barmode="stack",
                template="plotly_dark",
                height=500,
                title="Risk levels stacked by category",
                xaxis_title="Category",
                yaxis_title="Number of Tickets",
                xaxis_tickangle=-45,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0.2)",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig_risk_stack, use_container_width=True)
        
        with col2:
            # Risk gauge
            risk_counts = df["Complaint Risk Level"].value_counts()
            high_critical = risk_counts.get("High", 0) + risk_counts.get("Critical", 0)
            risk_pct = (high_critical / len(df) * 100) if len(df) > 0 else 0
            
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=risk_pct,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "High/Critical<br>Risk %", 'font': {'size': 20}},
                delta={'reference': 25, 'increasing': {'color': "#ef4444"}},
                gauge={
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},
                    'bar': {'color': "#ef4444" if risk_pct > 25 else "#10b981"},
                    'bgcolor': "rgba(0,0,0,0.3)",
                    'borderwidth': 2,
                    'bordercolor': "white",
                    'steps': [
                        {'range': [0, 15], 'color': 'rgba(16, 185, 129, 0.3)'},
                        {'range': [15, 30], 'color': 'rgba(245, 158, 11, 0.3)'},
                        {'range': [30, 100], 'color': 'rgba(239, 68, 68, 0.3)'}
                    ],
                    'threshold': {
                        'line': {'color': "white", 'width': 4},
                        'thickness': 0.75,
                        'value': 25
                    }
                }
            ))
            
            fig_gauge.update_layout(
                template="plotly_dark",
                height=350,
                paper_bgcolor="rgba(0,0,0,0)",
                font={'color': "white", 'family': "Arial"}
            )
            
            st.plotly_chart(fig_gauge, use_container_width=True)

    st.markdown("---")

    # =====================================================
    # INSIGHTS CARDS
    # =====================================================
    st.markdown("### 💡 Key Insights")

    cat_counts_series = df["Ticket Category"].value_counts()
    top_cat = cat_counts_series.idxmax() if len(cat_counts_series) > 0 else "N/A"

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info(f"""
        **📌 Volume Driver**
        - **{top_cat}** generates the highest ticket load
        - Primary contributor to operational demand
        - Automation or deflection can reduce pressure
        """)

    if "Sentiment Label" in df.columns and len(df[df["Sentiment Label"] == "Negative"]) > 0:
        worst_cat = (
            df[df["Sentiment Label"] == "Negative"]
            ["Ticket Category"]
            .value_counts()
            .idxmax()
        )

        with col2:
            st.warning(f"""
            **😞 Sentiment Risk**
            - **{worst_cat}** shows highest dissatisfaction
            - Indicates unmet expectations
            - Needs content, policy, or process correction
            """)

    if "resolution_hours" in df.columns:
        slow_cat = (
            df.groupby("Ticket Category")["resolution_hours"]
            .mean()
            .idxmax()
        )

        with col3:
            st.error(f"""
            **⏳ Efficiency Gap**
            - **{slow_cat}** resolves slowest
            - High SLA breach potential
            - Opportunity for SOP optimization
            """)

    st.markdown("---")

    # =====================================================
    # EXECUTIVE TAKEAWAY
    # =====================================================
    st.markdown("### 📌 Executive Takeaway")

    if "Sentiment Label" in df.columns:
        neg_pct = (df["Sentiment Label"] == "Negative").mean() * 100
        sentiment_state = (
            "healthy" if neg_pct < 20 else
            "moderate" if neg_pct < 35 else
            "at risk"
        )
        
        worst_cat_text = worst_cat if 'worst_cat' in locals() else top_cat

        st.caption(
            f"""
            📌 **Customer issue landscape is {sentiment_state}.**  
            Ticket volume is dominated by **{top_cat}**, while **{worst_cat_text}**
            disproportionately impacts customer sentiment.  
            Prioritizing resolution speed and quality improvements in these
            categories can deliver immediate CX gains.
            """
        )
    else:
        st.caption(
            f"""
            📌 Ticket volume is dominated by **{top_cat}**.  
            Prioritizing resolution speed and quality improvements in this
            category can deliver immediate CX gains.
            """
        )