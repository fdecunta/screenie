from string import Template
from typing import Optional, Union
import tomllib

from pydantic import BaseModel

class Model(BaseModel):
    model: str
    timeout: Optional[Union[float, int]] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    n: Optional[int] = None
    max_tokens: Optional[int] = None
    seed: Optional[int] = None
    deployment_id: Optional[str] = None
    base_url: Optional[str] = None
    api_version: Optional[str] = None


class Prompt(BaseModel):
    text: str


class Criteria(BaseModel):
    text: str


class Recipe(BaseModel):
    model: Model
    prompt: Prompt
    criteria: Criteria


def read_recipe(file: str):
    with open(file, "rb") as f:
        raw_recipe = tomllib.load(f)

    return Recipe(**raw_recipe)

