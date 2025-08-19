import bibtexparser
import click
import os
from pydantic import BaseModel
import sqlite3
import sys
from typing import Optional, List
import unicodedata


class Paper(BaseModel):
    """Paper schema matching the database table structure"""
    title: str
    author: str
    year: int
    abstract: str
    url: str
    doi: Optional[str] = None
    source: Optional[str] = None


def read_bib(path):
    """Read bib file"""
    try:
        with open(path, 'r', encoding='utf-8') as bibtex_file:
            parser = bibtexparser.bparser.BibTexParser()
            bib_database = bibtexparser.load(bibtex_file, parser=parser)
        
        for entry in bib_database.entries:
            for key, value in entry.items():
                if isinstance(value, str):
                    entry[key] = unicodedata.normalize('NFKC', value)
        
        return bib_database
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return None


def validate_papers(papers: List[dict]) -> List[Paper]:
    valid_papers = []

    for i, paper_data in enumerate(papers):
        try:
            paper = Paper(**paper_data)
            valid_papers.append(paper)
        except Exception as e:
            print(f"Invalid paper {i}: {e}")

    return valid_papers


def insert_file(db_path, file_path):
    filename = os.path.basename(file_path)

    fmt_filename = click.format_filename(filename)
    fmt_database = click.format_filename(os.path.basename(db_path))

    # read file as bytes
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    # use context manager for connection
    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        try:
            cur.execute("""
                INSERT INTO input_files (name, content)
                VALUES (?, ?)
            """, (filename, file_bytes))
            con.commit()
            click.secho(f"Added {fmt_filename} to {fmt_database}", fg="green")
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


def import_from_bib(db_path: str, file_path: str):
#    bib_database = read_bib(path)
#    papers_list = validate_papers(bib_database.entries)

    insert_file(db_path, file_path)


