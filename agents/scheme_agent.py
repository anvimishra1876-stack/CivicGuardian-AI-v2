"""Scheme Agent for CivicGuardian AI.

Transforms raw scheme database records into rich, display-ready card
dictionaries for the Streamlit UI.
"""

from __future__ import annotations

from typing import Any, Dict, List


class SchemeAgent:
    """Formats eligible scheme records into UI-ready cards."""

    def build_cards(self, schemes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert raw scheme dicts into display cards.

        Args:
            schemes: List of scheme dicts from EligibilityAgent (includes
                     ``match_score`` and ``status``).

        Returns:
            List of formatted card dictionaries.
        """
        return [self._format_card(scheme) for scheme in schemes]

    def _format_card(self, scheme: Dict[str, Any]) -> Dict[str, Any]:
        """Format a single scheme record into a display card.

        Args:
            scheme: Raw scheme dictionary.

        Returns:
            Formatted card dictionary.
        """
        income_limit = scheme.get("income_limit", 0)
        if income_limit == 0:
            income_display = "No limit"
        elif income_limit >= 100_000:
            income_display = f"₹{income_limit // 100_000:.1f}L/year"
        else:
            income_display = f"₹{income_limit:,}/year"

        docs = scheme.get("documents", [])
        docs_display = ", ".join(docs) if docs else "N/A"

        states = scheme.get("states", ["ALL"])
        states_display = "All India" if "ALL" in states else ", ".join(states[:3])
        if len(states) > 3 and "ALL" not in states:
            states_display += f" +{len(states) - 3} more"

        return {
            "id": scheme.get("id", ""),
            "name": scheme.get("name", "Unknown Scheme"),
            "category": scheme.get("category", "General"),
            "description": scheme.get("description", ""),
            "benefits": scheme.get("benefits", ""),
            "priority": str(scheme.get("priority", "Medium")).capitalize(),
            "income_limit_display": income_display,
            "documents_display": docs_display,
            "documents": docs,
            "states_display": states_display,
            "official_website": scheme.get("official_website", "#"),
            "match_score": scheme.get("match_score", 0),
            "status": scheme.get("status", "Eligible"),
            "gender": scheme.get("gender", "ANY"),
        }
