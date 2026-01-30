"""
Image Analyzer Module

This module handles vehicle damage analysis using AI vision models.
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path


class ImageAnalyzer:
    """
    Analyzes vehicle images for damage detection.

    This class uses Ollama vision models to detect and analyze
    vehicle damage from images.

    Attributes:
        ollama_client: OllamaClient instance for AI interactions
        logger: Logger instance for this analyzer
    """

    def __init__(self, ollama_client):
        """
        Initialize ImageAnalyzer with Ollama client.

        Args:
            ollama_client: OllamaClient instance for AI model interactions
        """
        self.ollama_client = ollama_client
        self.logger = logging.getLogger(__name__)

    def analyze_image(
        self, image_data: bytes, prompt: Optional[str] = None
    ) -> Optional[str]:
        """
        Analyze vehicle image for damage.

        Args:
            image_data: Image data as bytes
            prompt: Custom analysis prompt (optional)

        Returns:
            str: Damage analysis result or None on error
        """
        default_prompt = (
            "Identify visible vehicle damage only. "
            "Don't be verbose. List specific damage types, locations, "
            "and severity levels if visible."
        )

        analysis_prompt = prompt or default_prompt

        self.logger.info("Starting image analysis")

        result = self.ollama_client.analyze_image(image_data, analysis_prompt)

        if result:
            self.logger.info("Image analysis completed successfully")
            return result
        else:
            self.logger.error("Image analysis failed")
            return None

    def analyze_image_file(
        self, file_path: Path, prompt: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze vehicle image from file path.

        Args:
            file_path: Path to image file
            prompt: Custom analysis prompt (optional)

        Returns:
            Dict: Analysis result with metadata or None on error
        """
        try:
            from src.file_handler import FileHandler
            from src.config import get_config

            config = get_config()
            file_handler = FileHandler(config)

            image_data = file_handler.read_image(file_path)
            analysis = self.analyze_image(image_data, prompt)

            if analysis:
                return {
                    "file_path": str(file_path),
                    "file_name": file_path.name,
                    "analysis": analysis,
                    "status": "success",
                }
            else:
                return {
                    "file_path": str(file_path),
                    "file_name": file_path.name,
                    "analysis": None,
                    "status": "failed",
                }

        except Exception as e:
            self.logger.error(f"Failed to analyze image file {file_path}: {e}")
            return {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "analysis": None,
                "status": "error",
                "error": str(e),
            }

    def batch_analyze(
        self, image_files: list, progress_callback: Optional[callable] = None
    ) -> list:
        """
        Analyze multiple images in batch.

        Args:
            image_files: List of image file paths
            progress_callback: Optional callback function for progress updates

        Returns:
            list: List of analysis results for each image
        """
        results = []
        total = len(image_files)

        self.logger.info(f"Starting batch analysis of {total} images")

        for idx, file_path in enumerate(image_files):
            self.logger.debug(f"Analyzing image {idx + 1}/{total}: {file_path}")

            result = self.analyze_image_file(file_path)
            results.append(result)

            if progress_callback:
                progress_callback(idx + 1, total)

        successful = sum(1 for r in results if r.get("status") == "success")
        self.logger.info(f"Batch analysis complete: {successful}/{total} successful")

        return results

    def validate_analysis(self, analysis: str) -> bool:
        """
        Validate if analysis result is meaningful.

        Args:
            analysis: Analysis text to validate

        Returns:
            bool: True if analysis is valid, False otherwise
        """
        if not analysis or not isinstance(analysis, str):
            return False

        if len(analysis.strip()) < 10:
            return False

        if "no damage" in analysis.lower() and len(analysis) < 50:
            return False

        return True

    def extract_damage_types(self, analysis: str) -> list:
        """
        Extract damage types from analysis text.

        Args:
            analysis: Analysis text to parse

        Returns:
            list: List of detected damage types
        """
        damage_keywords = [
            "scratch",
            "dent",
            "crumpled",
            "broken",
            "shattered",
            "cracked",
            "damaged",
            "bent",
            "headlight",
            "windshield",
            "bumper",
            "grille",
            "hood",
            "door",
            "mirror",
            "fender",
        ]

        analysis_lower = analysis.lower()
        detected_damages = []

        for keyword in damage_keywords:
            if keyword in analysis_lower:
                detected_damages.append(keyword)

        return list(set(detected_damages))

    def extract_severity(self, analysis: str) -> Optional[str]:
        """
        Extract severity level from analysis text.

        Args:
            analysis: Analysis text to parse

        Returns:
            str: Severity level (minor, moderate, severe) or None
        """
        analysis_lower = analysis.lower()

        severity_keywords = {
            "severe": ["severe", "major", "extensive", "significant"],
            "moderate": ["moderate", "medium", "noticeable"],
            "minor": ["minor", "slight", "small", "light"],
        }

        for level, keywords in severity_keywords.items():
            if any(keyword in analysis_lower for keyword in keywords):
                return level

        return None
