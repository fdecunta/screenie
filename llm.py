import click
import json
import litellm
import os
import re

import config
import db
import screenie_printer



persona = "You are an assistant of an ecology researcher that is conducting the initial screening of papers for a meta-analysis.\n"
instruction = "Recommend inclusion or not of a scientific paper and give a one-sentence explanation of your decision.\n"
context = "You will be given criteria for inclusion. The user will give you the paper's title and abstract.\n"
data_format = """
Create a valid JSON output. Follow this schema:
{
    "verdict": "{1 inclusion, 0 not}",
    "reason": "{one-sentence explanation of your decision}"
}
"""

# -----------------------

criteria = """
This is the criteria:

1. The study has experimental data about how to use LLMs for ecology research.
2. The study compares LLMs vs humans.
\n
"""

system_prompt = persona + instruction + context + data_format + criteria


# -----------------------

def call_llm(system_prompt, msg):
    # Load config
    usr_config = config.get_provider_config()
 
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


def extract_json_block(text: str) -> str | None:
    """
    Extract the content of the first ```json ... ``` block in a string.
    
    Args:
        text: The text containing the JSON code block.
    
    Returns:
        The JSON string inside the block, or None if not found.
    """
    pattern = r"```json\s*([\s\S]*?)```"

    match = re.search(pattern, text)
    if match:
        json_str = match.group(1).strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None
    return None



def get_suggestion(db_path: str, criteria_id: int, paper_id: int):
    paper_id, title, authors, abstract = db.retrieve_paper(db_path=db_path, paper_id=paper_id)

    screenie_printer.print_paper(title, authors, abstract)

    msg = f"""
    Title:
    {title}
    
    Abstract:
    {abstract}
    """

    # Call LLM to get suggestion and save the call
    response = call_llm(system_prompt, msg)

    call_id = db.save_llm_call(
            db_path = db_path,
            prompt = system_prompt,
            response = response,
            criteria_id = criteria_id,
            paper_id = paper_id
    )

    # TODO: Validate LLM response
    #
    # If the LLM fails, for example with bad output or timeout, there must be a 
    # way to try again.
    # Maybe add a loop and only 
    #


    # Parse LLM response
    json_output = extract_json_block(response.choices[0].message.content)
    verdict = json_output['verdict']
    reason = json_output['reason']

    # Save screening_result
    suggestion_id = db.save_screening_result(
            db_path = db_path,
            criteria_id = criteria_id,
            paper_id = paper_id,
            call_id = call_id,
            verdict = verdict,
            reason = reason,
            human_validated = 0
    )

    screenie_printer.print_llm_suggestion(verdict, reason)
