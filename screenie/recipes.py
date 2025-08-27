from string import Template
import tomllib

from pydantic import (
        BaseModel,
        ConfigDict,
        confloat,
        PositiveInt
)


data_format = """
Create a valid JSON output. Follow this schema:
{
    "verdict": "{1 inclusion, 0 not}",
    "reason": "{short explanation supporting the decision}"
}
"""


class Model(BaseModel):
    provider: str | None
    model: str
    temperature: confloat(ge=0, lt=2) = 0    # temp defaults to 0 to reduce randomness
    max_tokens: PositiveInt = 4096    # defaults to a razonable big number


class Prompt(BaseModel):
    text: str


class Criteria(BaseModel):
    text: str


class Recipe(BaseModel):
    model: Model
    prompt: Prompt
    criteria: Criteria

    def substitute(self, study):
        prompt_template = Template(self.prompt.text)
        return prompt_template.substitute(study)



def read_recipe(file: str):
    with open(file, "rb") as f:
        raw_recipe = tomllib.load(f)

    return Recipe(**raw_recipe)

