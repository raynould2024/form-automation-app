# src/main.py
from selenium import webdriver
import time
import pandas as pd
# from form_filler import fill_form

from src.form_filler import fill_form 

# Load input data from CSV
data = pd.read_csv('data/data.csv')
print("Columns in CSV:", data.columns.tolist())
# Initialize WebDriver
driver = webdriver.Chrome(executable_path='drivers/chromedriver.exe')

for index, row in data.iterrows():
    driver.get('https://formautomationcomp-559875f1aa42.herokuapp.com/')
    # Use the separate first_name and last_name columns directly
    first_name = row['first_name']
    last_name = row['last_name']
    # Call fill_form with all required fields
    fill_form(
        driver,
        first_name,
        last_name,
        row['street'],
        row['city'],
        row['zip'],
        row['state'],
        row['home_phone'],
        row['work_phone']
    )
    time.sleep(1)

# Close the browser
driver.quit()