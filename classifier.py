import yaml

def load_prompt_config(path="prompts/classifier.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)
    
config = load_prompt_config()
print(config)