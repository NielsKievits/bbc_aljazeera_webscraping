# To open this file, python is required
# To run this file, aljazeera.py should be typed in the python3 terminal
# To use the code, the following packages are required:
import csv
from datetime import datetime
import time
from ftfy import fix_text

# Selenium is the package that allows for the web scraping
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--disable-gpu") # Disable GPU acceleration for stability
chrome_options.add_argument("--window-size=1920x1080") # To determine the screen size

# Initialize WebDriver
# The webdriver controls the browser
service = Service(ChromeDriverManager().install()) # Install ChromeDriverManager
driver = webdriver.Chrome(service=service, options=chrome_options) # Initialize Chrome driver

# Scrape URL, this can be changes into another relevant URL
url = "https://www.aljazeera.com/tag/israel-palestine-conflict/"

# Open the page, the browser will be opened and the URL will be visited
driver.get(url)
time.sleep(10)

# Accept cookies automatically. Cookies need to be accepted, as the page will not load properly otherwise and not all articles could be scraped
# Press the button to accept cookies
try: # try to accept the cookies
    # Wait for the button to appear (max 10 seconds)
    accept_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//button[@id="onetrust-accept-btn-handler"]'))
    )
    # Click the button
    accept_button.click()

    # Wait for the page to refresh
    time.sleep(2)  # Allow page refresh if needed
except Exception as e: # if cookies cannot be accepted, print an error and stop the analysis
    print("Error accepting cookies:", e)
    driver.quit()

# add a delay to ensure the page is fully loaded and not to look like a robot
time.sleep(3)

# Remove sticky footer ad, otherwise it will block the 'Show More' button
driver.execute_script("document.querySelector('.ads.fs-sticky-footer').style.display='none';")

# Click the 'Show More' button until a certain date
# The desired starting date can be adjusted here
reference_date = datetime.strptime("7 Oct 2023", "%d %b %Y")

# Execute this command until the starting date is reached
while True:
    try:
        # Wait for the button to appear
        # If the "show more button" cannot be found, stop the analysis
        show_more_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "show-more-button")]'))
        )

        # Scroll to the "show more button"
        ActionChains(driver).move_to_element(show_more_button).perform()

        # Click the button
        time.sleep(1)  # Small delay to ensure stability
        show_more_button.click()

        # Stop after reference_date
        # Temporally save news articles in a list
        articles = driver.find_elements(By.TAG_NAME, "article")
        # Retreive the last news article from the list
        last_article = articles[-1]
        # Extract published date
        # Compare the last article's date with the starting date
        try:
            # look for the last article's date
            date_element = last_article.find_element(By.CSS_SELECTOR, ".gc__date__date span[aria-hidden='true']")
            published_date = datetime.strptime(date_element.text.strip(), "%d %b %Y")

            # If the date of the last article is smaller than the starting date, stop the analysis
            if published_date < reference_date:
                break;
        except:
            print( "Error extracting date")
            published_date = ""  # If date is not available

        # Wait for the new content to load
        time.sleep(1)  # Small delay to ensure stability

    except Exception as e:
        print("No more 'Show More' button found or error:", e)
        break  # Exit loop if button no longer exists or any error occurs

# Extract article data, all articles loaded (End of code rule 66, which orders pressing the "load more button")

# List to store article data. Create a new empty list
articles_data = []

# Retreive collected all news articles from the webpage and put them in the new list one by one
articles = driver.find_elements(By.TAG_NAME, "article")
for article in articles:
    try:
        # Extract title. Search in de HTML (website's code) for the news articles' title
        title_element = article.find_element(By.CSS_SELECTOR, "h3.gc__title a") # Search for the news article's title
        title = fix_text(title_element.get_attribute("textContent")).strip() # Remove odd signs from the title

        # Extract URL
        url = title_element.get_attribute("href") # href is where the URL is

         # Extract source (if available) Label is sometimes present
        try:
            source_element = article.find_element(By.CSS_SELECTOR, "span.video-program-source__program-name")
            source = source_element.text.strip()
        except: # If not present, it remains empty
            source = ""  # If source is not available

        # Extract published date
        try:
            date_element = article.find_element(By.CSS_SELECTOR, ".gc__date__date span[aria-hidden='true']")
            published_date = date_element.text.strip()
        except:
            published_date = ""  # If date is not available

        # Append to list
        articles_data.append([title, url, source, published_date])

    except Exception as e:
        print(f"Skipping an article due to an error: {e}")

# Close the driver
driver.quit()

# Save to CSV file comma seperated values. Readable for Excel
csv_filename = "aljazeera_updates.csv"
with open(csv_filename, mode="w", newline="", encoding="utf-8-sig") as file:
    writer = csv.writer(file, delimiter=";", quoting=csv.QUOTE_ALL)
    writer.writerow(["Title", "URL", "Source", "Published Date"])  # Header
    writer.writerows(articles_data)

print(f"Exported {len(articles_data)} articles to {csv_filename}.")
