"""
Configuration Management Module

This module handles all configuration settings for the Vehicle Damage Analyzer.
It reads from environment variables and provides sensible defaults.
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class Config:
    """
    Configuration class for the Vehicle Damage Analyzer.

    This class manages all application settings, including Ollama configuration,
    logging settings, and directory paths. Settings can be overridden via
    environment variables.

    Attributes:
        ollama_host: URL of the Ollama server
        ollama_vision_model: Model to use for image analysis
        ollama_text_model: Model to use for text analysis
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (None for console only)
        input_dir: Directory containing input images
        output_dir: Directory for output reports
        supported_formats: List of supported image formats
    """

    ollama_host: str = field(
        default_factory=lambda: os.getenv("OLLAMA_HOST", "http://localhost:11434")
    )

    ollama_vision_model: str = field(
        default_factory=lambda: os.getenv("OLLAMA_MODEL_VISION", "llama3.2-vision")
    )

    ollama_text_model: str = field(
        default_factory=lambda: os.getenv("OLLAMA_MODEL_TEXT", "llama3.2")
    )

    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    log_file: Optional[str] = field(default_factory=lambda: os.getenv("LOG_FILE", None))

    input_dir: str = field(default_factory=lambda: os.getenv("INPUT_DIR", "input_data"))

    output_dir: str = field(
        default_factory=lambda: os.getenv("OUTPUT_DIR", "output_data")
    )

    supported_formats: list = field(default_factory=lambda: [".jpg", ".jpeg", ".png"])

    def __post_init__(self):
        """
        Validate and initialize configuration after creation.

        Converts directory paths to absolute paths and ensures they exist.
        """
        self.input_dir = str(Path(self.input_dir).absolute())
        self.output_dir = str(Path(self.output_dir).absolute())

        if self.log_file:
            self.log_file = str(Path(self.log_file).absolute())

    @classmethod
    def from_env(cls) -> "Config":
        """
        Create configuration from environment variables.

        Returns:
            Config: Configuration instance with values from environment
        """
        return cls()

    def get_ollama_url(self, endpoint: str = "") -> str:
        """
        Get full URL for Ollama API endpoint.

        Args:
            endpoint: API endpoint path (e.g., "/api/tags")

        Returns:
            str: Full URL for the endpoint
        """
        base_url = self.ollama_host.rstrip("/")
        endpoint = endpoint.lstrip("/")
        return f"{base_url}/{endpoint}"

    def ensure_directories(self) -> None:
        """
        Ensure that all required directories exist.

        Creates input and output directories if they don't exist.
        """
        Path(self.input_dir).mkdir(parents=True, exist_ok=True)
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

        if self.log_file:
            Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)

    def validate(self) -> bool:
        """
        Validate configuration settings.

        Returns:
            bool: True if configuration is valid, False otherwise
        """
        valid = True

        if not self.ollama_host:
            print("Warning: OLLAMA_HOST not set")
            valid = False

        if not self.ollama_vision_model:
            print("Warning: OLLAMA_MODEL_VISION not set")
            valid = False

        if not self.ollama_text_model:
            print("Warning: OLLAMA_MODEL_TEXT not set")
            valid = False

        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            print(f"Warning: Invalid LOG_LEVEL '{self.log_level}'")
            valid = False

        return valid

    def to_dict(self) -> dict:
        """
        Convert configuration to dictionary.

        Returns:
            dict: Dictionary representation of configuration
        """
        return {
            "ollama_host": self.ollama_host,
            "ollama_vision_model": self.ollama_vision_model,
            "ollama_text_model": self.ollama_text_model,
            "log_level": self.log_level,
            "log_file": self.log_file,
            "input_dir": self.input_dir,
            "output_dir": self.output_dir,
            "supported_formats": self.supported_formats,
        }


# Global configuration instance
_global_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get the global configuration instance.

    Creates a new instance if one doesn't exist.

    Returns:
        Config: Global configuration instance
    """
    global _global_config
    if _global_config is None:
        _global_config = Config.from_env()
        _global_config.ensure_directories()
    return _global_config


def set_config(config: Config) -> None:
    """
    Set the global configuration instance.

    Args:
        config: Configuration instance to set as global
    """
    global _global_config
    _global_config = config
    _global_config.ensure_directories()
