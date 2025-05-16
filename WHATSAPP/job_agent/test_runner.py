from agent import run_agent

if __name__ == "__main__":
    user_input = "Looking for a remote React developer job, $80k+"
    top_jobs = run_agent(user_input)
    for job in top_jobs:
        print(f"{job['match_score']} - {job['title']}\n{job['link']}\n") 