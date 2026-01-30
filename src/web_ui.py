"""
Web UI Module - Streamlit Interface

This module provides a web-based user interface using Streamlit
for the Vehicle Damage Analyzer.
"""

import streamlit as st
import logging
from pathlib import Path
from typing import Optional

from src.config import get_config, Config
from src.file_handler import FileHandler
from src.ollama_client import OllamaClient
from src.image_analyzer import ImageAnalyzer
from src.cost_estimator import CostEstimator
from src.report_generator import ReportGenerator


def setup_logging(config: Config) -> None:
    """
    Setup logging for the web UI.

    Args:
        config: Configuration instance
    """
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def initialize_session_state() -> None:
    """
    Initialize Streamlit session state variables.
    """
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None
    if "cost_result" not in st.session_state:
        st.session_state.cost_result = None
    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = None


def render_sidebar(config: Config) -> None:
    """
    Render the sidebar with configuration and troubleshooting info.

    Args:
        config: Configuration instance
    """
    with st.sidebar:
        st.title("Settings")

        model = st.text_input(
            "Ollama Vision Model",
            value=config.ollama_vision_model,
            help="Name of the Ollama vision model to use",
        )
        config.ollama_vision_model = model

        log_level = st.selectbox(
            "Log Level", ["DEBUG", "INFO", "WARNING", "ERROR"], index=1
        )
        config.log_level = log_level

        st.divider()

        st.title("Troubleshooting")
        st.write("If you encounter issues:")
        st.write("- Ensure the image is clear and well-lit")
        st.write("- Make sure the vehicle is fully visible")
        st.write("- Check that Ollama is running")
        st.write("- Verify the model is pulled in Ollama")


def render_upload_section() -> Optional[Path]:
    """
    Render the file upload section.

    Returns:
        Path: Path to uploaded file or None
    """
    st.title("Vehicle Damage Analyzer")
    st.write(
        "Upload images of damaged vehicles to get an automated damage "
        "assessment and repair cost estimate."
    )

    uploaded_file = st.file_uploader(
        "Upload a JPEG or PNG image",
        type=["jpeg", "jpg", "png"],
        help="Select an image file to analyze",
    )

    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file
        return Path(uploaded_file.name)

    return None


def analyze_image(file_path: Path, config: Config) -> Optional[dict]:
    """
    Analyze the uploaded image.

    Args:
        file_path: Path to the image file
        config: Configuration instance

    Returns:
        dict: Analysis result or None
    """
    logger = logging.getLogger(__name__)

    try:
        file_handler = FileHandler(config)
        ollama_client = OllamaClient(config)
        image_analyzer = ImageAnalyzer(ollama_client)

        if st.session_state.uploaded_file:
            image_data = st.session_state.uploaded_file.read()
        else:
            image_data = file_handler.read_image(file_path)

        analysis = image_analyzer.analyze_image(image_data)

        if analysis:
            return {"analysis": analysis, "status": "success"}
        else:
            return {
                "analysis": None,
                "status": "failed",
                "error": "Analysis returned no results",
            }

    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        return {"analysis": None, "status": "error", "error": str(e)}


def estimate_costs(analysis_text: str, config: Config) -> Optional[dict]:
    """
    Estimate repair costs based on analysis.

    Args:
        analysis_text: Analysis text from image analyzer
        config: Configuration instance

    Returns:
        dict: Cost estimation result or None
    """
    logger = logging.getLogger(__name__)

    try:
        ollama_client = OllamaClient(config)
        cost_estimator = CostEstimator(ollama_client)

        return cost_estimator.estimate_costs(analysis_text)

    except Exception as e:
        logger.error(f"Cost estimation failed: {e}")
        return {
            "total_cost": 0,
            "detailed_breakdown": [],
            "detected_damages": [],
            "ai_summary": None,
            "status": "error",
            "error": str(e),
        }


def render_analysis_results(analysis_result: dict) -> None:
    """
    Render the analysis results section.

    Args:
        analysis_result: Analysis result dictionary
    """
    st.header("Damage Analysis")

    if analysis_result.get("status") == "success":
        st.markdown(analysis_result.get("analysis", ""))
    else:
        st.error(f"Analysis failed: {analysis_result.get('error', 'Unknown error')}")


def render_cost_results(cost_result: dict) -> None:
    """
    Render the cost estimation results section.

    Args:
        cost_result: Cost estimation result dictionary
    """
    st.header("Cost Estimation")

    if cost_result.get("status") == "success":
        st.metric("Total Estimated Repair Cost", f"${cost_result.get('total_cost', 0)}")

        if cost_result.get("detailed_breakdown"):
            st.subheader("Detailed Breakdown")
            for item in cost_result.get("detailed_breakdown", []):
                st.text(item)

        if cost_result.get("detected_damages"):
            damages = ", ".join(cost_result.get("detected_damages", []))
            st.info(f"Detected Damages: {damages}")

        if cost_result.get("ai_summary"):
            st.subheader("AI Repair Summary")
            st.markdown(cost_result.get("ai_summary"))
    else:
        st.error(f"Cost estimation failed: {cost_result.get('error', 'Unknown error')}")


def download_report(
    analysis_result: dict, cost_result: dict, config: Config
) -> Optional[Path]:
    """
    Generate and provide download link for report.

    Args:
        analysis_result: Analysis result dictionary
        cost_result: Cost estimation result dictionary
        config: Configuration instance

    Returns:
        Path: Path to generated report or None
    """
    try:
        file_handler = FileHandler(config)
        report_generator = ReportGenerator(config, file_handler)

        output_format = st.selectbox("Select output format", ["csv", "txt", "json"])

        report_path = report_generator.generate_single_report(
            {
                "file_name": "uploaded_image",
                "analysis": analysis_result.get("analysis", ""),
                "status": "success",
            },
            cost_result,
            output_format,
        )

        if report_path:
            with open(report_path, "rb") as f:
                st.download_button(
                    label=f"Download Report ({output_format.upper()})",
                    data=f,
                    file_name=report_path.name,
                    mime="text/csv" if output_format == "csv" else "text/plain",
                )

            return report_path

    except Exception as e:
        st.error(f"Failed to generate report: {e}")
        return None


def main() -> None:
    """
    Main function for the Streamlit web UI.
    """
    config = get_config()
    setup_logging(config)
    initialize_session_state()

    st.set_page_config(
        page_title="Vehicle Damage Analyzer", page_icon="🚗", layout="wide"
    )

    render_sidebar(config)

    uploaded_file = render_upload_section()

    if uploaded_file:
        col1, col2 = st.columns([1, 1])

        with col1:
            st.image(
                st.session_state.uploaded_file,
                caption="Uploaded Image",
                use_column_width=True,
            )

        with col2:
            if st.button("Analyze Image", type="primary"):
                with st.spinner("Analyzing image..."):
                    analysis_result = analyze_image(uploaded_file, config)
                    st.session_state.analysis_result = analysis_result

            if st.session_state.analysis_result:
                analysis_result = st.session_state.analysis_result

                render_analysis_results(analysis_result)

                if analysis_result.get("status") == "success":
                    with st.spinner("Estimating costs..."):
                        cost_result = estimate_costs(
                            analysis_result.get("analysis", ""), config
                        )
                        st.session_state.cost_result = cost_result

                    if st.session_state.cost_result:
                        render_cost_results(st.session_state.cost_result)

                        st.divider()
                        st.subheader("Export Report")
                        download_report(
                            st.session_state.analysis_result,
                            st.session_state.cost_result,
                            config,
                        )


if __name__ == "__main__":
    main()
