"""
Dossier generation routes for creating professional portfolios
"""

from flask import Blueprint, request, jsonify
from app.routes.auth import token_required
from app.services.supabase_client import get_supabase_client
import json

bp = Blueprint('dossier', __name__, url_prefix='/api/dossier')

@bp.route('/generate', methods=['POST'])
@token_required
def generate_dossier(current_user):
    """Generate professional dossier based on stored analysis results in Supabase."""
    try:
        supabase = get_supabase_client()
        res = supabase.table('users').select(
            'email, first_name, last_name, course, primary_archetype, '
            'archetype_realistic_percentage, archetype_investigative_percentage, archetype_artistic_percentage, '
            'archetype_social_percentage, archetype_enterprising_percentage, archetype_conventional_percentage, tor_notes'
        ).eq('email', current_user).limit(1).execute()
        if not res.data:
            return jsonify({'message': 'User not found'}), 404

        row = res.data[0]
        try:
            notes = json.loads(row.get('tor_notes') or '{}')
        except Exception:
            notes = {}
        # Support both structures: notes.analysis_results.career_forecast or legacy fields
        analysis_results = notes.get('analysis_results') or notes.get('archetype_analysis') or {}
        career_forecast = analysis_results.get('career_forecast') or notes.get('career_forecast') or {}
        grades = notes.get('grades') or notes.get('academic_analysis', {}).get('grades') or []

        # Build academic metrics
        total_units = sum(float(g.get('units', 0) or 0) for g in grades) if grades else 0
        total_subjects = len(grades)
        avg_grade = (sum(float(g.get('grade', 0) or 0) for g in grades) / total_subjects) if total_subjects else 0

        # Career recommendations: take top 3 by score if mapping
        if isinstance(career_forecast, dict):
            careers_sorted = sorted(career_forecast.items(), key=lambda kv: kv[1], reverse=True)[:3]
            career_paths = [
                {'title': k, 'match': round(float(v) * 100) if v <= 1 else round(float(v)), 'demand': '—', 'salary': '—'}
                for k, v in careers_sorted
            ]
        else:
            career_paths = career_forecast if isinstance(career_forecast, list) else []

        dossier = {
            'personal_info': {
                'email': row.get('email'),
                'name': f"{row.get('first_name','')} {row.get('last_name','')}".strip(),
                'course': row.get('course'),
                'status': 'Generated'
            },
            'archetype': {
                'type': row.get('primary_archetype'),
                'percentages': {
                    'realistic': row.get('archetype_realistic_percentage'),
                    'investigative': row.get('archetype_investigative_percentage'),
                    'artistic': row.get('archetype_artistic_percentage'),
                    'social': row.get('archetype_social_percentage'),
                    'enterprising': row.get('archetype_enterprising_percentage'),
                    'conventional': row.get('archetype_conventional_percentage')
                }
            },
            'academic_performance': {
                'total_subjects': total_subjects,
                'total_units': total_units,
                'average_grade': round(avg_grade, 2)
            },
            'career_recommendations': career_paths,
        }

        return jsonify({'message': 'Dossier generated successfully', 'dossier': dossier}), 200

    except Exception as e:
        return jsonify({'message': 'Dossier generation failed', 'error': str(e)}), 500

@bp.route('/download', methods=['GET'])
@token_required
def download_dossier(current_user):
    """Download dossier as PDF (stub)."""
    try:
        # Stub response; real PDF generation not implemented here
        return jsonify({
            'message': 'PDF generation simulated',
            'download_url': f'/downloads/dossier-{current_user.split("@")[0]}.pdf',
            'file_size': '2.5 MB',
            'pages': 4
        }), 200
    except Exception as e:
        return jsonify({'message': 'Download failed', 'error': str(e)}), 500

@bp.route('/share', methods=['POST'])
@token_required
def share_dossier(current_user):
    """Generate shareable link for dossier (stub)."""
    try:
        share_token = f"share-{current_user.split('@')[0]}"
        share_url = f"https://gradalyze.com/shared/{share_token}"
        return jsonify({'message': 'Share link generated', 'share_url': share_url, 'expires_in': '30 days', 'access_type': 'view_only'}), 200
    except Exception as e:
        return jsonify({'message': 'Share link generation failed', 'error': str(e)}), 500

@bp.route('/preview', methods=['GET'])
@token_required
def preview_dossier(current_user):
    """Get dossier preview data by reading Supabase user record."""
    try:
        supabase = get_supabase_client()
        res = supabase.table('users').select('email, tor_notes, primary_archetype').eq('email', current_user).limit(1).execute()
        if not res.data:
            return jsonify({'message': 'User not found'}), 404
        row = res.data[0]
        try:
            notes = json.loads(row.get('tor_notes') or '{}')
        except Exception:
            notes = {}
        analysis_results = notes.get('analysis_results') or {}
        career_forecast = analysis_results.get('career_forecast') or {}
        if isinstance(career_forecast, dict):
            careers_sorted = sorted(career_forecast.items(), key=lambda kv: kv[1], reverse=True)[:2]
            career_paths = [{'title': k, 'match': round(float(v) * 100) if v <= 1 else round(float(v))} for k, v in careers_sorted]
        else:
            career_paths = career_forecast if isinstance(career_forecast, list) else []
        return jsonify({
            'message': 'Dossier preview',
            'preview': {
                'archetype': {'type': row.get('primary_archetype')},
                'career_paths': career_paths,
                'status': 'preview'
            }
        }), 200
    except Exception as e:
        return jsonify({'message': 'Preview generation failed', 'error': str(e)}), 500


