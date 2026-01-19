#!/bin/bash

# Customer Sentiment Dashboard - Quick Start Script
# This script will install dependencies and run the dashboard

echo "🚀 Customer Sentiment Analytics Dashboard - Quick Start"
echo "======================================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

echo "✅ Python 3 found"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3."
    exit 1
fi

echo "✅ pip3 found"

# Install requirements
echo ""
echo "📦 Installing required packages..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ All packages installed successfully"
else
    echo "❌ Failed to install packages. Please check your internet connection."
    exit 1
fi

# Check if data file exists
if [ ! -f "training_data_cs.xlsx" ]; then
    echo "❌ Data file 'training_data_cs.xlsx' not found!"
    echo "Please place the data file in the same directory as this script."
    exit 1
fi

echo "✅ Data file found"

# Run the dashboard
echo ""
echo "🎉 Starting the dashboard..."
echo "📝 Default password: sentiment2024"
echo "🌐 Dashboard will open in your browser automatically"
echo ""
echo "Press Ctrl+C to stop the dashboard"
echo "======================================================="
echo ""

streamlit run customer_sentiment_dashboard.py
