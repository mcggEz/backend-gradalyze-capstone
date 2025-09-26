from __future__ import annotations

from typing import Dict, Tuple
import os
import json
import numpy as np

_REGRESSION_WEIGHTS_ENV = "CAREER_REG_WEIGHTS"
_KMEANS_CENTROIDS_ENV = "KMEANS_CENTROIDS"
_KMEANS_LABELS_ENV = "KMEANS_LABELS"


def _softmax(x: np.ndarray) -> np.ndarray:
    x = x - np.max(x)
    e = np.exp(x)
    return e / (np.sum(e) or 1.0)


def predict_career_scores(vec: np.ndarray) -> Dict[str, float]:
    weights = os.getenv(_REGRESSION_WEIGHTS_ENV)
    W = None
    if weights:
        try:
            W = np.array(json.loads(weights), dtype=float)
        except Exception:
            W = None
    if W is None:
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


def predict_archetype_kmeans(vec: np.ndarray) -> Tuple[int, Dict[str, float]]:
    centroids_raw = os.getenv(_KMEANS_CENTROIDS_ENV)
    labels_raw = os.getenv(_KMEANS_LABELS_ENV)
    C = None
    labels = None
    if centroids_raw and labels_raw:
        try:
            C = np.array(json.loads(centroids_raw), dtype=float)
            labels = list(json.loads(labels_raw))
        except Exception:
            C, labels = None, None
    if C is None:
        rng = np.random.default_rng(42)
        C = rng.random((6, 7))
        C = C / (np.linalg.norm(C, axis=1, keepdims=True) + 1e-9)
        labels = ["realistic", "investigative", "artistic", "social", "enterprising", "conventional"]
    dists = np.linalg.norm(C - vec.reshape(1, -1), axis=1)
    probs = _softmax(-dists)
    cluster_id = int(np.argmin(dists))
    return cluster_id, {lab: float(p * 100.0) for lab, p in zip(labels, probs)}


