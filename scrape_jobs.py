import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import random
from urllib.parse import urljoin, quote
import logging
from typing import List, Dict, Optional
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobScraper:
    def __init__(self, headless: bool = True):
        """Initialize the job scraper with Chrome WebDriver"""
        self.driver = None
        self.headless = headless
        self.setup_driver()
        
        # Common skills to look for
        self.common_skills = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js', 'express',
            'django', 'flask', 'fastapi', 'sql', 'mysql', 'postgresql', 'mongodb', 'redis',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git', 'jenkins', 'ci/cd',
            'html', 'css', 'bootstrap', 'tailwind', 'sass', 'typescript', 'php', 'laravel',
            'spring', 'hibernate', 'rest api', 'graphql', 'microservices', 'agile', 'scrum',
            'machine learning', 'data science', 'pandas', 'numpy', 'tensorflow', 'pytorch',
            'spark', 'hadoop', 'kafka', 'elasticsearch', 'linux', 'bash', 'powershell',
            'c++', 'c#', '.net', 'ruby', 'rails', 'go', 'rust', 'scala', 'kotlin', 'swift'
        ]
        
    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("Chrome WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise
    
    def random_delay(self, min_seconds: float = 1, max_seconds: float = 3):
        """Add random delay to avoid being detected as bot"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from job description text"""
        if not text:
            return []
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.common_skills:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill.title())
        
        return list(set(found_skills))  # Remove duplicates
    
    def extract_experience_from_text(self, text: str) -> str:
        """Extract years of experience from text"""
        if not text:
            return "N/A"
        
        # Common patterns for experience
        patterns = [
            r'(\d+)[\s\-]*(?:to|-)[\s\-]*(\d+)[\s\-]*(?:years?|yrs?)',  # 2-5 years
            r'(\d+)\+?[\s\-]*(?:years?|yrs?)[\s\-]*(?:of\s+)?(?:experience|exp)',  # 3+ years experience
            r'(?:minimum|min|at least)[\s\-]*(\d+)[\s\-]*(?:years?|yrs?)',  # minimum 2 years
            r'(\d+)[\s\-]*(?:years?|yrs?)[\s\-]*(?:minimum|min|required)',  # 3 years minimum
            r'(\d+)[\s\-]*(?:to|-)[\s\-]*(\d+)[\s\-]*(?:yrs?|years?)',  # 2 to 5 yrs
        ]
        
        text_lower = text.lower()
        
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                match = matches[0]
                if isinstance(match, tuple):
                    if len(match) == 2 and match[1]:  # Range like "2-5"
                        return f"{match[0]}-{match[1]} years"
                    else:  # Single number
                        return f"{match[0]} years"
                else:  # Single match
                    return f"{match} years"
        
        return "N/A"
    
    def scrape_linkedin_job_details(self, job_url: str) -> Dict:
        """Scrape detailed information from LinkedIn job page"""
        details = {'skills': [], 'experience': 'N/A', 'description': ''}
        
        try:
            self.driver.get(job_url)
            self.random_delay(2, 4)
            
            # Wait for job description to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".description__text"))
                )
            except:
                logger.warning(f"Could not load job details for {job_url}")
                return details
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract job description
            description_elem = soup.find('div', class_='description__text')
            if description_elem:
                description = description_elem.get_text(strip=True)
                details['description'] = description
                
                # Extract skills and experience from description
                details['skills'] = self.extract_skills_from_text(description)
                details['experience'] = self.extract_experience_from_text(description)
            
            # Look for criteria section (LinkedIn specific)
            criteria_section = soup.find('ul', class_='description__job-criteria-list')
            if criteria_section:
                criteria_items = criteria_section.find_all('li')
                for item in criteria_items:
                    text = item.get_text(strip=True).lower()
                    if 'experience level' in text or 'seniority level' in text:
                        exp_text = item.get_text(strip=True)
                        if details['experience'] == 'N/A':
                            details['experience'] = exp_text
            
        except Exception as e:
            logger.error(f"Error scraping LinkedIn job details: {e}")
        
        return details
    
    def scrape_naukri_job_details(self, job_url: str) -> Dict:
        """Scrape detailed information from Naukri job page"""
        details = {'skills': [], 'experience': 'N/A', 'description': ''}
        
        try:
            self.driver.get(job_url)
            self.random_delay(2, 4)
            
            # Wait for job description to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".JDC_dang"))
                )
            except:
                logger.warning(f"Could not load job details for {job_url}")
                return details
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract job description
            description_elem = soup.find('div', class_='JDC_dang')
            if description_elem:
                description = description_elem.get_text(strip=True)
                details['description'] = description
                
                # Extract skills and experience from description
                details['skills'] = self.extract_skills_from_text(description)
                details['experience'] = self.extract_experience_from_text(description)
            
            # Look for key skills section
            skills_section = soup.find('div', class_='key-skill')
            if skills_section:
                skill_tags = skills_section.find_all('a')
                naukri_skills = [tag.get_text(strip=True) for tag in skill_tags]
                # Combine with extracted skills
                all_skills = list(set(details['skills'] + naukri_skills))
                details['skills'] = all_skills
            
            # Look for experience in job details section
            job_details = soup.find('div', class_='job-details')
            if job_details:
                exp_text = job_details.get_text(strip=True)
                extracted_exp = self.extract_experience_from_text(exp_text)
                if extracted_exp != 'N/A':
                    details['experience'] = extracted_exp
            
        except Exception as e:
            logger.error(f"Error scraping Naukri job details: {e}")
        
        return details
    
    def scrape_linkedin_jobs(self, job_title: str, location: str = "", max_pages: int = 3, detailed: bool = True) -> List[Dict]:
        """Scrape jobs from LinkedIn"""
        jobs = []
        
        try:
            # Format search parameters
            job_title_encoded = quote(job_title)
            location_encoded = quote(location) if location else ""
            
            for page in range(max_pages):
                start = page * 25
                url = f"https://www.linkedin.com/jobs/search/?keywords={job_title_encoded}&location={location_encoded}&start={start}"
                
                logger.info(f"Scraping LinkedIn page {page + 1}: {url}")
                self.driver.get(url)
                self.random_delay(2, 4)
                
                # Wait for job listings to load
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".job-search-card"))
                    )
                except:
                    logger.warning(f"No job listings found on page {page + 1}")
                    continue
                
                # Get page source and parse with BeautifulSoup
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                job_cards = soup.find_all('div', class_='job-search-card')
                
                for card in job_cards:
                    try:
                        job_data = self._extract_linkedin_job_data(card)
                        if job_data:
                            # Get detailed information if requested
                            if detailed and job_data['job_link'] != 'N/A':
                                logger.info(f"Getting details for: {job_data['title']}")
                                details = self.scrape_linkedin_job_details(job_data['job_link'])
                                job_data.update(details)
                                self.random_delay(1, 2)  # Shorter delay between detail pages
                            print(job_data)
                            
                            jobs.append(job_data)
                    except Exception as e:
                        logger.error(f"Error extracting LinkedIn job data: {e}")
                        continue
                
                self.random_delay(2, 4)
                
        except Exception as e:
            logger.error(f"Error scraping LinkedIn: {e}")
        
        logger.info(f"Scraped {len(jobs)} jobs from LinkedIn")
        return jobs
    
    def _extract_linkedin_job_data(self, card) -> Optional[Dict]:
        """Extract job data from LinkedIn job card"""
        try:
            # Job title
            title_elem = card.find('h3', class_='base-search-card__title')
            title = title_elem.get_text(strip=True) if title_elem else "N/A"
            
            # Company name
            company_elem = card.find('h4', class_='base-search-card__subtitle')
            company = company_elem.get_text(strip=True) if company_elem else "N/A"
            
            # Location
            location_elem = card.find('span', class_='job-search-card__location')
            location = location_elem.get_text(strip=True) if location_elem else "N/A"
            
            # Job link
            link_elem = card.find('a', class_='base-card__full-link')
            job_link = link_elem.get('href') if link_elem else "N/A"
            
            # Posted date
            date_elem = card.find('time')
            posted_date = date_elem.get('datetime') if date_elem else "N/A"
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'posted_date': posted_date,
                'job_link': job_link,
                'source': 'LinkedIn',
                'skills': [],
                'experience': 'N/A',
                'description': ''
            }
        except Exception as e:
            logger.error(f"Error extracting LinkedIn job data: {e}")
            return None
    
    def scrape_naukri_jobs(self, job_title: str, location: str = "", max_pages: int = 3, detailed: bool = True) -> List[Dict]:
        """Scrape jobs from Naukri.com"""
        jobs = []
        
        try:
            # Format search parameters
            job_title_encoded = quote(job_title)
            location_encoded = quote(location) if location else ""
            
            for page in range(max_pages):
                url = f"https://www.naukri.com/{job_title_encoded}-jobs"
                if location:
                    url += f"-in-{location_encoded}"
                if page > 0:
                    url += f"?k={job_title_encoded}&l={location_encoded}&p={page + 1}"
                
                logger.info(f"Scraping Naukri page {page + 1}: {url}")
                self.driver.get(url)
                self.random_delay(2, 4)
                
                # Wait for job listings to load
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".srp-jobtuple-wrapper"))
                    )
                except:
                    logger.warning(f"No job listings found on page {page + 1}")
                    continue
                
                # Get page source and parse with BeautifulSoup
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                job_cards = soup.find_all('div', class_='srp-jobtuple-wrapper')
                
                for card in job_cards:
                    try:
                        job_data = self._extract_naukri_job_data(card)
                        if job_data:
                            # Get detailed information if requested
                            if detailed and job_data['job_link'] != 'N/A':
                                logger.info(f"Getting details for: {job_data['title']}")
                                details = self.scrape_naukri_job_details(job_data['job_link'])
                                job_data.update(details)
                                self.random_delay(1, 2)  # Shorter delay between detail pages
                            
                            jobs.append(job_data)
                    except Exception as e:
                        logger.error(f"Error extracting Naukri job data: {e}")
                        continue
                
                self.random_delay(2, 4)
                
        except Exception as e:
            logger.error(f"Error scraping Naukri: {e}")
        
        logger.info(f"Scraped {len(jobs)} jobs from Naukri")
        return jobs
    
    def _extract_naukri_job_data(self, card) -> Optional[Dict]:
        """Extract job data from Naukri job card"""
        try:
            # Job title
            title_elem = card.find('a', class_='title')
            title = title_elem.get_text(strip=True) if title_elem else "N/A"
            
            # Company name
            company_elem = card.find('a', class_='subTitle')
            company = company_elem.get_text(strip=True) if company_elem else "N/A"
            
            # Experience
            exp_elem = card.find('span', class_='expwdth')
            experience = exp_elem.get_text(strip=True) if exp_elem else "N/A"
            
            # Salary
            salary_elem = card.find('span', class_='salary')
            salary = salary_elem.get_text(strip=True) if salary_elem else "N/A"
            
            # Location
            location_elem = card.find('span', class_='locWdth')
            location = location_elem.get_text(strip=True) if location_elem else "N/A"
            
            # Job link
            link_elem = card.find('a', class_='title')
            job_link = urljoin('https://www.naukri.com', link_elem.get('href')) if link_elem else "N/A"
            
            # Posted date
            date_elem = card.find('span', class_='job-post-day')
            posted_date = date_elem.get_text(strip=True) if date_elem else "N/A"
            
            # Skills from card (if available)
            skills_elem = card.find('span', class_='skill-tags')
            skills = []
            if skills_elem:
                skill_tags = skills_elem.find_all('span')
                skills = [tag.get_text(strip=True) for tag in skill_tags]
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'experience': experience,
                'salary': salary,
                'posted_date': posted_date,
                'job_link': job_link,
                'source': 'Naukri',
                'skills': skills,
                'description': ''
            }
        except Exception as e:
            logger.error(f"Error extracting Naukri job data: {e}")
            return None
    
    def scrape_all_jobs(self, job_title: str, location: str = "", max_pages: int = 3, detailed: bool = True) -> pd.DataFrame:
        """Scrape jobs from both LinkedIn and Naukri"""
        all_jobs = []
        
        #Scrape LinkedIn
        linkedin_jobs = self.scrape_linkedin_jobs(job_title, location, max_pages, detailed)
        all_jobs.extend(linkedin_jobs)

       

        
        # Scrape Naukri
        # naukri_jobs = self.scrape_naukri_jobs(job_title, location, max_pages, detailed)
        # all_jobs.extend(naukri_jobs)
        
        # Convert to DataFrame
        df = pd.DataFrame(all_jobs)
       
        # Clean and standardize data
        if not df.empty:
            df = self._clean_job_data(df)
        
        return df
    
    def _clean_job_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize job data"""
        # Remove duplicates based on title and company
        df = df.drop_duplicates(subset=['title', 'company'], keep='first')

        df.to_csv('output2.csv', index=False)
        
        
        # Clean text fields
        text_columns = ['title', 'company', 'location']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].str.strip()
                df[col] = df[col].replace('', 'N/A')
        
        # Convert skills list to string for better display
        if 'skills' in df.columns:
            df['skills_text'] = df['skills'].apply(lambda x: ', '.join(x) if isinstance(x, list) and x else 'N/A')
        
        # Sort by source and title
        df = df.sort_values(['source', 'title']).reset_index(drop=True)
       
        return df
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
if __name__ == "__main__":
    a=JobScraper()
    a.scrape_all_jobs(job_title='Data Engineer',location='India')