import bibtexparser
import click
import os
from pydantic import BaseModel
import sys
from typing import Optional, List
import unicodedata

import db


class Paper(BaseModel):
    """Paper schema matching the database table structure"""
    title: str
    authors: str
    year: int
    abstract: str
    url: str
    doi: Optional[str] = None


def normalize_entry_names(entry: dict) -> dict:
    """Convert various field names to canonical format"""
    field_mappings = {
        'authors': ['author', 'authors', 'author_name', 'authors_names'],
        'title': ['title', 'booktitle', 'article_title'],
        'year': ['year', 'date', 'publication_year', 'pub_year'],
        'abstract': ['abstract', 'summary', 'description'],
        'doi': ['doi', 'DOI'],
        'url': ['url', 'link']
    }
    
    normalized = {}
    for canonical_field, possible_names in field_mappings.items():
        for field_name in possible_names:
            if field_name in entry:
                normalized[canonical_field] = entry[field_name]
                break
        else:
            normalized[canonical_field] = None  
    
    return normalized


def read_bib(file_path):
    """Read bib file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as bibtex_file:
            parser = bibtexparser.bparser.BibTexParser()
            bib_database = bibtexparser.load(bibtex_file, parser=parser)
        
        for entry in bib_database.entries:
            for key, value in entry.items():
                if isinstance(value, str):
                    entry[key] = unicodedata.normalize('NFKC', value)
        
        return bib_database
    except Exception as e:
        click.secho(f"Error reading {file_path}: {e}", err=True, fg="red")
        return None


def validate_papers(papers: List[dict]) -> List[Paper]:
    valid_papers = []
    errors = []

    for i, paper_data in enumerate(papers):
        try:
            normalized_paper = normalize_entry_names(paper_data)
            paper = Paper(**normalized_paper)
            valid_papers.append(paper)
        except Exception as e:
            click.echo(f"{e}")
            errors.append(e)

    return valid_papers, errors



def import_from_bib(db_path: str, file_path: str):
    # Read bib file
    click.echo(f"Reading bibliography from: {click.format_filename(file_path)}...")
    try:
        bib_database = read_bib(file_path)
        click.secho(f"Found {len(bib_database.entries)} entries")
    except Exception as e:
        click.secho(f"Error reading file: {e}", fg="red")
        return

    papers_list, errors = validate_papers(bib_database.entries)

    if papers_list:
        click.secho(f"✓ Valid papers: {len(papers_list)}", fg="green")
    if errors:
        click.secho(f"✗ Invalid papers: {len(errors)}", fg="red")


    # Insert files into database
    file_id = db.insert_file(db_path, file_path)

    # Insert papers into database
    imported_count = db.insert_papers(db_path, file_id, papers_list)
    click.secho(f"Done!")

