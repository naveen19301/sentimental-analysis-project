# Customer Sentiment Analytics Dashboard

## 📊 Overview
A comprehensive Streamlit-based dashboard for analyzing customer sentiment data with advanced visualizations and insights.

## 🌟 Features

### Authentication
- **Password Protection**: Secure login system (Default password: `sentiment2024`)
- **Session Management**: Logout functionality

### Key Metrics Dashboard
- Total Tickets Count
- Average Sentiment Score
- Positive Rate Percentage
- Average Resolution Time
- High Risk Tickets Count

### Visualizations Included

1. **Sentiment Analysis Overview**
   - Sentiment Distribution Pie Chart (Positive/Neutral/Negative)
   - Top Emotions Detected Bar Chart

2. **Trend Analysis**
   - Daily Sentiment Trends Line Graph
   - Time-series analysis of sentiment changes

3. **Risk Analysis**
   - Complaint Risk Distribution
   - Risk Level vs Sentiment Heatmap

4. **Channel & LOB Analysis**
   - Sentiment by Channel (Stacked Bar Chart)
   - LOB Performance Scatter Plot (Volume vs Sentiment)

5. **Time-based Patterns**
   - Average Sentiment by Day of Week
   - Ticket Volume by Hour of Day

6. **Resolution Analysis**
   - Resolution Time by Sentiment (Box Plot)
   - Response Delay Distribution

7. **Detailed Insights**
   - High Risk Tickets Table
   - Category Performance Analysis
   - Statistical Summaries

### Interactive Filters
- Date Range Selection
- Sentiment Filter
- Channel Filter
- Line of Business Filter
- Risk Level Filter

## 🚀 Installation & Setup

### Prerequisites
```bash
pip install streamlit pandas plotly openpyxl
```

### Running the Dashboard

1. **Place the data file**: Ensure `training_data_cs.xlsx` is in the root directory.
2. **Run the dashboard**:
   - **Windows**: Run `start_dashboard.bat` or run `streamlit run customer_sentiment_dashboard.py`
   - **Linux/macOS**: Run `./start_dashboard.sh` or run `streamlit run customer_sentiment_dashboard.py`

3. **Access the dashboard**:
   - The dashboard will automatically open in your browser
   - Default URL: http://localhost:8501

4. **Login:**
   - Enter password: `sentiment2024`
   - Click enter or outside the text box

## 🔐 Security

### Changing the Password
Edit line 81 in `customer_sentiment_dashboard.py`:
```python
if st.session_state["password"] == "sentiment2024":  # Change this password
```
Replace `"sentiment2024"` with your desired password.

## 📁 Data Requirements

The dashboard expects an Excel file named `training_data_cs.xlsx` with the following columns:
- Ticket Id
- Email (Ticket)
- Contact Name (Ticket)
- Subject
- Ticket Description
- Status (Ticket)
- Resolution
- LOB
- Number of Reopen
- Channel
- Major Categories
- Sub Category
- Sub Sub Category
- Ticket Owner
- clean_message
- sentiment_score
- sentiment_label
- emotion
- created
- closed
- resolution_hours
- response_time_seconds
- response_delay_label
- complaint_risk
- complaint_risk_level
- sentiment_status

## 🎨 Design Features

- **Modern UI**: Gradient backgrounds and clean layouts
- **Responsive Design**: Works on desktop and tablet devices
- **Color-coded Metrics**: Visual indicators for positive/negative trends
- **Interactive Charts**: Hover, zoom, and pan capabilities
- **Custom Styling**: Professional color schemes and shadows

## 📊 Key Insights Provided

1. **Sentiment Distribution**: Understand overall customer satisfaction
2. **Risk Identification**: Quickly identify high-risk tickets
3. **Channel Performance**: Compare sentiment across different channels
4. **Temporal Patterns**: Identify peak hours and days
5. **Resolution Efficiency**: Monitor resolution times by sentiment
6. **Category Analysis**: Identify problematic categories
7. **Business Line Performance**: Compare different LOBs

## 🔧 Customization

### Adding New Visualizations
Add your charts in the main() function after line 300:
```python
st.markdown("## Your Custom Section")
# Add your visualization code here
```

### Modifying Colors
Update color schemes in the Plotly chart configurations:
```python
color_discrete_map={
    'Positive': '#10b981',  # Green
    'Neutral': '#6b7280',   # Gray
    'Negative': '#ef4444'   # Red
}
```

### Adjusting Filters
Add or modify filters in the sidebar section (lines 150-200)

## 💡 Usage Tips

1. **Use Filters Strategically**: Start broad, then narrow down to specific issues
2. **Compare Time Periods**: Select different date ranges to identify trends
3. **Focus on High Risk**: Use the High Risk Tickets tab for urgent issues
4. **Monitor Resolution Times**: Check if negative sentiment correlates with longer resolution times
5. **Channel Analysis**: Identify which channels need improvement

## 🐛 Troubleshooting

### Dashboard Won't Load
- Ensure all packages are installed (`pip install -r requirements.txt`)
- Check that `training_data_cs.xlsx` is in the root directory.
- Verify Python version (3.7+)

### Charts Not Displaying
- Clear browser cache
- Refresh the page
- Check console for errors

### Slow Performance
- Reduce date range in filters
- Close other browser tabs
- Check system resources

## 📈 Performance Metrics

The dashboard efficiently handles:
- 50,000+ ticket records
- Real-time filtering and aggregation
- Multiple simultaneous visualizations
- Responsive user interactions

## 🔄 Updates & Maintenance

To update the data:
1. Replace `training_data_cs.xlsx` with new data
2. Refresh the dashboard (Ctrl+R / Cmd+R)
3. Cache will automatically update

## 📞 Support

For issues or feature requests:
- Review the code comments
- Check Streamlit documentation: https://docs.streamlit.io
- Review Plotly documentation: https://plotly.com/python/

## 📝 License

This dashboard is provided as-is for internal use.

---

**Version**: 1.0  
**Last Updated**: November 2025  
**Created with**: Streamlit, Plotly, Pandas
