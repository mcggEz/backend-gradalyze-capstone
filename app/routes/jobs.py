from flask import Blueprint, request, jsonify
from app.services.supabase_client import get_supabase_client


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


