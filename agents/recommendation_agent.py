"""
Recommendation Agent for CivicGuardian AI.

Adds explainable AI recommendations on top of the rule-based
eligibility engine.
"""

from typing import List, Dict, Any


class RecommendationAgent:
    """Builds personalized recommendations for eligible schemes."""

    def recommend(
        self,
        profile: Dict[str, Any],
        schemes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        if not schemes:
            return {
                "top_scheme": None,
                "confidence": 0,
                "reasoning": [],
                "next_steps": [],
                "alternatives": []
            }

        top_scheme = schemes[0]

        reasoning = self._build_reasoning(profile, top_scheme)

        confidence = self._calculate_confidence(profile, top_scheme)

        next_steps = self._next_steps(top_scheme)

        alternatives = [
            scheme["name"]
            for scheme in schemes[1:4]
        ]

        return {
            "top_scheme": top_scheme["name"],
            "confidence": confidence,
            "reasoning": reasoning,
            "next_steps": next_steps,
            "alternatives": alternatives,
        }

    def _calculate_confidence(
        self,
        profile: Dict[str, Any],
        scheme: Dict[str, Any]
    ) -> int:

        confidence = scheme.get("match_score", 80)

        if profile.get("income", 0):
            confidence += 2

        if profile.get("occupation"):
            confidence += 2

        if profile.get("state"):
            confidence += 2

        return min(confidence, 100)

    def _build_reasoning(
        self,
        profile: Dict[str, Any],
        scheme: Dict[str, Any]
    ) -> List[str]:

        reasons = []

        reasons.append(
            f"You satisfy the eligibility requirements for {scheme['name']}."
        )

        reasons.append(
            f"Your occupation ({profile.get('occupation')}) aligns with the target beneficiaries."
        )

        reasons.append(
            f"Your income falls within the permitted limit."
        )

        reasons.append(
            "The scheme has been ranked highly based on your profile."
        )

        return reasons

    def _next_steps(
        self,
        scheme: Dict[str, Any]
    ) -> List[str]:

        return [
            "Review scheme details.",
            "Upload any missing documents.",
            "Visit the official application portal.",
            "Submit your application."
        ]