# C:\Users\Hp\Desktop\seleinum_code\src\app.py
from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
from src.process_csv import get_first_row_data, extract_form_fields, get_csv_headers
from src.main import run_selenium_automation
from openai import AzureOpenAI
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()
print("Environment Variables Loaded:")
print(f"OPENAI_ENDPOINT: {os.getenv('OPENAI_ENDPOINT')}")
print(f"OPENAI_KEY: {os.getenv('OPENAI_KEY')}")
print(f"OPENAI_DEPLOYMENT_NAME: {os.getenv('OPENAI_DEPLOYMENT_NAME')}")

# Configs
UPLOAD_FOLDER = 'Uploads'
ALLOWED_HTML = {'html'}
ALLOWED_DATA = {'csv', 'xlsx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Azure OpenAI client
try:
    client = AzureOpenAI(
        azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
        api_key=os.getenv("OPENAI_KEY"),
        api_version="2023-05-15",  # Use an appropriate API version for Azure OpenAI
        azure_deployment=os.getenv("OPENAI_DEPLOYMENT_NAME")
    )
    print("Azure OpenAI Client Initialized Successfully")
except Exception as e:
    print(f"Failed to Initialize Azure OpenAI Client: {e}")

def allowed_file(filename, allowed_exts):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_exts

def get_openai_field_mapping(html_fields, csv_headers):
    """Use Azure OpenAI to map CSV headers to HTML form fields."""
    prompt = f"""
    Given the following HTML form fields and CSV headers, map each HTML field to the most likely corresponding CSV header. 
    Return the mapping as a JSON object where keys are HTML fields and values are CSV headers.

    HTML Form Fields: {html_fields}
    CSV Headers: {csv_headers}

    Provide a mapping that best aligns the fields based on semantic similarity and common naming conventions. 
    For example:
    - 'first_name', 'fname', or 'first' might map to 'First Name' or 'FirstName'
    - 'phone' or 'mobile' might map to 'Phone Number' or 'Contact'
    If no clear match exists, use 'null' for that HTML field.
    """
    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_DEPLOYMENT_NAME"),  # Deployment name for Azure OpenAI
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.2
        )
        mapping_str = response.choices[0].message.content.strip()
        print(f"Raw OpenAI Mapping Response: {mapping_str}")
        # Parse the response (assuming OpenAI returns a JSON-like string)
        mapping = json.loads(mapping_str)
    except json.JSONDecodeError:
        # Fallback to a simple key-value mapping if JSON parsing fails
        mapping = {}
        lines = mapping_str.split('\n')
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                mapping[key.strip()] = value.strip() or None
    except Exception as e:
        raise Exception(f"Error with OpenAI API: {str(e)}")
    return mapping

@app.route('/')
def index():
    return redirect(url_for('upload_files'))

@app.route('/upload', methods=['GET', 'POST'])
def upload_files():
    html_uploaded = False
    data_uploaded = False

    if request.method == 'POST':
        if 'html_file' in request.files:
            html_file = request.files['html_file']
            if html_file and allowed_file(html_file.filename, ALLOWED_HTML):
                html_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'form.html'))
                html_uploaded = True

        if 'data_file' in request.files:
            data_file = request.files['data_file']
            if data_file and allowed_file(data_file.filename, ALLOWED_DATA):
                data_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'data.csv'))
                data_uploaded = True

        if html_uploaded and data_uploaded:
            return redirect(url_for('process_form'))

    return render_template('upload_combined.html')

# @app.route('/process_form')
# def process_form():
#     try:
#         html_path = os.path.join(app.config['UPLOAD_FOLDER'], 'form.html')
#         csv_path = os.path.join(app.config['UPLOAD_FOLDER'], 'data.csv')

#         html_fields = extract_form_fields(html_path)
#         csv_headers = get_csv_headers(csv_path)

#         print(f"HTML Fields: {html_fields}")
#         print(f"CSV Headers: {csv_headers}")

#         # Use Azure OpenAI to get field mapping
#         mapping = get_openai_field_mapping(html_fields, csv_headers)
#         print(f"OpenAI Mapping: {mapping}")

#         # Validate mapping
#         missing_fields = [field for field in html_fields if field not in mapping or mapping[field] is None or mapping[field] not in csv_headers]
#         print(f"Missing Fields: {missing_fields}")

#         if missing_fields:
#             return render_template('error.html', 
#                                  error=f"CSV is missing required fields: {', '.join(missing_fields)}")

#         # Proceed with automation using the mapped headers
#         results = run_selenium_automation(csv_path, mapping)

#         return render_template('process_form.html', 
#                              html_fields=html_fields, 
#                              csv_headers=csv_headers,
#                              results=results)
#     except Exception as e:
#         return render_template('error.html', error=str(e))
# C:\Users\Hp\Desktop\seleinum_code\src\app.py
@app.route('/process_form')
def process_form():
    try:
        html_path = os.path.join(app.config['UPLOAD_FOLDER'], 'form.html')
        csv_path = os.path.join(app.config['UPLOAD_FOLDER'], 'data.csv')

        html_fields = extract_form_fields(html_path)
        csv_headers = get_csv_headers(csv_path)

        print(f"HTML Fields: {html_fields}")
        print(f"CSV Headers: {csv_headers}")

        # Use Azure OpenAI to get field mapping
        mapping = get_openai_field_mapping(html_fields, csv_headers)
        print(f"OpenAI Mapping: {mapping}")

        # Validate mapping
        missing_fields = [field for field in html_fields if field not in mapping or mapping[field] is None or mapping[field] not in csv_headers]
        print(f"Missing Fields: {missing_fields}")

        if missing_fields:
            return render_template('error.html', 
                                 error=f"CSV is missing required fields: {', '.join(missing_fields)}")

        # Proceed with automation using the mapped headers
        results = run_selenium_automation(csv_path, mapping)

        # Calculate automation stats
        total_rows = len(results)
        success_rows = len([r for r in results if r.status.lower() == 'success'])
        success_rate = (success_rows / total_rows * 100) if total_rows > 0 else 0
        error_rate = ((total_rows - success_rows) / total_rows * 100) if total_rows > 0 else 0
        avg_processing_time = sum(r.processing_time for r in results) / total_rows if total_rows > 0 else 0

        return render_template('process_form.html', 
                             html_fields=html_fields, 
                             csv_headers=csv_headers,
                             results=results,
                             success_rate=success_rate,
                             error_rate=error_rate,
                             avg_processing_time=avg_processing_time)
    except Exception as e:
        return render_template('error.html', error=str(e))
if __name__ == '__main__':
    print("Starting Flask App...")
    app.run(debug=True)