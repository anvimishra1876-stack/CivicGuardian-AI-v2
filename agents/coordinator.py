"""Coordinator Agent for CivicGuardian AI.

Orchestrates the entire multi-agent pipeline end to end.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from agents.document_agent import DocumentAgent
from agents.eligibility_agent import EligibilityAgent
from agents.explainer_agent import ExplainerAgent
from agents.planner_agent import PlannerAgent
from agents.readiness_agent import ReadinessAgent
from agents.report_agent import ReportAgent
from agents.scheme_agent import SchemeAgent
from servers.scheme_server import SchemeServer
from agents.recommendation_agent import RecommendationAgent


class CoordinatorAgent:
    """Top-level orchestrator that wires all agents together."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        data_path: Optional[str] = None,
    ) -> None:
        self.scheme_server = SchemeServer(data_path=data_path)
        self.eligibility_agent = EligibilityAgent(self.scheme_server)
        self.scheme_agent = SchemeAgent()
        self.explainer_agent = ExplainerAgent(api_key=api_key, model_name=model_name)
        self.document_agent = DocumentAgent()
        self.planner_agent = PlannerAgent()
        self.readiness_agent = ReadinessAgent()
        self.report_agent = ReportAgent()
        self.recommendation_agent = RecommendationAgent()

    def run(
        self,
        profile: Dict[str, Any],
        uploads: Optional[List[Dict[str, Any]]] = None,
        explain_limit: int = 3,
        generate_pdf: bool = True,
    ) -> Dict[str, Any]:
        """Run the full navigation pipeline."""
        result: Dict[str, Any] = {"profile": profile, "errors": []}

        # 1) Eligibility.
        try:
            eligible = self.eligibility_agent.evaluate(profile)
        except Exception as exc:
            eligible = []
            result["errors"].append(f"Eligibility error: {exc}")
        result["schemes"] = eligible

        # 2) Scheme formatting.
        try:
            cards = self.scheme_agent.build_cards(eligible)
        except Exception as exc:
            cards = []
            result["errors"].append(f"Scheme formatting error: {exc}")
        result["cards"] = cards

        try:
            recommendations = self.recommendation_agent.recommend(
                profile,
                eligible
            )
        except Exception as exc:
            recommendations = {}
            result["errors"].append(f"Recommendation error: {exc}")

        result["recommendations"] = recommendations


        # 3) Gemini explanations (with built-in fallback).
        try:
            explanations = self.explainer_agent.explain_many(
                profile, eligible, limit=explain_limit
            )
        except Exception as exc:
            explanations = []
            result["errors"].append(f"Explanation error: {exc}")
        result["explanations"] = explanations

       # 4) Document detection.
        try:
            documents = self.document_agent.process_uploads(uploads)
        except Exception as exc:
            documents = {"detected": [], "per_file": {}}
            result["errors"].append(f"Document detection error: {exc}")

        result["documents"] = documents

        # Disable verbose AI document analysis
        result["document_ai"] = {}

        # 5) Planner.
        try:
            planner = self.planner_agent.build_plan(
                eligible, documents.get("detected", [])
            )
        except Exception as exc:
            planner = {
                "required": [], "uploaded": [], "missing": [],
                "action_plan": [], "timeline_days": 0,
            }
            result["errors"].append(f"Planner error: {exc}")
        result["planner"] = planner

        # 6) Readiness.
        try:
            readiness = self.readiness_agent.compute(
                planner.get("required", []), planner.get("uploaded", [])
            )
        except Exception as exc:
            readiness = {
                "score": 0, "level": "Unknown",
                "explanation": "Could not compute readiness.",
                "have_count": 0, "required_count": 0,
            }
            result["errors"].append(f"Readiness error: {exc}")
        result["readiness"] = readiness

        # 6.5) AI Recommendation Summary
        try:
            ai_recommendation = self.explainer_agent.generate_ai_recommendation(
                profile=profile,
                schemes=eligible,
                readiness=readiness,
                planner=planner,
            )
        except Exception as exc:
                ai_recommendation = self.explainer_agent.recommend(profile, eligible)
                result["errors"].append(f"AI Recommendation error: {exc}")

        result["ai_recommendation"] = ai_recommendation

        # Summary.
        result["summary"] = self._build_summary(profile, cards, planner, readiness)

        # 7) PDF report.
        if generate_pdf:
            try:
                result["report_pdf"] = self.report_agent.generate(result)
            except Exception as exc:
                result["report_pdf"] = b""
                result["errors"].append(f"Report error: {exc}")
        else:
            result["report_pdf"] = b""

        result["meta"] = {
            "explainer_source": self.explainer_agent.last_source,
            "gemini_ready": self.explainer_agent.gemini_ready,
            "total_schemes": self.scheme_server.count(),
        }
        return result

    def _build_summary(
        self,
        profile: Dict[str, Any],
        cards: List[Dict[str, Any]],
        planner: Dict[str, Any],
        readiness: Dict[str, Any],
    ) -> Dict[str, Any]:
        top_scheme = cards[0]["name"] if cards else "None found"
        recommendation = self.explainer_agent.recommend(profile, cards)
        return {
            "applicant": profile.get("occupation", "Citizen"),
            "income": profile.get("income", 0),
            "eligible_count": len(cards),
            "readiness_score": readiness.get("score", 0),
            "top_scheme": top_scheme,
            "missing_count": len(planner.get("missing", [])),
            "missing_documents": planner.get("missing", []),
            "recommendation": recommendation,
        }
