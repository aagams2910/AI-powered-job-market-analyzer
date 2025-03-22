import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import components
from app.components.sidebar import render_sidebar
from app.components.header import render_header
from app.components.skills_forecast import render_skills_forecast
from app.components.job_trends import render_job_trends
from app.components.salary_insights import render_salary_insights
from app.components.location_analysis import render_location_analysis
from app.components.skill_gap import render_skill_gap_analysis

# Import utils
from app.utils.load_data import load_job_data, load_skill_data, load_location_data

# Set page config
st.set_page_config(
    page_title="AI-Powered Job Market Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Render header
    render_header()
    
    # Render sidebar and get selected options
    filters = render_sidebar()
    
    # Load data based on filters
    with st.spinner("Loading data..."):
        job_data = load_job_data(filters)
        skill_data = load_skill_data(filters)
        location_data = load_location_data(filters)
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Job Trends", 
        "Skills Forecast", 
        "Salary Insights", 
        "Location Analysis",
        "Skill Gap Analysis"
    ])
    
    # Populate tabs with content
    with tab1:
        render_job_trends(job_data)
    
    with tab2:
        render_skills_forecast(skill_data)
    
    with tab3:
        render_salary_insights(job_data)
    
    with tab4:
        render_location_analysis(location_data)
    
    with tab5:
        render_skill_gap_analysis(skill_data, filters.get("user_skills", []))
    
    # Add footer
    st.markdown("---")
    st.markdown(
        "© 2025 AI-Powered Job Market Analyzer | Data sources: LinkedIn, Indeed, Glassdoor, BLS"
    )

if __name__ == "__main__":
    main() 