"""The main entrypoint of the application."""

import importlib
import json
from abc import ABC, abstractmethod

import typer
from bs4 import BeautifulSoup
from loguru import logger
from rich.console import Console
from rich.logging import RichHandler

from scraper.model import Link, Payload
from scraper.scrapers import MockScraper, WebScraper

logger.configure(handlers=[{"sink": RichHandler(markup=True), "format": "{message}"}])
app = typer.Typer()
console = Console()


class Parser(ABC):
    """Abstract base class defining the functionality supporting parsing."""

    @abstractmethod
    def parse(self, payload: Payload) -> Payload:
        """
        Parse the HTML in `payload.html_content`.

        Args:
          payload: A `Payload` containing the `html_content` to parse.

        Returns:
          A `Payload` object with the `json_content` populated with
          data from the parsed HTML.
        """
        ...


class Transformer(ABC):
    """Abstract base class defining the functionality supporting transformation."""

    @abstractmethod
    def transform(self, payload: Payload) -> list[Payload]:
        """
        Transform the JSON in `payload.json_content`.

        Args:
          payload: A `Payload` containing the `json_content` to transform.

        Returns:
          A `list` of `Payload` objects.  Each payload will be one of three different
          logical "types":
          - A link payload intended for follow up scraping, parsing, and transformation.
          - An intermediate payload needing follow-up transformation
            (by one or more other transformers).
          - A "terminal" content payload, requiring no further actions.
        """
        ...


class FactoryBase:
    """
    Base class for all concrete Factory classes.

    Provides generic functionality for dynamically instantiating objects
    based on string names.
    """

    def instantiate(self, fqn: str) -> any:
        """Instantiate an instance of a class dynamically based on the name provided."""
        name_components = fqn.split(".")
        class_name = name_components[-1]
        module_name = ".".join(name_components[:-1])

        module = importlib.import_module(module_name)
        class_ = getattr(module, class_name)
        return class_()


class ParserFactory(FactoryBase):
    """Factory class to instantiate HTML `Parser`s."""

    def __init__(self, mapping: dict) -> None:
        """
        Instantiate the `ParserFactory`.

        Args:
          mapping: A `dict` containing mappings from page types to
            the fully qualified class names of concrete parser classes
            to be used in parsing each of those types of pages.
            e.g.: `"demo_page": "scraper.parsers.DemoPageParser"`
        """
        self.mapping = mapping

    def build(self, link: Link) -> Parser:
        """
        Build a `Parser` instance for the `page_type` in `link`.

        Args:
          link: a `Link` containing the `page_type` to be parsed.

        Returns:
          A `Parser` instance appropriate for parsing the specified
          page type.
        """
        if link.page_type not in self.mapping:
            msg = f"Unexpected page_type: {link.page_type}"
            raise ValueError(msg)

        mapped_name = self.mapping[link.page_type]
        return self.instantiate(mapped_name)


class TransformerFactory(FactoryBase):
    """Factory class to instantiate JSON `Transformer`s."""

    def __init__(self, mapping: dict) -> None:
        """
        Instantiate the `TransformerFactory`.

        Args:
          mapping: A `dict` containing mappings from json schema to
            the fully qualified class names of concrete transformer
            classes to be used in transforming each of those types
            of json datasets.
            e.g.: `"demo_schema": "scraper.transformers.DemoParser"`
        """
        self.mapping = mapping

    def build(self, payload: Payload) -> Transformer:
        """
        Build a `Transformer` instance for the `json_schema` in `payload`.

        Args:
          payload: a `Payload` containing the `json_schema` to be transformed.

        Returns:
          A `Transformer` instance appropriate for transforming the specified
          json schema.
        """
        if payload.json_schema not in self.mapping:
            msg = f"Unexpected json_schema: {payload.json_schema}"
            raise ValueError(msg)

        mapped_name = self.mapping[payload.json_schema]
        return self.instantiate(mapped_name)


class Pipeline:
    """Scraping Pipeline."""

    def __init__(self, config: dict) -> None:
        """
        Instantiate a new Pipeline.

        Args:
          config: A `dict` containing mappings for `Parser` and
            `Transformer` instantiation.
        """
        self._scraper = MockScraper()
        self._parser_factory = ParserFactory(config["parser_map"])
        self._transformer_factory = TransformerFactory(config["transformer_map"])

    def _handle_payload(self, payload: Payload) -> list[Payload]:
        # base case: terminal payload handling
        if payload.is_complete:
            return [payload]

        # link payload (needs to be scraped and processed further)
        if payload.html_content is None and payload.json_content is None:
            next_payload = self._scraper.scrape(payload)
            return self._handle_payload(next_payload)

        # html payload needing parsing
        if payload.html_content is not None:
            parser = self._parser_factory.build(payload.link)
            next_payload = parser.parse(payload)
            return self._handle_payload(next_payload)

        # json payload needing transformation
        if payload.json_content is not None:
            transformer = self._transformer_factory.build(payload)
            next_payloads = transformer.transform(payload)
            result = []
            for next_payload in next_payloads:
                result.extend(self._handle_payload(next_payload))
            return result

        msg = "Unexpected payload."
        raise ValueError(msg)

    def run(self, url: str, page_type: str) -> None:
        """
        Run a pipeline instance.

        Args:
          url: The entrypoint URL to start scraping against.
          page_type: The page type of the URL.  This is used to decide which
            `Parser`s and `Transformer`s to use in processing the page.
        """
        link = Link(url=url, page_type=page_type)

        results = self._handle_payload(Payload(link=link))

        for payload in results:
            console.print(payload)


# -- concrete implementations --


class IbaCocktailListParser(Parser):
    """
    A `Parser` able to parse IBA Cocktails List pages.

    https://iba-world.com/cocktails/all-cocktails/
    """

    def parse(self, payload: Payload) -> Payload:
        """
        Parse the `html_content` within `payload`.

        Args:
          payload: A `Payload` containing the HTML content of an
          IBA Cocktail List page.

        Returns:
          A `Payload` containing the JSON content parsed from the
          page HTML.

          An example of the JSON produced:
          ```
          {
            "cocktails": [
              { "name": "Martini", "url": "https://iba-world.com/iba-cocktail/martini/" },
              ...
            ],
            "links": {
               "next": "https://iba-world.com/cocktails/all-cocktails/page/2"
             }
          }
          ```
        """  # noqa: E501
        soup = BeautifulSoup(payload.html_content, "html.parser")

        # parse out the cocktails on the current page
        cocktails = []
        for item in soup.css.select("li.cocktail"):
            link = item.find("a")

            cocktails.append({"name": link.text, "url": link.get("href")})

        # parse out the "next" link in the nav
        next_link = soup.css.select("div.nav a.next")

        if next_link is not None and len(next_link) > 0:
            next_link = next_link[0].get("href")
        else:
            next_link = None

        content = {
            "cocktails": cocktails,
            "links": {
                "next": next_link,
            },
        }

        return Payload(
            link=payload.link,
            json_content=json.dumps(content),
            json_schema="iba-all-cocktails",
        )

    def parse_v2(self, payload: Payload) -> Payload:
        """Parse the `html_content` within `payload` using new logic."""
        soup = BeautifulSoup(payload.html_content, features="html.parser")

        # get the next page link if present
        next_link = soup.css.select("a.next")
        next_link = next_link[0].get("href") if len(next_link) > 0 else None

        cocktails = [
            {
                "name": cocktail.find("h2").text,
                "url": cocktail.find("a").get("href"),
                "category": cocktail.find(
                    "div", {"class": "cocktail-category"}
                ).text.strip(),
                "picture_url": cocktail.find("img").get("src"),
            }
            for cocktail in soup.css.select("div.cocktail")
        ]

        content = {
            "cocktails": cocktails,
            "links": {"next": next_link},
        }

        return Payload(link=payload.link, json_content=json.dumps(content))


class IbaCocktailParser(Parser):
    """
    A `Parser` able to parse IBA Cocktail pages.

    e.g. https://iba-world.com/iba-cocktail/aviation/
    """

    def parse(self, payload: Payload) -> Payload:
        """
        Parse the `html_content` within `payload`.

        Args:
          payload: A `Payload` containing the HTML content of an
          IBA Cocktail page.

        Returns:
          A `Payload` containing the JSON content parsed from the
          page HTML.

          An example of the JSON produced:
          ```
          {
            "name": "Martini",
            "ingredients": [],
            "instructions": [],
            "garnish": ""
          }
          ```
        """
        soup = BeautifulSoup(payload.html_content, "html.parser")
        content = soup.css.select("div.cocktail")[0]
        name = content.find("h2").text

        ingredients = [
            item.text for item in content.css.select("ul.ingredients")[0].find_all("li")
        ]

        instructions = [
            item.text
            for item in content.css.select("ul.instructions")[0].find_all("li")
        ]

        garnish = content.css.select("p.garnish")[0].text

        cocktail = {
            "name": name,
            "ingredients": ingredients,
            "instructions": instructions,
            "garnish": garnish,
        }

        return Payload(
            link=payload.link,
            json_content=json.dumps(cocktail),
            json_schema="iba-cocktail",
            is_complete=True,
        )


class IbaCocktailListTransformer(Transformer):
    """
    Transforms the HTML of the IBA Cockatil List pages to JSON.

    https://iba-world.com/cocktails/all-cocktails/
    """

    def transform(self, payload: Payload) -> list[Payload]:
        """
        Transform the JSON of the IBA Cockatil List pages.

        This involves:
        - Creating `Payload`s for each cocktail on the page.
        - Creating a "next" link `Payload` if a next page exists.

        Args:
          payload: The `Payload` with JSON content parsed from
            an IBA Cocktail List page.

        Returns:
          A `list` of `Payloads` containing one for each cocktail parsed
          from the page, as well as a payload to scrape the next page.
        """
        obj = json.loads(payload.json_content)

        result = [
            Payload(link=Link(url=item["url"], page_type="iba-cocktail"))
            for item in obj["cocktails"]
        ]

        if "next" in obj["links"] and obj["links"]["next"] is not None:
            result.append(
                Payload(
                    link=Link(url=obj["links"]["next"], page_type="iba-all-cocktails")
                )
            )

        return result


@app.command()
def run_pipeline() -> None:
    """Run the scraping process."""
    config = {
        "html_root_dir": "./html-data",
        "json_root_dir": "./json-data",
        "read_sequence": ["web", "file"],
        "write_content": True,
        "write_backup": True,
        "parser_map": {
            "iba-all-cocktails": "scraper.main.IbaCocktailListParser",
            "iba-cocktail": "scraper.main.IbaCocktailParser",
        },
        "transformer_map": {
            "iba-all-cocktails": "scraper.main.IbaCocktailListTransformer"
        },
    }

    pipeline = Pipeline(config)
    pipeline.run("https://www.example.com/all-cocktails", "iba-all-cocktails")


@app.command()
def test_components() -> None:
    """Test the individual components of the pipeline."""
    scraper = WebScraper("./data/html-data", write_content=True, write_backup=True)
    payload = scraper.scrape(
        Payload(link=Link("https://iba-world.com/cocktails/all-cocktails/", "not_used"))
    )

    parser = IbaCocktailListParser()
    payload = parser.parse_v2(payload)

    console.print(payload)


if __name__ == "__main__":
    app()
