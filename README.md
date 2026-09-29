# Regression Detection System

Automated evaluation and CI/CD pipeline that detects quality regressions in
LLM-powered features before they reach production. Uses a support-email
classifier as the system under test.

## Why this exists

LLM-powered features don't fail like normal software. A prompt change or
model swap can silently degrade output quality (wrong classifications,
vaguer summaries, slower responses) with no crash and no error. This system
catches that class of failure automatically, by running every prompt-touching
PR against a hand-labeled golden dataset and flagging statistically
significant drops against the last known-good baseline.

## Architecture

- `prompts/classifier.yaml`, `prompts/judge.yaml` — versioned prompt configs
- `models.py` — Pydantic output contracts (`ClassificationOutput`, `JudgeOutput`)
- `classifier.py` — the feature under test: loads config, builds prompts,
  calls the LLM, validates output
- `judge.py` — LLM-as-judge scoring of summary quality against the source email
- `data/golden_dataset/` — 60 hand-labeled test cases (6 categories, 3
  difficulty tiers), used as ground truth
- `eval_runner.py` — orchestrates the eval run: async batch execution against
  the golden dataset, rate-limit handling, scoring, comparison, reporting
- `scoring.py` — per-run metrics: category pass rate, latency, token usage,
  judge score
- `comparison.py` — diffs a run against a baseline (per-metric thresholds),
  per-case regression detection, and drift detection (rolling 5-run windows)
- `report.py` — generates a self-contained HTML report per run
- `alerts.py` — Slack webhook alerts on critical/warning status
- `data/run_history/run_history.json` — full history of every run, used as
  the baseline source for comparisons and drift detection

## Setup (local)

```bash
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

Create a `.env` file in the project root:

GROQ_API_KEY=your_key_here
SLACK_WEBHOOK_URL=your_webhook_url_here


## Running an eval

```bash
python eval_runner.py
```

This runs all 60 golden dataset cases through the classifier and judge,
computes four scores, compares against the last saved run, checks for
per-case regressions and 5-run drift, writes `report.html`, sends a Slack
alert if anything is flagged, and appends the result to
`data/run_history/run_history.json`.

Exits with code 1 if any metric hits critical status — this is what blocks
merges in CI.

## Running with Docker

Build the image:

```bash
docker build -t regression-detector .
```

Run an eval, passing secrets in at runtime (never baked into the image):

```bash
docker run --rm \
  -e GROQ_API_KEY=your_key_here \
  -e SLACK_WEBHOOK_URL=your_webhook_url_here \
  -v "$(pwd)/data:/app/data" \
  regression-detector
```

The volume mount for `data/` keeps `run_history.json` and the golden dataset
persisted on the host, so results survive between container runs instead of
disappearing when the container exits. The container itself is disposable,
the run history isn't.

## Scoring dimensions

| Metric | What it measures | Direction |
|---|---|---|
| `category_pass_rate` | Exact-match classification accuracy | lower is worse |
| `average_latency` | API response time | higher is worse |
| `average_tokens` | Completion token usage (cost proxy) | higher is worse |
| `average_judge_score` | LLM-judged summary quality (1-10), scored against the source email, not the reference summary | lower is worse |

Thresholds (warning / critical) were derived from observed run-to-run noise
across ~13 baseline runs on an unchanged prompt, not picked arbitrarily.
Latency gets separate, wider thresholds (50% / 100%) since it showed
significantly higher natural variance than the other three metrics.

## CI/CD

`.github/workflows/eval.yml` runs on any PR touching `/prompts`:

1. Checkout, install Python + dependencies
2. Run the full eval (`GROQ_API_KEY` / `SLACK_WEBHOOK_URL` from repo secrets)
3. Block the merge if any metric is `critical`
4. Commit the updated run history back to the PR branch

## Known limitations

- Per-case regression detection is not filtered for noise, by design. It
  surfaces detail that aggregate thresholds would hide. Some flagged cases
  may be normal LLM non-determinism rather than true regressions.
- Drift detection uses the same thresholds as single-run comparisons.
  5-run averages are less noisy than single runs, so tighter drift-specific
  thresholds would be a reasonable future refinement.
- No trend chart yet, deferred due to insufficient run history for a
  first-version chart to be meaningful.
