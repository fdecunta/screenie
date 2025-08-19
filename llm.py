from dotenv import load_dotenv
import litellm
import os

load_dotenv()

LLM_MODEL="gradient_ai/llama3.3-70b-instruct"
#LLM_MODEL="gradient_ai/deepseek-r1-distill-llama-70b"

API_KEY=os.environ["DIGITALOCEAN_INFERENCE_KEY"]


persona = "You are an assistant of an ecology researcher that is conducting the initial screening of papers for a meta-analysis.\n"

instruction = "Recommend inclusion or not of a scientific paper and give a one-sentence explanation of your decision.\n"

context = "You will be given criteria for inclusion. The user will give you the paper's title and abstract.\n"

data_format = """
Create a JSON output using this schema:
{
    "verdict": {1 or 0: 1 for inclusion, 0 if not},
    "reason": {one-sentence explanation of your decision}

}
"""


import sqlite3

conn = sqlite3.connect("MA_llm.db")
cur = conn.cursor()

cur.execute("""SELECT title, abstract FROM papers LIMIT 1;""")
title, abstract = cur.fetchone()
conn.close()


msg = f"""
Title:
{title}

Abstract:
{abstract}
"""


# -----------------------


criteria = """
This is the criteria:

1. The study has experimental data about Epichloë endophytes and herbivory.
2. The study includes a factorial experiment with four treatments (endophytes x herbivory)
\n
"""


criteria2 = """
This is the criteria:

1. The study has experimental data about how to use LLMs for ecology research.
2. The study compares LLMs vs humans.
\n
"""



system_prompt = persona + instruction + context + data_format + criteria2


# -----------------------

def make_recommendation(system_prompt, msg):
    messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": msg},
    ]
    
    
    response = litellm.completion(
            model=LLM_MODEL,
            api_key=API_KEY,
            messages=messages,
            temperature=0,
    )

    return response
#    return response.choices[0].message.content



paper_id = 1
criteria_id = 1

response = make_recommendation(system_prompt, msg)

db_path = "MA_llm.db"

import db

try:
    db.save_llm_call(db_path=db_path, prompt=system_prompt, response=response, criteria_id=1, paper_id=1)
except Exception as e:
    print(e)

print(response.choices[0].message.content)
