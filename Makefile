.PHONY: help format lint mypy test test-all vulncheck

help:
	@echo "format    - Format python code with isort and black"
	@echo "lint      - Check style with pylint"
	@echo "mypy      - Run the static type checker"
	@echo "test      - Run tests suite with unittest"
	@echo "test-all  - Run lint, and test coverage"
	@echo "vulncheck - Check for packages vulnerabilities with pipenv"

format:
	isort -rc --apply nestor_api tests validator ./**.py
	black --line-length 100 nestor_api tests validator ./**.py

lint:
	isort -rc -c nestor_api tests validator ./**.py
	black --check --line-length 100 nestor_api tests validator ./**.py
	pylint tests --rcfile=tests/.pylintrc
	pylint nestor_api ./**.py --rcfile=nestor_api/.pylintrc
	pylint validator ./**.py --rcfile=nestor_api/.pylintrc

mypy:
	mypy nestor_api tests validator

test:
	coverage run -m unittest discover

coverage:
	coverage html --rcfile=.coveragerc

coverage-xml:
	coverage xml --rcfile=.coveragerc

test-all: lint mypy test

vulncheck:
	pipenv check
