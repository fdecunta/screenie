import click
import json
import os
import sqlite3
import sys

def init_db(db_name: str, sql_file="schema.sql"):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    with open(sql_file, "r", encoding="utf-8") as f:
        cur.executescript(f.read())
    conn.commit()

    # Test if it was created ok
    try:
        cur.execute("SELECT * FROM input_files;")
        _ = cur.fetchone()
        success = True
    except sqlite3.OperationalError:
        success = False

    conn.close()

    return success

# --- input_files table

def insert_file(db_path: str, file_path: str):
    filename = os.path.basename(file_path)

    fmt_filename = click.format_filename(filename)
    fmt_database = click.format_filename(os.path.basename(db_path))

    # read file as bytes to save as BLOB
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        try:
            cur.execute("""
                INSERT INTO input_files (name, content)
                VALUES (?, ?)
            """, (filename, file_bytes))
            con.commit()
#            click.secho(f"Added {fmt_filename} to {fmt_database}", fg="green")
        except sqlite3.IntegrityError as e:
            msg = str(e)
            if "UNIQUE constraint" in msg:
                click.secho(f"File {fmt_filename} already exists in the database.", fg="red", err=True)
            else:
                click.secho(f"Failed to import {fmt_filename}: {msg}", fg="red", err=True)
            sys.exit(1)
        except sqlite3.DatabaseError as e:
            click.secho(f"Database error: {e}", fg="red", err=True)
            sys.exit(1)

        file_id = cur.execute("SELECT file_id FROM input_files WHERE name = ?", (filename,)).fetchone()[0]

    return file_id


# --- papers table

def insert_papers(db_path, file_id, papers_list):
    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        cur.executemany("""
        INSERT INTO papers 
        (title, authors, year, abstract, url, doi, file_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [(p.title, p.authors, p.year, p.abstract, p.url, p.doi, file_id) for p in papers_list]
        )


def retrieve_paper(db_path, paper_id):
    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        res = cur.execute("""
        SELECT paper_id, title, authors, abstract
        FROM papers
        WHERE paper_id = ?
        """, (paper_id,)
        ).fetchone()

    return res

# --- criteria table

def save_criteria(db_path, text):
    with sqlite3.connect(db_path) as con:
        try:
            cur = con.cursor()
            cur.execute("INSERT INTO criteria (text) VALUES (?)", (text,))
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                return None

        except sqlite3.Error as e:
            print("Insert criteria failed:", e)
            sys.exit(1)


def read_last_criteria(db_path: str) -> str:
    with sqlite3.connect(db_path) as con:
        try:
            cur = con.cursor()
            result = cur.execute("""
            SELECT text FROM criteria
            WHERE created_at = (SELECT MAX(created_at) FROM criteria)
            """).fetchone()

            if result is None:
                text = ""
            else:
                text = result[0]
        except sqlite3.Error as e:
            print("Failed to read last criteria:", e)
            sys.exit(1)
    return(text)


# --- llm_calls table

def save_llm_call(db_path, prompt, response, criteria_id, paper_id):
    """
    Save LLM API call details to the database.
    
    Args:
        db_path (str): Database file path
        prompt (str): Prompt sent to LLM
        response: LLM API response object
        criteria_id (int): Criteria ID
        paper_id (int): Paper ID
        
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
        (model, prompt, input_tokens, output_tokens, criteria_id, paper_id, full_response)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (model, prompt, input_tokens, output_tokens, criteria_id, paper_id, full_response)
        )

        return cur.lastrowid   


# --- screening_results table

def save_screening_result(db_path, criteria_id, paper_id, call_id, verdict, reason, human_validated):
    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        cur.execute("""
        INSERT INTO screening_results
        (criteria_id, paper_id, call_id, verdict, reason, human_validated)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (criteria_id, paper_id, call_id, verdict, reason, human_validated)
        )

        return cur.lastrowid

