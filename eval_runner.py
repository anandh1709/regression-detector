import json
from classifier import classify_email

def load_golden_dataset(path="data/golden_dataset/golden_dataset_v1.json"):
    with open(path) as f:
        data = json.load(f)
    return data["cases"]

async def run_single_case(case, config):
    result = await classify_email(case["email_text"], config)
    return {
        "id": case["id"],
        "difficulty": case["difficulty"],
        "expected_category": case["category"],
        "expected_summary": case["reference_summary"],
        "actual_category": result.category,
        "actual_summary": result.summary
    }    