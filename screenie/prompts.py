
import screenie.db as db


persona = "You are an assistant of an ecology researcher that is conducting the initial screening of studies for a meta-analysis.\n"
instruction = "Recommend inclusion or not of a scientific study and explain your decision.\n"
context = "You will be given criteria for inclusion. The user will give you the study's title and abstract.\n"
data_format = """
Create a valid JSON output. Follow this schema:
{
    "verdict": "{1 inclusion, 0 not}",
    "reason": "{short explanation supporting the decision}"
}
"""


def compile_prompt(db_path: str, persona: str, instruction: str, context: str, data_format: str) -> str:

    user_criteria = db.read_last_criteria(db_path=db_path)
    if len(user_criteria) == 0:
        raise ValueError("No criteria defined")

    criteria = "\nThis is the criteria:\n" + user_criteria + "\n"

    system_prompt = persona + instruction + context + data_format + criteria
    return system_prompt


