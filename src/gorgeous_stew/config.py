"""Configuration support for Gorgeous Stew."""

import json
from pathlib import Path

from gorgeous_stew.model import PipelineConfig


class Config:
    """Configuration class for Gorgeous Stew."""

    @staticmethod
    def load_from_file(file_path: str) -> PipelineConfig:
        """
        Load configuration from a file.

        Args:
            file_path: Path to the configuration file.

        Returns:
            PipelineConfig: An instance of PipelineConfig
            with the loaded configuration.
        """
        with Path(file_path).open("r", encoding="utf-8") as file:
            config_data = json.load(file)
            return PipelineConfig(**config_data)
