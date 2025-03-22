import streamlit as st

def render_header():
    """
    Renders the application header with title and description.
    """
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.image("https://img.icons8.com/ios-filled/100/4a90e2/artificial-intelligence.png", width=80)
    
    with col2:
        st.title("AI-Powered Job Market Analyzer")
        st.markdown(
            """
            *Forecast job market trends and identify in-demand skills with AI-powered analysis.*
            """
        )
    
    st.markdown("---")
    
    # Overview metrics in a row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Job Postings Analyzed", 
            value="248,573", 
            delta="12,456"
        )
    
    with col2:
        st.metric(
            label="Fastest Growing Role", 
            value="Data Scientist", 
            delta="32%"
        )
    
    with col3:
        st.metric(
            label="Most In-Demand Skill", 
            value="Machine Learning", 
            delta="28%"
        )
    
    with col4:
        st.metric(
            label="Highest Paying Field", 
            value="Cloud Architecture", 
            delta="$145K avg."
        )
    
    st.markdown("---")
    
    # Introduction
    st.markdown(
        """
        ## How to use this dashboard
        
        1. Use the sidebar to filter job data by industry, role, location, and experience level
        2. Enter your skills for personalized career recommendations
        3. Explore different tabs to analyze job trends, skills forecasts, salary insights, and location-based opportunities
        4. Adjust the forecast horizon to see short and long-term predictions
        """
    ) 