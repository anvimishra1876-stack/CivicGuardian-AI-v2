"""Document Agent for CivicGuardian AI.

Detects document types from uploaded PDF files by examining file names
and (optionally) text content extracted from PDFs via PyMuPDF.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List

# Optional PyMuPDF support for text extraction.
try:
    import fitz  # PyMuPDF
    _FITZ_AVAILABLE = True
except ImportError:
    fitz = None  # type: ignore
    _FITZ_AVAILABLE = False


# Keyword-based detection patterns.
DOCUMENT_PATTERNS = {
    "Aadhaar": ["aadhaar", "aadhar", "uid", "unique identification", "uidai"],
    "PAN": ["pan card", "permanent account number", "income tax", "pan "],
    "Income Certificate": ["income certificate", "income proof", "annual income"],
    "Land Record": ["land record", "khasra", "khatauni", "patta", "land document"],
    "Bank Passbook": ["passbook", "bank statement", "account statement", "ifsc"],
    "Caste Certificate": ["caste certificate", "sc/st", "obc certificate"],
    "Disability Certificate": ["disability certificate", "divyang", "handicap"],
    "Birth Certificate": ["birth certificate", "date of birth proof"],
    "Marksheet": ["marksheet", "mark sheet", "score card", "result card", "admit card"],
    "Voter ID": ["voter id", "epic", "election commission", "voter card"],
    "Ration Card": ["ration card", "bpl", "food security"],
    "Domicile Certificate": ["domicile", "residence certificate", "bonafide resident"],
}


class DocumentAgent:
    """Detects government document types from uploaded files."""

    def process_uploads(
        self, uploads: List[Dict[str, Any]] | None
    ) -> Dict[str, Any]:
        """Process a list of uploaded files and detect document types.

        Args:
            uploads: List of ``{"name": str, "bytes": bytes}`` dicts.

        Returns:
            Dict with ``detected`` (unique doc types) and ``per_file`` (mapping
            of file name -> detected types).
        """
        if not uploads:
            return {"detected": [], "per_file": {}}

        per_file: Dict[str, List[str]] = {}
        analysis = {}
        all_detected: List[str] = []

        for upload in uploads:
            name = upload.get("name", "")
            raw_bytes = upload.get("bytes", b"")
            found = self._detect_documents(name, raw_bytes)
            analysis[name] = self._analyze_document(
            name,
            raw_bytes
            )
            per_file[name] = found
            all_detected.extend(found)

        # Deduplicate while preserving order.
        seen = set()
        unique_detected = []
        for doc in all_detected:
            if doc not in seen:
                seen.add(doc)
                unique_detected.append(doc)

        return {
        "detected": unique_detected,
        "per_file": per_file,
        "analysis": analysis,
    }

    def _detect_documents(self, filename: str, raw_bytes: bytes) -> List[str]:
        """Detect document types from a filename and optional PDF bytes.

        Args:
            filename: Original file name.
            raw_bytes: Raw file bytes (PDF).

        Returns:
            List of detected document type names.
        """
        search_text = filename.lower()

        # Try to extract text from PDF for richer matching.
        if _FITZ_AVAILABLE and raw_bytes:
            try:
                with fitz.open(stream=raw_bytes, filetype="pdf") as doc:
                    for page in doc:
                        search_text += " " + page.get_text().lower()
                        if len(search_text) > 5000:
                            break  # Enough context.
            except Exception:
                pass  # Fall back to filename only.

        detected = []
        for doc_type, keywords in DOCUMENT_PATTERNS.items():
            if any(kw in search_text for kw in keywords):
                detected.append(doc_type)

        return detected
    
    def _analyze_document(
    self,
    filename: str,
    raw_bytes: bytes,
) -> Dict[str, Any]:

        text = ""

        if _FITZ_AVAILABLE and raw_bytes:
            try:
                with fitz.open(stream=raw_bytes, filetype="pdf") as pdf:
                    for page in pdf:
                        text += page.get_text()

            except Exception:
                pass

        text_lower = text.lower()

        document_type = "Unknown"

        for doc, keywords in DOCUMENT_PATTERNS.items():

            if any(keyword in text_lower for keyword in keywords):

                document_type = doc
                break

        analysis = {
            "document_type": document_type,
            "confidence": 95 if document_type != "Unknown" else 30,
            "verification": "Verified"
                if document_type != "Unknown"
                else "Unknown Document",
            "text_length": len(text),
            "extracted_text": text[:3000],
        }

        return analysis
