import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

def render_salary_insights(job_data):
    """
    Renders salary insights visualizations based on the provided job data.
    
    Args:
        job_data (pd.DataFrame): Dataframe containing job posting data with salary information
    """
    st.header("Salary Insights")
    
    if job_data is None or job_data.empty:
        st.warning("No salary data available for the selected filters. Please adjust your filters or try again later.")
        return
    
    # Overview of salary distribution
    st.subheader("Salary Distribution")
    
    # Create a histogram of salary distribution
    fig = px.histogram(
        job_data,
        x='salary_avg',
        nbins=50,
        labels={'salary_avg': 'Average Salary ($)', 'count': 'Number of Job Postings'},
        color_discrete_sequence=['#3366CC']
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Salary by roles
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Paying Roles")
        
        # Calculate average salary by role
        role_salary = job_data.groupby('role')['salary_avg'].mean().sort_values(ascending=False).head(10)
        
        fig = px.bar(
            x=role_salary.values,
            y=role_salary.index,
            orientation='h',
            color=role_salary.values,
            color_continuous_scale='Viridis',
            labels={'x': 'Average Salary ($)', 'y': 'Job Role'}
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Salary Range by Experience Level")
        
        # Calculate salary statistics by experience level
        exp_salary = job_data.groupby('experience_level').agg({
            'salary_min': 'mean',
            'salary_max': 'mean',
            'salary_avg': 'mean'
        }).reset_index()
        
        # Sort by experience level order
        exp_order = {
            'Entry Level': 0, 
            'Mid Level': 1, 
            'Senior': 2, 
            'Executive': 3
        }
        exp_salary['order'] = exp_salary['experience_level'].map(exp_order)
        exp_salary = exp_salary.sort_values('order').drop('order', axis=1)
        
        # Create a range plot
        fig = go.Figure()
        
        for i, row in exp_salary.iterrows():
            fig.add_trace(
                go.Bar(
                    name=row['experience_level'],
                    y=[row['experience_level']],
                    x=[row['salary_max'] - row['salary_min']],
                    base=[row['salary_min']],
                    orientation='h',
                    marker=dict(
                        color=px.colors.sequential.Viridis[i],
                        line=dict(width=1, color='#333333')
                    )
                )
            )
            
            # Add average markers
            fig.add_trace(
                go.Scatter(
                    name=f"{row['experience_level']} (Average)",
                    y=[row['experience_level']],
                    x=[row['salary_avg']],
                    mode='markers',
                    marker=dict(
                        symbol='diamond',
                        size=12,
                        color='#FF5733',
                        line=dict(width=1, color='#333333')
                    ),
                    showlegend=False
                )
            )
        
        fig.update_layout(
            xaxis_title='Salary Range ($)',
            barmode='group',
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Salary by industry
    st.subheader("Average Salary by Industry")
    
    # Calculate average salary by industry
    industry_salary = job_data.groupby('industry')['salary_avg'].mean().sort_values(ascending=False)
    
    fig = px.bar(
        x=industry_salary.index,
        y=industry_salary.values,
        color=industry_salary.values,
        color_continuous_scale='Viridis',
        labels={'x': 'Industry', 'y': 'Average Salary ($)'}
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Salary by location
    st.subheader("Salary Comparison by Location")
    
    # Calculate average salary by location
    location_salary = job_data.groupby('location')['salary_avg'].mean().sort_values(ascending=False).head(15)
    
    fig = px.bar(
        x=location_salary.index,
        y=location_salary.values,
        color=location_salary.values,
        color_continuous_scale='Viridis',
        labels={'x': 'Location', 'y': 'Average Salary ($)'}
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Salary premium for skills
    st.subheader("Salary Premium for Skills")
    
    # For this example, we'll create a sample dataframe of skills and their salary premiums
    skills_premium = pd.DataFrame({
        'skill': ['Machine Learning', 'Cloud Architecture', 'DevOps', 'Mobile Development', 
                 'Cybersecurity', 'UI/UX Design', 'Data Engineering', 'Product Management'],
        'salary_premium': [15000, 18000, 12000, 10000, 17000, 9000, 14000, 11000]
    })
    
    fig = px.bar(
        skills_premium,
        x='salary_premium',
        y='skill',
        orientation='h',
        color='salary_premium',
        color_continuous_scale='Viridis',
        labels={'salary_premium': 'Salary Premium ($)', 'skill': 'Skill'}
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Salary forecast
    st.subheader("Salary Forecast by Role")
    
    # Create a sample forecast chart
    roles = ['Data Scientist', 'Software Engineer', 'Product Manager', 'DevOps Engineer', 'UX Designer']
    years = [2023, 2024, 2025, 2026, 2027]
    
    # Sample data for salary growth projections
    data = {
        'Data Scientist': [120000, 125000, 131000, 138000, 146000],
        'Software Engineer': [110000, 115000, 121000, 128000, 135000],
        'Product Manager': [115000, 120000, 126000, 133000, 141000],
        'DevOps Engineer': [105000, 110000, 116000, 123000, 130000],
        'UX Designer': [95000, 99000, 104000, 110000, 117000]
    }
    
    # Create a line chart for salary forecast
    fig = go.Figure()
    
    for role in roles:
        fig.add_trace(
            go.Scatter(
                x=years,
                y=data[role],
                mode='lines+markers',
                name=role
            )
        )
    
    fig.update_layout(
        xaxis_title='Year',
        yaxis_title='Projected Average Salary ($)',
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True) 