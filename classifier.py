import yaml

def load_prompt_config(path="prompts/classifier.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)

def build_prompt(email_text):
    config = load_prompt_config()
    prompt_template = config["prompt"]
    result = prompt_template.format(email=email_text)
    return result

print(build_prompt("Customer says their invoice is wrong"))
