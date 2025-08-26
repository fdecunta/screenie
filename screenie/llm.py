import json
import os
import re
import sys
from typing import Literal

import click
import litellm
from pydantic import BaseModel

# Should move this out
import screenie.db as db

from screenie.config import get_model_config


class LLMResponse(BaseModel):
    """LLM output schema"""
    verdict: Literal[0, 1]
    reason: str


def call_llm(system_prompt, msg):
    # Load config
    usr_config = get_model_config()
 
    messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": msg},
    ]
    
    response = litellm.completion(
            model = usr_config['model'],
            api_key = usr_config['api_key'],
            messages = messages,
            temperature = 0,    # temp = 0 to avoid randomness. but let the user select!
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

    
#def make_suggestion(paper_id: int, criteria_id: int, prompt_id: int, model_id: int):
def make_suggestion(title: str, abstract: int, criteria: str):

    system_prompt = compile_prompt(db_path, persona, instruction, context, data_format)
    msg = f"""
    Title:
    {title}
    
    Abstract:
    {abstract}
    """

    # Call LLM to get suggestion and save the call
    response = call_llm(system_prompt, msg)
    llm_output = parse_llm_response(response)

    # TODO: Validate LLM response
    # If the LLM fails, for example with bad output or timeout, there must be a 
    # way to try again.
    # Maybe add a loop and only break when success


    call_id = db.save_llm_call(
            db_path = db_path,
            prompt = system_prompt,
            response = response,
            criteria_id = criteria_id,
            study_id = study_id
    )


    # Save screening_result
    suggestion_id = db.save_screening_result(
            db_path = db_path,
            criteria_id = criteria_id,
            study_id = study_id,
            call_id = call_id,
            verdict = llm_output.verdict,
            reason = llm_output.reason
    )

