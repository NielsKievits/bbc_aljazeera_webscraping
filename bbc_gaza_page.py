# This code enables researchers and others to extract news articles on the search page of BBC World News using the search term 'Gaza'.
# Note that this web page has an inherent bias towards articles that include 'Gaza'.
# A more comprehensive understanding of BBC's reporting about the Israel-Palestine conflict requires the inclusion of additional web pages (which are included in this repository).

import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")

# Initialize WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# BBC Latest Updates URL
url = "https://www.bbc.com/search?q=gaza&edgeauth=eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJrZXkiOiAiZmFzdGx5LXVyaS10b2tlbi0xIiwiZXhwIjogMTc0Mzc2ODc2NCwibmJmIjogMTc0Mzc2ODQwNCwicmVxdWVzdHVyaSI6ICIlMkZzZWFyY2glM0ZxJTNEZ2F6YSJ9.MMWj_ni5maBuMaCVhUKbN0k_NxUMb5Hi2fbDGtmjv8w"

# Open the page
driver.get(url)

all_updates = []

# Step 1: Switch to the iframe using its title attribute
try:
    iframe = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//iframe[@title="SP Consent Message"]'))
    )
    driver.switch_to.frame(iframe)  # Switch to the iframe
    print("Switched to iframe by title.")
except Exception as e:
    print("Error switching to iframe:", e)

# Step 2: Wait for the "I agree" button and click it
try:
    accept_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="I agree"]'))
    )
    accept_button.click()
    print("Accepted cookies.")
    time.sleep(2)  # Allow page refresh if needed
except Exception as e:
    print("Error accepting cookies:", e)

driver.switch_to.default_content()

# Step 3: Accept cookies
try:
    cookie_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//button[@id="bbccookies-continue-button"]'))
    )
    cookie_button.click()
    print("Accepted cookies 2.")
    time.sleep(2)  # Allow page refresh if needed
except Exception as e:
    print("Error accepting cookies 2: ", e)


check_ad = True
iterator = 0
while True:
    iterator += 1
    try:
        print("Go to next page.")

        if check_ad:
            try:
                # Try to find iframe with ID starting with 'offer-0' within 2 seconds
                    iframe = WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.XPATH, "//iframe[starts-with(@id, 'offer-0')]"))
                    )
                    driver.switch_to.frame(iframe)

                    try:
                        # Try to find and click the close button in iframe within 2 seconds
                        close_button = WebDriverWait(driver, 2).until(
                            EC.element_to_be_clickable((By.CLASS_NAME, "pn-article__close"))
                        )
                        close_button.click()
                        check_ad = False
                        print("Close button clicked inside iframe.")
                    except TimeoutException:
                        print("Close button not found in iframe. Continuing...")

                    driver.switch_to.default_content()

            except NoSuchElementException:
                print("Iframe or close button not found.")
            except TimeoutException:
                print("Timed out waiting for iframe or close button.")

        # Find all update entries
        updates = driver.find_elements(By.CSS_SELECTOR, "div[data-testid=\"anchor-inner-wrapper\"]")

        for update in updates:
            link = update.find_element(By.CSS_SELECTOR, 'a')
            href = link.get_attribute("href")

            if not href:
                continue

            try:
                title = update.find_element(By.CSS_SELECTOR, 'h2').text
            except NoSuchElementException:
                title = ""

            try:
                # Try to find the SVG element inside the content-type label
                svg = update.find_element(By.CSS_SELECTOR, 'div[data-testid="content-type-label"] svg')
                icon_type = svg.get_attribute("icon")
            except NoSuchElementException:
                icon_type = ""

            try:
                # Try to find the SVG element inside the content-type label
                date = update.find_element(By.CSS_SELECTOR, 'span[data-testid="card-metadata-lastupdated"]').text.strip()
            except NoSuchElementException:
                date = ""

            try:
                # Try to find the SVG element inside the content-type label
                label = update.find_element(By.CSS_SELECTOR, 'span[data-testid="card-metadata-tag"]').text.strip()
            except NoSuchElementException:
                label = ""# If the date is not found, try to find the date in a different location

            if title and link:
                all_updates.append([title, href, icon_type, date, label])


        # Scroll to the button
        try:
            next_button = WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.XPATH,  '//button[@data-testid="pagination-next-button"]')))
            next_button.click()
            print("Clicked the 'Next Page' button.")
        except:
            print("Error clicking the 'Next Page' button.")
            break

    except Exception as e:
        print(e)
        print("No more pages. Scraping complete.")
        break

# Close the driver
driver.quit()

# Save to CSV file
csv_filename = "bbc_gaza-page.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Title", "Link", "Type", "Datum", "Label"])  # Header
    writer.writerows(all_updates)

print(f"Scraped {len(all_updates)} updates. Data saved to {csv_filename}.")
