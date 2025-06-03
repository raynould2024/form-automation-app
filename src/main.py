# C:\Users\Hp\Desktop\seleinum_code\src\main.py
from form_filler import fill_form
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
from dataclasses import dataclass
import time
import os

@dataclass
class AutomationResult:
    row: int
    status: str
    message: str
    processing_time: float

def run_selenium_automation(csv_path, field_mapping=None):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_binary = "/tmp/chrome/google-chrome"
    chrome_options.binary_location = chrome_binary
    if not os.path.exists(chrome_binary):
        raise FileNotFoundError("Chrome binary not found at /tmp/chrome/google-chrome")

    chromedriver_path = "/tmp/chromedriver/chromedriver"
    if not os.path.exists(chromedriver_path):
        raise FileNotFoundError("ChromeDriver not found at /tmp/chromedriver/chromedriver")

    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    results = []

    try:
        df = pd.read_csv(csv_path)
        for index, row in df.iterrows():
            start_time = time.time()
            try:
                driver.get("https://form-automation-app.onrender.com")  # Update to match your app's form URL
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
    results = run_selenium_automation("Uploads/data.csv", dummy_mapping)
    for result in results:
        print(result)