def score_match(user_pref, job):
    score = 0
    if user_pref["role"] and user_pref["role"].lower() in job["title"].lower():
        score += 0.4
    if user_pref["job_type"].lower() in job.get("location", "").lower():
        score += 0.2
    if any(tech.lower() in job.get("title", "").lower() + job.get("snippet", "").lower() for tech in user_pref["tech_stack"]):
        score += 0.3
    
    # Handle salary comparison
    job_salary = job.get("salary", "0")
    if isinstance(job_salary, str):
        # Remove any non-numeric characters and convert to int
        job_salary = ''.join(filter(str.isdigit, job_salary))
        job_salary = int(job_salary) if job_salary else 0
    
    if job_salary >= user_pref["salary_min"]:
        score += 0.1
    return round(score, 2)


def match_jobs(user_pref, jobs):
    return sorted([
        {"title": job["title"], "match_score": score_match(user_pref, job), "link": job["link"]}
        for job in jobs
    ], key=lambda x: x["match_score"], reverse=True) 