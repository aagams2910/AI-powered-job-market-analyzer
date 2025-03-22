import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

def render_location_analysis(location_data):
    """
    Renders location-based analysis visualizations.
    
    Args:
        location_data (pd.DataFrame): Dataframe containing location-based job posting data
    """
    st.header("Geographic Job Market Analysis")
    
    if location_data is None or location_data.empty:
        st.warning("No location data available for the selected filters. Please adjust your filters or try again later.")
        return
    
    # Job distribution by country/region
    st.subheader("Job Distribution by Region")
    
    # Create a choropleth map for global job distribution
    fig = px.choropleth(
        location_data.groupby('country').agg({'postings': 'sum'}).reset_index(),
        locations='country',
        locationmode='country names',
        color='postings',
        color_continuous_scale='Viridis',
        labels={'postings': 'Job Postings'}
    )
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='natural earth'
        ),
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # US job market heatmap
    if 'United States' in location_data['country'].unique():
        st.subheader("US Job Market Distribution")
        
        # Filter for US data
        us_data = location_data[location_data['country'] == 'United States']
        
        # Create a choropleth map for US states
        fig = px.choropleth(
            us_data.groupby('state').agg({'postings': 'sum'}).reset_index(),
            locations='state',
            locationmode='USA-states',
            color='postings',
            color_continuous_scale='Viridis',
            scope='usa',
            labels={'postings': 'Job Postings', 'state': 'State'}
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    # Job hotspots - top cities
    st.subheader("Top 15 Cities for Job Opportunities")
    
    # Create a bar chart for top cities
    top_cities = location_data.groupby('city')['postings'].sum().sort_values(ascending=False).head(15)
    
    fig = px.bar(
        x=top_cities.index,
        y=top_cities.values,
        color=top_cities.values,
        color_continuous_scale='Viridis',
        labels={'x': 'City', 'y': 'Number of Job Postings'}
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Remote work trends
    st.subheader("Remote Work Trends by Industry")
    
    # Create a grouped bar chart for remote vs. on-site jobs by industry
    remote_by_industry = pd.pivot_table(
        location_data, 
        values='postings',
        index='industry',
        columns='location_type',
        aggfunc='sum'
    ).fillna(0)
    
    # Sort by total job postings
    remote_by_industry['total'] = remote_by_industry.sum(axis=1)
    remote_by_industry = remote_by_industry.sort_values('total', ascending=False).drop('total', axis=1).head(10)
    
    fig = px.bar(
        remote_by_industry,
        barmode='group',
        labels={'value': 'Number of Job Postings', 'industry': 'Industry', 'location_type': 'Work Type'}
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Salary comparison by location
    st.subheader("Salary Comparison by Top Locations")
    
    # Create a grouped bar chart for salary ranges by location
    top_locations = location_data.groupby('city')['postings'].sum().sort_values(ascending=False).head(10).index
    salary_by_location = location_data[location_data['city'].isin(top_locations)].groupby('city').agg({
        'salary_min': 'mean',
        'salary_max': 'mean',
        'salary_avg': 'mean'
    }).reset_index()
    
    # Sort by average salary
    salary_by_location = salary_by_location.sort_values('salary_avg', ascending=False)
    
    # Create a bar chart with error bars
    fig = go.Figure()
    
    fig.add_trace(
        go.Bar(
            name='Average Salary',
            x=salary_by_location['city'],
            y=salary_by_location['salary_avg'],
            marker_color='rgb(55, 83, 109)'
        )
    )
    
    # Add error bars
    fig.add_trace(
        go.Scatter(
            name='Salary Range',
            x=salary_by_location['city'],
            y=salary_by_location['salary_min'],
            mode='lines',
            marker=dict(color='rgba(200, 0, 0, 0.4)'),
            line=dict(width=0),
            showlegend=False
        )
    )
    
    fig.add_trace(
        go.Scatter(
            name='Salary Range',
            x=salary_by_location['city'],
            y=salary_by_location['salary_max'],
            mode='lines',
            marker=dict(color='rgba(200, 0, 0, 0.4)'),
            line=dict(width=0),
            fill='tonexty',
            showlegend=False
        )
    )
    
    fig.update_layout(
        yaxis_title='Salary ($)',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Growth locations
    st.subheader("Emerging Job Markets")
    
    # For this example, we'll use a sample dataframe for location growth
    emerging_locations = pd.DataFrame({
        'location': ['Austin, TX', 'Raleigh, NC', 'Nashville, TN', 'Salt Lake City, UT', 
                    'Charlotte, NC', 'Columbus, OH', 'Denver, CO', 'Phoenix, AZ'],
        'growth_rate': [35, 32, 28, 26, 24, 22, 20, 18]
    })
    
    fig = px.bar(
        emerging_locations,
        x='growth_rate',
        y='location',
        orientation='h',
        color='growth_rate',
        color_continuous_scale='Viridis',
        labels={'growth_rate': 'YoY Growth Rate (%)', 'location': 'Location'}
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Cost of living adjustment
    st.subheader("Salary Adjusted for Cost of Living")
    
    # For this example, we'll use a sample dataframe
    col_data = pd.DataFrame({
        'city': ['San Francisco, CA', 'New York, NY', 'Seattle, WA', 'Austin, TX', 'Boston, MA',
                'Chicago, IL', 'Denver, CO', 'Atlanta, GA', 'Dallas, TX', 'Raleigh, NC'],
        'nominal_salary': [140000, 135000, 125000, 115000, 125000, 110000, 105000, 100000, 105000, 95000],
        'col_adjusted': [92000, 90000, 98000, 108000, 94000, 98000, 95000, 102000, 106000, 102000]
    })
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Bar(
            name='Nominal Salary',
            x=col_data['city'],
            y=col_data['nominal_salary'],
            marker_color='rgb(55, 83, 109)'
        )
    )
    
    fig.add_trace(
        go.Bar(
            name='Cost of Living Adjusted',
            x=col_data['city'],
            y=col_data['col_adjusted'],
            marker_color='rgb(26, 118, 255)'
        )
    )
    
    fig.update_layout(
        yaxis_title='Salary ($)',
        barmode='group',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True) 