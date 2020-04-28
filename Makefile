.PHONY: format lint coverage isort-format black-format

export BOLD=`tput bold`
export ENDBOLD=`tput sgr0`

help:
	@echo "black-format - Format python code with black"
	@echo "format - Format python code with isort and black"
	@echo "isort-format - Format python code with isort"
	@echo "lint - Check style with pylint"
	@echo "mypy - Run the static type checker"
	@echo "pytest - Run tests suite with pytest"
	@echo "test-all - Run format, lint, and test coverage"
	@echo "vulncheck - Check for packages vulnerabilities with pipenv"

black-format:
	@echo "$(BOLD)Formatting using black$(ENDBOLD)"
	black --line-length 80 nestor ./**.py

isort-format:
	@echo "$(BOLD)Formatting using isort$(ENDBOLD)"
	isort -rc nestor ./**.py --apply

format: isort-format black-format

lint:
	pylint nestor ./**.py

mypy:
	mypy nestor tests

pytest:
	pytest

test-all: format lint mypy pytest

vulncheck:
	pipenv check
