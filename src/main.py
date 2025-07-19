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
    from scraper.model import PipelineConfig  # noqa: PLC0415
    from scraper.pipeline import Pipeline  # noqa: PLC0415

    # Define the configuration for the scraping pipeline
    config = PipelineConfig(
        html_root_dir="./data/html",
        json_root_dir="./data/json",
        read_sequence=["file"],
        write_content=True,
        write_backup=False,
        scrape_delay_ms=1000,
        parser_map={
            "iba-all-cocktails": "scraper.iba.parsers.IbaCocktailListParser",
            "iba-cocktail": "scraper.iba.parsers.IbaCocktailParser",
        },
        transformer_map={
            "iba-all-cocktails": "scraper.iba.transformers.IbaCocktailListTransformer"
        },
    )

    pipeline = Pipeline(config)
    results = pipeline.run(
        url="https://iba-world.com/cocktails/all-cocktails/",
        page_type="iba-all-cocktails",
    )

    for payload in results:
        console.print(payload)


@app.command()
def test_components() -> None:
    """Test the individual components of the pipeline."""


if __name__ == "__main__":
    app()
