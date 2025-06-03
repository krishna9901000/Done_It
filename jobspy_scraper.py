import csv
from jobspy import scrape_jobs

def scrape_jobspy_jobs(role):
    jobs = scrape_jobs(
        site_name=["indeed", "linkedin", "glassdoor", "google"],
        search_term=role,
        location="India",
        results_wanted=2,
        hours_old=3,
        country_indeed='India',
    )
    jobs.to_csv("jobs_jobspy.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
