install:
	python -m venv .venv
	.venv/bin/python pip install requirements.txt -e .
test:
	.venv/bin/python -W ignore::UserWarning -m unittest discover -v tests/

coverage:
	.venv/bin/python -m coverage run -m unittest discover tests/
	.venv/bin/python -m coverage html
	open htmlcov/index.html

.PHONY: install test coverage
