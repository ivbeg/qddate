.PHONY: clean-pyc clean-build docs docs-serve docs-patterns clean
SHELL := /bin/bash

help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "lint - check style with flake8"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - build the Docusaurus documentation site"
	@echo "docs-serve - serve the documentation site locally"
	@echo "docs-patterns - regenerate language pattern pages"
	@echo "release - package and upload a release"
	@echo "dist - package"

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info
	rm -fr docs/build/
	rm -fr docs/.docusaurus/

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

lint:
	flake8 qddate tests --config=./flake8

coverage:
	pytest --cov=qddate --cov-report=term-missing --cov-report=html
	python3 -m webbrowser htmlcov/index.html

docs: ## Build documentation site (Docusaurus)
	cd docs && npm ci && npm run build

docs-serve: ## Serve documentation locally (Docusaurus)
	cd docs && npm start

docs-patterns: ## Regenerate language pattern pages
	python3 scripts/generate_pattern_docs.py

release: clean
	python3 -m build
	python3 -m twine upload dist/*

dist: clean
	python3 -m build
	ls -l dist
