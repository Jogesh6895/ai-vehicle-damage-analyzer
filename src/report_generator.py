"""
Report Generator Module

This module handles report generation for damage analysis and cost estimates.
"""

import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import pandas as pd


class ReportGenerator:
    """
    Generates reports for damage analysis and cost estimates.

    This class creates detailed reports in various formats including
    CSV, text, and structured data formats.

    Attributes:
        config: Configuration instance containing output directory
        logger: Logger instance for this generator
    """

    def __init__(self, config, file_handler):
        """
        Initialize ReportGenerator with configuration and file handler.

        Args:
            config: Configuration instance with output directory settings
            file_handler: FileHandler instance for file operations
        """
        self.config = config
        self.file_handler = file_handler
        self.logger = logging.getLogger(__name__)

    def generate_single_report(
        self,
        analysis_result: Dict[str, Any],
        cost_result: Dict[str, Any],
        output_format: str = "csv",
    ) -> Optional[Path]:
        """
        Generate a single report for one image analysis.

        Args:
            analysis_result: Analysis result from image analyzer
            cost_result: Cost estimation result from cost estimator
            output_format: Output format (csv, txt, json)

        Returns:
            Path: Path to generated report file or None on error
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"damage_report_{timestamp}"

            report_data = self._compile_report_data(analysis_result, cost_result)

            if output_format == "csv":
                filepath = self._generate_csv_report(report_data, filename)
            elif output_format == "txt":
                filepath = self._generate_text_report(report_data, filename)
            elif output_format == "json":
                filepath = self._generate_json_report(report_data, filename)
            else:
                self.logger.error(f"Unsupported output format: {output_format}")
                return None

            self.logger.info(f"Report generated: {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"Failed to generate report: {e}")
            return None

    def generate_batch_report(
        self, results: List[Dict[str, Any]], output_format: str = "csv"
    ) -> Optional[Path]:
        """
        Generate a batch report for multiple image analyses.

        Args:
            results: List of combined analysis and cost results
            output_format: Output format (csv, txt, json)

        Returns:
            Path: Path to generated batch report file or None on error
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"batch_report_{timestamp}"

            batch_data = self._compile_batch_data(results)

            if output_format == "csv":
                filepath = self._generate_batch_csv_report(batch_data, filename)
            elif output_format == "txt":
                filepath = self._generate_batch_text_report(batch_data, filename)
            elif output_format == "json":
                filepath = self._generate_batch_json_report(batch_data, filename)
            else:
                self.logger.error(f"Unsupported output format: {output_format}")
                return None

            self.logger.info(f"Batch report generated: {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"Failed to generate batch report: {e}")
            return None

    def _compile_report_data(
        self, analysis_result: Dict[str, Any], cost_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compile report data from analysis and cost results.

        Args:
            analysis_result: Analysis result from image analyzer
            cost_result: Cost estimation result

        Returns:
            Dict: Compiled report data
        """
        return {
            "file_name": analysis_result.get("file_name", "Unknown"),
            "file_path": analysis_result.get("file_path", ""),
            "analysis": analysis_result.get("analysis", ""),
            "total_cost": cost_result.get("total_cost", 0),
            "detailed_breakdown": "\n".join(cost_result.get("detailed_breakdown", [])),
            "detected_damages": ", ".join(cost_result.get("detected_damages", [])),
            "ai_summary": cost_result.get("ai_summary", ""),
            "status": analysis_result.get("status", "unknown"),
            "generated_at": datetime.now().isoformat(),
        }

    def _compile_batch_data(
        self, results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Compile batch data from multiple results.

        Args:
            results: List of combined analysis and cost results

        Returns:
            List: List of compiled report data
        """
        batch_data = []

        for result in results:
            analysis = result.get("analysis", {})
            costs = result.get("costs", {})

            report_data = self._compile_report_data(analysis, costs)
            batch_data.append(report_data)

        return batch_data

    def _generate_csv_report(self, data: Dict[str, Any], filename: str) -> Path:
        """
        Generate CSV format report.

        Args:
            data: Report data dictionary
            filename: Base filename (without extension)

        Returns:
            Path: Path to generated CSV file
        """
        csv_data = {
            "File Name": [data.get("file_name")],
            "File Path": [data.get("file_path")],
            "Damage Analysis": [data.get("analysis")],
            "Total Cost": [data.get("total_cost")],
            "Cost Breakdown": [data.get("detailed_breakdown")],
            "Detected Damages": [data.get("detected_damages")],
            "AI Summary": [data.get("ai_summary")],
            "Status": [data.get("status")],
            "Generated At": [data.get("generated_at")],
        }

        return self.file_handler.write_report(csv_data, f"{filename}.csv")

    def _generate_text_report(self, data: Dict[str, Any], filename: str) -> Path:
        """
        Generate text format report.

        Args:
            data: Report data dictionary
            filename: Base filename (without extension)

        Returns:
            Path: Path to generated text file
        """
        lines = []
        lines.append("=" * 80)
        lines.append("VEHICLE DAMAGE ANALYSIS REPORT")
        lines.append("=" * 80)
        lines.append(f"File Name: {data.get('file_name')}")
        lines.append(f"File Path: {data.get('file_path')}")
        lines.append(f"Generated At: {data.get('generated_at')}")
        lines.append(f"Status: {data.get('status')}")
        lines.append("")

        lines.append("-" * 80)
        lines.append("DAMAGE ANALYSIS")
        lines.append("-" * 80)
        lines.append(data.get("analysis", "No analysis available"))
        lines.append("")

        lines.append("-" * 80)
        lines.append("COST ESTIMATION")
        lines.append("-" * 80)
        lines.append(f"Total Estimated Cost: ${data.get('total_cost', 0)}")
        lines.append("")

        if data.get("detailed_breakdown"):
            lines.append("Cost Breakdown:")
            for line in data.get("detailed_breakdown", "").split("\n"):
                if line.strip():
                    lines.append(f"  {line}")
            lines.append("")

        if data.get("detected_damages"):
            lines.append(f"Detected Damages: {data.get('detected_damages')}")
            lines.append("")

        if data.get("ai_summary"):
            lines.append("-" * 80)
            lines.append("AI REPAIR SUMMARY")
            lines.append("-" * 80)
            lines.append(data.get("ai_summary"))

        lines.append("=" * 80)

        content = "\n".join(lines)
        return self.file_handler.write_text_report(content, f"{filename}.txt")

    def _generate_json_report(self, data: Dict[str, Any], filename: str) -> Path:
        """
        Generate JSON format report.

        Args:
            data: Report data dictionary
            filename: Base filename (without extension)

        Returns:
            Path: Path to generated JSON file
        """
        import json

        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        filepath = output_dir / f"{filename}.json"

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return filepath

    def _generate_batch_csv_report(
        self, data: List[Dict[str, Any]], filename: str
    ) -> Path:
        """
        Generate batch CSV report.

        Args:
            data: List of report data dictionaries
            filename: Base filename (without extension)

        Returns:
            Path: Path to generated CSV file
        """
        csv_data = {
            "File Name": [d.get("file_name") for d in data],
            "File Path": [d.get("file_path") for d in data],
            "Total Cost": [d.get("total_cost") for d in data],
            "Detected Damages": [d.get("detected_damages") for d in data],
            "Status": [d.get("status") for d in data],
            "Generated At": [d.get("generated_at") for d in data],
        }

        return self.file_handler.write_report(csv_data, f"{filename}.csv")

    def _generate_batch_text_report(
        self, data: List[Dict[str, Any]], filename: str
    ) -> Path:
        """
        Generate batch text report.

        Args:
            data: List of report data dictionaries
            filename: Base filename (without extension)

        Returns:
            Path: Path to generated text file
        """
        lines = []
        lines.append("=" * 80)
        lines.append(f"BATCH VEHICLE DAMAGE ANALYSIS REPORT")
        lines.append(f"Total Images: {len(data)}")
        lines.append(f"Generated At: {datetime.now().isoformat()}")
        lines.append("=" * 80)
        lines.append("")

        successful = sum(1 for d in data if d.get("status") == "success")
        failed = sum(1 for d in data if d.get("status") != "success")

        lines.append(f"Summary: {successful} successful, {failed} failed")
        lines.append("")

        lines.append("-" * 80)

        for idx, item in enumerate(data, 1):
            lines.append(f"Image {idx}: {item.get('file_name')}")
            lines.append(f"  Status: {item.get('status')}")
            lines.append(f"  Total Cost: ${item.get('total_cost', 0)}")
            lines.append(f"  Damages: {item.get('detected_damages', 'None')}")
            lines.append("")

        lines.append("=" * 80)

        content = "\n".join(lines)
        return self.file_handler.write_text_report(content, f"{filename}.txt")

    def _generate_batch_json_report(
        self, data: List[Dict[str, Any]], filename: str
    ) -> Path:
        """
        Generate batch JSON report.

        Args:
            data: List of report data dictionaries
            filename: Base filename (without extension)

        Returns:
            Path: Path to generated JSON file
        """
        import json

        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        filepath = output_dir / f"{filename}.json"

        batch_report = {
            "total_images": len(data),
            "successful": sum(1 for d in data if d.get("status") == "success"),
            "failed": sum(1 for d in data if d.get("status") != "success"),
            "generated_at": datetime.now().isoformat(),
            "reports": data,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(batch_report, f, indent=2)

        return filepath
