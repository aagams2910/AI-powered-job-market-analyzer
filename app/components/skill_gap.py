import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from collections import Counter

def render_skill_gap_analysis(skill_data, user_skills):
    """
    Renders skill gap analysis visualizations based on user's skills and market demand.
    
    Args:
        skill_data (pd.DataFrame): Dataframe containing skills data
        user_skills (list): List of user's skills
    """
    st.header("Personal Skill Gap Analysis")
    
    if skill_data is None or skill_data.empty:
        st.warning("No skill data available for the selected filters. Please adjust your filters or try again later.")
        return
    
    if not user_skills:
        st.info("Please enter your skills in the sidebar to receive personalized recommendations.")
        return
    
    # Display user's skills
    st.subheader("Your Skills")
    
    # Create a nice display of user's skills
    cols = st.columns(3)
    for i, skill in enumerate(user_skills):
        col_idx = i % 3
        with cols[col_idx]:
            st.markdown(f"**{skill}**")
    
    st.markdown("---")
    
    # Top in-demand skills matching user skills
    st.subheader("Your Skills in Demand")
    
    # Normalize user skills and market skills for comparison
    normalized_user_skills = [skill.lower().strip() for skill in user_skills if skill]
    
    # Calculate market demand for skills
    market_skills = skill_data.groupby('skill')['count'].sum().sort_values(ascending=False)
    
    # Find matching skills
    matching_skills = [skill for skill in market_skills.index if skill.lower() in normalized_user_skills]
    
    if matching_skills:
        matching_demand = market_skills.loc[matching_skills]
        
        # Create a bar chart for matching skills by demand
        fig = px.bar(
            x=matching_demand.values,
            y=matching_demand.index,
            orientation='h',
            color=matching_demand.values,
            color_continuous_scale='Greens',
            labels={'x': 'Market Demand', 'y': 'Your Skills'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("None of your skills exactly match our skill database. Try using more standardized skill names.")
    
    # Skill gap visualization
    st.subheader("Top Skills You Could Add")
    
    # Get top market skills that user doesn't have
    top_market_skills = market_skills.head(20).index.tolist()
    missing_skills = [skill for skill in top_market_skills if skill.lower() not in normalized_user_skills]
    
    if missing_skills:
        missing_demand = market_skills.loc[missing_skills[:10]]  # Show top 10 missing skills
        
        # Create a bar chart for missing skills by demand
        fig = px.bar(
            x=missing_demand.values,
            y=missing_demand.index,
            orientation='h',
            color=missing_demand.values,
            color_continuous_scale='Reds',
            labels={'x': 'Market Demand', 'y': 'Skills to Acquire'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Recommendations
        st.subheader("Personalized Recommendations")
        
        # For this example, we'll create sample recommendations
        st.markdown("Based on your current skills and market trends, here are personalized recommendations:")
        
        # Top 3 skills to learn
        st.markdown("### Top 3 Skills to Learn")
        top_3_missing = missing_skills[:3]
        
        for i, skill in enumerate(top_3_missing):
            st.markdown(f"**{i+1}. {skill}**")
            
            # Sample explanations for different skills
            if skill.lower() == "python":
                st.markdown("""
                    - High demand across data science, web development, and automation
                    - Complements your existing programming skills
                    - 28% salary premium on average
                """)
            elif "cloud" in skill.lower() or "aws" in skill.lower() or "azure" in skill.lower():
                st.markdown("""
                    - Critical for modern software deployment
                    - Highly sought after by 78% of enterprise companies
                    - Can increase your market value by up to 25%
                """)
            elif "machine learning" in skill.lower() or "ai" in skill.lower():
                st.markdown("""
                    - Fastest growing skill in tech sector
                    - Builds on existing technical skills
                    - Opens opportunities in cutting-edge fields
                """)
            else:
                st.markdown("""
                    - Strong market demand with projected growth
                    - Complements your existing skill set
                    - Significant salary premium in current market
                """)
        
        # Career path recommendations
        st.markdown("### Potential Career Paths")
        
        # For this example, we'll create sample career paths based on user skills
        has_programming = any(skill.lower() in ["python", "java", "javascript", "c++", "c#"] for skill in normalized_user_skills)
        has_data = any(skill.lower() in ["sql", "pandas", "data analysis", "statistics"] for skill in normalized_user_skills)
        has_design = any(skill.lower() in ["ui", "ux", "user experience", "design", "figma"] for skill in normalized_user_skills)
        
        if has_programming and has_data:
            st.markdown("""
                **1. Data Scientist / ML Engineer**
                - Strong alignment with your current skills
                - High market demand (32% YoY growth)
                - Median salary: $125,000
                
                **Next steps:** Focus on machine learning frameworks and big data technologies
            """)
        
        if has_programming:
            st.markdown("""
                **2. Backend Developer / Software Engineer**
                - Good match for your programming background
                - Steady demand across industries
                - Median salary: $110,000
                
                **Next steps:** Add cloud technologies and DevOps skills to your portfolio
            """)
        
        if has_design:
            st.markdown("""
                **3. UX/UI Designer**
                - Leverages your design skills
                - Growing demand as companies focus on user experience
                - Median salary: $95,000
                
                **Next steps:** Build a portfolio showcasing your design work and learn user research methodologies
            """)
        
        if not any([has_programming, has_data, has_design]):
            st.markdown("""
                **1. Digital Marketing Specialist**
                - Entry point to tech industry with diverse skills
                - Good demand across all business types
                - Median salary: $65,000
                
                **2. Project Manager**
                - Utilizes a variety of soft and technical skills
                - Stable demand across industries
                - Median salary: $85,000
            """)
        
        # Learning resources
        st.markdown("### Learning Resources")
        
        st.markdown("""
            **Top Courses for Recommended Skills:**
            
            1. **Online Courses**
               - Coursera: [Data Science Specialization](https://www.coursera.org/)
               - Udacity: [Full Stack Developer Nanodegree](https://www.udacity.com/)
               - edX: [Cloud Computing MicroMasters](https://www.edx.org/)
            
            2. **Certifications**
               - AWS Certified Solutions Architect
               - Google Professional Data Engineer
               - Microsoft Azure Developer Associate
            
            3. **Free Resources**
               - freeCodeCamp.org - Web Development & Data Science
               - Khan Academy - Computer Science Fundamentals
               - YouTube Channels: Tech With Tim, Corey Schafer, Traversy Media
        """)
    else:
        st.success("Great job! You already have all the top in-demand skills in your profile.")
    
    # Market fit score
    st.subheader("Your Market Fit Score")
    
    # Calculate a simple market fit score
    if matching_skills:
        matching_demand_sum = matching_demand.sum()
        top_demand_sum = market_skills.head(len(user_skills) * 2).sum()  # Compare to top skills twice the number of user skills
        
        # Calculate score as percentage of potential top demand
        market_fit_score = min(int(matching_demand_sum / top_demand_sum * 100), 100)
        
        # Display gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=market_fit_score,
            title={'text': "Market Fit"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkgreen"},
                'steps': [
                    {'range': [0, 30], 'color': "lightgray"},
                    {'range': [30, 70], 'color': "gray"},
                    {'range': [70, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # Interpretation
        if market_fit_score >= 80:
            st.success("Excellent! Your skills are highly aligned with current market demands.")
        elif market_fit_score >= 60:
            st.info("Good job! Your skills match well with the market, but there's room for improvement.")
        elif market_fit_score >= 40:
            st.warning("Your skills have moderate alignment with market demands. Consider adding some in-demand skills.")
        else:
            st.error("Your current skills have limited alignment with top market demands. Focus on acquiring the recommended skills.")
    else:
        st.warning("Unable to calculate market fit score due to no matching skills in our database.")
        
    # Salary potential chart
    st.subheader("Your Salary Potential")
    
    # For this example, we'll create a sample salary potential chart
    current_avg_salary = 85000  # Placeholder
    potential_salary = 110000  # Placeholder
    
    # Create a horizontal bar chart for salary potential
    salary_data = pd.DataFrame({
        'category': ['Current Average', 'Your Potential'],
        'salary': [current_avg_salary, potential_salary]
    })
    
    fig = px.bar(
        salary_data,
        x='salary',
        y='category',
        orientation='h',
        text=salary_data['salary'].apply(lambda x: f"${x:,}"),
        color=['blue', 'green'],
        labels={'salary': 'Annual Salary ($)', 'category': ''}
    )
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
        **Salary Potential Analysis:**
        
        By adding the recommended skills, you could increase your earning potential by approximately 30%. 
        This estimate is based on current market rates for professionals with your baseline skills plus the 
        recommended additions.
    """)
