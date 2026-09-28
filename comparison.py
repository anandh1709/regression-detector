import json

WARNING_THRESHOLD = 5
CRITICAL_THRESHOLD = 10
LATENCY_WARNING_THRESHOLD = 50
LATENCY_CRITICAL_THRESHOLD = 100

METRIC_DIRECTIONS = {
    "category_pass_rate": "lower_is_worse",
    "average_latency": "higher_is_worse",
    "average_tokens": "higher_is_worse",
    "average_judge_score": "lower_is_worse"
}

def compare_runs(new_run, baseline_run):
    results = []
    for metric in METRIC_DIRECTIONS:
        new_value = new_run[metric]
        old_value = baseline_run[metric]
        if metric == "category_pass_rate":
            delta = new_value - old_value
        else:
            delta = (new_value - old_value) / old_value * 100

        direction = METRIC_DIRECTIONS[metric]
        if direction == "lower_is_worse":
            severity = delta * -1
        else:
            severity = delta

        if metric == "average_latency":
            warn, crit = LATENCY_WARNING_THRESHOLD, LATENCY_CRITICAL_THRESHOLD
        else:
            warn, crit = WARNING_THRESHOLD, CRITICAL_THRESHOLD

        if severity >= crit:
            status = "critical"
        elif severity >= warn:
            status = "warning"
        else:
            status = "fine"

        print(f"{metric}: delta = {round(delta, 2)}, severity = {round(severity, 2)}, status = {status}")

        results.append({
            "metric": metric,
            "delta": round(delta, 2),
            "severity": round(severity, 2),
            "status": status
        })

    return results

def find_regressions(new_run, baseline_run):
    if "case_results" not in baseline_run:
        print("Baseline has no case-level data - skipping regression detection.")
        return []
    baseline_by_id = {case["id"]: case for case in baseline_run["case_results"]}

    regressions = []
    for new_case in new_run["case_results"]:
        baseline_case = baseline_by_id[new_case["id"]]
        baseline_passed = baseline_case["actual_category"] == baseline_case["expected_category"]
        new_failed = new_case["actual_category"] != new_case["expected_category"]
        if baseline_passed and new_failed:
            regressions.append({
                "id": new_case["id"],
                "email_expected_category": new_case["expected_category"],
                "baseline_actual_category": baseline_case["actual_category"],
                "new_actual_category": new_case["actual_category"]
            })
    return regressions

def average_runs(runs):
    averaged = {}
    for metric in METRIC_DIRECTIONS:
        total = 0
        for run in runs:
            total += run[metric]
        averaged[metric] = round(total / len(runs), 2)
    return averaged
    
def detect_drift(runs, window=5):
    if len(runs) < 2 * window:
        print("Not enough history")
        return []
    
    recent = average_runs(runs[-window:])
    earlier = average_runs(runs[-2*window:-window])
    return compare_runs(recent, earlier)
    
if __name__ == "__main__":
    with open("data/run_history/run_history.json", encoding="utf-8") as f:
        history = json.load(f)
    runs = history["runs"]
    latest = runs[-1]
    previous = runs[-2]
    compare_runs(latest, previous)
    regression = find_regressions(latest, previous)
    print(regression)
    print(average_runs(runs[-4:]))
    print("Drift check (last 5 runs vs previous 5):")
    drift = detect_drift(runs)