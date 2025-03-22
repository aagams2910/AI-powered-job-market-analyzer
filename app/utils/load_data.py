import pandas as pd
import numpy as np
import os
import json
from datetime import datetime, timedelta
import sqlite3
import pickle
from pathlib import Path

# Constants
DEFAULT_DB_PATH = Path(__file__).parent.parent.parent / 'data' / 'processed' / 'job_market.db'
DEFAULT_MODELS_PATH = Path(__file__).parent.parent.parent / 'data' / 'models'
MOCK_DATA = True  # Set to False when real data collection is implemented

def load_job_data(filters):
    """
    Load job posting data based on the provided filters.
    
    Args:
        filters (dict): Dictionary containing filter parameters
        
    Returns:
        pd.DataFrame: DataFrame containing job posting data
    """
    if MOCK_DATA:
        return _generate_mock_job_data(filters)
    
    # In a real implementation, this would query a database
    try:
        conn = sqlite3.connect(DEFAULT_DB_PATH)
        
        # Build query based on filters
        query = "SELECT * FROM job_postings WHERE 1=1"
        
        if filters.get("start_date") and filters.get("end_date"):
            query += f" AND posting_date BETWEEN '{filters['start_date']}' AND '{filters['end_date']}'"
            
        if filters.get("industry") and filters.get("industry") != "All Industries":
            query += f" AND industry = '{filters['industry']}'"
            
        if filters.get("role") and filters.get("role") != "All Roles":
            query += f" AND role = '{filters['role']}'"
            
        if filters.get("location") and filters.get("location") != "All Locations":
            query += f" AND location = '{filters['location']}'"
            
        if filters.get("experience") and filters.get("experience") != "All Levels":
            query += f" AND experience_level = '{filters['experience']}'"
            
        # Execute query and load into DataFrame
        job_data = pd.read_sql(query, conn)
        conn.close()
        
        return job_data
        
    except Exception as e:
        print(f"Error loading job data: {e}")
        return _generate_mock_job_data(filters)

def load_skill_data(filters):
    """
    Load skill data based on the provided filters.
    
    Args:
        filters (dict): Dictionary containing filter parameters
        
    Returns:
        pd.DataFrame: DataFrame containing skill data
    """
    if MOCK_DATA:
        return _generate_mock_skill_data(filters)
    
    # In a real implementation, this would query a database
    try:
        conn = sqlite3.connect(DEFAULT_DB_PATH)
        
        # Build query based on filters
        query = """
            SELECT s.*, jp.posting_date as date 
            FROM skills s
            JOIN job_posting_skills jps ON s.id = jps.skill_id
            JOIN job_postings jp ON jps.job_posting_id = jp.id
            WHERE 1=1
        """
        
        if filters.get("start_date") and filters.get("end_date"):
            query += f" AND jp.posting_date BETWEEN '{filters['start_date']}' AND '{filters['end_date']}'"
            
        if filters.get("industry") and filters.get("industry") != "All Industries":
            query += f" AND jp.industry = '{filters['industry']}'"
            
        if filters.get("role") and filters.get("role") != "All Roles":
            query += f" AND jp.role = '{filters['role']}'"
            
        if filters.get("location") and filters.get("location") != "All Locations":
            query += f" AND jp.location = '{filters['location']}'"
            
        if filters.get("experience") and filters.get("experience") != "All Levels":
            query += f" AND jp.experience_level = '{filters['experience']}'"
            
        # Execute query and load into DataFrame
        skill_data = pd.read_sql(query, conn)
        conn.close()
        
        return skill_data
        
    except Exception as e:
        print(f"Error loading skill data: {e}")
        return _generate_mock_skill_data(filters)

def load_location_data(filters):
    """
    Load location-based job data based on the provided filters.
    
    Args:
        filters (dict): Dictionary containing filter parameters
        
    Returns:
        pd.DataFrame: DataFrame containing location-based job data
    """
    if MOCK_DATA:
        return _generate_mock_location_data(filters)
    
    # In a real implementation, this would query a database
    try:
        conn = sqlite3.connect(DEFAULT_DB_PATH)
        
        # Build query based on filters
        query = """
            SELECT l.*, jp.* 
            FROM locations l
            JOIN job_postings jp ON l.id = jp.location_id
            WHERE 1=1
        """
        
        if filters.get("start_date") and filters.get("end_date"):
            query += f" AND jp.posting_date BETWEEN '{filters['start_date']}' AND '{filters['end_date']}'"
            
        if filters.get("industry") and filters.get("industry") != "All Industries":
            query += f" AND jp.industry = '{filters['industry']}'"
            
        if filters.get("role") and filters.get("role") != "All Roles":
            query += f" AND jp.role = '{filters['role']}'"
            
        if filters.get("location") and filters.get("location") != "All Locations":
            query += f" AND l.region = '{filters['location']}'"
            
        if filters.get("experience") and filters.get("experience") != "All Levels":
            query += f" AND jp.experience_level = '{filters['experience']}'"
            
        # Execute query and load into DataFrame
        location_data = pd.read_sql(query, conn)
        conn.close()
        
        return location_data
        
    except Exception as e:
        print(f"Error loading location data: {e}")
        return _generate_mock_location_data(filters)

def get_forecast_model(skill_name):
    """
    Load a trained forecasting model for a specific skill.
    
    Args:
        skill_name (str): Name of the skill to forecast
        
    Returns:
        object: Trained forecasting model
    """
    if MOCK_DATA:
        return None
    
    try:
        model_path = DEFAULT_MODELS_PATH / f"{skill_name.lower().replace(' ', '_')}_forecast_model.pkl"
        
        if model_path.exists():
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            return model
        else:
            return None
    except Exception as e:
        print(f"Error loading forecast model: {e}")
        return None

# Helper function to generate mock data for development
def _generate_mock_job_data(filters):
    """Generate mock job data for development purposes."""
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Generate dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Create industries
    industries = [
        "Technology", "Healthcare", "Finance", "Education",
        "Manufacturing", "Retail", "Media & Entertainment",
        "Government", "Non-profit"
    ]
    
    # Create roles
    roles = [
        "Software Engineer", "Data Scientist", "Product Manager", 
        "UX Designer", "Marketing Specialist", "Sales Representative",
        "Financial Analyst", "Human Resources", "Project Manager"
    ]
    
    # Create locations
    locations = [
        "San Francisco Bay Area", "New York", "Seattle", "Austin",
        "Boston", "Chicago", "Los Angeles", "London", "Berlin", 
        "Paris", "Amsterdam", "Dublin", "Stockholm", "Barcelona",
        "Singapore", "Tokyo", "Bangalore", "Hong Kong", "Seoul"
    ]
    
    # Create experience levels
    experience_levels = [
        "Entry Level", "Mid Level", "Senior", "Executive"
    ]
    
    # Generate random data
    n_samples = 1000
    
    data = {
        'date': np.random.choice(date_range, n_samples),
        'title': np.random.choice([f"{role} at Company {i}" for role in roles for i in range(1, 21)], n_samples),
        'company': np.random.choice([f"Company {i}" for i in range(1, 101)], n_samples),
        'industry': np.random.choice(industries, n_samples, p=[0.3, 0.15, 0.15, 0.1, 0.05, 0.05, 0.05, 0.1, 0.05]),
        'role': np.random.choice(roles, n_samples),
        'location': np.random.choice(locations, n_samples),
        'location_type': np.random.choice(['On-site', 'Remote', 'Hybrid'], n_samples, p=[0.4, 0.3, 0.3]),
        'experience_level': np.random.choice(experience_levels, n_samples, p=[0.3, 0.4, 0.25, 0.05]),
        'salary_min': np.random.normal(70000, 20000, n_samples),
        'salary_max': np.random.normal(120000, 30000, n_samples),
        'postings': np.random.randint(1, 50, n_samples)
    }
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Add salary_avg column
    df['salary_avg'] = (df['salary_min'] + df['salary_max']) / 2
    
    # Apply filters if provided
    if filters:
        if filters.get("start_date") and filters.get("end_date"):
            df = df[(df['date'] >= pd.Timestamp(filters['start_date'])) & 
                    (df['date'] <= pd.Timestamp(filters['end_date']))]
        
        if filters.get("industry") and filters.get("industry") != "All Industries":
            df = df[df['industry'] == filters['industry']]
        
        if filters.get("role") and filters.get("role") != "All Roles":
            df = df[df['role'] == filters['role']]
        
        if filters.get("location") and filters.get("location") != "All Locations":
            # Simplified location filtering for mock data
            if filters['location'] == "United States":
                us_locations = ["San Francisco Bay Area", "New York", "Seattle", "Austin", "Boston", "Chicago", "Los Angeles"]
                df = df[df['location'].isin(us_locations)]
            elif filters['location'] == "Europe":
                eu_locations = ["London", "Berlin", "Paris", "Amsterdam", "Dublin", "Stockholm", "Barcelona"]
                df = df[df['location'].isin(eu_locations)]
            elif filters['location'] == "Asia":
                asia_locations = ["Singapore", "Tokyo", "Bangalore", "Hong Kong", "Seoul"]
                df = df[df['location'].isin(asia_locations)]
            elif filters['location'] == "Remote":
                df = df[df['location_type'] == 'Remote']
        
        if filters.get("experience") and filters.get("experience") != "All Levels":
            df = df[df['experience_level'] == filters['experience']]
    
    # Add derived columns for display
    df['country'] = df['location'].apply(lambda x: "United States" if x in ["San Francisco Bay Area", "New York", "Seattle", "Austin", "Boston", "Chicago", "Los Angeles"] else
                                         "United Kingdom" if x == "London" else
                                         "Germany" if x == "Berlin" else
                                         "France" if x == "Paris" else
                                         "Netherlands" if x == "Amsterdam" else
                                         "Ireland" if x == "Dublin" else
                                         "Sweden" if x == "Stockholm" else
                                         "Spain" if x == "Barcelona" else
                                         "Singapore" if x == "Singapore" else
                                         "Japan" if x == "Tokyo" else
                                         "India" if x == "Bangalore" else
                                         "Hong Kong" if x == "Hong Kong" else
                                         "South Korea" if x == "Seoul" else "Other")
    
    df['state'] = df['location'].apply(lambda x: "CA" if x in ["San Francisco Bay Area", "Los Angeles"] else
                                      "NY" if x == "New York" else
                                      "WA" if x == "Seattle" else
                                      "TX" if x == "Austin" else
                                      "MA" if x == "Boston" else
                                      "IL" if x == "Chicago" else "")
    
    df['city'] = df['location'].apply(lambda x: "San Francisco" if x == "San Francisco Bay Area" else
                                     x.split(",")[0] if "," in x else x)
    
    return df

def _generate_mock_skill_data(filters):
    """Generate mock skill data for development purposes."""
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Generate dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Create skills
    skills = [
        "Python", "Java", "JavaScript", "SQL", "AWS", 
        "Machine Learning", "Data Analysis", "React", "Node.js", 
        "Product Management", "UX Design", "Agile", "Scrum",
        "Digital Marketing", "Cloud Computing", "Azure", "DevOps",
        "Docker", "Kubernetes", "Natural Language Processing",
        "Deep Learning", "Tableau", "Power BI", "Excel", "R",
        "C++", "C#", "Git", "Linux", "Salesforce"
    ]
    
    # Generate random data
    n_samples = 5000
    
    data = {
        'skill': np.random.choice(skills, n_samples),
        'count': np.random.randint(1, 100, n_samples),
        'date': np.random.choice(date_range, n_samples)
    }
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Apply filters if provided
    if filters:
        if filters.get("start_date") and filters.get("end_date"):
            df = df[(df['date'] >= pd.Timestamp(filters['start_date'])) & 
                    (df['date'] <= pd.Timestamp(filters['end_date']))]
    
    return df

def _generate_mock_location_data(filters):
    """Generate mock location data for development purposes."""
    # Use the job data as a base and add location-specific columns
    job_data = _generate_mock_job_data(filters)
    
    # Add some more location-specific columns if needed
    job_data['region'] = job_data['location'].apply(lambda x: 
                                              "West Coast" if x in ["San Francisco Bay Area", "Seattle", "Los Angeles"] else
                                              "East Coast" if x in ["New York", "Boston"] else
                                              "Central US" if x in ["Austin", "Chicago"] else
                                              "Europe" if x in ["London", "Berlin", "Paris", "Amsterdam", "Dublin", "Stockholm", "Barcelona"] else
                                              "Asia" if x in ["Singapore", "Tokyo", "Bangalore", "Hong Kong", "Seoul"] else "Other")
    
    job_data['cost_of_living_index'] = job_data['location'].apply(lambda x: 
                                                           180 if x == "San Francisco Bay Area" else
                                                           170 if x == "New York" else
                                                           160 if x == "Boston" else
                                                           150 if x in ["Seattle", "London"] else
                                                           140 if x in ["Los Angeles", "Tokyo", "Dublin"] else
                                                           130 if x in ["Chicago", "Paris", "Amsterdam", "Hong Kong"] else
                                                           120 if x in ["Austin", "Berlin", "Stockholm", "Singapore"] else
                                                           110 if x in ["Barcelona", "Seoul"] else
                                                           100 if x == "Bangalore" else 130)
    
    return job_data 