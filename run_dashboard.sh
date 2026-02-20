#!/bin/bash
# Judge.me Ads Analysis Dashboard
# Run this script to start the Streamlit dashboard

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting Judge.me Ads Analysis Dashboard..."
streamlit run app.py --server.port 8501
