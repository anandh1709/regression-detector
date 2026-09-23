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

if __name__ == "__main__":
    with open("data/run_history/run_history.json", encoding="utf-8") as f:
        history = json.load(f)
    runs = history["runs"]
    latest = runs[-1]
    previous = runs[-2]
    compare_runs(latest, previous)