import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

def render_job_trends(job_data):
    """
    Renders job trends visualization based on the provided job data.
    
    Args:
        job_data (pd.DataFrame): Dataframe containing job posting data
    """
    st.header("Job Market Trends")
    
    if job_data is None or job_data.empty:
        st.warning("No job data available for the selected filters. Please adjust your filters or try again later.")
        return
    
    # Create two columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Job Posting Volume Over Time")
        # Line chart for job posting volume over time
        fig = px.line(
            job_data.groupby('date')['postings'].sum().reset_index(),
            x='date',
            y='postings',
            title='Job Posting Volume Trend',
            labels={'postings': 'Number of Job Postings', 'date': 'Date'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Top 10 Job Roles in Demand")
        # Bar chart for top job roles
        top_roles = job_data.groupby('role')['postings'].sum().sort_values(ascending=False).head(10)
        fig = px.bar(
            x=top_roles.values,
            y=top_roles.index,
            orientation='h',
            labels={'x': 'Number of Job Postings', 'y': 'Job Role'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Growth rates
    st.subheader("Fastest Growing Job Roles")
    
    # Calculate growth rates
    earliest_date = job_data['date'].min()
    latest_date = job_data['date'].max()
    midpoint_date = earliest_date + (latest_date - earliest_date) / 2
    
    early_data = job_data[job_data['date'] <= midpoint_date].groupby('role')['postings'].sum()
    late_data = job_data[job_data['date'] > midpoint_date].groupby('role')['postings'].sum()
    
    # Calculate growth percentage
    roles_with_sufficient_data = early_data[early_data >= 10].index
    early_counts = early_data.loc[roles_with_sufficient_data]
    late_counts = late_data.loc[roles_with_sufficient_data]
    
    growth_rates = ((late_counts - early_counts) / early_counts * 100).sort_values(ascending=False)
    
    # Display top growing roles
    top_growing_roles = growth_rates.head(5)
    fig = px.bar(
        x=top_growing_roles.values,
        y=top_growing_roles.index,
        orientation='h',
        labels={'x': 'Growth Rate (%)', 'y': 'Job Role'},
        color=top_growing_roles.values,
        color_continuous_scale='RdYlGn'
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Industry breakdown
    st.subheader("Job Distribution by Industry")
    
    # Pie chart for industry distribution
    industry_distribution = job_data.groupby('industry')['postings'].sum()
    fig = px.pie(
        values=industry_distribution.values,
        names=industry_distribution.index,
        hole=0.4
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Experience level breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Jobs by Experience Level")
        exp_distribution = job_data.groupby('experience_level')['postings'].sum()
        fig = px.bar(
            x=exp_distribution.index,
            y=exp_distribution.values,
            labels={'x': 'Experience Level', 'y': 'Number of Job Postings'},
            color=exp_distribution.values,
            color_continuous_scale='Viridis'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Remote vs. On-site Jobs")
        location_type = job_data.groupby('location_type')['postings'].sum()
        fig = px.pie(
            values=location_type.values,
            names=location_type.index,
            color_discrete_sequence=px.colors.sequential.Plasma
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Job growth forecast
    st.subheader("Job Growth Forecast (Next 6 Months)")
    
    # Use historical data to create a simple forecast
    dates = pd.date_range(start=latest_date, periods=180, freq='D')
    last_value = job_data.groupby('date')['postings'].sum().iloc[-1]
    forecast_values = [last_value * (1 + 0.001 * i) for i in range(180)]
    
    # Create confidence interval
    lower_bound = [value * 0.9 for value in forecast_values]
    upper_bound = [value * 1.1 for value in forecast_values]
    
    # Plot forecast
    fig = go.Figure()
    
    # Add historical data
    historical_data = job_data.groupby('date')['postings'].sum().reset_index()
    fig.add_trace(
        go.Scatter(
            x=historical_data['date'],
            y=historical_data['postings'],
            name='Historical',
            line=dict(color='blue')
        )
    )
    
    # Add forecast
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=forecast_values,
            name='Forecast',
            line=dict(color='red', dash='dash')
        )
    )
    
    # Add confidence interval
    fig.add_trace(
        go.Scatter(
            x=list(dates) + list(dates)[::-1],
            y=upper_bound + lower_bound[::-1],
            fill='toself',
            fillcolor='rgba(255,0,0,0.2)',
            line=dict(color='rgba(255,0,0,0)'),
            name='Confidence Interval'
        )
    )
    
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Number of Job Postings',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True) 