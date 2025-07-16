test:  ## Run all tests
	uv run coverage run -m pytest

coverage:  ## Display a test coverage report
	uv run coverage report -m

run-pipeline:  ## Run the scraping pipeline
	uv run src/scraper/main.py run-pipeline

run-components:  ## Test a single component of the scraping pipeline
	uv run src/scraper/main.py test-components

demo:  ## Run a demo of the application (main.py)
	uv run src/scraper/main.py --help
	uv run src/scraper/main.py hello --name "$$(whoami)"
	uv run src/scraper/main.py goodbye --name "$$(whoami)" --formal

lint:  ## Run the linter via ruff
	uv run ruff check .

fix:  ## Fix all (fixable) linter items via ruff
	uv run ruff check --fix .

format:  ## Run code formatting via ruff
	uv run ruff format .

typecheck:  ## Run type checking via mypy
	uv run mypy .

pydoclint:  ## Run the pydoclint tool to check docstrings
	uv run pydoclint --style=google --arg-type-hints-in-docstring=False --check-return-types=False --allow-init-docstring=True ./src

precommit:  ## Run the pre-commit process (against changes staged for git commit)
	uv run pre-commit run

readme:  ## Render README markdown to console.
	uv run python -m rich.markdown README.md

.PHONY: help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
