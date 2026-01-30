"""
Main Module - CLI Interface

This module provides the command-line interface for the Vehicle Damage Analyzer.
It supports multiple modes: interactive, batch, and API.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
import click

from src.config import get_config, set_config, Config
from src.file_handler import FileHandler
from src.ollama_client import OllamaClient
from src.image_analyzer import ImageAnalyzer
from src.cost_estimator import CostEstimator
from src.report_generator import ReportGenerator


def setup_logging(config: Config, verbose: bool = False) -> None:
    """
    Setup logging configuration.

    Args:
        config: Configuration instance
        verbose: Enable verbose logging
    """
    log_level = logging.DEBUG if verbose else getattr(logging, config.log_level)

    handlers = [logging.StreamHandler()]

    if config.log_file:
        handlers.append(logging.FileHandler(config.log_file))

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )


def interactive_mode(config: Config) -> None:
    """
    Run the application in interactive CLI mode.

    Args:
        config: Configuration instance
    """
    logger = logging.getLogger(__name__)
    logger.info("Starting interactive mode")

    file_handler = FileHandler(config)
    ollama_client = OllamaClient(config)
    image_analyzer = ImageAnalyzer(ollama_client)
    cost_estimator = CostEstimator(ollama_client)
    report_generator = ReportGenerator(config, file_handler)

    click.echo("\n" + "=" * 60)
    click.echo("Vehicle Damage Analyzer - Interactive Mode")
    click.echo("=" * 60 + "\n")

    while True:
        try:
            image_path = click.prompt(
                "\nEnter path to image file (or 'quit' to exit)",
                type=click.Path(exists=False),
            )

            if image_path.lower() in ["quit", "exit", "q"]:
                click.echo("Exiting...")
                break

            image_path = Path(image_path)

            if not image_path.exists():
                click.echo(f"Error: File not found: {image_path}")
                continue

            if not file_handler.validate_image_format(image_path):
                click.echo(
                    f"Error: Unsupported image format. Supported formats: {config.supported_formats}"
                )
                continue

            click.echo(f"\nAnalyzing image: {image_path.name}")

            with click.progressbar(length=100, label="Analyzing") as bar:
                bar.update(50)
                analysis_result = image_analyzer.analyze_image_file(image_path)
                bar.update(100)

            if analysis_result.get("status") != "success":
                click.echo(
                    f"\nError: Analysis failed - {analysis_result.get('error', 'Unknown error')}"
                )
                continue

            click.echo("\n" + "-" * 60)
            click.echo("DAMAGE ANALYSIS")
            click.echo("-" * 60)
            click.echo(analysis_result.get("analysis", ""))

            click.echo("\n" + "-" * 60)
            click.echo("COST ESTIMATION")
            click.echo("-" * 60)

            cost_result = cost_estimator.estimate_costs(
                analysis_result.get("analysis", "")
            )

            if cost_result.get("status") == "success":
                click.echo(f"Total Estimated Cost: ${cost_result.get('total_cost', 0)}")

                if cost_result.get("detailed_breakdown"):
                    click.echo("\nDetailed Breakdown:")
                    for item in cost_result.get("detailed_breakdown", []):
                        click.echo(f"  - {item}")

                if cost_result.get("ai_summary"):
                    click.echo("\nAI Repair Summary:")
                    click.echo(cost_result.get("ai_summary"))

            generate_report = click.confirm("\nGenerate report file?", default=True)

            if generate_report:
                output_format = click.prompt(
                    "Select output format",
                    type=click.Choice(["csv", "txt", "json"], case_sensitive=False),
                    default="csv",
                )

                report_path = report_generator.generate_single_report(
                    analysis_result, cost_result, output_format
                )

                if report_path:
                    click.echo(f"Report saved to: {report_path}")
                else:
                    click.echo("Error: Failed to generate report")

        except KeyboardInterrupt:
            click.echo("\n\nInterrupted by user")
            break
        except Exception as e:
            logger.error(f"Error in interactive mode: {e}")
            click.echo(f"\nError: {e}")

    logger.info("Interactive mode ended")


def batch_mode(
    config: Config, input_dir: str, output_dir: Optional[str] = None
) -> None:
    """
    Run the application in batch processing mode.

    Args:
        config: Configuration instance
        input_dir: Input directory containing images
        output_dir: Output directory for reports (optional)
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Starting batch mode with input directory: {input_dir}")

    if output_dir:
        config.output_dir = output_dir

    file_handler = FileHandler(config)
    ollama_client = OllamaClient(config)
    image_analyzer = ImageAnalyzer(ollama_client)
    cost_estimator = CostEstimator(ollama_client)
    report_generator = ReportGenerator(config, file_handler)

    try:
        image_files = file_handler.get_input_files(input_dir)

        if not image_files:
            click.echo(f"No images found in {input_dir}")
            return

        click.echo(f"\nFound {len(image_files)} images to process")
        click.echo("-" * 60)

        results = []

        def progress_callback(current, total):
            click.echo(f"Progress: {current}/{total} images processed")

        results = image_analyzer.batch_analyze(image_files, progress_callback)

        for result in results:
            if result.get("status") == "success":
                cost_result = cost_estimator.estimate_costs(result.get("analysis", ""))
                results[-1]["costs"] = cost_result

        click.echo("\n" + "-" * 60)
        click.echo("BATCH SUMMARY")
        click.echo("-" * 60)

        successful = sum(1 for r in results if r.get("status") == "success")
        click.echo(f"Total Images: {len(results)}")
        click.echo(f"Successful: {successful}")
        click.echo(f"Failed: {len(results) - successful}")

        if successful > 0:
            total_cost = sum(
                r.get("costs", {}).get("total_cost", 0)
                for r in results
                if r.get("costs", {}).get("status") == "success"
            )
            click.echo(f"Total Estimated Cost: ${total_cost}")

        generate_report = click.confirm("\nGenerate batch report?", default=True)

        if generate_report:
            output_format = click.prompt(
                "Select output format",
                type=click.Choice(["csv", "txt", "json"], case_sensitive=False),
                default="csv",
            )

            report_path = report_generator.generate_batch_report(results, output_format)

            if report_path:
                click.echo(f"Batch report saved to: {report_path}")
            else:
                click.echo("Error: Failed to generate batch report")

        logger.info("Batch processing completed")

    except Exception as e:
        logger.error(f"Error in batch mode: {e}")
        click.echo(f"\nError: {e}")


def api_mode(config: Config) -> None:
    """
    Run the application in API mode (for programmatic use).

    Args:
        config: Configuration instance
    """
    logger = logging.getLogger(__name__)
    logger.info("Starting API mode")

    file_handler = FileHandler(config)
    ollama_client = OllamaClient(config)
    image_analyzer = ImageAnalyzer(ollama_client)
    cost_estimator = CostEstimator(ollama_client)

    class API:
        def __init__(self):
            self.file_handler = file_handler
            self.analyzer = image_analyzer
            self.estimator = cost_estimator
            self.config = config

        def analyze_image(self, image_path: str) -> dict:
            """Analyze a single image."""
            result = self.analyzer.analyze_image_file(Path(image_path))
            return result

        def estimate_costs(self, analysis_text: str) -> dict:
            """Estimate costs from analysis text."""
            result = self.estimator.estimate_costs(analysis_text)
            return result

        def get_input_files(self) -> list:
            """Get list of input image files."""
            files = self.file_handler.get_input_files()
            return [str(f) for f in files]

    return API()


@click.command()
@click.option(
    "--mode",
    type=click.Choice(["interactive", "batch", "api"], case_sensitive=False),
    default="interactive",
    help="Operation mode",
)
@click.option(
    "--input", type=click.Path(exists=True), help="Input directory (for batch mode)"
)
@click.option("--output", type=click.Path(), help="Output directory (optional)")
@click.option("--model", help="Ollama model to use")
@click.option("--verbose", is_flag=True, help="Enable verbose logging")
def main(
    mode: str,
    input: Optional[str],
    output: Optional[str],
    model: Optional[str],
    verbose: bool,
):
    """
    Vehicle Damage Analyzer - CLI Interface

    Analyze vehicle damage images and estimate repair costs using AI.
    """
    config = get_config()

    if model:
        config.ollama_vision_model = model
        config.ollama_text_model = model

    if verbose:
        config.log_level = "DEBUG"

    setup_logging(config, verbose)

    if not config.validate():
        click.echo("Warning: Configuration validation failed")

    logger = logging.getLogger(__name__)
    logger.info(f"Starting Vehicle Damage Analyzer in {mode} mode")

    if mode == "interactive":
        interactive_mode(config)
    elif mode == "batch":
        if not input:
            click.echo("Error: --input directory required for batch mode")
            sys.exit(1)
        batch_mode(config, input, output)
    elif mode == "api":
        api = api_mode(config)
        click.echo("API mode initialized. Access the API object programmatically.")
        logger.info("API mode initialized")

    logger.info("Vehicle Damage Analyzer ended")


if __name__ == "__main__":
    main()
