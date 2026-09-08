import json
from classifier import classify_email
from classifier import load_prompt_config
import asyncio

def load_golden_dataset(path="data/golden_dataset/golden_dataset_v1.json"):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data["cases"]

semaphore = asyncio.Semaphore(2)

async def run_single_case(case, config):
    async with semaphore:
        result = await classify_email(case["email_text"], config)
        return {
            "id": case["id"],
            "difficulty": case["difficulty"],
            "expected_category": case["category"],
            "expected_summary": case["reference_summary"],
            "actual_category": result.category,
            "actual_summary": result.summary
        }    

async def main():
    data = load_golden_dataset()
    config = load_prompt_config()
    result = await asyncio.gather(*(run_single_case(i, config) for i in data))
    print(len(result))
    print(result[5])
asyncio.run(main())