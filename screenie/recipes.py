from strings import Template
import tomllib

from pydantic import BaseModel, HttpUrl


data_format = """
Create a valid JSON output. Follow this schema:
{
    "verdict": "{1 inclusion, 0 not}",
    "reason": "{short explanation supporting the decision}"
}
"""

def expand_prompt(text, study):
    prompt_template = Template(text)
    return prompt_template.substitute(study)
    

class Model(BaseModel):
    model: str
    api_base: HttpUrl
    api_key: str
    max_tokens: int

class Prompt(BaseModel):
    text: str

class Criteria(BaseModel):
    text: str


#class Recipe(BaseModel):
    



def read_recipe(file: str):
    with open(file, "rb") as f:
        raw_recipe = tomllib.load(f)

    return raw_recipe

