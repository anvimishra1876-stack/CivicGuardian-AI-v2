"""CivicGuardian AI - Streamlit application entry point.

An intelligent multi-agent government benefits navigator that helps citizens
discover schemes, verify documents, and prepare applications. This module
builds the entire user interface and delegates all business logic to the
CoordinatorAgent and its sub-agents.

Run with:
    streamlit run app.py
"""

from __future__ import annotations

import os
from typing import Any, Dict, List

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from agents.coordinator import CoordinatorAgent

# Load environment variables from a .env file if present.
load_dotenv()

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #
APP_TITLE = "CivicGuardian AI"
APP_TAGLINE = "Your Intelligent Government Benefits Navigator"

OCCUPATIONS = ["Student", "Farmer", "Entrepreneur", "Senior Citizen", "Other"]
GENDERS = ["Male", "Female", "Other"]
STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
    "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
    "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand",
    "West Bengal", "Delhi", "Jammu & Kashmir", "Ladakh", "Puducherry",
]


# --------------------------------------------------------------------------- #
# Styling
# --------------------------------------------------------------------------- #
def inject_css() -> None:
    """Inject custom CSS for a modern, award-worthy government dashboard."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        :root {
            --cg-primary:      #0B3D91;
            --cg-primary-dark: #072d6e;
            --cg-accent:       #138808;
            --cg-accent-light: #1aab0a;
            --cg-bg:           #EEF2F9;
            --cg-card:         #FFFFFF;
            --cg-text:         #111827;
            --cg-muted:        #6B7280;
            --cg-border:       #DDE3EF;
            --cg-shadow:       0 4px 20px rgba(11,61,145,0.10);
        }

        /* ── Global ── */
        html, body, [class*="css"] { font-family: 'Inter', 'Segoe UI', sans-serif !important; }
        .stApp { background: var(--cg-bg) !important; }
        .block-container { padding-top: 1.4rem !important; max-width: 1200px !important; }

        /* ── SIDEBAR — fixed white-text-on-white bug ── */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #071e47 0%, #0B2A5B 60%, #0d3366 100%) !important;
        }

        /* Labels — light blue, readable on dark background */
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] .stTextInput label,
        section[data-testid="stSidebar"] .stNumberInput label,
        section[data-testid="stSidebar"] .stSelectbox label,
        section[data-testid="stSidebar"] .stFileUploader label,
        section[data-testid="stSidebar"] .stCheckbox label,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p {
            color: #C5D5F0 !important;
            font-size: 0.83rem !important;
            font-weight: 500 !important;
        }

        /* Sidebar headings */
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }

        /* Input fields — WHITE background, DARK text so text is always visible */
        section[data-testid="stSidebar"] input[type="text"],
        section[data-testid="stSidebar"] input[type="number"],
        section[data-testid="stSidebar"] textarea {
            background: #FFFFFF !important;
            color: #111827 !important;
            border: 1.5px solid #3A5FA0 !important;
            border-radius: 8px !important;
        }
        section[data-testid="stSidebar"] input[type="text"]::placeholder,
        section[data-testid="stSidebar"] input[type="number"]::placeholder {
            color: #9CA3AF !important;
        }

        /* Selectbox container — white bg, dark text */
        section[data-testid="stSidebar"] .stSelectbox > div > div,
        section[data-testid="stSidebar"] [data-baseweb="select"] > div {
            background: #FFFFFF !important;
            color: #111827 !important;
            border: 1.5px solid #3A5FA0 !important;
            border-radius: 8px !important;
        }
        section[data-testid="stSidebar"] [data-baseweb="select"] span {
            color: #111827 !important;
        }

        /* Selectbox dropdown list items */
        [data-baseweb="popover"] li,
        [data-baseweb="menu"] li {
            color: #111827 !important;
            background: #fff !important;
        }
        [data-baseweb="popover"] li:hover,
        [data-baseweb="menu"] li:hover {
            background: #EEF2F9 !important;
        }

        /* Number input stepper buttons */
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepDown"],
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepUp"] {
            color: #0B3D91 !important;
            background: #E8EEF8 !important;
        }

        /* Checkbox */
        section[data-testid="stSidebar"] .stCheckbox span {
            color: #C5D5F0 !important;
        }

        /* File uploader */
        section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
            background: rgba(255,255,255,0.08) !important;
            border: 1.5px dashed #4A70B0 !important;
            border-radius: 10px !important;
        }
        section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] p,
        section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] span {
            color: #A0B8DC !important;
        }

        /* Caption / small text */
        section[data-testid="stSidebar"] small,
        section[data-testid="stSidebar"] .stCaption {
            color: #7A9BC8 !important;
        }

        /* Sidebar divider */
        section[data-testid="stSidebar"] hr {
            border-color: rgba(255,255,255,0.15) !important;
        }

        /* ── Hero Banner ── */
        .cg-hero {
            background: linear-gradient(125deg, #0B3D91 0%, #1258CC 55%, #138808 100%);
            border-radius: 20px;
            padding: 30px 36px;
            color: #fff;
            box-shadow: 0 12px 40px rgba(11,61,145,0.30);
            margin-bottom: 22px;
            position: relative;
            overflow: hidden;
        }
        .cg-hero::after {
            content: "🏛️";
            position: absolute;
            right: 30px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 5rem;
            opacity: 0.12;
        }
        .cg-hero h1 { margin: 0; font-size: 2.2rem; font-weight: 800; letter-spacing: -0.6px; }
        .cg-hero p  { margin: 7px 0 0; font-size: 1.02rem; opacity: 0.92; }
        .cg-hero .version { font-size: 0.73rem; opacity: 0.65; margin-top: 10px; letter-spacing: 0.3px; }

        /* ── Cards ── */
        .cg-card {
            background: var(--cg-card);
            border-radius: 18px;
            padding: 22px 24px;
            box-shadow: var(--cg-shadow);
            border: 1px solid var(--cg-border);
            margin-bottom: 18px;
        }
        .cg-card h3 { margin: 0 0 8px; color: #0B3D91 !important; font-size: 1.15rem; font-weight: 700; }
        .cg-card p  { margin: 7px 0; color: #111827 !important; font-size: 0.94rem; line-height: 1.55; }
        .cg-card b, .cg-card strong { color: #111827 !important; }
        .cg-card span { color: inherit; }

        /* ── Badges ── */
        .cg-badge {
            display: inline-block; padding: 3px 11px; border-radius: 999px;
            font-size: 0.7rem; font-weight: 700; margin-right: 5px; color: #fff;
        }
        .cg-badge-high   { background: #C62828; }
        .cg-badge-medium { background: #EF6C00; }
        .cg-badge-low    { background: #2E7D32; }
        .cg-badge-cat    { background: var(--cg-primary); }

        /* ── Metric tiles ── */
        .cg-metric {
            background: var(--cg-card);
            border-radius: 16px;
            padding: 18px;
            border: 1px solid var(--cg-border);
            box-shadow: var(--cg-shadow);
            text-align: center;
        }
        .cg-metric .label {
            color: #6B7280 !important; font-size: 0.73rem;
            text-transform: uppercase; letter-spacing: 0.6px; font-weight: 600;
        }
        .cg-metric .value {
            color: #0B3D91 !important; font-size: 1.6rem;
            font-weight: 800; margin-top: 5px;
        }

        /* ── Progress bar ── */
        .cg-bar-track {
            width: 100%; height: 24px; border-radius: 999px;
            background: #DDE3EF; overflow: hidden; margin: 8px 0;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.06);
        }
        .cg-bar-fill {
            height: 100%; border-radius: 999px;
            transition: width 1.4s cubic-bezier(0.4,0,0.2,1);
            display: flex; align-items: center; justify-content: flex-end;
            padding-right: 12px; font-size: 0.76rem; font-weight: 700;
            color: #fff; min-width: 44px;
        }

        /* ── Document pills ── */
        .cg-doc-pill {
            display: inline-block; padding: 5px 13px; margin: 3px;
            border-radius: 8px; font-size: 0.8rem; font-weight: 600;
        }
        .cg-doc-have { background: #E6F4EA; color: #1B5E20 !important; border: 1px solid #A5D6A7; }
        .cg-doc-miss { background: #FDECEA; color: #B71C1C !important; border: 1px solid #EF9A9A; }

        /* ── Tip box ── */
        .cg-tip {
            background: #E8F5E9; border-left: 4px solid #138808;
            padding: 11px 16px; border-radius: 6px; margin: 8px 0;
            font-size: 0.87rem; color: #1B5E20 !important;
        }

        /* ── Section heading ── */
        .cg-section-heading {
            font-size: 1.18rem; font-weight: 700; color: #0B3D91 !important;
            margin: 24px 0 14px; padding-bottom: 8px;
            border-bottom: 2px solid #DDE3EF;
        }

        /* ── Scheme card ribbon ── */
        .scheme-ribbon {
            height: 4px; border-radius: 4px 4px 0 0;
            margin: -22px -24px 14px; background: #0B3D91;
        }

        /* ── Footer ── */
        .cg-footer {
            text-align: center; color: #6B7280 !important;
            font-size: 0.78rem; margin-top: 28px; padding: 14px 0;
            border-top: 1px solid #DDE3EF;
        }

        /* ── Main content — force dark text everywhere ── */

        /* All markdown text in the main panel */
        .main [data-testid="stMarkdownContainer"] p,
        .main [data-testid="stMarkdownContainer"] li,
        .main [data-testid="stMarkdownContainer"] span,
        .main [data-testid="stMarkdownContainer"] a,
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li,
        [data-testid="stMarkdownContainer"] div {
            color: #111827 !important;
        }

        /* Headings */
        .main h1, .main h2, .main h3, .main h4, .main h5,
        [data-testid="stMarkdownContainer"] h1,
        [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h3,
        [data-testid="stMarkdownContainer"] h4 {
            color: #0B3D91 !important;
            font-weight: 700 !important;
        }

        /* Success / info / warning / error boxes */
        [data-testid="stAlert"] p,
        [data-testid="stAlert"] span,
        div[class*="stSuccess"] p,
        div[class*="stInfo"] p,
        div[class*="stWarning"] p {
            color: inherit !important;
        }

        /* Metric labels and values */
        [data-testid="stMetricLabel"],
        [data-testid="stMetricLabel"] p,
        [data-testid="stMetricValue"],
        [data-testid="stMetricDelta"] {
            color: #111827 !important;
        }

        /* Captions */
        .main [data-testid="stCaptionContainer"] p,
        .stCaption p, .stCaption span {
            color: #6B7280 !important;
        }

        /* Dataframe / table */
        [data-testid="stDataFrame"] td,
        [data-testid="stDataFrame"] th {
            color: #111827 !important;
        }

        /* Expander header */
        [data-testid="stExpander"] summary span,
        [data-testid="stExpander"] summary p {
            color: #0B3D91 !important;
            font-weight: 600 !important;
        }

        /* Expander body text */
        [data-testid="stExpander"] [data-testid="stMarkdownContainer"] p {
            color: #111827 !important;
        }

        /* ── Streamlit widget tweaks ── */
        .stButton > button {
            border-radius: 10px !important;
            font-weight: 700 !important;
            transition: transform 0.1s, box-shadow 0.2s !important;
        }
        .stButton > button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 18px rgba(11,61,145,0.20) !important;
        }
        .stDownloadButton > button {
            background: linear-gradient(135deg, var(--cg-accent), #1aab0a) !important;
            color: white !important; border: none !important;
            border-radius: 10px !important; font-weight: 700 !important;
        }
        div[data-testid="stExpander"] {
            border: 1px solid var(--cg-border) !important;
            border-radius: 12px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------- #
# UI Components
# --------------------------------------------------------------------------- #
def render_hero() -> None:
    """Render the top hero banner."""
    gemini_status = "🟢 AI Connected" if os.getenv("GEMINI_API_KEY") else "🟡 Rule-based Mode"
    st.markdown(
        f"""
        <div class="cg-hero">
            <h1>🏛️ {APP_TITLE}</h1>
            <p>{APP_TAGLINE} — discover schemes, verify documents &amp; prepare applications with AI.</p>
            <div class="version">v2.0 · {gemini_status} · India's Benefits Compass</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_progress_bar(score: int, label: str = "") -> None:
    """Render an animated horizontal progress bar."""
    pct = max(0, min(100, int(score)))
    text = label or f"{pct}%"
    color = "#138808" if pct >= 70 else ("#EF6C00" if pct >= 40 else "#C62828")
    st.markdown(
        f"""
        <div class="cg-bar-track">
            <div class="cg-bar-fill" style="width:{pct}%; background: linear-gradient(90deg, {color}, {color}cc);">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric(label: str, value: Any) -> None:
    """Render a single styled metric card."""
    st.markdown(
        f"""
        <div class="cg-metric">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def priority_badge(priority: str) -> str:
    """Return HTML for a priority badge."""
    cls = {
        "high": "cg-badge-high",
        "medium": "cg-badge-medium",
        "low": "cg-badge-low",
    }.get(str(priority).lower(), "cg-badge-medium")
    return f'<span class="cg-badge {cls}">{priority} Priority</span>'


def render_scheme_card(card: Dict[str, Any], explanation: Dict[str, Any] | None) -> None:
    """Render a single scheme card with an optional AI explanation."""
    badges = (
        f'<span class="cg-badge cg-badge-cat">{card.get("category")}</span>'
        + priority_badge(card.get("priority", "Medium"))
    )
    match_score = card.get("match_score", 0)
    match_color = "#138808" if match_score >= 80 else ("#EF6C00" if match_score >= 60 else "#C62828")

    st.markdown(
        f"""
        <div class="cg-card">
            <h3>📌 {card.get('name')}</h3>
            {badges}
            <p>{card.get('description')}</p>
            <p>💰 <b>Benefits:</b> {card.get('benefits')}</p>
            <p>
              📊 <b>Income Limit:</b> {card.get('income_limit_display')} &nbsp;|&nbsp;
              🎯 <b>Match Score:</b> <span style="color:{match_color}; font-weight:700;">{card.get('match_score')}%</span> &nbsp;|&nbsp;
              ✅ <b>Status:</b> {card.get('status')}
            </p>
            <p>📄 <b>Required Documents:</b> {card.get('documents_display')}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    tab1, tab2 = st.tabs(["📄 Scheme Details", "🤖 AI Advisor"])
    with tab1:
        website = card.get("official_website", "#")

        if website and website != "#":
            st.link_button(
                "🌐 Apply on Official Website",
                website,
                use_container_width=True
            )
    with tab2:
        if explanation:

            source = explanation.get("source", "rule-based")

            badge = "🤖 Gemini AI" if source == "gemini" else "📋 Rule-Based"

            st.info(badge)

            st.markdown(explanation.get("text", ""))
    


def render_documents(
    planner: Dict[str, Any],
    documents: Dict[str, Any],
   
) -> None:
    """Render document availability and detection results."""
    st.markdown("#### 📁 Document Verification")
    detected = documents.get("detected", [])
    if detected:
        st.success(f"✅ Detected {len(detected)} document type(s) in your uploads: {', '.join(detected)}")
    else:
        st.info("💡 No documents detected yet. Upload your PDFs to auto-detect them.")

    uploaded = planner.get("uploaded", [])
    missing = planner.get("missing", [])

    pills = ""
    for doc in uploaded:
        pills += f'<span class="cg-doc-pill cg-doc-have">✅ {doc}</span>'
    for doc in missing:
        pills += f'<span class="cg-doc-pill cg-doc-miss">❌ {doc}</span>'
    if not pills:
        pills = "<i>No required documents for your matched schemes.</i>"
    st.markdown(f"<div class='cg-card'>{pills}</div>", unsafe_allow_html=True)

    per_file = documents.get("per_file", {})
    if per_file:
        with st.expander("🔍 Per-file detection details"):
            for name, found in per_file.items():
                st.write(f"**{name}** → {', '.join(found) if found else 'Nothing detected'}")

    if missing:
        st.markdown(
            f"<div class='cg-tip'>💡 <b>Tip:</b> Gather the following missing documents to improve your readiness: {', '.join(missing[:3])}{'...' if len(missing) > 3 else ''}</div>",
            unsafe_allow_html=True,
        )
    # --------------------------------------------------------
# 🤖 AI Document Analysis
# --------------------------------------------------------

    analysis = documents.get("analysis", {})

    if analysis:

        st.markdown("---")
        st.markdown("## 🤖 AI Document Intelligence")

        for filename, info in analysis.items():

            with st.container(border=True):

                st.markdown(f"### 📄 {filename}")

                c1, c2 = st.columns(2)

                with c1:
                    st.metric(
                        "Document Type",
                        info.get("document_type", "Unknown"),
                    )

                    st.metric(
                        "Confidence",
                        f"{info.get('confidence',0)}%",
                    )

                with c2:
                    st.metric(
                        "Verification",
                        info.get("verification", "Unknown"),
                    )

                    st.metric(
                        "Extracted Text",
                        f"{info.get('text_length',0)} characters",
                    )

                


def render_action_plan(planner: Dict[str, Any]) -> None:
    """Render the action plan table and timeline."""
    plan = planner.get("action_plan", [])
    st.markdown("#### 🗺️ Your Action Plan")
    if not plan:
        st.success("🎉 You have all required documents! You're ready to apply.")
        return
    df = pd.DataFrame(plan)
    if not df.empty:
        rename_map = {}
        if "step" in df.columns:
            rename_map["step"] = "Step"
        if "document" in df.columns:
            rename_map["document"] = "Document"
        if "action" in df.columns:
            rename_map["action"] = "Action"
        df = df.rename(columns=rename_map)
    st.dataframe(df, use_container_width=True, hide_index=True)
    days = planner.get("timeline_days", 0)
    st.caption(f"⏱️ Estimated preparation time: ~{days} day(s) to gather missing documents.")


def render_summary(
    summary: Dict[str, Any],
    ai_recommendation: str = "",
) -> None:
    """Render the AI summary block with metrics."""
    st.markdown("### 🧠 Your Benefits Summary")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric("Profile", summary.get("applicant", "-"))
    with c2:
        income = summary.get("income", 0)
        render_metric("Annual Income", f"₹{int(income):,}" if isinstance(income, (int, float)) else income)
    with c3:
        render_metric("Eligible Schemes", summary.get("eligible_count", 0))
    with c4:
        render_metric("Readiness Score", f"{summary.get('readiness_score', 0)}%")

    st.markdown("<br>", unsafe_allow_html=True)
    c5, c6 = st.columns(2)
    with c5:
        render_metric("Top Priority Scheme", summary.get("top_scheme", "-"))
    with c6:
        render_metric("Missing Documents", summary.get("missing_count", 0))

    st.markdown("<br>", unsafe_allow_html=True)
    recommendation = ai_recommendation or summary.get("recommendation", "")

    st.info("🤖 AI Benefit Advisor")

    st.markdown(recommendation)


# --------------------------------------------------------------------------- #
# Sidebar / Inputs
# --------------------------------------------------------------------------- #
def render_sidebar() -> Dict[str, Any]:
    """Render the sidebar profile form and return the collected profile."""
    with st.sidebar:
        st.markdown("## 🧭 CivicGuardian AI")
        st.markdown("### 👤 Citizen Profile")

        name = st.text_input("Your Name (optional)", placeholder="e.g. Rahul Kumar")
        occupation = st.selectbox("Occupation", OCCUPATIONS, index=0)
        income = st.number_input(
            "Annual Income (₹)",
            min_value=0,
            max_value=100_000_000,
            value=150_000,
            step=10_000,
            help="Enter your total annual household income",
        )
        age = st.number_input("Age", min_value=0, max_value=120, value=25, step=1)
        state = st.selectbox("State", STATES, index=STATES.index("Maharashtra"))
        gender = st.selectbox("Gender", GENDERS, index=0)
        disability = st.checkbox("Person with Disability", value=False)
        caste = st.selectbox(
            "Social Category",
            ["General", "OBC", "SC", "ST"],
            index=0,
            help="Used to match caste-specific schemes",
        )

        st.markdown("---")
        st.markdown("### 📄 Upload Documents (PDF)")
        uploaded_files = st.file_uploader(
            "Upload Aadhaar, PAN, Income Certificate, etc.",
            type=["pdf"],
            accept_multiple_files=True,
            help="We detect document types automatically from file names and content",
        )

        st.markdown("---")
        analyze = st.button("🚀 Analyze My Benefits", use_container_width=True, type="primary")

        st.markdown("---")
        gemini_status = "🟢 AI Connected" if os.getenv("GEMINI_API_KEY") else "🟡 Rule-based Mode"
        st.caption(f"AI Status: {gemini_status}")
        if not os.getenv("GEMINI_API_KEY"):
            st.caption("Set GEMINI_API_KEY in .env to enable Gemini AI explanations.")
        st.caption("CivicGuardian AI v2.0 © 2025")
        st.caption("ℹ️ This is an informational tool, not an official service.")

    uploads: List[Dict[str, Any]] = []
    if uploaded_files:
        for file in uploaded_files:
            try:
                uploads.append({"name": file.name, "bytes": file.getvalue()})
            except Exception:
                continue

    return {
        "name": name,
        "occupation": occupation,
        "income": income,
        "age": age,
        "state": state,
        "gender": gender.upper(),
        "disability": disability,
        "caste": caste,
        "uploads": uploads,
        "analyze": analyze,
    }


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
@st.cache_resource(show_spinner=False)
def get_coordinator() -> CoordinatorAgent:
    """Create (and cache) the CoordinatorAgent across reruns."""
    return CoordinatorAgent(
        api_key=os.getenv("GEMINI_API_KEY"),
        model_name=os.getenv("GEMINI_MODEL"),
    )


def render_results(result: Dict[str, Any]) -> None:
    """Render the full results dashboard from a pipeline result."""
    summary = result.get("summary", {})
    
    render_summary(
    summary,
    result.get("ai_recommendation", "")
)

    st.markdown("---")
    readiness = result.get("readiness", {})
    st.markdown("### 📈 Application Readiness")
    score = readiness.get("score", 0)
    level = readiness.get("level", "")
    render_progress_bar(score, f"{score}% — {level}")
    if readiness.get("explanation"):
        st.caption(readiness["explanation"])

    st.markdown("---")
    st.markdown("### 🎯 Eligible Government Schemes")
    cards = result.get("cards", [])
    explanations = {e.get("scheme_id"): e for e in result.get("explanations", [])}
    if not cards:
        st.warning(
            "⚠️ No schemes matched your profile. Try adjusting your income, age, "
            "or occupation. Some schemes may require a lower income or specific age."
        )
    else:
        st.success(f"✅ Found **{len(cards)} eligible scheme(s)** for your profile!")
        for card in cards:
            render_scheme_card(card, explanations.get(card.get("id")))

    st.markdown("---")
    render_documents(
    result.get("planner", {}),
    result.get("documents", {}),
)
    render_action_plan(result.get("planner", {}))

    st.markdown("---")
    st.markdown("### 📥 Download Your Personalized Report")
    pdf_bytes = result.get("report_pdf", b"")
    if pdf_bytes:
        st.download_button(
            "⬇️ Download PDF Report",
            data=pdf_bytes,
            file_name="CivicGuardian_Benefits_Report.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary",
        )
        st.caption("Your personalized benefits report with action plan and scheme details.")
    else:
        st.info("📄 Report generation unavailable. Ensure reportlab is installed: `pip install reportlab`")

    errors = result.get("errors", [])
    if errors:
        with st.expander("⚠️ Diagnostics / Warnings"):
            for err in errors:
                st.write(f"- {err}")


def main() -> None:
    """Application entry point."""
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_css()
    render_hero()

    inputs = render_sidebar()

    try:
        coordinator = get_coordinator()
    except Exception as e:
        st.error(f"Failed to initialize CivicGuardian: {e}")
        st.stop()

    if inputs["analyze"]:
        profile = {
            "name": inputs.get("name", ""),
            "occupation": inputs["occupation"],
            "income": inputs["income"],
            "age": inputs["age"],
            "state": inputs["state"],
            "gender": inputs["gender"],
            "disability": inputs["disability"],
            "caste": inputs.get("caste", "General"),
        }
        with st.spinner("🤖 CivicGuardian agents are analyzing your eligibility..."):
            try:
                result = coordinator.run(profile=profile, uploads=inputs["uploads"])
                st.session_state["result"] = result
                st.session_state["profile"] = profile
            except Exception as exc:
                st.error(f"Analysis failed: {exc}")
                st.session_state.pop("result", None)

    if "result" in st.session_state:
        render_results(st.session_state["result"])
    else:
        # Welcome / instructions panel.
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(
                """
                <div class="cg-card">
                    <h3>👋 Welcome to CivicGuardian AI</h3>
                    <p>Fill in your <b>citizen profile</b> in the sidebar, optionally upload your
                    documents as PDFs, and click <b>Analyze My Benefits</b>.</p>
                    <p>Our multi-agent AI system will:</p>
                    <p>✅ Match you to eligible Indian government schemes<br>
                       ✅ Detect documents from your uploads automatically<br>
                       ✅ Build a personalized step-by-step action plan<br>
                       ✅ Calculate your application readiness score<br>
                       ✅ Generate a downloadable PDF report</p>
                    <p style="color:#6B7280; font-size:0.85rem;">Works for students, farmers, entrepreneurs, senior citizens, and more.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col2:
            try:
                c1, c2, c3 = st.columns(1), st.columns(1), st.columns(1)
                render_metric("Schemes in Database", coordinator.scheme_server.count())
                st.markdown("<br>", unsafe_allow_html=True)
                render_metric("AI Agents Active", 8)
                st.markdown("<br>", unsafe_allow_html=True)
                cats = len(coordinator.scheme_server.get_categories())
                render_metric("Categories Covered", cats)
            except Exception:
                pass

    st.markdown(
        "<div class='cg-footer'>Built with ❤️ using Streamlit · "
        "CivicGuardian AI is an informational tool, not an official government service. "
        "Always verify eligibility on official portals.</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
