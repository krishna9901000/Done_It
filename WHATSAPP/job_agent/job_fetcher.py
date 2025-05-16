import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

JOOBLE_API_KEY = os.getenv("JOOBLE_API_KEY")

def fetch_jooble_jobs(query, location="Remote"):
    if not JOOBLE_API_KEY:
        raise ValueError("JOOBLE_API_KEY not found in environment variables")
        
    url = f"https://jooble.org/api/{JOOBLE_API_KEY}"
    payload = {
        "keywords": query,
        "location": location
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        data = response.json()
        if not data or "jobs" not in data:
            print(f"Warning: No jobs found for query: {query}")
            return []
            
        return data.get("jobs", [])
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching jobs: {str(e)}")
        return []
    except ValueError as e:
        print(f"Error parsing response: {str(e)}")
        return [] 