"""Report Agent for CivicGuardian AI.

Generates a professional downloadable PDF report using ReportLab.
"""

from __future__ import annotations

import io
from datetime import datetime
from typing import Any, Dict, List

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
    )
    _REPORTLAB_AVAILABLE = True
except ImportError:
    _REPORTLAB_AVAILABLE = False


class ReportAgent:
    """Builds a formatted PDF report from the pipeline results."""

    PRIMARY = None
    ACCENT = None

    def __init__(self) -> None:
        if _REPORTLAB_AVAILABLE:
            self.PRIMARY = colors.HexColor("#0B3D91")
            self.ACCENT = colors.HexColor("#138808")
            self.LIGHT = colors.HexColor("#F0F4FA")
            self.GREY = colors.HexColor("#555555")
            self.styles = getSampleStyleSheet()
            self._register_styles()

    def _register_styles(self) -> None:
        if not _REPORTLAB_AVAILABLE:
            return
        custom = {
            "CG_Title": ParagraphStyle(
                name="CG_Title", fontName="Helvetica-Bold", fontSize=22,
                textColor=self.PRIMARY, alignment=TA_CENTER, spaceAfter=4,
            ),
            "CG_Subtitle": ParagraphStyle(
                name="CG_Subtitle", fontName="Helvetica", fontSize=11,
                textColor=self.GREY, alignment=TA_CENTER, spaceAfter=12,
            ),
            "CG_Section": ParagraphStyle(
                name="CG_Section", fontName="Helvetica-Bold", fontSize=14,
                textColor=self.PRIMARY, spaceBefore=14, spaceAfter=6, alignment=TA_LEFT,
            ),
            "CG_Body": ParagraphStyle(
                name="CG_Body", fontName="Helvetica", fontSize=10,
                textColor=colors.black, leading=14, alignment=TA_LEFT,
            ),
            "CG_Small": ParagraphStyle(
                name="CG_Small", fontName="Helvetica", fontSize=8,
                textColor=self.GREY, alignment=TA_CENTER,
            ),
        }
        for name, style in custom.items():
            try:
                self.styles.add(style)
            except Exception:
                pass

    def generate(self, result: Dict[str, Any]) -> bytes:
        """Generate PDF report from pipeline result. Returns raw bytes."""
        if not _REPORTLAB_AVAILABLE:
            return b""

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            leftMargin=20 * mm, rightMargin=20 * mm,
            topMargin=20 * mm, bottomMargin=20 * mm,
        )

        story: List[Any] = []
        profile = result.get("profile", {})
        cards = result.get("cards", [])
        planner = result.get("planner", {})
        readiness = result.get("readiness", {})
        summary = result.get("summary", {})

        # Header
        story.append(Paragraph("🏛️ CivicGuardian AI", self.styles["CG_Title"]))
        story.append(Paragraph("Government Benefits Report", self.styles["CG_Subtitle"]))
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}",
            self.styles["CG_Small"],
        ))
        story.append(HRFlowable(width="100%", thickness=2, color=self.PRIMARY))
        story.append(Spacer(1, 8))

        # Profile section
        story.append(Paragraph("Citizen Profile", self.styles["CG_Section"]))
        profile_data = [
            ["Field", "Value"],
            ["Name", profile.get("name") or profile.get("occupation", "-")],
            ["Occupation", profile.get("occupation", "-")],
            ["Annual Income", f"Rs {int(profile.get('income', 0)):,}"],
            ["Age", str(profile.get("age", "-"))],
            ["State", profile.get("state", "-")],
            ["Gender", profile.get("gender", "-")],
            ["Disability", "Yes" if profile.get("disability") else "No"],
            ["Caste Category", profile.get("caste", "General")],
        ]
        t = Table(profile_data, colWidths=[70 * mm, 100 * mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), self.PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BACKGROUND", (0, 1), (-1, -1), self.LIGHT),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [self.LIGHT, colors.white]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(t)
        story.append(Spacer(1, 12))

        # Summary
        story.append(Paragraph("Benefits Summary", self.styles["CG_Section"]))
        story.append(Paragraph(
            f"Eligible Schemes: {summary.get('eligible_count', 0)} | "
            f"Readiness Score: {readiness.get('score', 0)}% ({readiness.get('level', '')}) | "
            f"Missing Documents: {summary.get('missing_count', 0)}",
            self.styles["CG_Body"],
        ))
        if summary.get("recommendation"):
            story.append(Spacer(1, 6))
            story.append(Paragraph(
                f"AI Recommendation: {summary['recommendation']}",
                self.styles["CG_Body"],
            ))
        story.append(Spacer(1, 8))

        # Eligible Schemes
        story.append(Paragraph("Eligible Government Schemes", self.styles["CG_Section"]))
        if not cards:
            story.append(Paragraph("No schemes matched your current profile.", self.styles["CG_Body"]))
        else:
            scheme_data = [["#", "Scheme Name", "Category", "Match", "Priority", "Benefits"]]
            for i, card in enumerate(cards, 1):
                scheme_data.append([
                    str(i),
                    card.get("name", ""),
                    card.get("category", ""),
                    f"{card.get('match_score', 0)}%",
                    card.get("priority", ""),
                    card.get("benefits", "")[:60] + "..." if len(card.get("benefits", "")) > 60 else card.get("benefits", ""),
                ])
            t2 = Table(scheme_data, colWidths=[8*mm, 55*mm, 25*mm, 15*mm, 20*mm, 47*mm])
            t2.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), self.PRIMARY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [self.LIGHT, colors.white]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("WORDWRAP", (0, 0), (-1, -1), True),
            ]))
            story.append(t2)
        story.append(Spacer(1, 12))

        # Document Status
        story.append(Paragraph("Document Status", self.styles["CG_Section"]))
        uploaded = planner.get("uploaded", [])
        missing = planner.get("missing", [])
        if uploaded:
            story.append(Paragraph(
                f"Documents Available ({len(uploaded)}): {', '.join(uploaded)}",
                self.styles["CG_Body"],
            ))
        if missing:
            story.append(Paragraph(
                f"Documents Missing ({len(missing)}): {', '.join(missing)}",
                self.styles["CG_Body"],
            ))
        story.append(Spacer(1, 8))

        # Action Plan
        action_plan = planner.get("action_plan", [])
        if action_plan:
            story.append(Paragraph("Your Action Plan", self.styles["CG_Section"]))
            ap_data = [["Step", "Document Needed", "Action", "Est. Days"]]
            for step in action_plan:
                ap_data.append([
                    str(step.get("step", "")),
                    step.get("document", ""),
                    step.get("action", "")[:80],
                    str(step.get("estimated_days", 7)),
                ])
            t3 = Table(ap_data, colWidths=[12*mm, 35*mm, 100*mm, 18*mm])
            t3.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), self.ACCENT),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F1F8E9"), colors.white]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            story.append(t3)
            story.append(Spacer(1, 6))
            story.append(Paragraph(
                f"Estimated total preparation time: ~{planner.get('timeline_days', 0)} days",
                self.styles["CG_Body"],
            ))

        # Footer
        story.append(Spacer(1, 16))
        story.append(HRFlowable(width="100%", thickness=1, color=self.GREY))
        story.append(Spacer(1, 4))
        story.append(Paragraph(
            "CivicGuardian AI is an informational tool, not an official government service. "
            "Always verify eligibility on official government portals before applying.",
            self.styles["CG_Small"],
        ))

        doc.build(story)
        buffer.seek(0)
        return buffer.read()
