import importlib.resources
import json
import os
import sqlite3
import sys

import click
import pandas as pd


def init_db(db_name: str):
    """Create database"""
    sql_schema = "schema.sql"

    with sqlite3.connect(db_name) as con:
        cur = con.cursor()
        with importlib.resources.open_text("screenie", sql_schema, encoding="utf-8") as f:
            cur.executescript(f.read())


def insert_file(db_path: str, input_file: str):
    filename = os.path.basename(input_file)

    # Read file as bytes to save as BLOB
    with open(input_file, "rb") as f:
        file_bytes = f.read()

    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        cur.execute("""
            INSERT INTO input_files (name, content)
            VALUES (?, ?)
        """, (filename, file_bytes))

    file_id = cur.execute("SELECT file_id FROM input_files WHERE name = ?", (filename,)).fetchone()[0]

    return file_id


def insert_studies(db_path, file_id, studies_list):
    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        cur.executemany("""
        INSERT INTO studies 
        (title, authors, year, abstract, journal, url, doi, file_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [(i.title, i.authors, i.year, i.abstract, i.journal, i.url, i.doi, file_id) for i in studies_list])


def fetch_study(db_path, study_id) -> tuple[str, str]:
    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        study = cur.execute("""
        SELECT title, abstract
        FROM studies
        WHERE study_id = ?
        """, (study_id,)
        ).fetchone()

    return study


def save_criteria(db_path, text) -> str:
    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        cur.execute("INSERT INTO criteria (text) VALUES (?)", (text,))

    return text


def fetch_criteria(db_path: str) -> tuple[int, str]:
    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        result = cur.execute("""
        SELECT criteria_id, text FROM criteria
        WHERE created_at = (SELECT MAX(created_at) FROM criteria)
        """).fetchone()

        if result is None:
            raise ValueError("No criteria found. Please define criteria first.")

        return result


def read_last_criteria(db_path: str) -> str:
    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        result = cur.execute("""
        SELECT text FROM criteria
        WHERE created_at = (SELECT MAX(created_at) FROM criteria)
        """).fetchone()

        if result is None:
            text = ""
        else:
            text = result[0]
    return(text)


# --- llm_calls table

def save_llm_call(db_path, prompt, response, criteria_id, study_id):
    """
    Save LLM API call details to the database.
    
    Args:
        db_path (str): Database file path
        prompt (str): Prompt sent to LLM
        response: LLM API response object
        criteria_id (int): Criteria ID
        study_id (int): Paper ID
        
    Returns:
        int: ID of the inserted record
    """
    response_data = response.json()
    
    model = response_data['model']
    input_tokens = response_data['usage']['prompt_tokens']
    output_tokens = response_data['usage']['completion_tokens']
    full_response = json.dumps(response_data)

    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        cur.execute("""
        INSERT INTO llm_calls
        (model, prompt, input_tokens, output_tokens, criteria_id, study_id, full_response)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (model, prompt, input_tokens, output_tokens, criteria_id, study_id, full_response)
        )

        return cur.lastrowid   

# --- screening_results table

def save_screening_result(db_path, criteria_id, study_id, call_id, verdict, reason, human_validated):
    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        cur.execute("""
        INSERT INTO screening_results
        (criteria_id, study_id, call_id, verdict, reason, human_validated)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (criteria_id, study_id, call_id, verdict, reason, human_validated)
        )

        return cur.lastrowid


def export_screening_results(db_path: str, output_format: str, output_file: str):
    """Export all the studies and what the LLM output"""

    query = """
    SELECT 
        st.study_id,
        st.title,
        st.authors,
        st.year,
        st.journal,
        st.abstract,
        st.url,
        st.doi,
        r.verdict,
        r.reason,
        r.human_validated
    FROM studies AS st
    LEFT JOIN screening_results AS r
    ON st.study_id = r.study_id
    """

    with sqlite3.connect(db_path) as con:
        df = pd.read_sql_query(query, con)

    fmt = output_format.lower()
    if fmt == "csv":
        df.to_csv(output_file, index=False)
    elif fmt in {"xlsx", "excel"}:
        df.to_excel(output_file, index=False, engine="openpyxl")
    else:
        raise ValueError(f"Unsupported format: {output_format}")


def fetch_pending_studies_ids(db_path: str, batch_size: int) -> list[int]:
    """Fetch a batch of study IDs that haven't been screened yet."""

    query = """\
    SELECT study_id
    FROM studies
    WHERE study_id NOT IN (SELECT study_id FROM screening_results)
    ORDER BY study_id
    LIMIT ?
    """
    with sqlite3.connect(db_path) as con:
       cur = con.cursor()
       res = cur.execute(query, (batch_size,))
       studies_ids = [row[0] for row in res.fetchall()]

    return studies_ids

