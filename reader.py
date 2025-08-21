import bibtexparser
import click
import os
from pathlib import Path
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
    journal: str
    url: str
    doi: Optional[str] = None


def normalize_entry_names(entry: dict) -> dict:
    """Convert various field names to canonical format"""
    field_mappings = {
        'authors': ['author', 'authors', 'first_authors'],
        'title': ['title', 'article_title', 'primary_title'],
        'year': ['year', 'publication_year', 'pub_year'],
        'abstract': ['abstract', 'summary'],
        'journal': ['journal', 'journal_name'],
        'doi': ['doi', 'DOI'],
        'url': ['url', 'link', 'urls']
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


def validate_studies(studies: List[dict]) -> List[Paper]:
    valid_studies = []
    errors = []

    for i, study_data in enumerate(studies):
        try:
            normalized_study = normalize_entry_names(study_data)
            study = Paper(**normalized_study)
            valid_studies.append(study)
        except Exception as e:
            click.echo(f"{e}")
            errors.append(e)

    return valid_studies, errors


# BIB format
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


def import_from_bib(db_path: str, input_file: str):
    try:
        bib_database = read_bib(input_file)
        click.secho(f"Found {len(bib_database.entries)} entries")
    except Exception as e:
        click.secho(f"Error reading file: {e}", fg="red")
        return

    studies_list, errors = validate_studies(bib_database.entries)

    if studies_list:
        click.secho(f"Valid studies: {len(studies_list)}", fg="green")
    if errors:
        click.secho(f"Invalid studies: {len(errors)}", fg="red")

    # TODO: 
    # Better open the connection with the DB here and close only if all goes ok

    file_id = db.insert_file(db_path, input_file)
    imported_count = db.insert_studies(db_path, file_id, studies_list)


# RIS format
def read_ris(input_file: str):
    import rispy

    with open(input_file, "r", encoding="utf-8") as f:
        entries = rispy.load(f)

    return entries


def import_from_ris(db_path: str, input_file: str):
    read_ris(input_file)
    # TODO 
    print("FAIL!")
    sys.exit(1)


def import_studies(db_path: str, input_file: str):
    """Import bibliography data from a file into the database.
 
    Automatically detects the file format based on extension and uses
    the appropriate import function. Supports BibTeX (.bib) and RIS (.ris) formats.
 
    Args:
        db_path: Path to the SQLite database file
        input_file: Path to the bibliography file to import
 
    Raises:
        SystemExit: If the file format is not supported
    """
    file_path = Path(input_file)
    extension = file_path.suffix.lower()

    if extension == ".bib":
        import_from_bib(db_path=db_path, input_file=input_file)
    elif extension == ".ris":
        import_from_ris(db_path=db_path, input_file=input_file)
    else:
        click.secho(
            f"Error: Unsupported file format '{extension}'. "
            f"Only .bib and .ris files are supported.\\n"
            f"File: {input_file}", 
            err=True, 
            fg="red"
        )
        sys.exit(1)
    click.secho(f"Done!")
    return 
