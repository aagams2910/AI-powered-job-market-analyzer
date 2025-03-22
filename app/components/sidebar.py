import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def render_sidebar():
    """
    Renders the sidebar with filter options and returns the selected filters.
    """
    with st.sidebar:
        st.title("Filters")
        
        # Time range filter
        st.subheader("Time Range")
        date_options = ["Last 30 days", "Last 3 months", "Last 6 months", "Last year", "Custom"]
        selected_date_option = st.selectbox("Select time range", date_options)
        
        if selected_date_option == "Custom":
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=90)
            date_range = st.date_input(
                "Select date range",
                value=(start_date, end_date),
                min_value=end_date - timedelta(days=730),
                max_value=end_date
            )
            if len(date_range) == 2:
                start_date, end_date = date_range
            else:
                start_date, end_date = end_date - timedelta(days=90), end_date
        else:
            end_date = datetime.now().date()
            if selected_date_option == "Last 30 days":
                start_date = end_date - timedelta(days=30)
            elif selected_date_option == "Last 3 months":
                start_date = end_date - timedelta(days=90)
            elif selected_date_option == "Last 6 months":
                start_date = end_date - timedelta(days=180)
            else:  # Last year
                start_date = end_date - timedelta(days=365)
        
        # Industry filter
        st.subheader("Industry")
        industries = [
            "All Industries", 
            "Technology", 
            "Healthcare", 
            "Finance", 
            "Education",
            "Manufacturing",
            "Retail",
            "Media & Entertainment",
            "Government",
            "Non-profit"
        ]
        selected_industry = st.selectbox("Select industry", industries)
        
        # Job role filter
        st.subheader("Job Role")
        roles = [
            "All Roles", 
            "Software Engineer", 
            "Data Scientist", 
            "Product Manager", 
            "UX Designer",
            "Marketing Specialist",
            "Sales Representative",
            "Financial Analyst",
            "Human Resources",
            "Project Manager"
        ]
        selected_role = st.selectbox("Select job role", roles)
        
        # Location filter
        st.subheader("Location")
        locations = [
            "All Locations", 
            "United States", 
            "Europe", 
            "Asia", 
            "Remote"
        ]
        selected_location = st.selectbox("Select location", locations)
        
        if selected_location != "All Locations":
            if selected_location == "United States":
                sub_locations = [
                    "All US", 
                    "San Francisco Bay Area", 
                    "New York", 
                    "Seattle", 
                    "Austin",
                    "Boston",
                    "Chicago",
                    "Los Angeles"
                ]
            elif selected_location == "Europe":
                sub_locations = [
                    "All Europe", 
                    "London", 
                    "Berlin", 
                    "Paris", 
                    "Amsterdam",
                    "Dublin",
                    "Stockholm",
                    "Barcelona"
                ]
            elif selected_location == "Asia":
                sub_locations = [
                    "All Asia", 
                    "Singapore", 
                    "Tokyo", 
                    "Bangalore", 
                    "Hong Kong",
                    "Seoul",
                    "Shanghai",
                    "Beijing"
                ]
            else:  # Remote
                sub_locations = ["All Remote"]
                
            selected_sub_location = st.selectbox("Select specific location", sub_locations)
        else:
            selected_sub_location = "All"
            
        # Experience level filter
        st.subheader("Experience Level")
        experience_levels = [
            "All Levels", 
            "Entry Level", 
            "Mid Level", 
            "Senior", 
            "Executive"
        ]
        selected_experience = st.selectbox("Select experience level", experience_levels)
        
        # Skills input for personalized analysis
        st.subheader("Your Skills")
        st.markdown("Enter your skills for personalized analysis")
        user_skills = st.text_area("Enter skills (comma-separated)")
        user_skills = [skill.strip() for skill in user_skills.split(",")] if user_skills else []
        
        # Forecast horizon
        st.subheader("Forecast Horizon")
        forecast_horizon = st.slider("Months to forecast", min_value=1, max_value=24, value=6)
        
    # Return filters as dictionary
    return {
        "start_date": start_date,
        "end_date": end_date,
        "industry": selected_industry,
        "role": selected_role,
        "location": selected_location,
        "sub_location": selected_sub_location,
        "experience": selected_experience,
        "user_skills": user_skills,
        "forecast_horizon": forecast_horizon
    } 