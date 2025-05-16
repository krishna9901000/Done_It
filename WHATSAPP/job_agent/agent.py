from user_parser import parse_user_input
from job_fetcher import fetch_jooble_jobs
from matcher import match_jobs

def run_agent(user_input):
    preferences = parse_user_input(user_input)
    jobs = fetch_jooble_jobs(preferences["role"] or "developer")
    matches = match_jobs(preferences, jobs)
    return matches[:5]  # Top 5 