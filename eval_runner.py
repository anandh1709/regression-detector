import json

def load_golden_dataset(path="data/golden_dataset/golden_dataset_v1.json"):
    with open(path) as f:
        data = json.load(f)
    return data["cases"]
    