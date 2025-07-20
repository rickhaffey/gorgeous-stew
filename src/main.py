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

    config = Config.load_from_file("./config/iba-cocktail-list-scrape-config.json")

    pipeline = Pipeline(config)
    results = pipeline.run(
        url="https://iba-world.com/cocktails/all-cocktails/",
        content_type="iba-all-cocktails",
    )

    for payload in results:
        console.print(payload)


@app.command()
def test_components() -> None:
    """Test the individual components of the pipeline."""


if __name__ == "__main__":
    app()
