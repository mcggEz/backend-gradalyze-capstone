"""
Recommendations API endpoints for company and job recommendations using Gemini AI
"""

from flask import Blueprint, request, jsonify, current_app
from app.services.supabase_client import get_supabase_client
from app.services.gemini_recommendations import GeminiRecommendationEngine
import json

bp = Blueprint("recommendations", __name__, url_prefix="/api/recommendations")

@bp.route("/companies/<email>", methods=["GET"])
def get_company_recommendations_for_user(email):
    """
    Get personalized company recommendations for a user
    
    Args:
        email: User's email address
        
    Returns:
        List of recommended companies
    """
    try:
        email = email.strip().lower()
        
        # Get user profile from database
        supabase = get_supabase_client()
        user_result = supabase.table("users").select(
            "email, course, student_number, primary_archetype, "
            "archetype_realistic_percentage, archetype_investigative_percentage, "
            "archetype_artistic_percentage, archetype_social_percentage, "
            "archetype_enterprising_percentage, archetype_conventional_percentage, "
            "tor_notes"
        ).eq("email", email).execute()
        
        if not user_result.data:
            return jsonify({"error": "User not found"}), 404
        
        user_profile = user_result.data[0]
        
        # Get company recommendations using Gemini AI
        try:
            engine = GeminiRecommendationEngine()
            companies = engine.generate_company_recommendations(user_profile)
        except Exception as e:
            return jsonify({
                "error": "Failed to generate company recommendations", 
                "details": str(e),
                "message": "Gemini AI service is required but not available. Please ensure GEMINI_API_KEY is configured."
            }), 500
        
        return jsonify({
            "message": "Company recommendations generated successfully",
            "companies": companies,
            "total_count": len(companies)
        }), 200
        
    except Exception as e:
        current_app.logger.exception("Failed to get company recommendations for %s", email)
        return jsonify({"error": "Failed to get company recommendations", "details": str(e)}), 500

@bp.route("/jobs/<email>", methods=["GET"])
def get_job_openings_for_user(email):
    """
    Get personalized job openings for a user
    
    Args:
        email: User's email address
        
    Returns:
        List of job openings
    """
    try:
        email = email.strip().lower()
        
        # Get user profile from database
        supabase = get_supabase_client()
        user_result = supabase.table("users").select(
            "email, course, student_number, primary_archetype, "
            "archetype_realistic_percentage, archetype_investigative_percentage, "
            "archetype_artistic_percentage, archetype_social_percentage, "
            "archetype_enterprising_percentage, archetype_conventional_percentage, "
            "tor_notes"
        ).eq("email", email).execute()
        
        if not user_result.data:
            return jsonify({"error": "User not found"}), 404
        
        user_profile = user_result.data[0]
        
        # Get company recommendations using Gemini AI
        try:
            engine = GeminiRecommendationEngine()
            companies = engine.generate_company_recommendations(user_profile)
        except Exception as e:
            return jsonify({
                "error": "Failed to generate company recommendations", 
                "details": str(e),
                "message": "Gemini AI service is required but not available. Please ensure GEMINI_API_KEY is configured."
            }), 500
        
        # Get job openings using Gemini AI
        try:
            job_openings = engine.generate_job_openings(user_profile, companies)
        except Exception as e:
            return jsonify({
                "error": "Failed to generate job openings", 
                "details": str(e),
                "message": "Gemini AI service is required but not available. Please ensure GEMINI_API_KEY is configured."
            }), 500
        
        return jsonify({
            "message": "Job openings generated successfully",
            "job_openings": job_openings,
            "total_count": len(job_openings)
        }), 200
        
    except Exception as e:
        current_app.logger.exception("Failed to get job openings for %s", email)
        return jsonify({"error": "Failed to get job openings", "details": str(e)}), 500

@bp.route("/complete/<email>", methods=["GET"])
def get_complete_recommendations(email):
    """
    Get both company recommendations and job openings for a user
    
    Args:
        email: User's email address
        
    Returns:
        Complete recommendations including companies and jobs
    """
    try:
        email = email.strip().lower()
        
        # Get user profile from database
        supabase = get_supabase_client()
        user_result = supabase.table("users").select(
            "email, course, student_number, primary_archetype, "
            "archetype_realistic_percentage, archetype_investigative_percentage, "
            "archetype_artistic_percentage, archetype_social_percentage, "
            "archetype_enterprising_percentage, archetype_conventional_percentage, "
            "tor_notes"
        ).eq("email", email).execute()
        
        if not user_result.data:
            return jsonify({"error": "User not found"}), 404
        
        user_profile = user_result.data[0]
        
        # Get company recommendations using Gemini AI
        try:
            engine = GeminiRecommendationEngine()
            companies = engine.generate_company_recommendations(user_profile)
        except Exception as e:
            return jsonify({
                "error": "Failed to generate company recommendations", 
                "details": str(e),
                "message": "Gemini AI service is required but not available. Please ensure GEMINI_API_KEY is configured."
            }), 500
        
        # Get job openings using Gemini AI
        try:
            job_openings = engine.generate_job_openings(user_profile, companies)
        except Exception as e:
            return jsonify({
                "error": "Failed to generate job openings", 
                "details": str(e),
                "message": "Gemini AI service is required but not available. Please ensure GEMINI_API_KEY is configured."
            }), 500
        
        return jsonify({
            "message": "Complete recommendations generated successfully",
            "user_profile": {
                "email": user_profile.get("email"),
                "course": user_profile.get("course"),
                "primary_archetype": user_profile.get("primary_archetype")
            },
            "companies": companies,
            "job_openings": job_openings,
            "summary": {
                "total_companies": len(companies),
                "total_jobs": len(job_openings),
                "top_companies": companies[:5],
                "top_jobs": job_openings[:5]
            }
        }), 200
        
    except Exception as e:
        current_app.logger.exception("Failed to get complete recommendations for %s", email)
        return jsonify({"error": "Failed to get complete recommendations", "details": str(e)}), 500

@bp.route("/companies", methods=["POST"])
def get_company_recommendations_with_profile():
    """
    Get company recommendations with provided user profile
    
    Body JSON: {
        "name": "Student Name",
        "course": "BS Information Technology",
        "primary_archetype": "investigative",
        "archetype_percentages": {...},
        "career_forecast": {...}
    }
    
    Returns:
        List of recommended companies
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Profile data is required"}), 400
        
        # Get company recommendations using provided profile
        companies = get_company_recommendations(data)
        
        return jsonify({
            "message": "Company recommendations generated successfully",
            "companies": companies,
            "total_count": len(companies)
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to get company recommendations", "details": str(e)}), 500

@bp.route("/jobs", methods=["POST"])
def get_job_openings_with_profile():
    """
    Get job openings with provided user profile and companies
    
    Body JSON: {
        "user_profile": {...},
        "companies": [...]
    }
    
    Returns:
        List of job openings
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Profile and company data is required"}), 400
        
        user_profile = data.get("user_profile", {})
        companies = data.get("companies", [])
        
        # Get job openings using provided data
        job_openings = get_job_openings(user_profile, companies)
        
        return jsonify({
            "message": "Job openings generated successfully",
            "job_openings": job_openings,
            "total_count": len(job_openings)
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to get job openings", "details": str(e)}), 500
