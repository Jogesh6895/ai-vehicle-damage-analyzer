"""
Vehicle Damage Analyzer - Main Package
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from src.config import Config
from src.file_handler import FileHandler
from src.ollama_client import OllamaClient

__all__ = ["Config", "FileHandler", "OllamaClient"]
