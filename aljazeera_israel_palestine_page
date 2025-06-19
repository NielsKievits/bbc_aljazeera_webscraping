# Om dit bestand uit te voeren heb je python nodig op je machine
# Je runt dit bestand vervolgens door python3 aljazeera.py in de terminal te typen

# Om deze code te gebruiken zijn de volgende packages nodig:
import csv
from datetime import datetime
import time
from ftfy import fix_text

# Selenium is een package die het mogelijk maakt om webpagina's te scrapen
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
chrome_options.add_argument("--window-size=1920x1080") # Om de grootte van het scherm te bepalen

# Initialize WebDriver
# De webdriver stuurt de browser aan
service = Service(ChromeDriverManager().install()) # Install ChromeDriverManager
driver = webdriver.Chrome(service=service, options=chrome_options) # Initialize Chrome driver

# Scrape URL, deze kan je aanpassen naar de URL die je wilt scrapen
url = "https://www.aljazeera.com/tag/israel-palestine-conflict/"

# Open the page, de browser wordt geopend en de URL wordt bezocht
driver.get(url)
time.sleep(10)

# Accept cookies automatisch. Als de cookies niet geaccepteerd worden, kan de pagina niet volledig geladen worden
# en kunnen niet alle artikelen worden gescraped
# Klik op de knop om cookies te accepteren
try: # probeer de cookies te accepteren
    # Wait for the button to appear (max 10 seconds)
    accept_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//button[@id="onetrust-accept-btn-handler"]'))
    )
    # Click the button
    accept_button.click()

    # Wait for the page to refresh
    time.sleep(2)  # Allow page refresh if needed
except Exception as e: # als het niet lukt om de cookies te accepteren, print dan een error en dan stopt de analyse
    print("Error accepting cookies:", e)
    driver.quit()

# add a delay to ensure the page is fully loaded and not to look like a robot
time.sleep(3)

# Remove sticky footer ad, otherwise it will block the 'Show More' button
driver.execute_script("document.querySelector('.ads.fs-sticky-footer').style.display='none';")

# Click the 'Show More' button until a certain date.
# Hier kan je de begindatum aanpassen tot wanneer je de artikelen wilt scrapen
reference_date = datetime.strptime("7 Oct 2023", "%d %b %Y")

# Voer dit uit totdat de begindatum is bereikt
while True:
    try:
        # Wait for the button to appear
        # Als de knop "show more button" niet gevonden wordt, dan stopt de analyse
        show_more_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "show-more-button")]'))
        )

        # Scroll to the button
        # Scroll naar de knop "show more button"
        ActionChains(driver).move_to_element(show_more_button).perform()

        # Click the button
        time.sleep(1)  # Small delay to ensure stability
        show_more_button.click()

        # Stop after reference_date
        # Sla op dit moment tijdelijk de artikelen op in een lijst
        articles = driver.find_elements(By.TAG_NAME, "article")
        # Haal het laatste artikel op uit die lijst
        last_article = articles[-1]
        # Extract published date
        # vergelijk de datum van het laatste artikel met de begindatum
        try:
            # zoek van het laatste artikel de datum op
            date_element = last_article.find_element(By.CSS_SELECTOR, ".gc__date__date span[aria-hidden='true']")
            published_date = datetime.strptime(date_element.text.strip(), "%d %b %Y")

            # Als de datum van het laatste artikel kleiner is dan de begindatum, dan stop de analyse
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

# Extract article data, all articles loaded (Einde van coderegel 66, waar het klikken op laad meer begint)

# List to store article data. Dit wordt de export een nieuwe lege lijst
articles_data = []

# Haal alle artikelen op dit moment van de pagina en zet ze een voor een in de nieuwe lijst
articles = driver.find_elements(By.TAG_NAME, "article")
for article in articles:
    try:
        # Extract title. Zoeken in de HTML (code van de website) naar de titel van het artikel
        title_element = article.find_element(By.CSS_SELECTOR, "h3.gc__title a") # Zoek de titel van het artikel
        title = fix_text(title_element.get_attribute("textContent")).strip() # haal vreemde tekens uit de titel

        # Extract URL
        url = title_element.get_attribute("href") # href is waar de url in staat

         # Extract source (if available) Label is soms gevuld
        try:
            source_element = article.find_element(By.CSS_SELECTOR, "span.video-program-source__program-name")
            source = source_element.text.strip()
        except: # als het niet gevuld is laten we het leeg
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

# Save to CSV file comma seperated values. Leesbaar voor excel
csv_filename = "aljazeera_updates.csv"
with open(csv_filename, mode="w", newline="", encoding="utf-8-sig") as file:
    writer = csv.writer(file, delimiter=";", quoting=csv.QUOTE_ALL)
    writer.writerow(["Title", "URL", "Source", "Published Date"])  # Header
    writer.writerows(articles_data)

print(f"Exported {len(articles_data)} articles to {csv_filename}.")
