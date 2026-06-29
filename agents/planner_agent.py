"""Planner Agent for CivicGuardian AI.

Builds a personalized document action plan by comparing the documents
required for all eligible schemes against the documents already uploaded
by the user.
"""

from __future__ import annotations

from typing import Any, Dict, List


# Estimated days to obtain each type of document.
DOCUMENT_TIMELINES: Dict[str, int] = {
    "Aadhaar": 3,
    "PAN": 15,
    "Income Certificate": 7,
    "Land Record": 10,
    "Bank Passbook": 2,
    "Caste Certificate": 14,
    "Disability Certificate": 21,
    "Birth Certificate": 7,
    "Marksheet": 5,
    "Voter ID": 30,
    "Ration Card": 14,
    "Domicile Certificate": 10,
}

DEFAULT_TIMELINE = 7  # Days for unknown documents.

DOCUMENT_ACTIONS: Dict[str, str] = {
    "Aadhaar": "Visit nearest Aadhaar Seva Kendra or update online at uidai.gov.in",
    "PAN": "Apply online at tin.tin.nsdl.com or incometaxindiaefiling.gov.in",
    "Income Certificate": "Apply at your local Tehsil/Block office with salary slips",
    "Land Record": "Obtain from local Patwari or state land records portal",
    "Bank Passbook": "Collect from your nearest bank branch",
    "Caste Certificate": "Apply at Sub-Divisional Magistrate (SDM) office",
    "Disability Certificate": "Obtain from Chief Medical Officer at district hospital",
    "Birth Certificate": "Apply at municipal/panchayat office or online portal",
    "Marksheet": "Collect from your school/college/university",
    "Voter ID": "Apply online at voters.eci.gov.in or nearest BLO office",
    "Ration Card": "Apply at Food & Civil Supplies department office",
    "Domicile Certificate": "Apply at Tehsil/SDM office with residence proof",
}


class PlannerAgent:
    """Creates a prioritized document checklist and action plan."""

    def build_plan(
        self,
        eligible_schemes: List[Dict[str, Any]],
        uploaded_documents: List[str],
    ) -> Dict[str, Any]:
        """Build a document readiness plan for the user.

        Args:
            eligible_schemes: List of eligible scheme dicts (with ``documents`` list).
            uploaded_documents: Document types the user has uploaded.

        Returns:
            Dict with ``required``, ``uploaded``, ``missing``, ``action_plan``,
            and ``timeline_days``.
        """
        # Collect all required documents across eligible schemes.
        required_set: set[str] = set()
        for scheme in eligible_schemes:
            docs = scheme.get("documents", [])
            if isinstance(docs, list):
                required_set.update(docs)

        required = sorted(required_set)
        uploaded_set = set(uploaded_documents)

        # Identify what's available and what's missing.
        uploaded = sorted(required_set & uploaded_set)
        missing = sorted(required_set - uploaded_set)

        # Build step-by-step action plan for missing documents.
        action_plan = []
        for i, doc in enumerate(missing, start=1):
            action = DOCUMENT_ACTIONS.get(doc, f"Obtain {doc} from the relevant government office")
            action_plan.append({
                "step": i,
                "document": doc,
                "action": action,
                "estimated_days": DOCUMENT_TIMELINES.get(doc, DEFAULT_TIMELINE),
            })

        # Estimate total timeline (parallel processing, take max).
        timeline_days = max(
            (DOCUMENT_TIMELINES.get(doc, DEFAULT_TIMELINE) for doc in missing),
            default=0,
        )

        return {
            "required": required,
            "uploaded": uploaded,
            "missing": missing,
            "action_plan": action_plan,
            "timeline_days": timeline_days,
        }
