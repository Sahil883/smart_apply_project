from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

import requests
from bs4 import BeautifulSoup

import random

# the list of proxy to rotate on 
PROXIES = [
    "http://93.115.200.159:8001",
    "http://93.115.200.158:8002",
    "http://93.115.200.157:8003"
]

# randomly select a proxy
proxy = random.choice(PROXIES)

# set selenium-wire options to use the proxy
seleniumwire_options = {
    "proxy": {
        "http": proxy,
        "https": proxy
    },
}

# set Chrome options to run in headless mode
options = Options()
options.add_argument("--headless=new")


# initialize the Chrome driver with service, selenium-wire options, and chrome options
driver = webdriver.Chrome()


# Go to LinkedIn's login page
driver.get("https://www.linkedin.com/login")

# Find the username and password fields
username = driver.find_element(By.ID,"username")
password = driver.find_element(By.ID,"password")

# Enter your credentials
username.send_keys("9075767854")
password.send_keys("Shi@#2992000")

# Submit the login form
password.send_keys(Keys.RETURN)
time.sleep(3)
driver.get("https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4220570289")


# Step 4: Wait and get page source
time.sleep(5)  # Let the page fully load
soup = BeautifulSoup(driver.page_source, "html.parser")


job_cards = soup.find_all('li',{'class':'ember-view'}) # Class might change, inspect it live
print(job_cards)
a=input()
for job in job_cards:
    base_card_div = job.find('div', {'class':'base-card'})
    print(base_card_div)
    exit()
