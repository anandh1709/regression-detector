import requests
from dotenv import load_dotenv
import os

load_dotenv()

webhook_url = os.getenv("SLACK_WEBHOOK_URL")

if not webhook_url:
    raise ValueError("SLACK_WEBHOOK_URL not found — check your .env file")

def send_slack_alert(run_data, comparison_results, regressions):
    flagged = []
    for r in comparison_results:
        if r["status"] != "fine":
            flagged.append(r)
    if len(flagged) == 0:
         return

    is_critical = False
    for r in flagged:
        if r["status"] == "critical":
            is_critical = True
    if is_critical:
        headline =  f":rotating_light: CRITICAL regression detected (prompt v{run_data['prompt_version']})"
    else:
        headline = f":warning: Warning: metric drift detected (prompt v{run_data['prompt_version']})"

    message = headline + "\n"
    for r in flagged:
        message += f"{r['metric']}: delta {r['delta']} ({r['status']})\n"

    if len(regressions) > 0:
        ids = ", ".join(r["id"] for r in regressions)
        message += f"Regressed cases: {ids}\n" 

    message += "Full report: report.html\n"
    
    response = requests.post(webhook_url, json={"text": message}, timeout= 10)
    response.raise_for_status()