import yaml
import json
from models import ClassificationOutput
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found — check your .env file")

client = Groq(api_key=api_key)

def load_prompt_config(path="prompts/classifier.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)

def build_prompt(email_text):
    config = load_prompt_config()
    prompt_template = config["prompt"]
    result = prompt_template.format(email=email_text)
    return result

def classify_email(email_text):
    prompt = build_prompt(email_text)
    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "classification_output",
            "schema": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["Billing", "Technical Issue", "Account/Access", "Feature Request", "Complaint", "Other"]
                    },
                    "summary": {
                        "type": "string"
                    }
                },
                "required": ["category", "summary"]
            }
        }
    }
    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[{"role": "user", "content": prompt}],
        response_format=response_format
    )
    result_dict = json.loads(response.choices[0].message.content)
    validated = ClassificationOutput(**result_dict)
    return validated

result = classify_email("Customer says their invoice is wrong")
print(result)

