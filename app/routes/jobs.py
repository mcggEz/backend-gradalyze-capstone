from flask import Blueprint, request, jsonify
from app.services.supabase_client import get_supabase_client
from app.services.job_scraper import run_job_scraper, run_job_scraper_for_user


bp = Blueprint("jobs", __name__, url_prefix="/api/jobs")


@bp.route("/", methods=["GET"])
def list_jobs():
    """List jobs with simple pagination (limit/offset) ordered by posted_at desc, then scraped_at desc.

    Query params:
      - limit: int (default 20, max 100)
      - offset: int (default 0)
    """
    try:
        limit = min(int(request.args.get("limit", 20)), 100)
        offset = max(int(request.args.get("offset", 0)), 0)

        supabase = get_supabase_client()

        # Build the select with ordering and range
        # Supabase python client: range is inclusive, so use offset..offset+limit-1
        start = offset
        end = offset + limit - 1

        query = (
            supabase
            .table("jobs")
            .select(
                "id,title,company,location,employment_type,remote,salary_min,salary_max,currency,url,source,posted_at,scraped_at,tags,description"
            )
            .order("posted_at", desc=True)
            .order("scraped_at", desc=True)
            .range(start, end)
        )

        res = query.execute()
        rows = res.data or []

        # Determine has_more by attempting to see if there are exactly 'limit' rows returned
        has_more = len(rows) == limit

        return jsonify({
            "jobs": rows,
            "limit": limit,
            "offset": offset,
            "has_more": has_more,
        }), 200
    except Exception as error:
        return jsonify({"message": "Failed to fetch jobs", "error": str(error)}), 500


@bp.route("/scrape", methods=["POST"])
def scrape_jobs():
    """Trigger job scraping from multiple sources"""
    try:
        data = request.get_json() or {}
        
        # Check if this is a user-specific scrape
        user_email = data.get("user_email")
        
        if user_email:
            # User-specific scraping based on archetype percentages
            location = data.get("location", "Philippines")
            sources = data.get("sources", ["google", "linkedin", "indeed"])
            jobs_per_query = data.get("jobs_per_query", 5)
            
            # Run the user-specific scraper
            result = run_job_scraper_for_user(user_email, location, sources)
            
            return jsonify({
                "message": "User-specific job scraping completed",
                "result": result
            }), 200
        else:
            # Legacy scraping with specific query
            query = data.get("query", "software engineer")
            location = data.get("location", "Philippines")
            sources = data.get("sources", ["google", "linkedin", "indeed"])
            
            # Run the scraper
            result = run_job_scraper(query, location, sources)
            
            return jsonify({
                "message": "Job scraping completed",
                "result": result
            }), 200
        
    except Exception as error:
        return jsonify({"message": "Failed to scrape jobs", "error": str(error)}), 500


@bp.route("/scrape-for-user/<email>", methods=["POST"])
def scrape_jobs_for_user(email):
    """Trigger user-specific job scraping based on archetype percentages"""
    try:
        data = request.get_json() or {}
        
        location = data.get("location", "Philippines")
        sources = data.get("sources", ["google", "linkedin", "indeed"])
        jobs_per_query = data.get("jobs_per_query", 5)
        
        # Run the user-specific scraper
        result = run_job_scraper_for_user(email, location, sources)
        
        return jsonify({
            "message": "User-specific job scraping completed",
            "result": result
        }), 200
        
    except Exception as error:
        return jsonify({"message": "Failed to scrape jobs for user", "error": str(error)}), 500


