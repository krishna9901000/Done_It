import os
import json
import time
import pandas as pd

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from selenium.webdriver.common.keys import Keys



INTERNSHALA_BASE_URL = "https://internshala.com/internships/"
GLASSDOOR_BASE_URL = "https://www.glassdoor.co.in/Job/index.html"
SEARCH_QUERY = ['Software-Development', 'Data-Science', 'Machine-Learning', 'Web-Development']

COOKIE_FILE = 'glassdoor_cookies.json'
LINKEDIN_BASE_URL = "https://www.linkedin.com/jobs/search/?keywords="


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
def load_cookies(driver, base_url):
    print("Loading cookies...")
    if not os.path.exists(COOKIE_FILE):
        print("Missing cookie file.")
        return
    driver.get(base_url)
    time.sleep(2)
    with open(COOKIE_FILE) as f:
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



def extract_internshala(driver,query):

    driver.get(INTERNSHALA_BASE_URL+query+"-internship/"+"early-applicant-25")
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
    for card in internship_cards[:10]:
        title = card.find('a',class_='job-title-href').text.strip() if card.find('a',class_='job-title-href') else 'N/A'
        company = card.find('p','company-name').text.strip() if card.find('p','company-name') else 'N/A'
        location = card.find('div', class_='location').text.strip() if card.find('div', class_='location') else 'N/A'
        stipend = card.find('span', class_='stipend').text.strip()  if card.find('span', class_='stipend') else 'N/A'
        link = INTERNSHALA_BASE_URL+card.find('a')['href'] if card.find('a') else 'N/A'
        data.append([title, company, location, stipend, link])

    # Create a DataFrame and save to CSV
    df = pd.DataFrame(data, columns=['Title', 'Company', 'Location', 'Stipend', 'Link'])
    df.to_csv('internships_internshala.csv', index=False)
    print("Data extracted and saved to internships.csv")


def scrap_glassdoor(driver,query):
    print("Scraping Glassdoor...")
    # Implement Glassdoor scraping logic here
    # This is a placeholder function
    driver.get("https://www.glassdoor.co.in/Job/index.html")
    wait = WebDriverWait(driver, 10)

    search_button = driver.find_element(By.CLASS_NAME, "Cxgo6B1ivcP5yK7VbPmO")

    search_button.click()

    time.sleep(1)
    
    search_box= driver.find_element(By.CLASS_NAME, "wB7UtoU5xZpudGkCjAIA")
    
    search_box.clear()
    search_box.send_keys(query)

    search_box.send_keys(Keys.ENTER)
    time.sleep(3)

    # Parse the page source
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find all job cards

    script_tag = soup.find('script', type='application/ld+json')

    # Load the JSON content
    data = json.loads(script_tag.string)

    # Extract URLs from itemListElement
    urls = [item['url'] for item in data.get('itemListElement', [])]

    datas=[]

    # Print the URLs
    for url in urls[:10]:
        try:
            driver.get(url)
            time.sleep(2)
            # Wait for the page to load
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Extract the job title
            job_title = soup.find('h4', class_='heading_Heading__BqX5z').text.strip() if soup.find('h4', class_='heading_Heading__BqX5z') else 'N/A'

            # Extract the company name
            company_name = soup.find('h1', class_='heading_Heading__BqX5J').text.strip() if soup.find('h1', class_='heading_Heading__BqX5J') else 'N/A'
            # Extract the location
            location = soup.find('div', class_='location').text.strip() if soup.find('div', class_='location') else 'N/A'

            Stipend = soup.find('div', class_='JobCard_salaryEstimate__QpbTW').text.strip() if soup.find('div', class_='JobCard_salaryEstimate__QpbTW') else 'N/A'

            datas.append([job_title, company_name, location, Stipend, url])
        except Exception as e:
            print(f"Error occurred while processing URL {url}: {e}")
            continue

    # Create a DataFrame and save to CSV
    df = pd.DataFrame(datas, columns=['Title', 'Company', 'Location', 'Stipend', 'Link'])
    df.to_csv('internships_glassdoor.csv', index=False)
    print("Data extracted and saved to internships_glassdoor.csv")
        


def extract_linkedin(driver, query):
    print(f"Scraping LinkedIn for: {query}")

    # Construct search URL
    url = f"{LINKEDIN_BASE_URL}{query}"
    driver.get(url)
    time.sleep(3)

    # Load results page fully
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'job-card-list__title'))
    )

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    jobs_data = []
    cards = soup.find_all('li', class_='jobs-search-results__list-item')
    for card in cards[:10]:  # Limit to first 10 results
        try:
            title_tag = card.find('a', class_='job-card-list__title')
            title = title_tag.text.strip() if title_tag else 'N/A'
            link = "https://www.linkedin.com" + title_tag['href'] if title_tag else 'N/A'

            company_tag = card.find('a', class_='job-card-container__company-name')
            company = company_tag.text.strip() if company_tag else 'N/A'

            location_tag = card.find('span', class_='job-card-container__metadata-item')
            location = location_tag.text.strip() if location_tag else 'N/A'

            jobs_data.append([title, company, location, 'N/A', link])
        except Exception as e:
            print(f"Error parsing job card: {e}")
            continue

    df = pd.DataFrame(jobs_data, columns=['Title', 'Company', 'Location', 'Stipend', 'Link'])
    df.to_csv('internships_linkedin.csv', index=False)
    print("Saved LinkedIn internships to internships_linkedin.csv")


if __name__ == "__main__":
    driver = setup_driver()
    for query in SEARCH_QUERY:
        extract_internshala(driver,query)
        load_cookies(driver, GLASSDOOR_BASE_URL)
        time.sleep(2)
        scrap_glassdoor(driver,query)
        time.sleep(2)
        extract_linkedin(driver,query)
    print("Driver setup complete.")
    driver.quit()
    