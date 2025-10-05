from __future__ import annotations

from typing import Dict, Tuple, List, Any, Iterable
import os
import json
import numpy as np
## CourseRIASECMapper removed from simplified stack

_REGRESSION_WEIGHTS_ENV = None
_KMEANS_CENTROIDS_ENV = None
_KMEANS_LABELS_ENV = None


def _softmax(x: np.ndarray) -> np.ndarray:
    x = x - np.max(x)
    e = np.exp(x)
    return e / (np.sum(e) or 1.0)


# Inlined from features.py to simplify the stack
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
    import re as _re
    s = subject.lower()
    for fam, keys in _FAMILY_KEYWORDS.items():
        for k in keys:
            if k in s:
                return fam
    return "programming" if _re.search(r"cs|comp(uter)?", s) else "data"

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

def build_feature_vector_from_grades_it(grades: List[dict]) -> np.ndarray:
    fam = summarize_subject_families(grades)
    order = ["programming", "systems", "data", "ux", "math", "management", "communication"]
    raw = np.array([fam.get(k, 0.0) for k in order], dtype=float)
    scaled = 1.0 - np.clip(raw / 5.0, 0.0, 1.0)
    norm = np.linalg.norm(scaled) or 1.0
    return (scaled / norm).astype(float)

def build_feature_vector_from_grades_cs(grades: List[dict]) -> np.ndarray:
    fam = summarize_subject_families(grades)
    order = ["math", "programming", "data", "systems", "ux", "communication", "management"]
    raw = np.array([fam.get(k, 0.0) for k in order], dtype=float)
    scaled = 1.0 - np.clip(raw / 5.0, 0.0, 1.0)
    norm = np.linalg.norm(scaled) or 1.0
    return (scaled / norm).astype(float)


def predict_career_scores(vec: np.ndarray) -> Dict[str, float]:
    """Deterministic linear scoring for careers used by /analysis/process."""
    W = np.array([
        [0.7, 0.3, 0.2, 0.0, 0.1, 0.1, 0.8],
        [0.2, 0.3, 0.8, 0.0, 0.1, 0.1, 0.2],
        [0.3, 0.8, 0.4, 0.1, 0.2, 0.2, 0.3],
        [0.0, 0.4, 0.1, 0.9, 0.3, 0.1, 0.1],
        [0.1, 0.2, 0.2, 0.2, 0.6, 0.9, 0.1],
    ], dtype=float)
    scores = W @ vec.reshape(-1, 1)
    scores = scores.flatten()
    scores = (scores - scores.min()) / ((scores.max() - scores.min()) or 1.0)
    careers = ["data_science", "systems_engineering", "software_engineering", "ui_ux", "product_management"]
    return {c: float(v) for c, v in zip(careers, scores)}


# Removed random forest path to reduce complexity


def predict_career_scores_it(vec: np.ndarray) -> Dict[str, float]:
    """Program-specific career scoring for IT using linear head on features."""
    # Emphasize systems, cloud, devops oriented roles
    careers = ["systems_engineering", "cloud_engineering", "software_engineering", "devops", "product_management", "data_science", "ui_ux"]
    W = np.array([
        [0.2, 0.8, 0.6, 0.4, 0.2, 0.3, 0.2],  # systems
        [0.2, 0.7, 0.5, 0.6, 0.2, 0.3, 0.2],  # cloud
        [0.5, 0.4, 0.7, 0.3, 0.2, 0.3, 0.2],  # software
        [0.2, 0.6, 0.6, 0.7, 0.2, 0.2, 0.2],  # devops
        [0.1, 0.2, 0.5, 0.2, 0.6, 0.4, 0.2],  # pm
        [0.2, 0.3, 0.4, 0.2, 0.2, 0.7, 0.3],  # data
        [0.2, 0.2, 0.3, 0.8, 0.2, 0.2, 0.5],  # ui/ux
    ], dtype=float)
    s = W @ vec.reshape(-1, 1)
    s = s.flatten()
    s = (s - s.min()) / ((s.max() - s.min()) or 1.0)
    return {c: float(v) for c, v in zip(careers, s)}


def predict_career_scores_cs(vec: np.ndarray) -> Dict[str, float]:
    """Program-specific career scoring for CS prioritizing math/algorithms heavy roles."""
    careers = ["data_science", "software_engineering", "systems_engineering", "product_management", "ui_ux", "cloud_engineering", "devops"]
    W = np.array([
        [0.8, 0.5, 0.3, 0.2, 0.2, 0.3, 0.2],  # data science
        [0.5, 0.8, 0.4, 0.2, 0.2, 0.3, 0.2],  # software
        [0.4, 0.6, 0.7, 0.2, 0.2, 0.3, 0.2],  # systems
        [0.2, 0.5, 0.3, 0.7, 0.3, 0.2, 0.2],  # pm
        [0.2, 0.4, 0.3, 0.3, 0.7, 0.2, 0.2],  # ui/ux
        [0.3, 0.5, 0.5, 0.2, 0.2, 0.7, 0.4],  # cloud
        [0.2, 0.5, 0.6, 0.2, 0.2, 0.6, 0.7],  # devops
    ], dtype=float)
    s = W @ vec.reshape(-1, 1)
    s = s.flatten()
    s = (s - s.min()) / ((s.max() - s.min()) or 1.0)
    return {c: float(v) for c, v in zip(careers, s)}


def predict_archetype_kmeans(vec: np.ndarray) -> Tuple[int, Dict[str, float]]:
    """Deterministic mock K-means using fixed centroids and labels."""
    labels = ["realistic", "investigative", "artistic", "social", "enterprising", "conventional"]
    C = np.array([
        [0.9,0.1,0.0,0.1,0.1,0.1,0.8],  # realistic
        [0.1,0.9,0.1,0.1,0.1,0.1,0.2],  # investigative
        [0.1,0.1,0.9,0.8,0.1,0.1,0.3],  # artistic
        [0.1,0.1,0.2,0.1,0.1,0.1,0.1],  # social
        [0.1,0.1,0.1,0.1,0.9,0.2,0.2],  # enterprising
        [0.1,0.1,0.1,0.1,0.2,0.9,0.1],  # conventional
    ], dtype=float)
    C = C / (np.linalg.norm(C, axis=1, keepdims=True) + 1e-9)
    dists = np.linalg.norm(C - vec.reshape(1, -1), axis=1)
    probs = _softmax(-dists)
    cluster_id = int(np.argmin(dists))
    return cluster_id, {lab: float(p * 100.0) for lab, p in zip(labels, probs)}


# Removed course-based mapping path to reduce complexity


def predict_archetype_kmeans_riasec(grades_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Predict RIASEC archetype using K-means clustering (as requested by client)
    
    This method uses K-means clustering on academic features to classify students
    into RIASEC archetypes, as specifically requested by the client.
    
    Args:
        grades_data: List of course grades with course_code and grade fields
        
    Returns:
        Complete archetype analysis with scores, primary archetype, and insights
    """
    from .kmeans_riasec import predict_archetype_kmeans_riasec as kmeans_predict
    return kmeans_predict(grades_data)


# Removed hybrid method to avoid dual pathways


