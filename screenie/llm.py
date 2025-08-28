import json
import re
from string import Template
import textwrap
from typing import Literal

import litellm
from pydantic import BaseModel, field_validator


class LLMResponse(BaseModel):
    """LLM output schema"""
    verdict: Literal[0, 1]
    reason: str

    @field_validator("verdict", mode="before")
    def coerce_verdict(cls, verdict):
        if isinstance(verdict, str) and verdict in ("0", "1"):
            return int(verdict)
        return verdict


def compile_prompt(recipe, study):
    """
    Compile a prompt for a study using a recipe.
    - Inserts study fields and criteria into the template.
    - Appends JSON output instructions.
    """

    # Merge study info with criteria
    context = {**study, "criteria": recipe.criteria}

    prompt_template = Template(recipe.prompt)
    filled_prompt = prompt_template.substitute(context)

    data_format = """\nCreate a valid JSON output. Follow this schema:
```json
{
    "verdict": "{1 inclusion, 0 not}",
    "reason": "{explanation supporting the decision}"
}
```
"""

    return filled_prompt + data_format


def call_llm(recipe, study):
    msg = compile_prompt(recipe, study)
    usr_config = recipe.model.model_dump()
    
    response = litellm.completion(
        messages = [{"role": "user", "content": msg}],
        **usr_config  
    )

    return response.model_dump()


def extract_json(text: str) -> str:
    """
    Extract the content of the first {...} JSON object in a string.
    Returns the JSON string inside the braces, or raises ValueError if not found.
    """
    pattern = r"\{[^{}]*\}"
    match = re.search(pattern, text)
    
    if not match:
        raise ValueError("No JSON object found")
    
    # Parse and de-parse to ensure is a valida JSON
    json_str = json.loads(match.group(0))
    return json.dumps(json_str)


def parse_response(response):
    """Parse response from LLM and return it as dict"""
    json_output = extract_json(response['choices'][0]['message']['content'])
    parsed_output = LLMResponse.model_validate_json(json_output)

    return parsed_output.model_dump()
