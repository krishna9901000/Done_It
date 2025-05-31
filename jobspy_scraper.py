import csv
from jobspy import scrape_jobs

def scrape_jobspy_jobs():
    jobs = scrape_jobs(
        site_name=["indeed", "linkedin", "glassdoor", "google"],
        search_term="Data Science Intern",
        location="India",
        results_wanted=10,
        hours_old=24,
        country_indeed='India',
    )
    jobs.to_csv("jobs_jobspy.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
