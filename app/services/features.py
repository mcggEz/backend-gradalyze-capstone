from __future__ import annotations

from typing import Dict, Iterable, List
import re
import numpy as np

_FAMILY_KEYWORDS: Dict[str, Iterable[str]] = {
    "math": ("math", "calculus", "algebra", "statistics", "probability"),
    "programming": ("program", "coding", "cs", "oop", "data structure"),
    "systems": ("system", "network", "os", "hardware", "architecture"),
    "ux": ("ux", "ui", "design", "human-computer", "multimedia"),
    "communication": ("communication", "english", "writing", "speech"),
    "management": ("management", "project", "entrepreneur", "leadership"),
    "data": ("data", "ml", "ai", "analytics", "database"),
}


def _family_for_subject(subject: str) -> str:
    s = subject.lower()
    for fam, keys in _FAMILY_KEYWORDS.items():
        for k in keys:
            if k in s:
                return fam
    return "programming" if re.search(r"cs|comp(uter)?", s) else "data"


def summarize_subject_families(grades: List[dict]) -> Dict[str, float]:
    totals: Dict[str, float] = {k: 0.0 for k in _FAMILY_KEYWORDS}
    weights: Dict[str, float] = {k: 0.0 for k in _FAMILY_KEYWORDS}
    for row in grades or []:
        try:
            subject = str(row.get("subject") or "")
            units = float(row.get("units") or 0.0)
            grade = float(row.get("grade") or 0.0)
        except Exception:
            continue
        fam = _family_for_subject(subject)
        totals[fam] += grade * max(units, 0.0)
        weights[fam] += max(units, 0.0)

    out: Dict[str, float] = {}
    for fam in totals:
        w = weights[fam]
        out[fam] = (totals[fam] / w) if w > 0 else 0.0
    return out


def build_feature_vector_from_grades(grades: List[dict]) -> np.ndarray:
    families = summarize_subject_families(grades)
    order = ["math", "programming", "systems", "ux", "communication", "management", "data"]
    raw = np.array([families.get(k, 0.0) for k in order], dtype=float)
    scaled = 1.0 - np.clip(raw / 5.0, 0.0, 1.0)
    norm = np.linalg.norm(scaled) or 1.0
    return (scaled / norm).astype(float)


