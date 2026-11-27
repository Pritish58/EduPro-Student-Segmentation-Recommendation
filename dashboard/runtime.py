import streamlit as st
from dashboard.data_loader import build_data, save_processed_data

@st.cache_resource(show_spinner="Loading EduPro learner data...")
def load_project_data():
    data = build_data()
    # Keep processed files and model metadata refreshed whenever the source workbook is used.
    if data.get("data_source") != "processed_csv":
        save_processed_data(data)
    return data
