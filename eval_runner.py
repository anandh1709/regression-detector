import json
from classifier import classify_email
from classifier import load_prompt_config
import asyncio
from scoring import category_pass_rate, average_latency, average_completion_tokens, average_judge_score
from judge import judge_summary
from datetime import datetime
from comparison import compare_runs, find_regressions, detect_drift
from report import generate_html_report
from alerts import send_slack_alerts
import sys

# Load the golden test cases
def load_golden_dataset(path="data/golden_dataset/golden_dataset_v1.json"):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data["cases"]

# Limit concurrent cases to avoid rate limits
semaphore = asyncio.Semaphore(2)

# Classify one case and judge its summary
async def run_single_case(case, config, judge_config):
    async with semaphore:
        result, latency, completion_tokens = await classify_email(case["email_text"], config)
        score_output = await judge_summary(case["email_text"], result.summary, judge_config)
        return {
            "id": case["id"],
            "difficulty": case["difficulty"],
            "expected_category": case["category"],
            "expected_summary": case["reference_summary"],
            "actual_category": result.category,
            "actual_summary": result.summary,
            "latency": latency,
            "completion_tokens": completion_tokens,
            "judge_score": score_output.score
        }    
    
# Append this run to the history file
def save_run_history(run_data, path="data/run_history/run_history.json"):
    try:
        with open (path, encoding="utf-8") as f:
            history = json.load(f)
    except FileNotFoundError:
        history = {"runs": []}

    history["runs"].append(run_data)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

async def main():
    data = load_golden_dataset()
    config = load_prompt_config()
    judge_config = load_prompt_config(path="prompts/judge.yaml")
    result = await asyncio.gather(*(run_single_case(i, config, judge_config) for i in data))
    pass_rate = category_pass_rate(result)
    avg_latency = average_latency(result)
    avg_tokens = average_completion_tokens(result)
    avg_score = average_judge_score(result)
    print(f"Average Latency: {avg_latency}s")
    print(f"Category Pass Rate: {pass_rate}%")
    print(f"Average Completion Tokens: {avg_tokens}")
    print(f"Average Judge Score: {avg_score}")

    run_data = {
        "timestamp": datetime.now().isoformat(),
        "prompt_version": config["version"],
        "category_pass_rate": pass_rate,
        "average_latency": avg_latency,
        "average_tokens": avg_tokens,
        "average_judge_score": avg_score,
        "case_results": result
    }

    try:
        with open("data/run_history/run_history.json", encoding="utf-8") as f:
            history = json.load(f)
        existing_runs = history["runs"]
    except FileNotFoundError:
        existing_runs = []
    
    has_critical = False

    # Compare against the previous run, if any
    if len(existing_runs) > 0:
        baseline = existing_runs[-1]
        regressions = find_regressions(run_data, baseline)
        if regressions:
            print(f"Found {len(regressions)} regressed case(s):")
            for r in regressions:
                print(r)
        else:
            print("No regressed case found.")
        comparison_results = compare_runs(run_data, baseline)
        
        print("Drift check (last 5 runs vs previous 5):")
        drift_results = detect_drift(existing_runs + [run_data])
        
        generate_html_report(run_data, baseline, comparison_results, regressions, drift_results)
        send_slack_alerts(run_data, comparison_results, regressions, drift_results)
        
        for r in comparison_results:
            if r["status"] == "critical":
                has_critical = True
    else:
        print("No baseline yet — this is the first run.")

    save_run_history(run_data)
    
    # Non-zero exit so CI fails on critical regressions
    if has_critical:
        sys.exit(1)
asyncio.run(main())





