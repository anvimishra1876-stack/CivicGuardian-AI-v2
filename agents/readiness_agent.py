"""Readiness Agent for CivicGuardian AI.

Computes an application readiness score based on how many required
documents the user has already prepared.
"""

from __future__ import annotations

from typing import Any, Dict, List


class ReadinessAgent:
    """Computes application readiness from document availability."""

    def compute(
        self,
        required: List[str],
        uploaded: List[str],
    ) -> Dict[str, Any]:
        """Calculate readiness score and descriptive level.

        Args:
            required: All documents required for eligible schemes.
            uploaded: Documents the user has provided.

        Returns:
            Dict with ``score`` (0-100), ``level``, ``explanation``,
            ``have_count``, and ``required_count``.
        """
        required_count = len(required)
        have_count = len(uploaded)

        if required_count == 0:
            # No schemes found or no documents needed.
            score = 50
            level = "Partial"
            explanation = "No required documents identified yet. Fill in your profile and run the analysis."
        else:
            score = int((have_count / required_count) * 100)
            if score >= 90:
                level = "Ready"
                explanation = "🎉 Excellent! You have almost all required documents. You can apply now."
            elif score >= 70:
                level = "Almost Ready"
                explanation = f"You have {have_count} of {required_count} required documents. Gather the remaining ones before applying."
            elif score >= 40:
                level = "In Progress"
                explanation = f"You have {have_count} of {required_count} required documents. Follow the action plan below."
            else:
                level = "Needs Preparation"
                explanation = f"You have {have_count} of {required_count} required documents. Start with Aadhaar and PAN card first."

        return {
            "score": score,
            "level": level,
            "explanation": explanation,
            "have_count": have_count,
            "required_count": required_count,
        }
