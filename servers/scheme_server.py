"""Scheme data access layer for CivicGuardian AI."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional


class SchemeServer:
    """Loads and serves government scheme records from a JSON datastore."""

    DEFAULT_RELATIVE_PATH = os.path.join("data", "schemes.json")

    def __init__(self, data_path: Optional[str] = None) -> None:
        if data_path is None:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_path = os.path.join(project_root, self.DEFAULT_RELATIVE_PATH)
        self.data_path: str = data_path
        self._schemes: List[Dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        try:
            with open(self.data_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            self._schemes = data if isinstance(data, list) else []
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            self._schemes = []

    def reload(self) -> None:
        self._load()

    def get_all_schemes(self) -> List[Dict[str, Any]]:
        return list(self._schemes)

    def get_scheme_by_id(self, scheme_id: str) -> Optional[Dict[str, Any]]:
        for scheme in self._schemes:
            if scheme.get("id") == scheme_id:
                return scheme
        return None

    def get_categories(self) -> List[str]:
        categories = {scheme.get("category", "Other") for scheme in self._schemes}
        return sorted(categories)

    def count(self) -> int:
        return len(self._schemes)
