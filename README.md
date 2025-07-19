# Gorgeous Stew

A config-driven web scraping pipeline app.

## Setup

If not already installed, [install UV](https://docs.astral.sh/uv/getting-started/installation/).

From the root of the project, run the following, to ensure that pre-commit
checks run locally:

```console
uv run pre-commit install
```

## Usage

To run the scraping pipeline, use the following command:

```console
make run-pipeline
```

This will run the scraping pipeline, which includes fetching data from the web,
processing it, and storing it in the './data/html' and './data/json' directories.
The pipeline config is currently hardcoded in main.py.

TODO: Update usage notes as features are implemented.

## Make Commands

* `fix`: Fix all (fixable) linter items via ruff
* `format`: Run code formatting via ruff
* `lint`: Run the linter via ruff
* `precommit`: Run the pre-commit process (against changes staged for git commit)
* `pydoclint`: Run the pydoclint tool to check docstrings
* `readme`: Render README markdown to console.
* `run-pipeline`: Run the scraping pipeline
* `test`: Run all tests and display a coverage report
* `typecheck`: Run type checking via mypy

(Running `make` at the command line will display the above listing in the console.)

## Tooling

* Python package management via [uv](https://docs.astral.sh/uv/)
* Git pre-commit hooks via [pre-commit](https://pre-commit.com/)
* Python linting and formatting via [Ruff](https://docs.astral.sh/ruff/)
* Unit testing via [pytest](https://docs.pytest.org/en/stable/)
  * Test coverage via [coverage.py](https://coverage.readthedocs.io/en/7.9.1/)
* CLI via [Typer](https://typer.tiangolo.com/)
* Console rendering via [Rich](https://github.com/Textualize/rich)
* Logging via [Loguru](https://github.com/Delgan/loguru)
* Task automation via [Make](https://makefiletutorial.com/)
  * With a properly defined Makefile, it can also be [self-documenting](https://medium.com/aigent/makefiles-for-python-and-beyond-5cf28349bf05).
* Markdown linting via [markdownlint](https://github.com/DavidAnson/markdownlint)
  and [markdownlint-cli2](https://github.com/DavidAnson/markdownlint-cli2)

## Footnotes

This package was created with
[Cookiecutter](https://github.com/audreyr/cookiecutter) and the
[TODO](https://www.example.com/TODO) project template.
