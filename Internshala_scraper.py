import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

BASE_URL = "https://internshala.com/internships/"

def setup_driver():
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return uc.Chrome(options=options)

def extract_internshala_jobs(query):
    driver = setup_driver()
    driver.get(BASE_URL + query + "-internship/")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "internship_meta"))
    )
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    internship_cards = soup.select('div.individual_internship')
    data = []
    for card in internship_cards[:10]:
        title = card.find('a', class_='job-title-href')
        company = card.find('p', class_='company-name')
        location = card.find('div', class_='location')
        stipend = card.find('span', class_='stipend')
        link = card.find('a')['href'] if card.find('a') else 'N/A'
        data.append([
            title.text.strip() if title else 'N/A',
            company.text.strip() if company else 'N/A',
            location.text.strip() if location else 'N/A',
            stipend.text.strip() if stipend else 'N/A',
            "https://internshala.com" + link
        ])
    df = pd.DataFrame(data, columns=['Title', 'Company', 'Location', 'Stipend', 'Link'])
    df.to_csv("internships_internshala.csv", index=False)
