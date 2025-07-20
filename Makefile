all-checks: format lint typecheck pydoclint test ## Run formatting, then all checks: format lint, typecheck, pydoclint, and tests

test:  ## Run all tests and display a coverage report
	uv run coverage run -m pytest && uv run coverage report -m

run-pipeline:  ## Run the scraping pipeline
	uv run src/main.py run-pipeline

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
