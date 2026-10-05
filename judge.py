from classifier import load_prompt_config, client
import asyncio
import groq
import json
from models import JudgeOutput

# Fill the email and summary into the judge prompt
def build_judge_prompt(email_text, summary_text, config):
    prompt_template = config["prompt"]
    result = prompt_template.format(email=email_text, summary=summary_text)
    return result

# Score a summary (1-10) using an LLM judge
async def judge_summary(email_text, summary_text, config):
    prompt = build_judge_prompt(email_text, summary_text, config)
    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "judge_output",
            "schema": {
                "type": "object",
                "properties": {
                    "score": {
                        "type": "integer"
                    }
                },
                "required": ["score"]
            }
        }
    }

    # Retry with exponential backoff
    for attempt in range(9):
        try:
            response = await asyncio.wait_for(
                client.chat.completions.create(
                model="qwen/qwen3.8-27b",
                messages=[{"role": "user", "content": prompt}],
                response_format=response_format
            ),
            timeout = 30
            )
            break
        except (groq.RateLimitError, asyncio.TimeoutError, groq.BadRequestError):
            if attempt == 8:
                raise
            wait_time = 2 ** attempt
            await asyncio.sleep(wait_time)
    result_dict = json.loads(response.choices[0].message.content)
    validated = JudgeOutput(**result_dict)
    return validated
