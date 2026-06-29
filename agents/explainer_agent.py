"""Explainer Agent for CivicGuardian AI.

Generates personalised explanations via Google Gemini with rule-based fallback.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

try:
    import google.generativeai as genai
    _GENAI_AVAILABLE = True
except Exception:
    genai = None  # type: ignore
    _GENAI_AVAILABLE = False


class ExplainerAgent:
    """Produces explanations via Gemini with a robust rule-based fallback."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self._model = None
        self.last_source = "rule-based"

        if _GENAI_AVAILABLE and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self._model = genai.GenerativeModel(self.model_name)
            except Exception:
                self._model = None

    @property
    def gemini_ready(self) -> bool:
        return self._model is not None

    # def _build_prompt(self, profile: Dict[str, Any], scheme: Dict[str, Any]) -> str:
    #     return (
    #         "You are CivicGuardian, an expert advisor on Indian government "
    #         "welfare schemes. Explain in clear, encouraging, simple English.\n\n"
    #         f"User profile:\n"
    #         f"- Occupation: {profile.get('occupation')}\n"
    #         f"- Annual income: Rs {profile.get('income')}\n"
    #         f"- Age: {profile.get('age')}\n"
    #         f"- State: {profile.get('state')}\n"
    #         f"- Gender: {profile.get('gender')}\n"
    #         f"- Disability: {'Yes' if profile.get('disability') else 'No'}\n"
    #         f"- Caste: {profile.get('caste', 'General')}\n\n"
    #         f"Scheme: {scheme.get('name')}\n"
    #         f"Description: {scheme.get('description')}\n"
    #         f"Benefits: {scheme.get('benefits')}\n"
    #         f"Required documents: {', '.join(scheme.get('documents', []))}\n\n"
    #         "Write a concise explanation with these four short sections:\n"
    #         "Why You Qualify:\n"
    #         "Key Benefits:\n"
    #         "How To Apply:\n"
    #         "Next Steps:\n"
    #         "Keep it under 200 words. Do not invent facts."
    #     )

    def _build_prompt(self, profile: Dict[str, Any], scheme: Dict[str, Any]) -> str:

            return f"""
        You are CivicGuardian AI, an expert Government Benefits Advisor for India.

        Your task is NOT to summarize the scheme.

        Instead, analyze whether this scheme is a strong recommendation for the citizen based on their profile.

        Be practical, encouraging, and accurate.

        Never invent eligibility rules.

        ----------------------------------------------------
        Citizen Profile

        Occupation: {profile.get("occupation")}
        Age: {profile.get("age")}
        Annual Income: ₹{profile.get("income")}
        State: {profile.get("state")}
        Gender: {profile.get("gender")}
        Category: {profile.get("caste")}
        Disability: {"Yes" if profile.get("disability") else "No"}

        ----------------------------------------------------
        Government Scheme

        Name:
        {scheme.get("name")}

        Description:
        {scheme.get("description")}

        Benefits:
        {scheme.get("benefits")}

        Required Documents:
        {", ".join(scheme.get("documents", []))}

        Match Score:
        {scheme.get("match_score")}%

        ----------------------------------------------------

        Write your response using EXACTLY these headings:

        ## Recommendation

        Should this citizen prioritize this scheme?
        Explain why.

        ## Why this scheme matches

        Mention profile attributes that match.

        ## Benefits for this citizen

        Explain the practical benefits.

        ## Documents Required

        Mention the important documents.

        ## Suggested Next Action

        Tell the citizen exactly what they should do next.

        Keep the response under 250 words.

        Do NOT make up benefits or eligibility rules.
        """

    def _rule_based_explanation(self, profile: Dict[str, Any], scheme: Dict[str, Any]) -> str:
        occupation = profile.get("occupation", "citizen")
        income = profile.get("income", 0)
        docs = scheme.get("documents", [])
        docs_text = ", ".join(docs) if docs else "standard identity documents"

        why = (
            f"As a {occupation.lower()} with an annual income of Rs {income:,}, "
            f"you fall within the eligibility limits for {scheme.get('name')}. "
            "Your profile matches the scheme's age, income, and category criteria."
        )
        benefits = scheme.get("benefits", "Financial and welfare support.")
        apply = (
            f"Visit the official portal at {scheme.get('official_website', 'the government website')}, "
            "register or log in, complete the application form, upload the required "
            f"documents ({docs_text}), and submit for verification."
        )
        steps = (
            "1) Keep your documents ready and self-attested. "
            "2) Verify your bank account is linked to Aadhaar for Direct Benefit Transfer. "
            "3) Track your application status online after submission."
        )
        return (
            f"Why You Qualify:\n{why}\n\n"
            f"Key Benefits:\n{benefits}\n\n"
            f"How To Apply:\n{apply}\n\n"
            f"Next Steps:\n{steps}"
        )

    def explain(self, profile: Dict[str, Any], scheme: Dict[str, Any]) -> Dict[str, Any]:
        if self.gemini_ready:
            try:
                prompt = self._build_prompt(profile, scheme)
                response = self._model.generate_content(prompt)  # type: ignore
                text = (getattr(response, "text", "") or "").strip()
                if text:
                    self.last_source = "gemini"
                    return {
                        "scheme_id": scheme.get("id", ""),
                        "scheme_name": scheme.get("name", ""),
                        "text": text,
                        "source": "gemini",
                    }
            except Exception as e:
                print("Gemini Error:", e)

        self.last_source = "rule-based"
        return {
            "scheme_id": scheme.get("id", ""),
            "scheme_name": scheme.get("name", ""),
            "text": self._rule_based_explanation(profile, scheme),
            "source": "rule-based",
        }

    def explain_many(self, profile: Dict[str, Any], schemes: List[Dict[str, Any]], limit: int = 3) -> List[Dict[str, Any]]:
        return [self.explain(profile, scheme) for scheme in schemes[:limit]]

    def recommend(self, profile: Dict[str, Any], schemes: List[Dict[str, Any]]) -> str:
        if not schemes:
            return (
                "Based on the details provided, we could not match an active scheme. "
                "Try adjusting your income or exploring schemes in a different category."
            )
        top = schemes[0]
        count = len(schemes)
        return (
            f"We found {count} eligible scheme(s) for you. We recommend prioritising "
            f"'{top.get('name')}' ({top.get('match_score', 0)}% match) — it offers strong "
            f"benefits for your profile as a {profile.get('occupation', 'citizen').lower()}. "
            "Prepare your documents and apply via the official portal."
        )
    
    def generate_ai_recommendation(
    self,
    profile: Dict[str, Any],
    schemes: List[Dict[str, Any]],
    readiness: Dict[str, Any],
    planner: Dict[str, Any],
) -> str:

        if not schemes:
            return "No suitable schemes were found."

        prompt = f"""
        You are CivicGuardian AI, an expert advisor on Indian Government welfare schemes.

        Analyze the citizen profile and ALL eligible schemes together.

        Citizen Profile

        Occupation: {profile.get("occupation")}
        Age: {profile.get("age")}
        Income: ₹{profile.get("income")}
        State: {profile.get("state")}
        Gender: {profile.get("gender")}
        Category: {profile.get("caste")}

        Eligible Schemes:

        {chr(10).join([f"- {s['name']} (Match Score: {s.get('match_score',0)}%)" for s in schemes])}

        Readiness Score:

        {readiness.get("score")}%

        Missing Documents:

        {", ".join(planner.get("missing", []))}

        Respond using EXACTLY these headings:

        ## 🏆 Best Scheme

        ## ⭐ Confidence

        Give a confidence percentage.

        ## 📌 Why this is your best option

        Three bullet points.

        ## 📋 Immediate Next Steps

        Numbered list.

        ## ⚠ Missing Documents

        List missing documents.

        ## 🥈 Alternative Schemes

        Mention two alternatives.

        Keep under 250 words.
        """

        if self.gemini_ready:
                try:
                    response = self._model.generate_content(prompt)
                    text = (getattr(response, "text", "") or "").strip()

                    if text:
                        return text

                except Exception as e:
                    print("Recommendation Error:", e)

        return self.recommend(profile, schemes)
        
    def analyze_document(
        self,
        extracted_text: str,
    ) -> str:

            prompt = f"""
    You are an AI Government Document Verification Assistant.

    Analyze the following document text.

    Identify:

    1. Document Type

    2. Important Information
    (Name, Income, Aadhaar Number, PAN, etc.)

    3. Confidence (0-100)

    4. Verification Status

    5. Which government schemes could use this document.

    Return your answer in markdown.

    Document:

        {extracted_text[:5000]}
        """

            if self.gemini_ready:
                try:
                    response = self._model.generate_content(prompt)

                    if response.text:
                        return response.text

                except Exception as e:
                    print(e)

            return "AI analysis unavailable."
