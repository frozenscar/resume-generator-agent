from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import pandas as pd


def get_job_data(job_link="https://www.linkedin.com/jobs/view/4025823296"):
    # Set up Chrome options
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")

    # Use your Google profile
    user_data_dir = "/Users/venkateshwarreddy/Library/Application Support/Google/Chrome/Default"
    if os.path.exists(user_data_dir):
        options.add_argument(f"user-data-dir={user_data_dir}")
    else:
        print(f"Warning: User data directory not found: {user_data_dir}")

    # Initialize the Chrome driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # Navigate to LinkedIn
        driver.get("https://www.linkedin.com")

        # Wait for the login button to be clickable (adjust timeout as needed)
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-tracking-control-name='guest_homepage-basic_nav-header-signin']"))
        )

        # If the login button is present, click it
        if login_button:
            login_button.click()
            print("Clicked on login button")

        # Wait for the page to load after clicking login
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )

        # Check if we're on the login page
        if "login" in driver.current_url:
            print("Login required. Please check your Google profile settings.")
        else:
            print("Successfully logged in")

        # Navigate to the specific job page
        
        driver.get(job_link)
        print("Navigated to the job page")

        show_more_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.show-more-less-html__button.show-more-less-button.show-more-less-html__button--more"))
    )
        
        driver.execute_script("arguments[0].scrollIntoView();", show_more_button)

    # Click the button
        driver.execute_script("arguments[0].click();", show_more_button)
        print("Job page loaded successfully")


        title = driver.find_elements(By.TAG_NAME, "h1")[0].text

        #print(title)
        description_div = driver.find_element(By.CLASS_NAME, "description__text--rich")
        description = description_div.text
        #print(description)

        posted_time_element = driver.find_element(By.CLASS_NAME, "posted-time-ago__text")
        posted_time = posted_time_element.text


        #print(posted_time)


    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Keep the browser open for 10 seconds to see the result
        import time
        time.sleep(3)
        driver.quit()
    return [title,posted_time,description,job_link]

def save_to_csv(data, path="jobs.csv"):
    columns = ["Job Title", "Posted Time", "Description", "link","resume","status"]

    # Check if the file exists
    if os.path.exists(path):
        # Load existing data
        df_existing = pd.read_csv(path)

        # Check if the job link already exists
        if data[3] in df_existing['link'].values:
            print("Job link already exists, data not appended.")
            return
        else:
            # Append the new data
            df_new = pd.DataFrame([data], columns=columns)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            df_combined.to_csv(path, index=False)
            print(f"Data appended to {path}")
    else:
        # Create a new CSV file
        df = pd.DataFrame([data], columns=columns)
        df.to_csv(path, index=False)
        print(f"New file created and data saved to {path}")



if __name__ == "__main__":
    data = get_job_data()
    save_to_csv(data)
    print()
