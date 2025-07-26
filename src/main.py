"""The main entrypoint of the application."""

import typer
from loguru import logger
from rich.console import Console
from rich.logging import RichHandler

logger.configure(handlers=[{"sink": RichHandler(markup=True), "format": "{message}"}])
app = typer.Typer()
console = Console()


@app.command()
def run_pipeline() -> None:
    """Run the scraping process."""
    from gorgeous_stew.config import Config  # noqa: PLC0415
    from gorgeous_stew.pipeline import Pipeline  # noqa: PLC0415

    config = Config.load_from_file(
        "./config/wikipedia-cocktail-list-scrape-config.json"
    )

    pipeline = Pipeline(config)
    results = pipeline.run(
        url="https://en.wikipedia.org/wiki/List_of_cocktails",
        content_type="text/vnd.wikipedia.cocktail-list+html",
    )

    for payload in results:
        console.print(payload)


@app.command()
def sandbox() -> None:
    """Test the individual components of the pipeline."""
    raise NotImplementedError


if __name__ == "__main__":
    app()
