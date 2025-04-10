import os
import json
import time
import pandas as pd

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc



BASE_URL = "https://internshala.com/internships/"
SEARCH_QUERY = ['Software-Development', 'Data-Science', 'Machine-Learning', 'Web-Development']
# === DRIVER SETUP ===
def setup_driver():
    options = uc.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-infobars')
    #options.add_argument('--headless')  # Uncomment for headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return uc.Chrome(options=options)

# === LOAD COOKIES ===
def load_cookies(driver, cookie_file, base_url):
    print("Loading cookies...")
    if not os.path.exists(cookie_file):
        print("Missing cookie file.")
        return
    driver.get(base_url)
    time.sleep(2)
    with open(cookie_file) as f:
        cookies = json.load(f)
    for cookie in cookies:
        cookie.pop('sameSite', None)
        if 'expiry' in cookie:
            cookie['expires'] = cookie.pop('expiry')
        try:
            driver.add_cookie(cookie)
        except:
            continue
    driver.get(base_url)
    time.sleep(1)
    print("Cookies loaded.")



def extract_data(driver,query):

    driver.get(BASE_URL+query+"-internship/"+"early-applicant-25")
    time.sleep(2)

    # Wait for the page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "internship_meta"))
    )

    # Parse the page source
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find all internship cards
    internship_card = soup.select_one('div', class_='.internship_list_container_1')

    # Extract data from each card
    data=[]
    internship_cards = internship_card.find_all('div', class_='individual_internship')
    for card in internship_cards:
        title = card.find('a',class_='job-title-href').text.strip() if card.find('a',class_='job-title-href') else 'N/A'
        company = card.find('p','company-name').text.strip() if card.find('p','company-name') else 'N/A'
        location = card.find('div', class_='location').text.strip() if card.find('div', class_='location') else 'N/A'
        stipend = card.find('span', class_='stipend').text.strip()  if card.find('span', class_='stipend') else 'N/A'
        link = card.find('a')['href'] if card.find('a') else 'N/A'
        data.append([title, company, location, stipend, link])

    # Create a DataFrame and save to CSV
    df = pd.DataFrame(data, columns=['Title', 'Company', 'Location', 'Stipend', 'Link'])
    df.to_csv('internships.csv', index=False)
    print("Data extracted and saved to internships.csv")

if __name__ == "__main__":
    driver = setup_driver()
    for query in SEARCH_QUERY:
        extract_data(driver,query)
        
        time.sleep(2)
    print("Driver setup complete.")
    driver.quit()
    