.PHONY: help format lint mypy test test-all vulncheck

help:
	@echo "format    - Format python code with isort and black"
	@echo "lint      - Check style with pylint"
	@echo "mypy      - Run the static type checker"
	@echo "test      - Run tests suite with python"
	@echo "test-all  - Run lint, and test coverage"
	@echo "vulncheck - Check for packages vulnerabilities with pipenv"

format:
	isort -rc --apply nestor_api tests validator yaml_lib ./**.py
	black --line-length 100 nestor_api tests validator yaml_lib ./**.py

lint:
	isort -rc -c nestor_api tests validator yaml_lib ./**.py
	black --check --line-length 100 nestor_api tests validator yaml_lib ./**.py
	pylint tests --rcfile=tests/.pylintrc
	pylint nestor_api ./**.py --rcfile=nestor_api/.pylintrc
	pylint validator ./**.py --rcfile=nestor_api/.pylintrc
	pylint yaml_lib ./**.py --rcfile=nestor_api/.pylintrc

mypy:
	mypy nestor_api tests validator yaml_lib

test:
	coverage run -m unittest discover -v -s ./tests
	coverage report
	coverage html
	coverage xml

test-all: lint mypy test

vulncheck:
	pipenv check
