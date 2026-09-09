import json
from classifier import classify_email
from classifier import load_prompt_config
import asyncio
from scoring import category_pass_rate, average_latency

def load_golden_dataset(path="data/golden_dataset/golden_dataset_v1.json"):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data["cases"]

semaphore = asyncio.Semaphore(2)

async def run_single_case(case, config):
    async with semaphore:
        result, latency = await classify_email(case["email_text"], config)
        print(f"Done: {case['id']} ({latency:.2f}s)")
        return {
            "id": case["id"],
            "difficulty": case["difficulty"],
            "expected_category": case["category"],
            "expected_summary": case["reference_summary"],
            "actual_category": result.category,
            "actual_summary": result.summary,
            "latency": latency
        }    

async def main():
    data = load_golden_dataset()
    config = load_prompt_config()
    result = await asyncio.gather(*(run_single_case(i, config) for i in data))
    pass_rate = category_pass_rate(result)
    avg_latency = average_latency(result)
    print(f"Average Latency: {avg_latency}s")
    print(f"Category Pass Rate: {pass_rate}%")

asyncio.run(main())