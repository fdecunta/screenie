import tempfile
import os
import unittest

from screenie.reader import (
    clean_strings,
    normalize_field_name,
    normalize_entry,
    read_bib
)


class TestNormalizeStrings(unittest.TestCase):

    def test_normalizes_unicode(self):
        entry = {
            "title": "Ｔｅｓｔ", # fullwidth characters
            "author": "José",    # accented character
            "year": 2024         # non-string, should do nothing here
        }

        clean_strings(entry)

        self.assertEqual(entry["title"], "Test")
        self.assertEqual(entry["author"], "José")
        self.assertEqual(entry["year"], 2024)

class TestReaderAuxiliaryFunctions(unittest.TestCase):

    def test_normalize_field_name(self):
        # Names to test are those from Paper class:
        self.assertEqual(normalize_field_name('foo'), 'foo')
        self.assertEqual(normalize_field_name('author'), 'authors')
        self.assertEqual(normalize_field_name('YEAR'), 'year')
        self.assertEqual(normalize_field_name('SUMMARY'), 'abstract')
        self.assertEqual(normalize_field_name('DOI'), 'doi')
        self.assertEqual(normalize_field_name('URLS'), 'url')

    def test_normalize_entry(self):
        foo = {'author': "Bla bla", 'journal_name': "Fake Journal"}
        bar = {'authors': "Bla bla", 'journal': "Fake Journal"}
        self.assertEqual(normalize_entry(foo), bar)

        bad_names = {'YEAR': 1992, 'SUMMARY': "Awesome paper, believe me."}
        good_names = {'year': 1992, 'abstract': "Awesome paper, believe me."}
        self.assertEqual(normalize_entry(bad_names), good_names)


class TestReadBib(unittest.TestCase):
    def test_read_bib(self):
        example_bib = """
        @article{MARKJEZ2025,
        title = {The most amazing paper in the world},
        journal = {Amazing Journal},
        year = {2025},
        doi = {https://doi.org/xxxx/blaxxxx},
        url = {https://www.bla.com/markjez2025},
        author = {Mark and Jezz},
        keywords = {Artificial intelligence, Systematic review, Ecosystem condition, GPT},
        abstract = {bla bla bla}
        }
        """

        with tempfile.NamedTemporaryFile(delete=False, suffix=".bib") as tmp:
            tmp.write(example_bib.encode("utf-8"))
            tmp_path = tmp.name

        try:
            bib_db = read_bib(tmp_path)
            self.assertIsNotNone(bib_db)
            self.assertEqual(bib_db.entries[0]["title"], "The most amazing paper in the world")
            self.assertEqual(bib_db.entries[0]["abstract"], "bla bla bla")
        finally:
            os.remove(tmp_path)


if __name__ == "__main__":
    unittest.main()
