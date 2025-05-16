import requests
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_jobs_from_jooble(keywords, location=""):
    api_key = os.getenv("JOOBLE_API_KEY")
    url = f"https://jooble.org/api/{api_key}"
    payload = {
        "keywords": keywords,
        "location": location,
        "page": 1
    }

    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json().get("jobs", [])
    else:
        print("Failed to fetch jobs:", response.status_code, response.text)
        return []

if __name__ == "__main__":
    jobs = fetch_jobs_from_jooble("React Developer", "Remote")
    for job in jobs[:3]:
        print(job['title'], "|", job['location'], "|", job['link'])
