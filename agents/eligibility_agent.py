"""Eligibility Agent for CivicGuardian AI.

Evaluates which government schemes a citizen qualifies for based on their
profile. Applies income, age, gender, state, disability, and caste filters
and computes a match score for ranking.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from servers.scheme_server import SchemeServer


class EligibilityAgent:
    """Filters schemes from the database against a user profile."""

    def __init__(self, scheme_server: SchemeServer) -> None:
        self.scheme_server = scheme_server

    def evaluate(self, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Return eligible schemes, sorted by match score (descending)."""
        schemes = self.scheme_server.get_all_schemes()
        results = []

        for scheme in schemes:
            eligible, score = self._check_eligibility(profile, scheme)
            if eligible:
                enriched = dict(scheme)
                enriched["match_score"] = score
                enriched["status"] = "Eligible"
                results.append(enriched)

        priority_order = {"high": 0, "medium": 1, "low": 2}
        results.sort(
            key=lambda s: (
                -s["match_score"],
                priority_order.get(str(s.get("priority", "medium")).lower(), 1),
            )
        )
        return results

    def _check_eligibility(
        self, profile: Dict[str, Any], scheme: Dict[str, Any]
    ) -> Tuple[bool, int]:
        """Check if a profile meets a scheme's criteria."""
        score = 80  # Base score

        # Income check
        income_limit = scheme.get("income_limit", 0)
        user_income = int(profile.get("income", 0))
        if income_limit > 0 and user_income > income_limit:
            return False, 0
        if income_limit > 0:
            income_ratio = user_income / income_limit
            score -= int(income_ratio * 10)

        # Age check
        user_age = int(profile.get("age", 0))
        min_age = scheme.get("min_age", 0)
        max_age = scheme.get("max_age", 120)
        if user_age < min_age or user_age > max_age:
            return False, 0

        # Occupation / Category match
        occupation = str(profile.get("occupation", "Other")).strip()
        scheme_category = str(scheme.get("category", "Other")).strip()
        category_map = {
            "Farmer": ["Farmer"],
            "Student": ["Student", "Education"],
            "Entrepreneur": ["Entrepreneur", "Business", "MSME"],
            "Senior Citizen": ["Senior Citizen", "Pension"],
        }
        universal_cats = {"General", "All", "Healthcare", "Insurance", "Housing"}

        if scheme_category in universal_cats:
            score += 5
        elif occupation == "Other":
            if scheme_category not in universal_cats:
                score -= 15
        elif scheme_category in category_map.get(occupation, []):
            score += 15
        else:
            if scheme_category not in universal_cats:
                return False, 0

        # State check
        scheme_states = scheme.get("states", ["ALL"])
        user_state = str(profile.get("state", "")).strip()
        if "ALL" not in scheme_states and user_state not in scheme_states:
            return False, 0
        if "ALL" not in scheme_states and user_state in scheme_states:
            score += 5  # State-specific bonus

        # Gender check
        scheme_gender = str(scheme.get("gender", "ANY")).upper()
        user_gender = str(profile.get("gender", "OTHER")).upper()
        if scheme_gender not in ("ANY", "ALL") and scheme_gender != user_gender:
            return False, 0

        # Disability
        scheme_disability = scheme.get("disability_only", False)
        user_disability = bool(profile.get("disability", False))
        if scheme_disability and not user_disability:
            return False, 0
        if user_disability and scheme.get("disability_benefit", False):
            score += 10

        # Caste
        scheme_caste = scheme.get("caste", [])
        user_caste = str(profile.get("caste", "General")).strip()
        if scheme_caste and "ALL" not in scheme_caste:
            if user_caste not in scheme_caste:
                return False, 0

        return True, max(0, min(100, score))
