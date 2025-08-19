import bibtexparser
import os
from pydantic import BaseModel
import sqlite3
from typing import Optional, List
import unicodedata

SCREENIE_DB = ""


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


def insert_file(path):
    filename = os.path.basename(path)

    with open(path, "rb") as f:
        file_bytes = f.read()

    con = sqlite3.connect(SCREENIE_DB)
    cur = con.cursor()

    cur.execute("""
    INSERT input_files (name, content)
    VALUES (?, ?)
    """, (filename, file_bytes)
    )

    con.commit()
    con.close()

    print(f"Saved new file {filename}")



def insert_paper(paper):
    con = sqlite3.connect(SCREENIE_DB)
    cur = con.cursor()

    cur.execute("""
    INSERT INTO papers 
    """)




def import_from_bib(path):
    bib_database = read_bib(path)
    papers_list = validate_papers(bib_database.entries)

    insert_file(path)

#    for paper in papers_list:
#        print(paper.title)
#        print()

