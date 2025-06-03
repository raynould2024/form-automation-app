# C:\Users\Hp\Desktop\seleinum_code\src\app.py
from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
from process_csv import get_first_row_data, extract_form_fields, get_csv_headers
from main import run_selenium_automation
from openai import AzureOpenAI
from dotenv import load_dotenv
import json
import subprocess
import logging
import glob
import shutil

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()
logger.debug("Environment Variables Loaded:")
logger.debug(f"OPENAI_ENDPOINT: {os.getenv('OPENAI_ENDPOINT')}")
logger.debug(f"OPENAI_KEY: {os.getenv('OPENAI_KEY')}")
logger.debug(f"OPENAI_DEPLOYMENT_NAME: {os.getenv('OPENAI_DEPLOYMENT_NAME')}")

UPLOAD_FOLDER = 'Uploads'
ALLOWED_HTML = {'html'}
ALLOWED_DATA = {'csv', 'xlsx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

try:
    client = AzureOpenAI(
        azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
        api_key=os.getenv("OPENAI_KEY"),
        api_version="2023-05-15",
        azure_deployment=os.getenv("OPENAI_DEPLOYMENT_NAME")
    )
    logger.debug("Azure OpenAI Client Initialized Successfully")
except Exception as e:
    logger.error(f"Failed to Initialize Azure OpenAI Client: {e}")

def ensure_chrome_installed():
    chrome_path = "/tmp/chrome/chrome"
    chromedriver_path = "/tmp/chromedriver/chromedriver"
    if os.path.exists(chrome_path) and os.path.exists(chromedriver_path):
        logger.debug("Chrome and ChromeDriver already installed")
        return

    logger.debug("Installing Chrome and ChromeDriver at runtime...")
    try:
        # Create directories
        os.makedirs("/tmp/chrome-install", exist_ok=True)
        os.makedirs("/tmp/chrome", exist_ok=True)
        os.makedirs("/tmp/chromedriver", exist_ok=True)

        # Download and extract Chrome
        logger.debug("Downloading Chrome .deb package...")
        subprocess.run(["wget", "-q", "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb", "-O", "/tmp/chrome-install/chrome.deb"], check=True)
        logger.debug("Extracting Chrome .deb package...")
        subprocess.run(["ar", "x", "/tmp/chrome-install/chrome.deb"], cwd="/tmp/chrome-install", check=True)
        tar_file = None
        for f in ["data.tar.xz", "data.tar.gz"]:
            if os.path.exists(os.path.join("/tmp/chrome-install", f)):
                tar_file = f
                break
        if not tar_file:
            raise Exception("No data.tar.xz or data.tar.gz found in .deb package")
        logger.debug(f"Extracting {tar_file}...")
        subprocess.run(["tar", "-xJf" if tar_file.endswith(".xz") else "-xzf", tar_file, "-C", "/tmp/chrome-install"], cwd="/tmp/chrome-install", check=True)
        logger.debug(f"Contents of /tmp/chrome-install/ after extraction: {os.listdir('/tmp/chrome-install')}")

        # Find the Chrome directory dynamically
        chrome_dir = None
        for root, dirs, files in os.walk("/tmp/chrome-install"):
            if "chrome" in files:
                chrome_dir = root
                break
        if not chrome_dir:
            raise Exception("Chrome binary not found in extracted files")
        logger.debug(f"Found Chrome directory: {chrome_dir}")
        logger.debug(f"Contents of Chrome directory: {os.listdir(chrome_dir)}")

        # Copy all files from chrome_dir to /tmp/chrome/
        for item in os.listdir(chrome_dir):
            src_path = os.path.join(chrome_dir, item)
            dst_path = os.path.join("/tmp/chrome/", item)
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
            else:
                shutil.copy2(src_path, dst_path)
        logger.debug(f"Chrome installed at: {os.listdir('/tmp/chrome/')}")

        # Download and extract ChromeDriver
        logger.debug("Downloading ChromeDriver...")
        subprocess.run(["wget", "-q", "https://chromedriver.storage.googleapis.com/127.0.6533.88/chromedriver_linux64.zip", "-O", "/tmp/chromedriver/chromedriver.zip"], check=True)
        logger.debug("Extracting ChromeDriver...")
        subprocess.run(["unzip", "chromedriver.zip", "-d", "/tmp/chromedriver"], cwd="/tmp/chromedriver", check=True)
        if os.path.exists("/tmp/chromedriver/chromedriver-linux64/chromedriver"):
            subprocess.run(["mv", "/tmp/chromedriver/chromedriver-linux64/chromedriver", "/tmp/chromedriver/chromedriver"], check=True)
            subprocess.run(["rm", "-rf", "/tmp/chromedriver/chromedriver-linux64"], check=True)
        subprocess.run(["chmod", "+x", "/tmp/chromedriver/chromedriver"], check=True)
        logger.debug(f"ChromeDriver installed at: {os.listdir('/tmp/chromedriver/')}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install Chrome/ChromeDriver at runtime: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Installation error: {str(e)}")
        raise

def allowed_file(filename, allowed_exts):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_exts

def get_openai_field_mapping(html_fields, csv_headers):
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
            model=os.getenv("OPENAI_DEPLOYMENT_NAME"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.2
        )
        mapping_str = response.choices[0].message.content.strip()
        logger.debug(f"Raw OpenAI Mapping Response: {mapping_str}")
        mapping = json.loads(mapping_str)
    except json.JSONDecodeError:
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

@app.route('/process_form')
def process_form():
    try:
        ensure_chrome_installed()

        html_path = os.path.join(app.config['UPLOAD_FOLDER'], 'form.html')
        csv_path = os.path.join(app.config['UPLOAD_FOLDER'], 'data.csv')

        html_fields = extract_form_fields(html_path)
        csv_headers = get_csv_headers(csv_path)

        logger.debug(f"HTML Fields: {html_fields}")
        logger.debug(f"CSV Headers: {csv_headers}")

        mapping = get_openai_field_mapping(html_fields, csv_headers)
        logger.debug(f"OpenAI Mapping: {mapping}")

        missing_fields = [field for field in html_fields if field not in mapping or mapping[field] is None or mapping[field] not in csv_headers]
        logger.debug(f"Missing Fields: {missing_fields}")

        if missing_fields:
            return render_template('error.html', 
                                 error=f"CSV is missing required fields: {', '.join(missing_fields)}")

        results = run_selenium_automation(csv_path, mapping)

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
    logger.debug("Starting Flask App...")
    app.run(debug=True)