import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

def render_skills_forecast(skill_data):
    """
    Renders skills forecast visualization based on the provided skill data.
    
    Args:
        skill_data (pd.DataFrame): Dataframe containing skills data
    """
    st.header("Skills Demand Forecast")
    
    if skill_data is None or skill_data.empty:
        st.warning("No skill data available for the selected filters. Please adjust your filters or try again later.")
        return
    
    # Top skills currently in demand
    st.subheader("Top Skills in Demand")
    
    # Bar chart for top skills
    top_skills = skill_data.groupby('skill')['count'].sum().sort_values(ascending=False).head(15)
    fig = px.bar(
        x=top_skills.values,
        y=top_skills.index,
        orientation='h',
        color=top_skills.values,
        color_continuous_scale='Viridis',
        labels={'x': 'Demand (Job Postings Count)', 'y': 'Skill'}
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Skills growth trend
    st.subheader("Skills Growth Trend")
    
    # Select top 5 skills for trend analysis
    top_5_skills = top_skills.head(5).index.tolist()
    
    # Filter data for top 5 skills and aggregate by date
    skill_trend_data = skill_data[skill_data['skill'].isin(top_5_skills)]
    skill_trends = pd.pivot_table(
        skill_trend_data, 
        values='count', 
        index='date', 
        columns='skill', 
        aggfunc='sum'
    ).fillna(0)
    
    # Create line chart for skill trends
    fig = go.Figure()
    for skill in skill_trends.columns:
        fig.add_trace(
            go.Scatter(
                x=skill_trends.index,
                y=skill_trends[skill],
                mode='lines',
                name=skill
            )
        )
    
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Demand (Job Postings Count)',
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Skills forecast
    st.subheader("Skills Demand Forecast (Next 6 Months)")
    
    # Create forecast for top 5 skills
    latest_date = skill_data['date'].max()
    forecast_dates = pd.date_range(start=latest_date, periods=180, freq='D')
    
    # Initialize figure
    fig = go.Figure()
    
    # For each skill, create a forecast
    for skill in top_5_skills:
        # Get historical data for the skill
        skill_history = skill_data[skill_data['skill'] == skill].groupby('date')['count'].sum()
        
        if not skill_history.empty:
            # Last value
            last_value = skill_history.iloc[-1]
            
            # Simple trend-based forecast
            growth_factor = 1.001  # 0.1% daily growth
            if skill == top_5_skills[0]:  # Assume top skill grows faster
                growth_factor = 1.002
            elif skill == top_5_skills[-1]:  # Assume last skill grows slower
                growth_factor = 1.0005
                
            # Generate forecast values
            forecast_values = [last_value * (growth_factor ** i) for i in range(180)]
            
            # Add to plot
            # Historical data
            fig.add_trace(
                go.Scatter(
                    x=skill_history.index,
                    y=skill_history.values,
                    mode='lines',
                    name=f"{skill} (Historical)",
                    line=dict(width=1)
                )
            )
            
            # Forecast
            fig.add_trace(
                go.Scatter(
                    x=forecast_dates,
                    y=forecast_values,
                    mode='lines',
                    name=f"{skill} (Forecast)",
                    line=dict(dash='dash', width=1)
                )
            )
    
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Demand (Job Postings Count)',
        height=600,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Skills clusters
    st.subheader("Skills Clusters")
    
    # Create a sample skills network visualization
    # In a real app, this would be based on skills co-occurrence in job postings
    st.markdown("""
        Skills often appear together in job postings, forming natural clusters. 
        The visualization below shows skills that frequently appear together.
    """)
    
    # Create a sample network visualization (in a real app, this would be generated from data)
    st.image("https://miro.medium.com/max/1400/1*3FIRsKOvLLt88eOXLJHQIQ.png", 
             caption="Sample visualization of skills clusters", 
             use_column_width=True)
    
    # Emerging skills
    st.subheader("Emerging Skills to Watch")
    
    # For this example, we'll create a sample dataframe of emerging skills
    emerging_skills = pd.DataFrame({
        'skill': ['Rust', 'WebAssembly', 'GraphQL', 'JAMstack', 'MLOps', 'Edge Computing', 'Zero Trust Security'],
        'growth_rate': [120, 95, 78, 65, 62, 58, 52]
    })
    
    fig = px.bar(
        emerging_skills,
        x='growth_rate',
        y='skill',
        orientation='h',
        color='growth_rate',
        color_continuous_scale='Viridis',
        labels={'growth_rate': 'Growth Rate (%)', 'skill': 'Emerging Skill'}
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True) 