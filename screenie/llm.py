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
    context = {**study, "criteria": recipe.criteria.text}

    prompt_template = Template(recipe.prompt.text)
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

    return response



def extract_json(text: str) -> str:
    """
    Extract the content of the first {...} JSON object in a string.
    Returns the JSON string inside the braces, or raises ValueError if not found.
    """

    pattern = r"\{([\s\S]*?)\}"
    match = re.search(pattern, text)
    
    if not match:
        raise ValueError("No JSON object found")
    
    # Dedent in case the LLM indented the content
    json_str = textwrap.dedent(match.group(0)).strip()  # include the braces
    return json_str



#def extract_json(text: str) -> str:
#    """
#    Extract the content of the first ```json ... ``` block in a string.
#    Returns the JSON string inside the block.
#    """
#    pattern = r"```json\s*([\s\S]*?)```"
#    match = re.search(pattern, text)
#
#    if not match:
#        raise ValueError("No JSON block found")
#
#    json_str = match.group(1).strip()
#    return json_str


def parse_response(response):
    """Parse response from LLM and return it as dict"""
    json_output = extract_json(response.choices[0].message.content)
    parsed_output = LLMResponse.model_validate_json(json_output)

    return parsed_output.model_dump()
