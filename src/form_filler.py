# C:\Users\Hp\Desktop\seleinum_code\src\form_filler.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

def fill_form(driver, field_mapping, row_data):
    """
    Dynamically fill a form using a mapping of HTML field names to CSV column names and row data.
    
    Args:
        driver: Selenium WebDriver instance.
        field_mapping: Dict mapping HTML field names to CSV column names.
        row_data: Dict of CSV row data.
    """
    # Wait for form elements to be present (up to 10 seconds)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input | //select | //textarea"))
        )
    except Exception as e:
        print(f"Error: Form elements not loaded within 10 seconds: {str(e)}")
        raise

    # Find all input, select, and textarea elements on the page
    try:
        elements = driver.find_elements(By.XPATH, "//input | //select | //textarea")
    except NoSuchElementException:
        print("Error: No input, select, or textarea elements found on the page.")
        raise

    for element in elements:
        # Get the field name
        field_name = element.get_attribute('name')
        if not field_name:
            continue  # Skip elements without a name attribute

        # Skip submit/reset/hidden buttons
        if element.tag_name == "input" and element.get_attribute('type') in ['submit', 'reset', 'hidden']:
            continue

        # Check if this field is in the mapping and has a corresponding CSV column
        if field_name in field_mapping and field_mapping[field_name] in row_data:
            value = row_data[field_mapping[field_name]]
            try:
                if element.tag_name == "select":
                    state_dropdown = Select(element)
                    available_options = [opt.get_attribute('value') for opt in state_dropdown.options if opt.get_attribute('value')]
                    if str(value) in available_options:
                        state_dropdown.select_by_value(str(value))
                    else:
                        print(f"Value '{value}' not found in dropdown for field '{field_name}'. Valid options: {available_options}. Defaulting to first option.")
                        state_dropdown.select_by_index(0)
                elif element.tag_name == "textarea":
                    element.clear()
                    element.send_keys(str(value))
                elif element.tag_name == "input":
                    input_type = element.get_attribute('type')
                    if input_type == "checkbox":
                        # Debug the element state
                        is_enabled = element.is_enabled()
                        is_displayed = element.is_displayed()
                        should_check = str(value).lower() in ['true', 'on', 'yes', '1']
                        current_state = element.is_selected()
                        print(f"Checkbox '{field_name}': Enabled={is_enabled}, Displayed={is_displayed}, ShouldCheck={should_check}, CurrentState={current_state}, Value={value}")
                        if is_enabled and is_displayed:
                            if should_check != current_state:
                                element.click()
                        else:
                            print(f"Checkbox '{field_name}' is not interactable. Enabled={is_enabled}, Displayed={is_displayed}")
                            raise Exception("Checkbox not interactable")
                    elif input_type == "radio":
                        radio_group = driver.find_elements(By.NAME, field_name)
                        for radio in radio_group:
                            if radio.get_attribute('value') == str(value):
                                radio.click()
                                break
                    else:
                        if field_name == "zipcode":
                            value = str(value).zfill(5)[:5]
                        elif "phone" in field_name.lower():
                            value = ''.join(filter(str.isdigit, str(value)))[:10]
                        elif "email" in field_name.lower():
                            value = str(value).strip()
                            if "@" not in value:
                                print(f"Warning: Invalid email format for field '{field_name}': {value}")
                                value = "default@example.com"
                        elif "date" in field_name.lower():
                            import re
                            date_pattern = r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})"
                            match = re.match(date_pattern, str(value))
                            if match:
                                month, day, year = match.groups()
                                value = f"{int(month):02d}/{int(day):02d}/{year}"
                            else:
                                print(f"Warning: Invalid date format for field '{field_name}': {value}")
                                value = "01/01/2000"
                        element.clear()
                        element.send_keys(str(value))
            except NoSuchElementException:
                print(f"Error: Unable to interact with field '{field_name}'.")
                raise
            except Exception as e:
                print(f"Error filling field '{field_name}' with value '{value}': {str(e)}")
                raise

    # Submit the form
    try:
        submit_button = driver.find_element(By.XPATH, "//input[@type='submit']")
        submit_button.click()
    except NoSuchElementException:
        print("Error: Submit button not found.")
        raise