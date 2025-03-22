import requests
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
import logging
from dotenv import load_dotenv
import re
import json

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("linkedin_scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LinkedInScraper:
    """
    A class for scraping job postings from LinkedIn.
    """
    
    def __init__(self):
        """
        Initialize the LinkedIn scraper with credentials from environment variables.
        """
        self.username = os.getenv("LINKEDIN_USERNAME")
        self.password = os.getenv("LINKEDIN_PASSWORD")
        self.driver = None
        self.jobs_data = []
        
        if not self.username or not self.password:
            logger.error("LinkedIn credentials not found in environment variables")
            raise ValueError("LinkedIn credentials not found. Please check .env file.")
    
    def setup_driver(self):
        """
        Set up the Chrome WebDriver for automated browsing.
        """
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"user-agent={os.getenv('USER_AGENT')}")
            
            chrome_driver_path = os.getenv("CHROME_DRIVER_PATH")
            
            if chrome_driver_path:
                service = Service(executable_path=chrome_driver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                self.driver = webdriver.Chrome(options=chrome_options)
                
            logger.info("WebDriver set up successfully")
        
        except Exception as e:
            logger.error(f"Error setting up WebDriver: {e}")
            raise
    
    def login(self):
        """
        Login to LinkedIn using the provided credentials.
        """
        try:
            self.driver.get("https://www.linkedin.com/login")
            
            # Wait for login page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            
            # Enter credentials
            self.driver.find_element(By.ID, "username").send_keys(self.username)
            self.driver.find_element(By.ID, "password").send_keys(self.password)
            self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
            
            # Wait for login to complete
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "global-nav"))
            )
            
            logger.info("Successfully logged in to LinkedIn")
            
        except TimeoutException:
            logger.error("Timeout while logging in to LinkedIn")
            raise
        except Exception as e:
            logger.error(f"Error logging in to LinkedIn: {e}")
            raise
    
    def search_jobs(self, keywords, location="United States", job_type=None, experience_level=None, max_pages=5):
        """
        Search for jobs using the provided filters.
        
        Args:
            keywords (str): Job keywords to search for
            location (str): Location to search in
            job_type (str, optional): Job type (Full-time, Part-time, Contract, etc.)
            experience_level (str, optional): Experience level
            max_pages (int, optional): Maximum number of pages to scrape
            
        Returns:
            list: List of job postings
        """
        try:
            # Construct the search URL
            base_url = "https://www.linkedin.com/jobs/search/?"
            query_params = {
                "keywords": keywords,
                "location": location,
                "f_AL": "true"  # Filter for "Easy Apply" jobs
            }
            
            # Add job type filter
            if job_type:
                job_type_mapping = {
                    "full-time": "F",
                    "part-time": "P",
                    "contract": "C",
                    "temporary": "T",
                    "internship": "I",
                    "volunteer": "V"
                }
                job_type_code = job_type_mapping.get(job_type.lower())
                if job_type_code:
                    query_params[f"f_JT"] = job_type_code
            
            # Add experience level filter
            if experience_level:
                exp_level_mapping = {
                    "internship": "1",
                    "entry level": "2",
                    "associate": "3",
                    "mid-senior level": "4",
                    "director": "5",
                    "executive": "6"
                }
                exp_level_code = exp_level_mapping.get(experience_level.lower())
                if exp_level_code:
                    query_params[f"f_E"] = exp_level_code
            
            # Construct query string
            query_string = "&".join([f"{key}={value}" for key, value in query_params.items()])
            search_url = base_url + query_string
            
            # Navigate to the search page
            self.driver.get(search_url)
            
            # Wait for search results to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobs-search__results-list"))
            )
            
            # Scrape each page
            for page in range(max_pages):
                logger.info(f"Scraping page {page + 1}")
                
                # Get all job cards on the current page
                job_cards = self.driver.find_elements(By.CLASS_NAME, "jobs-search-results__list-item")
                
                for job_card in job_cards:
                    try:
                        # Click on the job card to load details
                        job_card.click()
                        time.sleep(1)  # Wait for job details to load
                        
                        # Extract job details
                        job_data = self._extract_job_data()
                        if job_data:
                            self.jobs_data.append(job_data)
                    
                    except Exception as e:
                        logger.warning(f"Error extracting job data: {e}")
                        continue
                
                # Go to next page if not the last page
                if page < max_pages - 1:
                    try:
                        next_button = self.driver.find_element(By.XPATH, "//button[@aria-label='Next']")
                        if next_button.is_enabled():
                            next_button.click()
                            time.sleep(2)  # Wait for next page to load
                        else:
                            logger.info("No more pages available")
                            break
                    except Exception:
                        logger.info("No more pages available")
                        break
            
            logger.info(f"Scraped {len(self.jobs_data)} job postings")
            return self.jobs_data
            
        except Exception as e:
            logger.error(f"Error searching jobs: {e}")
            raise
    
    def _extract_job_data(self):
        """
        Extract job data from the currently selected job card.
        
        Returns:
            dict: Job data
        """
        try:
            # Wait for job details to load
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobs-unified-top-card"))
            )
            
            # Extract basic job info
            job_title_elem = self.driver.find_element(By.CLASS_NAME, "jobs-unified-top-card__job-title")
            job_title = job_title_elem.text.strip() if job_title_elem else "N/A"
            
            company_elem = self.driver.find_element(By.CLASS_NAME, "jobs-unified-top-card__company-name")
            company = company_elem.text.strip() if company_elem else "N/A"
            
            location_elem = self.driver.find_element(By.CLASS_NAME, "jobs-unified-top-card__bullet")
            location = location_elem.text.strip() if location_elem else "N/A"
            
            # Try to get posting date
            try:
                date_elem = self.driver.find_element(By.CLASS_NAME, "jobs-unified-top-card__posted-date")
                posting_date = date_elem.text.strip() if date_elem else "N/A"
            except:
                posting_date = "N/A"
            
            # Extract job description
            try:
                show_more_button = self.driver.find_element(By.CLASS_NAME, "jobs-description__see-more-button")
                show_more_button.click()
                time.sleep(0.5)
            except:
                pass
            
            description_elem = self.driver.find_element(By.CLASS_NAME, "jobs-description__content")
            description = description_elem.text.strip() if description_elem else "N/A"
            
            # Extract job details (seniority, employment type, etc.)
            job_criteria_elements = self.driver.find_elements(By.CLASS_NAME, "jobs-unified-top-card__job-insight")
            job_details = {}
            
            for elem in job_criteria_elements:
                text = elem.text.strip()
                if "Seniority level" in text:
                    job_details["seniority_level"] = text.replace("Seniority level", "").strip()
                elif "Employment type" in text:
                    job_details["employment_type"] = text.replace("Employment type", "").strip()
                elif "Job function" in text:
                    job_details["job_function"] = text.replace("Job function", "").strip()
                elif "Industries" in text:
                    job_details["industries"] = text.replace("Industries", "").strip()
            
            # Extract application details (number of applicants)
            try:
                applicants_elem = self.driver.find_element(By.CLASS_NAME, "jobs-unified-top-card__applicant-count")
                applicants = applicants_elem.text.strip() if applicants_elem else "N/A"
            except:
                applicants = "N/A"
            
            # Construct job data dictionary
            job_data = {
                "title": job_title,
                "company": company,
                "location": location,
                "posting_date": posting_date,
                "applicants": applicants,
                "seniority_level": job_details.get("seniority_level", "N/A"),
                "employment_type": job_details.get("employment_type", "N/A"),
                "job_function": job_details.get("job_function", "N/A"),
                "industries": job_details.get("industries", "N/A"),
                "description": description
            }
            
            return job_data
            
        except Exception as e:
            logger.warning(f"Error extracting job details: {e}")
            return None
    
    def extract_skills(self, job_data):
        """
        Extract skills from job descriptions.
        
        Args:
            job_data (list): List of job data dictionaries
            
        Returns:
            list: Updated job data with extracted skills
        """
        # Common technical skills to look for
        common_skills = [
            "Python", "Java", "JavaScript", "TypeScript", "C\\+\\+", "C#", "Ruby", "PHP", "Swift", "Kotlin",
            "HTML", "CSS", "SQL", "NoSQL", "MongoDB", "PostgreSQL", "MySQL", "Oracle",
            "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Jenkins", "Git",
            "React", "Angular", "Vue", "Node.js", "Express", "Django", "Flask", "Spring",
            "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "Data Science",
            "TensorFlow", "PyTorch", "scikit-learn", "Pandas", "NumPy", "R",
            "Agile", "Scrum", "Jira", "Confluence", "Product Management", "UI/UX",
            "Figma", "Sketch", "Adobe XD", "Photoshop", "Illustrator",
            "Excel", "PowerPoint", "Word", "Google Workspace", "Power BI", "Tableau"
        ]
        
        # Compile regex pattern for faster matching
        pattern = re.compile('|'.join(r'\b{}\b'.format(skill) for skill in common_skills), re.IGNORECASE)
        
        for job in job_data:
            description = job.get("description", "")
            skills_found = pattern.findall(description)
            
            # Normalize skills (remove duplicates and standardize case)
            skills_normalized = list(set(skill.title() for skill in skills_found))
            
            # Add skills to job data
            job["skills"] = skills_normalized
        
        return job_data
    
    def save_to_csv(self, filename="linkedin_jobs.csv"):
        """
        Save the scraped job data to a CSV file.
        
        Args:
            filename (str): Name of the output CSV file
        """
        if not self.jobs_data:
            logger.warning("No job data to save")
            return
        
        try:
            # Extract skills before saving
            self.jobs_data = self.extract_skills(self.jobs_data)
            
            # Convert to DataFrame and save
            df = pd.DataFrame(self.jobs_data)
            
            # Convert skills list to comma-separated string
            df["skills"] = df["skills"].apply(lambda x: ", ".join(x) if isinstance(x, list) else "")
            
            # Save to CSV
            df.to_csv(filename, index=False)
            logger.info(f"Saved {len(df)} job postings to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving job data to CSV: {e}")
    
    def close(self):
        """
        Close the browser instance.
        """
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")

def main():
    """
    Main function to run the LinkedIn scraper.
    """
    try:
        # Initialize scraper
        scraper = LinkedInScraper()
        
        # Set up driver and login
        scraper.setup_driver()
        scraper.login()
        
        # Search for jobs
        keywords = "Data Scientist"
        location = "United States"
        job_type = "full-time"
        experience_level = "mid-senior level"
        
        scraper.search_jobs(
            keywords=keywords,
            location=location,
            job_type=job_type,
            experience_level=experience_level,
            max_pages=3
        )
        
        # Save data to CSV
        output_file = f"data/raw/linkedin_{keywords.replace(' ', '_').lower()}_{time.strftime('%Y%m%d')}.csv"
        scraper.save_to_csv(output_file)
        
    except Exception as e:
        logger.error(f"Error running LinkedIn scraper: {e}")
    
    finally:
        if 'scraper' in locals():
            scraper.close()

if __name__ == "__main__":
    main() 