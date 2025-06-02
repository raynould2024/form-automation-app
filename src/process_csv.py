# src/process_csv.py
import pandas as pd
from bs4 import BeautifulSoup

def get_first_row_data(csv_path):
    """Read the first row of the CSV as a dictionary."""
    try:
        data = pd.read_csv(csv_path)
        return data.iloc[0].to_dict()
    except Exception as e:
        raise Exception(f"Error reading CSV: {str(e)}")

def extract_form_fields(html_path):
    """Extract input and select field names from the HTML file."""
    try:
        with open(html_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
        fields = []
        for tag in soup.find_all(['input', 'select']):
            if tag.get('name') and tag.get('type') not in ['submit', 'reset']:
                fields.append(tag['name'])
        return fields
    except Exception as e:
        raise Exception(f"Error parsing HTML: {str(e)}")

def get_csv_headers(csv_path):
    """Extract header names from the CSV file."""
    try:
        data = pd.read_csv(csv_path)
        print(data.columns)
        return data.columns.tolist()
    except Exception as e:
        raise Exception(f"Error reading CSV headers: {str(e)}")