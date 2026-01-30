"""
Ollama Client Module

This module provides a wrapper for the Ollama API to interact with
AI models for image and text analysis.
"""

import logging
from typing import List, Dict, Optional, Any
import ollama


class OllamaClient:
    """
    Wrapper for Ollama API interactions.

    This class handles communication with Ollama models for both
    vision and text analysis tasks.

    Attributes:
        config: Configuration instance containing Ollama settings
        logger: Logger instance for this client
    """

    def __init__(self, config):
        """
        Initialize OllamaClient with configuration.

        Args:
            config: Configuration instance with Ollama settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._check_connection()

    def _check_connection(self) -> bool:
        """
        Check if Ollama server is accessible.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            models = ollama.list()
            self.logger.info(f"Connected to Ollama at {self.config.ollama_host}")
            self.logger.debug(
                f"Available models: {[m['name'] for m in models['models']]}"
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Ollama: {e}")
            return False

    def chat(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        images: Optional[List[bytes]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Send chat request to Ollama.

        Args:
            model: Model name to use
            messages: List of message dictionaries with 'role' and 'content'
            images: Optional list of image data bytes

        Returns:
            Dict: Response from Ollama API or None on error
        """
        try:
            request = {"model": model, "messages": messages}

            if images:
                request["images"] = images

            self.logger.debug(f"Sending request to model: {model}")
            response = ollama.chat(**request)

            if "message" in response and "content" in response["message"]:
                self.logger.debug("Received successful response from Ollama")
                return response
            else:
                self.logger.error("Response missing 'message' or 'content' field")
                return None

        except Exception as e:
            self.logger.error(f"Ollama chat request failed: {e}")
            return None

    def analyze_image(
        self,
        image_data: bytes,
        prompt: str = "Identify visible vehicle damage only. Don't be verbose.",
    ) -> Optional[str]:
        """
        Analyze image using vision model.

        Args:
            image_data: Image data as bytes
            prompt: Analysis prompt for the model

        Returns:
            str: Analysis result or None on error
        """
        try:
            response = self.chat(
                model=self.config.ollama_vision_model,
                messages=[{"role": "user", "content": prompt}],
                images=[image_data],
            )

            if response and "message" in response and "content" in response["message"]:
                result = response["message"]["content"]
                self.logger.info("Image analysis completed successfully")
                return result
            else:
                self.logger.error("Invalid response format from vision model")
                return None

        except Exception as e:
            self.logger.error(f"Image analysis failed: {e}")
            return None

    def analyze_text(self, text: str, prompt: Optional[str] = None) -> Optional[str]:
        """
        Analyze text using text model.

        Args:
            text: Text to analyze
            prompt: Analysis prompt (default: uses provided text directly)

        Returns:
            str: Analysis result or None on error
        """
        try:
            content = prompt or text

            response = self.chat(
                model=self.config.ollama_text_model,
                messages=[{"role": "user", "content": content}],
            )

            if response and "message" in response and "content" in response["message"]:
                result = response["message"]["content"]
                self.logger.info("Text analysis completed successfully")
                return result
            else:
                self.logger.error("Invalid response format from text model")
                return None

        except Exception as e:
            self.logger.error(f"Text analysis failed: {e}")
            return None

    def generate_repair_summary(self, damage_analysis: str) -> Optional[str]:
        """
        Generate comprehensive repair summary using text model.

        Args:
            damage_analysis: Damage analysis text to summarize

        Returns:
            str: Repair summary or None on error
        """
        prompt = (
            f"Based on the following damages, provide a detailed repair cost "
            f"breakdown and suggestions: {damage_analysis}"
        )

        return self.analyze_text(prompt)

    def list_models(self) -> Optional[List[Dict[str, Any]]]:
        """
        List available models in Ollama.

        Returns:
            List: List of model information dictionaries
        """
        try:
            response = ollama.list()
            models = response.get("models", [])
            self.logger.debug(f"Found {len(models)} available models")
            return models
        except Exception as e:
            self.logger.error(f"Failed to list models: {e}")
            return None

    def check_model_available(self, model_name: str) -> bool:
        """
        Check if a specific model is available.

        Args:
            model_name: Name of the model to check

        Returns:
            bool: True if model is available, False otherwise
        """
        models = self.list_models()

        if not models:
            return False

        for model in models:
            if model_name in model["name"]:
                return True

        self.logger.warning(f"Model '{model_name}' not found in available models")
        return False

    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a model.

        Args:
            model_name: Name of the model

        Returns:
            Dict: Model information or None if not found
        """
        try:
            info = ollama.show(model_name)
            self.logger.debug(f"Retrieved info for model: {model_name}")
            return info
        except Exception as e:
            self.logger.error(f"Failed to get model info for '{model_name}': {e}")
            return None
