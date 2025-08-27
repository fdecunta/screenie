import json
import re
from typing import Literal

import litellm
from pydantic import BaseModel

from screenie.config import get_model_config


class LLMResponse(BaseModel):
    """LLM output schema"""
    verdict: Literal[0, 1]
    reason: str


class LLM():
    def __init__(self, recipe):
        


def call_llm(system_prompt, msg):
    usr_config = get_model_config()
 
    messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": msg},
    ]
    
    response = litellm.completion(
            model = usr_config['model'],
            api_key = usr_config['api_key'],
            messages = messages,
            temperature = 0,    
    )
    return response


def extract_json_block(text: str) -> str:
    """
    Extract the content of the first ```json ... ``` block in a string.
    Returns the JSON string inside the block, or None if not found.
    """
    pattern = r"```json\s*([\s\S]*?)```"
    match = re.search(pattern, text)

    if not match:
        raise ValueError("No JSON block found")

    json_str = match.group(1).strip()
    return json_str


def parse_llm_response(response):
    """Parse response from LLM"""
    json_output = extract_json_block(response.choices[0].message.content)
    parsed_output = LLMResponse.model_validate_json(json_output)

    return parsed_output
