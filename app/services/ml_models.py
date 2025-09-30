from __future__ import annotations

from typing import Dict, Tuple, List, Any
import os
import json
import numpy as np
from .course_riasec_mapping import CourseRIASECMapper

_REGRESSION_WEIGHTS_ENV = "CAREER_REG_WEIGHTS"
_KMEANS_CENTROIDS_ENV = "KMEANS_CENTROIDS"
_KMEANS_LABELS_ENV = "KMEANS_LABELS"


def _softmax(x: np.ndarray) -> np.ndarray:
    x = x - np.max(x)
    e = np.exp(x)
    return e / (np.sum(e) or 1.0)


def predict_career_scores(vec: np.ndarray) -> Dict[str, float]:
    """Legacy linear regression career prediction - kept for backward compatibility"""
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


def predict_career_scores_random_forest(grades_data: List[Dict[str, Any]], 
                                     archetype_scores: Dict[str, float]) -> Dict[str, float]:
    """
    Predict career scores using Random Forest (Objective 1)
    
    This is the new, improved method that uses Random Forest algorithm
    instead of simple linear regression.
    
    Args:
        grades_data: List of course grades with course_code and grade fields
        archetype_scores: RIASEC archetype percentages
        
    Returns:
        Dictionary of career scores
    """
    from .random_forest_career import predict_career_scores_random_forest as rf_predict
    return rf_predict(grades_data, archetype_scores)


def predict_archetype_kmeans(vec: np.ndarray) -> Tuple[int, Dict[str, float]]:
    """Legacy K-means archetype prediction - kept for backward compatibility"""
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


def predict_archetype_course_based(grades_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Predict student archetype using course-based RIASEC mapping (Objective 2)
    
    This is the new, improved method that uses actual course curriculum mapping
    instead of generic K-means clustering.
    
    Args:
        grades_data: List of course grades with course_code and grade fields
        
    Returns:
        Complete archetype analysis with scores, primary archetype, and insights
    """
    mapper = CourseRIASECMapper()
    return mapper.get_archetype_analysis(grades_data)


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


def predict_archetype_hybrid(vec: np.ndarray, grades_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Hybrid archetype prediction combining course-based mapping with feature vector
    
    Args:
        vec: Feature vector from academic analysis
        grades_data: List of course grades
        
    Returns:
        Combined archetype analysis
    """
    # Get course-based analysis
    course_analysis = predict_archetype_course_based(grades_data)
    
    # Get K-means analysis
    cluster_id, kmeans_scores = predict_archetype_kmeans(vec)
    
    # Combine the results (weighted average: 70% course-based, 30% K-means)
    combined_scores = {}
    for archetype in course_analysis['archetype_scores']:
        course_score = course_analysis['archetype_scores'][archetype]
        kmeans_score = kmeans_scores.get(archetype, 0.0)
        combined_scores[archetype] = (course_score * 0.7) + (kmeans_score * 0.3)
    
    # Normalize combined scores
    total = sum(combined_scores.values())
    if total > 0:
        combined_scores = {k: (v / total) * 100 for k, v in combined_scores.items()}
    
    # Get primary archetype from combined scores
    primary_archetype = max(combined_scores.items(), key=lambda x: x[1])[0]
    
    return {
        'primary_archetype': primary_archetype,
        'archetype_name': course_analysis['archetype_name'],
        'archetype_description': course_analysis['archetype_description'],
        'archetype_traits': course_analysis['archetype_traits'],
        'archetype_scores': combined_scores,
        'course_based_scores': course_analysis['archetype_scores'],
        'kmeans_scores': kmeans_scores,
        'insights': course_analysis['insights'],
        'total_courses_analyzed': course_analysis['total_courses_analyzed'],
        'analysis_method': 'hybrid_course_kmeans'
    }


