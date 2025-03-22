import pandas as pd
import numpy as np
import re
import os
import sqlite3
import logging
from pathlib import Path
import nltk
import spacy
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data_processor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
DB_PATH = Path(__file__).parent.parent.parent / 'data' / 'processed' / 'job_market.db'

class JobDataProcessor:
    """
    A class for processing and normalizing job posting data from various sources.
    """
    
    def __init__(self):
        """
        Initialize the data processor.
        """
        self.nlp = None
        self.initialize_nlp()
    
    def initialize_nlp(self):
        """
        Initialize NLP models (spaCy and NLTK).
        """
        try:
            # Load spaCy model
            self.nlp = spacy.load("en_core_web_sm")
            
            # Download NLTK resources if not already downloaded
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt')
            
            try:
                nltk.data.find('corpora/stopwords')
            except LookupError:
                nltk.download('stopwords')
                
            try:
                nltk.data.find('corpora/wordnet')
            except LookupError:
                nltk.download('wordnet')
                
            logger.info("NLP models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing NLP models: {e}")
            raise
    
    def load_data(self, file_path):
        """
        Load data from a CSV file.
        
        Args:
            file_path (str): Path to the CSV file
            
        Returns:
            pd.DataFrame: Loaded DataFrame
        """
        try:
            df = pd.read_csv(file_path)
            logger.info(f"Loaded {len(df)} records from {file_path}")
            return df
        except Exception as e:
            logger.error(f"Error loading data from {file_path}: {e}")
            raise
    
    def clean_data(self, df):
        """
        Clean and normalize the data.
        
        Args:
            df (pd.DataFrame): Input DataFrame
            
        Returns:
            pd.DataFrame: Cleaned DataFrame
        """
        try:
            # Make a copy to avoid modifying the original
            df_clean = df.copy()
            
            # Fill missing values
            df_clean = df_clean.fillna({
                'title': 'Unknown',
                'company': 'Unknown',
                'location': 'Unknown',
                'description': '',
                'skills': ''
            })
            
            # Clean the location field
            df_clean['location_clean'] = df_clean['location'].apply(self._clean_location)
            
            # Extract country, state, and city from location
            location_details = df_clean['location_clean'].apply(self._extract_location_components)
            df_clean['country'] = location_details.apply(lambda x: x.get('country', 'Unknown'))
            df_clean['state'] = location_details.apply(lambda x: x.get('state', 'Unknown'))
            df_clean['city'] = location_details.apply(lambda x: x.get('city', 'Unknown'))
            
            # Extract remote/hybrid/onsite status
            df_clean['location_type'] = df_clean['description'].apply(self._detect_location_type)
            
            # Clean and normalize the posting date
            if 'posting_date' in df_clean.columns:
                df_clean['posting_date_clean'] = df_clean['posting_date'].apply(self._normalize_date)
            
            # Normalize job titles
            df_clean['title_normalized'] = df_clean['title'].apply(self._normalize_job_title)
            
            # Extract seniority level if not already present
            if 'seniority_level' not in df_clean.columns or df_clean['seniority_level'].isna().all():
                df_clean['seniority_level'] = df_clean['title'].apply(self._extract_seniority)
            
            # Clean the skills field (ensure it's a list)
            if 'skills' in df_clean.columns:
                df_clean['skills_list'] = df_clean['skills'].apply(
                    lambda x: [s.strip() for s in str(x).split(',')] if pd.notna(x) else []
                )
            
            # Extract additional skills from job description
            df_clean['extracted_skills'] = df_clean['description'].apply(self._extract_skills)
            
            # Combine existing skills with extracted ones
            if 'skills_list' in df_clean.columns:
                df_clean['all_skills'] = df_clean.apply(
                    lambda row: list(set(row['skills_list'] + row['extracted_skills'])), axis=1
                )
            else:
                df_clean['all_skills'] = df_clean['extracted_skills']
            
            # Extract industry if not present
            if 'industries' not in df_clean.columns or df_clean['industries'].isna().all():
                df_clean['industry'] = df_clean['description'].apply(self._extract_industry)
            else:
                df_clean['industry'] = df_clean['industries']
            
            logger.info(f"Cleaned {len(df_clean)} records")
            return df_clean
            
        except Exception as e:
            logger.error(f"Error cleaning data: {e}")
            raise
    
    def _clean_location(self, location_str):
        """
        Clean and normalize location strings.
        
        Args:
            location_str (str): Raw location string
            
        Returns:
            str: Cleaned location string
        """
        if pd.isna(location_str) or location_str == "N/A":
            return "Unknown"
        
        # Remove "Greater" prefix
        location_str = re.sub(r'^Greater\s+', '', location_str)
        
        # Remove common suffixes
        location_str = re.sub(r'\s+Area$', '', location_str)
        location_str = re.sub(r'\s+Metropolitan Area$', '', location_str)
        
        # Remove trailing whitespace
        location_str = location_str.strip()
        
        return location_str
    
    def _extract_location_components(self, location_str):
        """
        Extract country, state, and city from a location string.
        
        Args:
            location_str (str): Cleaned location string
            
        Returns:
            dict: Dictionary with country, state, and city
        """
        components = {'country': 'Unknown', 'state': 'Unknown', 'city': 'Unknown'}
        
        if location_str == "Unknown":
            return components
        
        # Split by common delimiters
        parts = re.split(r'[,;]', location_str)
        parts = [p.strip() for p in parts]
        
        # Handle US locations
        us_pattern = r'\b(AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY|D\.C\.|DC)\b'
        
        # Check for US state abbreviations
        for part in parts:
            state_match = re.search(us_pattern, part)
            if state_match:
                components['country'] = 'United States'
                components['state'] = state_match.group(0)
                
                # Extract city (usually the first part if in US)
                if len(parts) > 1 and parts[0] != part:
                    components['city'] = parts[0]
                return components
        
        # Check for full US state names
        us_states = {
            'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 
            'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 
            'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 
            'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 
            'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 
            'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 
            'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 
            'Wisconsin', 'Wyoming', 'District of Columbia'
        }
        
        for part in parts:
            if part in us_states:
                components['country'] = 'United States'
                components['state'] = part
                
                # Extract city (usually the first part if in US)
                if len(parts) > 1 and parts[0] != part:
                    components['city'] = parts[0]
                return components
        
        # Handle common countries
        common_countries = {
            'UK': 'United Kingdom', 'United Kingdom': 'United Kingdom', 'England': 'United Kingdom',
            'Canada': 'Canada', 'Australia': 'Australia', 'Germany': 'Germany', 'France': 'France',
            'India': 'India', 'Japan': 'Japan', 'China': 'China', 'Brazil': 'Brazil',
            'Netherlands': 'Netherlands', 'Ireland': 'Ireland', 'Spain': 'Spain',
            'Italy': 'Italy', 'Singapore': 'Singapore', 'Sweden': 'Sweden'
        }
        
        for part in parts:
            if part in common_countries:
                components['country'] = common_countries[part]
                
                # Extract city (usually the first part if country is last)
                if parts.index(part) > 0:
                    components['city'] = parts[0]
                return components
        
        # If no matches, assume the last part is the country and the first is the city
        if len(parts) >= 2:
            components['country'] = parts[-1]
            components['city'] = parts[0]
        elif len(parts) == 1:
            components['city'] = parts[0]
        
        return components
    
    def _detect_location_type(self, description):
        """
        Detect if a job is remote, hybrid, or on-site based on the description.
        
        Args:
            description (str): Job description
            
        Returns:
            str: Location type (Remote, Hybrid, On-site)
        """
        if pd.isna(description):
            return "Unknown"
            
        description = description.lower()
        
        # Check for remote indicators
        remote_patterns = [
            r'\bremote\b', r'\bwork from home\b', r'\bwfh\b', r'\bwork from anywhere\b',
            r'\bfully remote\b', r'\b100% remote\b', r'\bremotely\b'
        ]
        
        for pattern in remote_patterns:
            if re.search(pattern, description):
                return "Remote"
        
        # Check for hybrid indicators
        hybrid_patterns = [
            r'\bhybrid\b', r'\bpartially remote\b', r'\bremote hybrid\b', r'\bhybrid remote\b',
            r'\bflexible work\b', r'\bflexible location\b', r'\bflexible working\b',
            r'\bwfh \d+ days\b', r'\bremote \d+ days\b', r'\boffice \d+ days\b'
        ]
        
        for pattern in hybrid_patterns:
            if re.search(pattern, description):
                return "Hybrid"
        
        # Check for on-site indicators
        onsite_patterns = [
            r'\bon-site\b', r'\bonsite\b', r'\bin office\b', r'\bin-office\b',
            r'\bon location\b', r'\bin-person\b', r'\bin person\b'
        ]
        
        for pattern in onsite_patterns:
            if re.search(pattern, description):
                return "On-site"
        
        # Default to on-site if no indicators found
        return "On-site"
    
    def _normalize_date(self, date_str):
        """
        Normalize date strings into a standard format.
        
        Args:
            date_str (str): Raw date string
            
        Returns:
            datetime: Normalized date
        """
        if pd.isna(date_str) or date_str == "N/A":
            return None
            
        # Common date formats
        try:
            # Handle "X days/months/years ago" format
            ago_match = re.search(r'(\d+)\s+(day|days|month|months|year|years)\s+ago', date_str.lower())
            if ago_match:
                num = int(ago_match.group(1))
                unit = ago_match.group(2)
                
                today = datetime.now().date()
                
                if unit in ['day', 'days']:
                    return today - timedelta(days=num)
                elif unit in ['month', 'months']:
                    return today - timedelta(days=num * 30)
                elif unit in ['year', 'years']:
                    return today - timedelta(days=num * 365)
            
            # Try standard date formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%B %d, %Y', '%b %d, %Y']:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
                    
            # If all else fails, return None
            return None
            
        except Exception:
            return None
    
    def _normalize_job_title(self, title):
        """
        Normalize job titles to standard forms.
        
        Args:
            title (str): Raw job title
            
        Returns:
            str: Normalized job title
        """
        if pd.isna(title) or title == "Unknown":
            return "Unknown"
            
        title = title.lower()
        
        # Remove company names and other non-title text
        title = re.sub(r'\bat\s+.*$', '', title)
        title = re.sub(r'\s-\s.*$', '', title)
        
        # Normalize software engineering roles
        if re.search(r'software\s+engineer|software\s+developer|programmer|coder|developer', title):
            return "Software Engineer"
            
        # Normalize data science roles
        if re.search(r'data\s+scien(ce|tist)|machine\s+learning|ml\s+engineer|ai\s+engineer', title):
            return "Data Scientist"
            
        # Normalize data analyst roles
        if re.search(r'data\s+analyst|business\s+analyst|bi\s+analyst|analytics', title):
            return "Data Analyst"
            
        # Normalize product management roles
        if re.search(r'product\s+manager|product\s+owner|program\s+manager', title):
            return "Product Manager"
            
        # Normalize UX/UI roles
        if re.search(r'ux|ui|user\s+experience|user\s+interface|designer', title):
            return "UX/UI Designer"
            
        # Normalize marketing roles
        if re.search(r'market|seo|content|social\s+media', title):
            return "Marketing Specialist"
            
        # Normalize sales roles
        if re.search(r'sales|account\s+executive|business\s+development', title):
            return "Sales Representative"
            
        # Normalize finance roles
        if re.search(r'financ(e|ial)|accountant|accounting', title):
            return "Financial Analyst"
            
        # Normalize HR roles
        if re.search(r'hr|human\s+resources|recruiter|talent', title):
            return "Human Resources"
            
        # Normalize project management roles
        if re.search(r'project\s+manager|project\s+lead|scrum\s+master', title):
            return "Project Manager"
            
        # If no match, return cleaned title with first letter of each word capitalized
        return ' '.join(w.capitalize() for w in title.split())
    
    def _extract_seniority(self, title):
        """
        Extract seniority level from job title.
        
        Args:
            title (str): Job title
            
        Returns:
            str: Seniority level
        """
        if pd.isna(title) or title == "Unknown":
            return "Unknown"
            
        title = title.lower()
        
        # Check for executive/C-level
        if re.search(r'ceo|cto|cio|cfo|chief|executive|president|director|vp|vice\s+president', title):
            return "Executive"
            
        # Check for senior level
        if re.search(r'senior|sr\.?|lead|principal|staff|architect', title):
            return "Senior"
            
        # Check for mid level
        if re.search(r'mid|intermediate|ii|2', title):
            return "Mid Level"
            
        # Check for junior/entry level
        if re.search(r'junior|jr\.?|entry|associate|intern|trainee|graduate', title):
            return "Entry Level"
            
        # Default to mid level if no indicators
        return "Mid Level"
    
    def _extract_skills(self, description):
        """
        Extract skills from job description using NLP.
        
        Args:
            description (str): Job description
            
        Returns:
            list: List of extracted skills
        """
        if pd.isna(description) or not description:
            return []
            
        # Common technical skills to look for
        common_skills = [
            "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Ruby", "PHP", "Swift", "Kotlin",
            "HTML", "CSS", "SQL", "NoSQL", "MongoDB", "PostgreSQL", "MySQL", "Oracle",
            "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Jenkins", "Git",
            "React", "Angular", "Vue", "Node.js", "Express", "Django", "Flask", "Spring",
            "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "Data Science",
            "TensorFlow", "PyTorch", "scikit-learn", "Pandas", "NumPy", "R",
            "Agile", "Scrum", "Jira", "Confluence", "Product Management", "UI/UX",
            "Figma", "Sketch", "Adobe XD", "Photoshop", "Illustrator",
            "Excel", "PowerPoint", "Word", "Google Workspace", "Power BI", "Tableau"
        ]
        
        # Process the text with spaCy
        doc = self.nlp(description)
        
        # Extract all noun phrases as potential skills
        noun_phrases = [chunk.text.strip() for chunk in doc.noun_chunks]
        
        # Match potential skills against common skills
        skills_found = []
        
        # Use regex for exact matches
        for skill in common_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', description, re.IGNORECASE):
                skills_found.append(skill)
                
        # Add any noun phrases that look like skills
        for phrase in noun_phrases:
            for skill in common_skills:
                if phrase.lower() == skill.lower():
                    skills_found.append(skill)
                    break
        
        # Normalize and deduplicate
        normalized_skills = list(set(skill for skill in skills_found))
        
        return normalized_skills
    
    def _extract_industry(self, description):
        """
        Extract industry from job description.
        
        Args:
            description (str): Job description
            
        Returns:
            str: Extracted industry
        """
        if pd.isna(description) or not description:
            return "Unknown"
            
        description = description.lower()
        
        # Industry patterns to check
        industry_patterns = {
            "Technology": [r'software', r'tech', r'information technology', r'it company', r'saas'],
            "Healthcare": [r'health', r'medical', r'hospital', r'pharmaceutical', r'biotech'],
            "Finance": [r'finance', r'banking', r'investment', r'fintech', r'insurance'],
            "Education": [r'education', r'school', r'university', r'college', r'teaching'],
            "Manufacturing": [r'manufacturing', r'industrial', r'production', r'factory'],
            "Retail": [r'retail', r'e-commerce', r'consumer goods', r'shopping'],
            "Media & Entertainment": [r'media', r'entertainment', r'publishing', r'broadcast', r'film', r'music'],
            "Government": [r'government', r'public sector', r'federal', r'state agency'],
            "Non-profit": [r'non-profit', r'ngo', r'charity', r'social service']
        }
        
        # Count matches for each industry
        industry_matches = {industry: 0 for industry in industry_patterns}
        
        for industry, patterns in industry_patterns.items():
            for pattern in patterns:
                matches = re.findall(r'\b' + pattern + r'\b', description)
                industry_matches[industry] += len(matches)
        
        # Find industry with most matches
        if max(industry_matches.values()) > 0:
            return max(industry_matches.items(), key=lambda x: x[1])[0]
        
        # Default to Technology if no matches
        return "Technology"
    
    def save_to_database(self, df, table_name="job_postings"):
        """
        Save processed data to SQLite database.
        
        Args:
            df (pd.DataFrame): DataFrame to save
            table_name (str): Name of the table to save to
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
            
            # Connect to database
            conn = sqlite3.connect(str(DB_PATH))
            
            # Save to database
            df.to_sql(table_name, conn, if_exists='append', index=False)
            
            # If it's the skills table, extract skills
            if table_name == "job_postings" and 'all_skills' in df.columns:
                # Create skills table if necessary
                skills_df = self._create_skills_dataframe(df)
                skills_df.to_sql("skills", conn, if_exists='append', index=False)
                
                # Create job posting skills relationship table
                job_skills_df = self._create_job_skills_dataframe(df)
                job_skills_df.to_sql("job_posting_skills", conn, if_exists='append', index=False)
            
            conn.close()
            
            logger.info(f"Saved {len(df)} records to {table_name} table")
            
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
            raise
    
    def _create_skills_dataframe(self, job_df):
        """
        Create a DataFrame of unique skills.
        
        Args:
            job_df (pd.DataFrame): Job postings DataFrame
            
        Returns:
            pd.DataFrame: Skills DataFrame
        """
        # Extract all skills
        all_skills = []
        for skills in job_df['all_skills']:
            if isinstance(skills, list):
                all_skills.extend(skills)
        
        # Get unique skills
        unique_skills = list(set(all_skills))
        
        # Create DataFrame
        skills_df = pd.DataFrame({
            'id': range(1, len(unique_skills) + 1),
            'skill': unique_skills,
            'created_at': datetime.now()
        })
        
        return skills_df
    
    def _create_job_skills_dataframe(self, job_df):
        """
        Create a DataFrame relating job postings to skills.
        
        Args:
            job_df (pd.DataFrame): Job postings DataFrame
            
        Returns:
            pd.DataFrame: Job-skills relationship DataFrame
        """
        # Connect to database to get skill IDs
        conn = sqlite3.connect(str(DB_PATH))
        skills_df = pd.read_sql("SELECT id, skill FROM skills", conn)
        conn.close()
        
        # Create a mapping of skill name to ID
        skill_id_map = dict(zip(skills_df['skill'], skills_df['id']))
        
        # Create job-skill relationships
        job_skills = []
        
        for idx, row in job_df.iterrows():
            job_id = idx  # Use the index as a temporary job ID
            skills = row['all_skills'] if isinstance(row['all_skills'], list) else []
            
            for skill in skills:
                if skill in skill_id_map:
                    job_skills.append({
                        'job_posting_id': job_id,
                        'skill_id': skill_id_map[skill],
                        'created_at': datetime.now()
                    })
        
        # Create DataFrame
        job_skills_df = pd.DataFrame(job_skills)
        
        return job_skills_df
    
    def process_data(self, file_path, save_to_db=True):
        """
        Process job data from file to database.
        
        Args:
            file_path (str): Path to the data file
            save_to_db (bool): Whether to save to database
            
        Returns:
            pd.DataFrame: Processed DataFrame
        """
        try:
            # Load data
            df = self.load_data(file_path)
            
            # Clean and process data
            processed_df = self.clean_data(df)
            
            # Save to database if requested
            if save_to_db:
                self.save_to_database(processed_df)
            
            return processed_df
            
        except Exception as e:
            logger.error(f"Error processing data: {e}")
            raise
    
    def process_directory(self, directory_path, save_to_db=True):
        """
        Process all data files in a directory.
        
        Args:
            directory_path (str): Path to directory containing data files
            save_to_db (bool): Whether to save to database
            
        Returns:
            pd.DataFrame: Combined processed DataFrame
        """
        try:
            directory = Path(directory_path)
            processed_dfs = []
            
            for file_path in directory.glob("*.csv"):
                try:
                    df = self.process_data(file_path, save_to_db=save_to_db)
                    processed_dfs.append(df)
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    continue
            
            if processed_dfs:
                combined_df = pd.concat(processed_dfs, ignore_index=True)
                logger.info(f"Processed {len(combined_df)} records from {len(processed_dfs)} files")
                return combined_df
            else:
                logger.warning(f"No data processed from {directory_path}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error processing directory {directory_path}: {e}")
            raise

def main():
    """
    Main function to run the data processor.
    """
    try:
        processor = JobDataProcessor()
        
        # Process all files in the raw data directory
        raw_data_dir = Path(__file__).parent.parent.parent / 'data' / 'raw'
        processor.process_directory(raw_data_dir)
        
    except Exception as e:
        logger.error(f"Error in main data processing: {e}")

if __name__ == "__main__":
    main() 