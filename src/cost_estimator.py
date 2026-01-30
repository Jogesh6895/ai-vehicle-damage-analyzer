"""
Cost Estimator Module

This module handles repair cost estimation based on damage analysis.
"""

import logging
from typing import Dict, List, Optional, Any


class CostEstimator:
    """
    Estimates repair costs based on damage analysis.

    This class calculates repair costs using predefined cost tables
    and AI-generated repair summaries.

    Attributes:
        ollama_client: OllamaClient instance for AI interactions
        logger: Logger instance for this estimator
        repair_costs: Dictionary of repair costs by damage type and severity
    """

    def __init__(self, ollama_client):
        """
        Initialize CostEstimator with Ollama client.

        Args:
            ollama_client: OllamaClient instance for AI model interactions
        """
        self.ollama_client = ollama_client
        self.logger = logging.getLogger(__name__)

        self.repair_costs = {
            "scratches": {"minor": 100, "moderate": 300, "severe": 500},
            "dented_and_crumpled": {"minor": 200, "moderate": 600, "severe": 1000},
            "broken_headlights": {"minor": 150, "moderate": 400, "severe": 800},
            "shattered_windshield": {"minor": 300, "moderate": 800, "severe": 1200},
            "damaged_bumper": {"minor": 250, "moderate": 700, "severe": 1100},
            "crushed_grille": {"minor": 200, "moderate": 500, "severe": 900},
            "crumpled_hood": {"minor": 400, "moderate": 1000, "severe": 2000},
            "damaged_mirrors": {"minor": 100, "moderate": 300, "severe": 500},
            "bent_frame": {"minor": 1000, "moderate": 3000, "severe": 5000},
        }

    def estimate_costs(
        self, analysis_result: str, severity: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Estimate repair costs based on damage analysis.

        Args:
            analysis_result: Text analysis result from image analyzer
            severity: Default severity level if not detected (defaults to "moderate")

        Returns:
            Dict: Cost breakdown including total and detailed breakdown
        """
        try:
            total_cost = 0
            detailed_cost = []
            detected_damages = []

            default_severity = severity or "moderate"
            analysis_lower = analysis_result.lower()

            for damage_type, severity_costs in self.repair_costs.items():
                damage_keyword = damage_type.replace("_", " ")

                if damage_keyword in analysis_lower:
                    detected_damages.append(damage_type)

                    if "severe" in analysis_lower or "major" in analysis_lower:
                        current_severity = "severe"
                    elif "minor" in analysis_lower or "slight" in analysis_lower:
                        current_severity = "minor"
                    else:
                        current_severity = default_severity

                    cost = severity_costs[current_severity]
                    total_cost += cost
                    detailed_cost.append(
                        f"{damage_keyword.replace('_', ' ').title()} "
                        f"({current_severity}): ${cost}"
                    )

            ai_summary = self._generate_ai_summary(analysis_result, total_cost)

            result = {
                "total_cost": total_cost,
                "detailed_breakdown": detailed_cost,
                "detected_damages": detected_damages,
                "ai_summary": ai_summary,
                "status": "success",
            }

            self.logger.info(f"Cost estimation complete: ${total_cost}")
            return result

        except Exception as e:
            self.logger.error(f"Cost estimation failed: {e}")
            return {
                "total_cost": 0,
                "detailed_breakdown": [],
                "detected_damages": [],
                "ai_summary": None,
                "status": "error",
                "error": str(e),
            }

    def _generate_ai_summary(
        self, analysis_result: str, total_cost: int
    ) -> Optional[str]:
        """
        Generate AI-based repair summary.

        Args:
            analysis_result: Text analysis result
            total_cost: Total estimated cost

        Returns:
            str: AI-generated summary or None on error
        """
        prompt = (
            f"Based on the following damages (estimated total cost: ${total_cost}), "
            f"provide a detailed repair cost breakdown and suggestions: {analysis_result}"
        )

        return self.ollama_client.generate_repair_summary(prompt)

    def get_cost_for_damage(
        self, damage_type: str, severity: str = "moderate"
    ) -> Optional[int]:
        """
        Get cost for a specific damage type and severity.

        Args:
            damage_type: Type of damage (e.g., "scratches", "dented_and_crumpled")
            severity: Severity level (minor, moderate, severe)

        Returns:
            int: Cost amount or None if damage type not found
        """
        damage_key = damage_type.lower().replace(" ", "_")

        if damage_key in self.repair_costs:
            if severity in self.repair_costs[damage_key]:
                return self.repair_costs[damage_key][severity]
            else:
                self.logger.warning(
                    f"Severity '{severity}' not found for damage type '{damage_type}'"
                )
                return None
        else:
            self.logger.warning(f"Damage type '{damage_type}' not found in cost table")
            return None

    def update_cost_table(self, damage_type: str, costs: Dict[str, int]) -> bool:
        """
        Update cost table for a damage type.

        Args:
            damage_type: Type of damage to update
            costs: Dictionary of costs by severity (minor, moderate, severe)

        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            damage_key = damage_type.lower().replace(" ", "_")
            self.repair_costs[damage_key] = costs
            self.logger.info(f"Updated cost table for '{damage_type}'")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update cost table: {e}")
            return False

    def get_all_damage_types(self) -> List[str]:
        """
        Get list of all damage types in cost table.

        Returns:
            List: List of damage type names
        """
        return list(self.repair_costs.keys())

    def format_cost_breakdown(self, cost_result: Dict[str, Any]) -> str:
        """
        Format cost result into human-readable string.

        Args:
            cost_result: Cost estimation result from estimate_costs()

        Returns:
            str: Formatted cost breakdown
        """
        if cost_result.get("status") == "error":
            return (
                f"Error estimating costs: {cost_result.get('error', 'Unknown error')}"
            )

        lines = []

        if cost_result.get("detailed_breakdown"):
            lines.append("Cost Breakdown:")
            lines.extend([f"  - {item}" for item in cost_result["detailed_breakdown"]])
            lines.append(f"\nTotal Estimated Repair Cost: ${cost_result['total_cost']}")

        if cost_result.get("ai_summary"):
            lines.append("\nAI Repair Analysis:")
            lines.append(cost_result["ai_summary"])

        return "\n".join(lines)

    def batch_estimate_costs(
        self, analysis_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Estimate costs for multiple analysis results.

        Args:
            analysis_results: List of analysis result dictionaries

        Returns:
            List: List of cost estimation results
        """
        results = []
        total = len(analysis_results)

        self.logger.info(f"Starting batch cost estimation for {total} analyses")

        for idx, analysis in enumerate(analysis_results):
            self.logger.debug(f"Estimating costs {idx + 1}/{total}")

            analysis_text = analysis.get("analysis", "")
            if analysis_text:
                cost_result = self.estimate_costs(analysis_text)
            else:
                cost_result = {
                    "total_cost": 0,
                    "detailed_breakdown": [],
                    "detected_damages": [],
                    "ai_summary": None,
                    "status": "skipped",
                    "error": "No analysis text provided",
                }

            results.append(cost_result)

        self.logger.info("Batch cost estimation complete")
        return results
