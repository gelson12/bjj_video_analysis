# extract_cookies.py

import time
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Configure Selenium to run headlessly
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Path to your ChromeDriver
CHROMEDRIVER_PATH = '/usr/local/bin/chromedriver'  # As installed in Dockerfile

# Initialize the WebDriver
driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=chrome_options)

try:
    # Navigate to YouTube
    driver.get("https://www.youtube.com")

    # Click on the "Sign In" button
    sign_in_button = driver.find_element(By.XPATH, '//tp-yt-paper-button[@aria-label="Sign in"]')
    sign_in_button.click()

    # Allow time for the login page to load
    time.sleep(2)

    # Enter your email
    email_input = driver.find_element(By.ID, "identifierId")
    email_input.send_keys(os.getenv('YOUTUBE_EMAIL'))
    driver.find_element(By.ID, "identifierNext").click()

    # Allow time for password input
    time.sleep(2)

    # Enter your password
    password_input = driver.find_element(By.NAME, "password")
    password_input.send_keys(os.getenv('YOUTUBE_PASSWORD'))
    driver.find_element(By.ID, "passwordNext").click()

    # Allow time for login to complete
    time.sleep(5)

    # Navigate to YouTube again to ensure login
    driver.get("https://www.youtube.com")

    # Allow time for the page to load
    time.sleep(5)

    # Extract cookies
    cookies = driver.get_cookies()

    # Save cookies to a JSON file
    with open("cookies.json", "w") as file:
        json.dump(cookies, file)

    print("Cookies extracted and saved to cookies.json")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()