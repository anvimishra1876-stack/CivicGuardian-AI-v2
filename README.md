# 🏛️ CivicGuardian AI v2.0

**Your Intelligent Government Benefits Navigator**

CivicGuardian AI is a multi-agent Streamlit application that helps Indian citizens discover eligible government schemes, verify their documents, and prepare complete applications — all powered by AI.

---

## ✨ Features

- 🎯 **Smart Eligibility Matching** — Matches your profile against 16+ government schemes using income, age, state, gender, disability, and caste criteria
- 🤖 **AI-Powered Explanations** — Personalized explanations via Google Gemini (or rule-based fallback)
- 📄 **Document Detection** — Auto-detects document types from uploaded PDFs
- 🗺️ **Action Plan** — Step-by-step guide to gather missing documents
- 📈 **Readiness Score** — Real-time application readiness percentage
- 📥 **PDF Report** — Downloadable, formatted benefits report

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
cd civicguardian-ai
pip install -r requirements.txt
```

### 2. Configure (Optional)

```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY (from https://aistudio.google.com/app/apikey)
```

### 3. Run

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## 🏗️ Architecture

```
civicguardian-ai/
├── app.py                    # Streamlit UI entry point
├── agents/
│   ├── coordinator.py        # Orchestrates the full pipeline
│   ├── eligibility_agent.py  # Filters schemes by profile
│   ├── scheme_agent.py       # Formats schemes for display
│   ├── explainer_agent.py    # Gemini AI + rule-based explanations
│   ├── document_agent.py     # PDF document type detection
│   ├── planner_agent.py      # Action plan builder
│   ├── readiness_agent.py    # Application readiness scorer
│   └── report_agent.py       # PDF report generator
├── servers/
│   └── scheme_server.py      # Scheme data access layer
├── data/
│   └── schemes.json          # Government schemes database
├── requirements.txt
└── .env.example
```

### Agent Pipeline

```
User Profile + Documents
        ↓
  EligibilityAgent      → Filter matching schemes
        ↓
   SchemeAgent          → Format for display
        ↓
  ExplainerAgent        → Personalized AI explanations (Gemini/fallback)
        ↓
  DocumentAgent         → Detect document types from uploads
        ↓
  PlannerAgent          → Build action plan for missing docs
        ↓
  ReadinessAgent        → Compute readiness score
        ↓
  ReportAgent           → Generate downloadable PDF
        ↓
  CoordinatorAgent      → Assembles everything → Streamlit UI
```

---

## 📋 Supported Schemes

| Category | Schemes |
|----------|---------|
| Farmer | PM-KISAN, Kisan Credit Card, PM Fasal Bima Yojana |
| Student | NSP Scholarship, Post-Matric Scholarship |
| Entrepreneur | PM MUDRA Yojana, PM SVANidhi, Startup India Seed Fund |
| Senior Citizen | Pradhan Mantri Vaya Vandana, NSAP Old Age Pension |
| General | PM-JAY Ayushman Bharat, PM Awas Yojana, Ujjwala Yojana, PM-SURAKSHA BIMA |
| Other | PMEGP (employment generation), PMJJBY (life insurance) |

---

## ⚙️ Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | (none) | Google Gemini API key for AI explanations |
| `GEMINI_MODEL` | `gemini-1.5-flash` | Gemini model to use |

Without `GEMINI_API_KEY`, the app runs in rule-based mode (fully functional, no API calls needed).

---

## 🛠️ Troubleshooting

**`ModuleNotFoundError: No module named 'fitz'`**
→ `pip install PyMuPDF`

**PDF report not generating**
→ `pip install reportlab`

**Gemini explanations not working**
→ Check your `GEMINI_API_KEY` in `.env`

---

## 📄 License

MIT License — see LICENSE file.

---

*CivicGuardian AI is an informational tool. Always verify eligibility on official government portals.*

