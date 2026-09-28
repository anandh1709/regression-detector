import requests
from dotenv import load_dotenv
import os

load_dotenv()

webhook_url = os.getenv("SLACK_WEBHOOK_URL")

if not webhook_url:
    raise ValueError("SLACK_WEBHOOK_URL not found — check your .env file")

def get_flagged(results):
    flagged = []
    for r in results:
        if r["status"] != "fine":
            flagged.append(r)
    return flagged

def post_to_slack(message):
    response = requests.post(webhook_url, json={"text": message}, timeout=10)
    response.raise_for_status()

def send_slack_alerts(run_data, comparison_results, regressions, drift_results):
    flagged = get_flagged(comparison_results)
    if flagged:
        is_critical = False
        for r in flagged:
            if r["status"] == "critical":
                is_critical = True
        if is_critical:
            headline = f":rotating_light: CRITICAL regression detected (prompt v{run_data['prompt_version']})"
        else:
            headline = f":warning: Warning: metric change detected (prompt v{run_data['prompt_version']})"

        message = headline + "\n"
        for r in flagged:
            message += f"{r['metric']}: delta {r['delta']} ({r['status']})\n"
        if len(regressions) > 0:
            ids = ", ".join(r["id"] for r in regressions)
            message += f"Regressed cases: {ids}\n"
        message += "Full report: report.html\n"
        post_to_slack(message)

    drift_flagged = get_flagged(drift_results)
    if drift_flagged:
        message = f":chart_with_downwards_trend: Slow drift detected (last 5 runs vs previous 5, prompt v{run_data['prompt_version']})\n"
        for r in drift_flagged:
            message += f"{r['metric']}: delta {r['delta']} ({r['status']})\n"
        message += "Full report: report.html\n"
        post_to_slack(message)

if __name__ == "__main__":
    fake_run = {"prompt_version": 1}
    fake_comparison = [
        {"metric": "category_pass_rate", "delta": 1.0, "severity": -1.0, "status": "fine"},
        {"metric": "average_latency", "delta": 5.0, "severity": 5.0, "status": "critical"},
    ]
    fake_regressions = []
    fake_drift = [
        {"metric": "category_pass_rate", "delta": -7.0, "severity": 7.0, "status": "warning"},
        {"metric": "average_tokens", "delta": 1.0, "severity": 1.0, "status": "fine"},
    ]
    send_slack_alerts(fake_run, fake_comparison, fake_regressions, fake_drift)