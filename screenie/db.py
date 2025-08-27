import importlib.resources
import json
from pathlib import Path 
import sqlite3
import sys

import click
import pandas as pd


class Database():
    def __init__(self, path):
        self.path = path
        self.con = sqlite3.connect(path)


    def init(self):
        """Create database"""
        sql_schema = "schema.sql"
    
        cur = self.con.cursor()
        with importlib.resources.open_text("screenie", sql_schema, encoding="utf-8") as f:
            cur.executescript(f.read())
        self.con.close()

    def commit(self):
        self.con.commit()

    def rollback(self):
        self.con.rollback()

    def close(self):
        self.con.close()
    
    
    def save_file(self, input_file: str) -> int:
        """Save a file as a BLOB in the database and return its ID."""	
        # Read file as bytes to save as BLOB
        f = Path(input_file)

        query = """
        INSERT INTO files (name, content)
        VALUES (?, ?)
        """
        cur = self.con.cursor()
        cur.execute(query, (f.name, f.read_bytes()))
    
        return cur.lastrowid


    def fetch_file_id(self, input_file: str) -> int:
        """Get file_id based on content"""
        f = Path(input_file)

        query = "SELECT file_id FROM files WHERE content = ? "
        cur = self.con.cursor()
        file_id = cur.execute(query, (f.read_bytes(),)).fetchone()[0]
    
        return file_id

       
    def save_studies(self, file_id, studies_list):
        query = """ 
        insert into studies 
        (title, authors, year, abstract, journal, url, doi, file_id)
        values (?, ?, ?, ?, ?, ?, ?, ?)
        """
        cur = self.con.cursor()
        cur.executemany(query, [(i.title, i.authors, i.year, i.abstract, i.journal, i.url, i.doi, file_id) for i in studies_list])


    def fetch_study(self, study_id) -> tuple[str, str]:
        query = """
        SELECT json_object(
            'title', title, 
            'authors', authors,
            'year', year,
            'abstract', abstract,
            'journal', journal,
            'url', url,
            'doi', doi
        ) 
        FROM studies WHERE study_id = ?
        """
        cur = self.con.cursor()
        study = cur.execute(query, (study_id,)).fetchone()[0]

        return json.loads(study)
    

    def save_recipe(self, recipe, file_id) -> int:
        query = "INSERT INTO recipes (content, file_id) VALUES (?, ?)"
        cur = self.con.cursor()
        cur.execute(query, (recipe.model_dump_json(), file_id))

        return cur.lastrowid


    def fetch_recipe_id(self, recipe) -> int:
        query = "SELECT recipe_id FROM recipes WHERE content = ?"
        cur = self.con.cursor()
        recipe_id = cur.execute(query, (recipe.model_dump_json(),)).fetchone()[0]

        return recipe_id

   
    def save_llm_call(self, study_id, recipe_id, response):
        response_data = response.json()
        
        model = response_data['model']
        input_tokens = response_data['usage']['prompt_tokens']
        output_tokens = response_data['usage']['completion_tokens']
        full_response = json.dumps(response_data)
    
        query = """
        INSERT INTO llm_calls
        (recipe_id, input_tokens, output_tokens, study_id, full_response)
        VALUES (?, ?, ?, ?, ?)
        """

        cur = self.con.cursor()
        cur.execute(query, (recipe_id, input_tokens, output_tokens, study_id, full_response))
    
        return cur.lastrowid   
    
    
    def save_result(self, recipe_id, study_id, call_id, verdict, reason):
        query = """
        INSERT INTO results
        (recipe_id, study_id, call_id, verdict, reason)
        VALUES (?, ?, ?, ?, ?)
        """
        cur = self.con.cursor()
        cur.execute(query, (recipe_id, study_id, call_id, verdict, reason))
        
        return cur.lastrowid
    
    
    def export_results(self, output_format: str, output_file: str):
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
        FROM studies AS st
        LEFT JOIN results AS r
        ON st.study_id = r.study_id
        """
    
        df = pd.read_sql_query(query, self.con)
    
        fmt = output_format.lower()
        if fmt == "csv":
            df.to_csv(output_file, index=False)
        elif fmt in {"xlsx", "excel"}:
            df.to_excel(output_file, index=False, engine="openpyxl")
        else:
            raise ValueError(f"Unsupported format: {output_format}")
    
    
    def fetch_pending_studies_ids(self, recipe_id, limit: int) -> list[int]:
        """Fetch a group of study IDs that haven't been screened yet with some recipe."""
        query = """
        SELECT s.study_id
        FROM studies s
        WHERE NOT EXISTS (
            SELECT 1 FROM results r 
            WHERE r.study_id = s.study_id AND r.recipe_id = ?
        )
        ORDER BY s.study_id
        LIMIT ?
        """

        cur = self.con.cursor()
        res = cur.execute(query, (recipe_id, limit,))

        return [row[0] for row in res.fetchall()]
    
