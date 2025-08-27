from pathlib import Path
import sys
from typing import Optional, List
import unicodedata

import bibtexparser
import click
from pydantic import BaseModel
import rispy


class Study(BaseModel):
    """Study schema matching the database table structure"""
    title: str
    authors: str
    year: int
    abstract: str
    journal: str
    url: str
    doi: Optional[str] = None


def clean_strings(entry: dict) -> None:
    """Normalize all string values in-place. This helps with difficult chars and symbols"""
    for key in entry:
        value = entry[key]
        if isinstance(value, str):
            entry[key] = unicodedata.normalize("NFKC", value)


def normalize_field_name(raw_name: str) -> str:
    """Convert field name to the expected name by Study class"""
    field_mappings = {
        'authors': ['author', 'authors', 'first_authors'],
        'title': ['title', 'article_title', 'primary_title'],
        'year': ['year', 'publication_year', 'pub_year'],
        'abstract': ['abstract', 'summary'],
        'journal': ['journal', 'journal_name'],
        'doi': ['doi'],
        'url': ['url', 'link', 'urls']
    }

    for canonical_field, possible_names in field_mappings.items():
        if raw_name.lower() in possible_names:
            return canonical_field

    # If don't match return the raw_name
    return raw_name
    

def normalize_entry(entry: dict) -> dict:
    """Convert various field names to their canonical format"""
    normalized_entry = {}
    for old_name in entry.keys():
        new_name = normalize_field_name(old_name)
        normalized_entry[new_name] = entry[old_name]

    return normalized_entry


def validate_studies(studies: List[dict]) -> List[Study]:
    valid_studies = []
    errors = []

    # TODO: Write useful messages about what fails.
    # Also, what to do when an entry fails? How to retry?

    for i, study_data in enumerate(studies):
        try:
            normalized_study = normalize_entry(study_data)
            study = Study(**normalized_study)
            valid_studies.append(study)
        except Exception as e:
            click.echo(f"{e}")
            errors.append(e)

    return valid_studies, errors


def read_bib(file_path):
    """Read data from .bib file"""
    with open(file_path, 'r', encoding='utf-8') as bibtex_file:
        parser = bibtexparser.bparser.BibTexParser()
        bib_database = bibtexparser.load(bibtex_file, parser=parser)
    
    for entry in bib_database.entries:
        clean_strings(entry)

    return bib_database.entries


def read_ris(input_file: str):
    """Read data from .ris file"""
    with open(input_file, "r", encoding="utf-8") as f:
        ris_data = rispy.load(f)
        for entry in ris_data:
            # Two problems with rispy outputs:
            # - Authors is a list of strings. Must be one string
            # - URLs is a list uf urls. But only one needed.
            entry['authors'] = "; ".join(entry['authors'])
            entry['url'] = entry['urls'][0]
            clean_strings(entry)

    return ris_data


def import_studies(input_file: str) -> List[Study]:
    """Import bibliography data from a file into the database.
 
    Automatically detects the file format based on extension and uses
    the appropriate import function. 

    For the moment, it only supports BibTeX and RIS formats.
    """
    file_path = Path(input_file)
    extension = file_path.suffix.lower()

    if extension == ".bib":
        imported_data = read_bib(input_file)
    elif extension == ".ris":
        imported_data = read_ris(input_file)
    else:
        raise ValueError(f"Unsupported file format '{extension}' \nOnly .bib and .ris files are supported")

    return validate_studies(imported_data)
