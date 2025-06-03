# C:\Users\Hp\Desktop\seleinum_code\src\main.py
from form_filler import fill_form
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
from dataclasses import dataclass
import time
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
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    results = []

    try:
        df = pd.read_csv(csv_path)
        for index, row in df.iterrows():
            start_time = time.time()  # Start timer
            try:
                # driver.get("https://formautomationcomp-559875f1aa42.herokuapp.com/")
                # driver.get("https://event-form--test-c038faf429db.herokuapp.com/")
                driver.get("https://regi-form-9644bcddc60b.herokuapp.com/")
                # Convert row to dict for dynamic access
                row_data = row.to_dict()
                # Use dummy mapping if none provided (for standalone testing)
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
                # Extract name for success message (if available)
                # first_name = row_data.get(field_mapping.get('first_name', ''), 'Unknown')
                # last_name = row_data.get(field_mapping.get('last_name', ''), '')
                # results.append(AutomationResult(index + 1, "Success", f"Form filled for {first_name} {last_name}".strip()))
                end_time = time.time()  # End timer
                processing_time = end_time - start_time
                results.append(AutomationResult(index + 1, "Success", f"Form filled for Done".strip(),processing_time=processing_time))
            except Exception as e:
                results.append(AutomationResult(index + 1, "Failure", str(e)))
    finally:
        driver.quit()

    return results

if __name__ == '__main__':
    # For testing, provide a dummy mapping
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