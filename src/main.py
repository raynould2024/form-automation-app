# C:\Users\Hp\Desktop\seleinum_code\src\main.py
from form_filler import fill_form
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager

from selenium.common.exceptions import NoSuchElementException
import pandas as pd
from dataclasses import dataclass
import time
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@dataclass
class AutomationResult:
    row: int
    status: str
    message: str
    processing_time: float

def run_selenium_automation(csv_path, field_mapping=None, webpage_url=None):
    if not webpage_url or not webpage_url.startswith(('http://', 'https://')):
        raise ValueError("A valid webpage URL is required (must start with http:// or https://).")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Try multiple Chrome binary paths
    possible_chrome_paths = [
        "/tmp/chrome/google-chrome",
        "/tmp/chrome/chrome"
    ]
    chrome_binary = None
    for path in possible_chrome_paths:
        logger.debug(f"Checking Chrome binary at: {path}")
        if os.path.exists(path):
            chrome_binary = path
            break

    if not chrome_binary:
        logger.error("No Chrome binary found in possible paths")
        raise FileNotFoundError(f"No Chrome binary found in {possible_chrome_paths}")

    logger.debug(f"Using Chrome binary: {chrome_binary}")
    chrome_options.binary_location = chrome_binary

    chromedriver_path = "/tmp/chromedriver/chromedriver"
    logger.debug(f"Checking ChromeDriver at: {chromedriver_path}")
    if not os.path.exists(chromedriver_path):
        logger.error("ChromeDriver not found")
        raise FileNotFoundError(f"ChromeDriver not found at {chromedriver_path}")

    service = Service(executable_path=chromedriver_path)
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.debug("Chrome driver initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Chrome driver: {str(e)}")
        raise
    
    
    
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    results = []
    try:
        df = pd.read_csv(csv_path)
        for index, row in df.iterrows():
            start_time = time.time()
            try:
                driver.get(webpage_url)  # Use the dynamically passed webpage_url
                # driver.get("https://regi-form-9644bcddc60b.herokuapp.com/")
                row_data = row.to_dict()
                if field_mapping is None:
                    field_mapping = {
                        'first_name': 'First Name',
                        'last_name': 'Last Name',
                        'street': 'Street',
                        'city': 'City',
                        'zipcode': 'Zipcode',
                        'state': 'State',
                        'home_phone': 'Home Phone',
                        'work_phone': 'Work Phone'
                    }
                fill_form(driver, field_mapping, row_data)
                end_time = time.time()
                processing_time = end_time - start_time
                results.append(AutomationResult(index + 1, "Success", f"Form filled for Done", processing_time))
            except Exception as e:
                end_time = time.time()
                processing_time = end_time - start_time
                results.append(AutomationResult(index + 1, "Failure", str(e), processing_time))
    finally:
        driver.quit()

    return results

if __name__ == '__main__':
    dummy_mapping = {
        'first_name': 'First Name',
        'last_name': 'Last Name',
        'street': 'Street',
        'city': 'City',
        'zipcode': 'Zipcode',
        'state': 'State',
        'home_phone': 'Home Phone',
        'work_phone': 'Work Phone'
    }
    results = run_selenium_automation("Uploads/data.csv", dummy_mapping, webpage_url="https://regi-form-9644bcddc60b.herokuapp.com/")
    for result in results:
        print(result)