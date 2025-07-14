# scraper

A simple web scraping pipeline app.

## Setup

If not already installed, [install UV](https://docs.astral.sh/uv/getting-started/installation/).

From the root of the project, run the following, to ensure that pre-commit
checks run locally:

```console
uv run pre-commit install
```

## Make Commands

* `test`: Run all tests
* `coverage`: Display a test coverage report
* `fix`: Fix all (fixable) linter items via ruff
* `format`: Run code formatting via ruff
* `lint`: Run the linter via ruff
* `precommit`: Run the pre-commit process (against changes staged for git commit)
* `readme`: Render README markdown to console.
* `demo`: Run a demo of the application (main.py)

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

## Footnotes

This package was created with
[Cookiecutter](https://github.com/audreyr/cookiecutter) and the
[TODO](https://www.example.com/TODO) project template.
