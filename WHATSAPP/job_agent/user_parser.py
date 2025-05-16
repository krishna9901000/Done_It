import re

def parse_user_input(user_input):
    # Simple regex-based parser (can be replaced with LLM later)
    role = re.search(r"(?i)(developer|engineer|designer|manager)", user_input)
    tech = re.findall(r"(?i)(React|Node|JavaScript|Python|Java|Django|Flask|Angular)", user_input)
    remote = "remote" in user_input.lower()
    salary = re.search(r"\$?(\d{2,6})[kK]?", user_input)

    return {
        "role": role.group(0) if role else None,
        "tech_stack": list(set(tech)),
        "job_type": "Remote" if remote else "On-site",
        "salary_min": int(salary.group(1)) * 1000 if salary else 0
    } 