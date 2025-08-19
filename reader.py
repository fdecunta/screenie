import bibtexparser
import click
import os
from pydantic import BaseModel
import sqlite3
import sys
from typing import Optional, List
import unicodedata
import db


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



def import_from_bib(db_path: str, file_path: str):
#    bib_database = read_bib(path)
#    papers_list = validate_papers(bib_database.entries)

    db.insert_file(db_path, file_path)


