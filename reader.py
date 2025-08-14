import bibtexparser

with open('./scopus.bib', 'r', encoding='utf-8') as bibtex_file:
    parser = bibtexparser.bparser.BibTexParser()
    bib_database = bibtexparser.load(bibtex_file, parser=parser)

for entry in bib_database.entries:
    print(entry["title"])

