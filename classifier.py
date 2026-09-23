import yaml
import json
from models import ClassificationOutput
from groq import AsyncGroq
from dotenv import load_dotenv
import os
import groq
import asyncio
import time

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found — check your .env file")

client = AsyncGroq(api_key=api_key)

def load_prompt_config(path="prompts/classifier.yaml"):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)

def build_prompt(email_text, config):
    prompt_template = config["prompt"]
    result = prompt_template.format(email=email_text)
    return result

async def classify_email(email_text, config):
    prompt = build_prompt(email_text, config)
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

    for attempt in range(9):
        try:
            start = time.perf_counter()
            response = await asyncio.wait_for(
                client.chat.completions.create(
                model="qwen/qwen3.8-27b",
                messages=[{"role": "user", "content": prompt}],
                response_format=response_format
            ),
            timeout = 30
            )
            end = time.perf_counter()
            latency = end - start
            completion_tokens = response.usage.completion_tokens
            break
        except (groq.RateLimitError, asyncio.TimeoutError, groq.BadRequestError):
            if attempt == 8:
                raise
            wait_time = 2 ** attempt
            await asyncio.sleep(wait_time)
    result_dict = json.loads(response.choices[0].message.content)
    validated = ClassificationOutput(**result_dict)
    return validated, latency, completion_tokens



