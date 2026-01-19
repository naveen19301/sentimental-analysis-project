# 📊 Customer Sentiment Analysis Platform  
**Zoho Desk + Excel | Rule-Based NLP | Streamlit Dashboard**

An end-to-end Python solution for extracting Zoho Desk ticket conversations, performing rule-based sentiment analysis, and visualizing customer insights through an interactive Streamlit dashboard.

---

## 🚀 What This Repo Does

- Fetches inbound & outbound ticket threads from **Zoho Desk API**
- Processes local **Excel (.xlsx)** ticket files
- Applies **rule-based sentiment, emotion & risk analysis**
- Generates a **business-ready analytics dashboard**

---

## 🧩 Components

### 1️⃣ Sentiment Analysis Engine
- Zoho Desk OAuth authentication
- Rule-based sentiment & emotion detection
- Complaint risk scoring
- Excel-based input/output

**Main Files**
- `main.py` – Entry point  
- `zoho_client.py` – Zoho API handler  
- `sentiment_engine.py` – NLP rules  
- `utils.py` – Text cleaning helpers  

---

### 2️⃣ Customer Sentiment Dashboard
- Built with **Streamlit + Plotly**
- Username login (`admin`)
- Password-protected login (`admin123`)
- KPI cards, trends, risk analysis & filters
- Handles large datasets (50k+ tickets)

**Dashboard File**
- `customer_sentiment_dashboard.py`

---
