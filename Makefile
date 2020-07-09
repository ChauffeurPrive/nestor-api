.PHONY: help format lint mypy pytest test-all vulncheck

help:
	@echo "format    - Format python code with isort and black"
	@echo "lint      - Check style with pylint"
	@echo "mypy      - Run the static type checker"
	@echo "pytest    - Run tests suite with pytest"
	@echo "test-all  - Run lint, and test coverage"
	@echo "vulncheck - Check for packages vulnerabilities with pipenv"

format:
	isort -rc --apply nestor_api tests ./**.py
	black --line-length 100 nestor_api tests ./**.py

lint:
	isort -rc -c nestor_api tests ./**.py
	black --check --line-length 100 nestor_api tests ./**.py
	pylint tests --rcfile=tests/.pylintrc
	pylint nestor_api ./**.py --rcfile=nestor_api/.pylintrc

mypy:
	mypy nestor_api tests

pytest:
	pytest

test-all: lint mypy pytest

vulncheck:
	pipenv check
