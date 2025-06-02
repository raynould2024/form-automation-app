# src/utils.py

import time
from selenium.webdriver.common.by import By

def wait_for_element(driver, by, value, timeout=10):
    """
    Waits for an element to appear on the page.
    
    :param driver: The WebDriver instance.
    :param by: The method to locate the element (By.NAME, By.XPATH, etc.).
    :param value: The value to locate the element.
    :param timeout: Maximum wait time in seconds.
    :return: The WebElement if found, or None if not found in time.
    """
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            element = driver.find_element(by, value)
            return element
        except:
            time.sleep(1)
    return None
