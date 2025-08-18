"""
Dossier generation routes for creating professional portfolios
"""

from flask import Blueprint, request, jsonify
from app.routes.auth import token_required
from app.routes.analysis import user_analysis_data

bp = Blueprint('dossier', __name__, url_prefix='/api/dossier')

@bp.route('/generate', methods=['POST'])
@token_required
def generate_dossier(current_user):
    """Generate professional dossier based on analysis results"""
    try:
        if current_user not in user_analysis_data:
            return jsonify({'message': 'No analysis data found'}), 404
        
        user_data = user_analysis_data[current_user]
        results = user_data.get('results', {})
        
        if not results:
            return jsonify({'message': 'Analysis must be completed first'}), 400
        
        # Generate comprehensive dossier data
        dossier = {
            'personal_info': {
                'email': current_user,
                'analysis_date': user_data.get('admin_review', {}).get('approved_at'),
                'status': 'Generated'
            },
            'archetype': results.get('archetype', {}),
            'academic_performance': results.get('academic_metrics', {}),
            'career_recommendations': results.get('career_paths', []),
            'skills_assessment': {
                'technical_skills': [
                    {'name': 'Programming', 'level': 90, 'category': 'Technical'},
                    {'name': 'Database Design', 'level': 85, 'category': 'Technical'},
                    {'name': 'System Analysis', 'level': 80, 'category': 'Analytical'},
                    {'name': 'Problem Solving', 'level': 95, 'category': 'Cognitive'},
                    {'name': 'Technical Writing', 'level': 75, 'category': 'Communication'}
                ]
            },
            'professional_summary': f"A dedicated student with an {results.get('archetype', {}).get('type', 'Unknown')} learning archetype, demonstrating exceptional analytical and problem-solving capabilities.",
            'generated_at': user_data.get('admin_review', {}).get('approved_at'),
            'document_id': f"GRAD-{current_user.split('@')[0].upper()}-2025"
        }
        
        # Store dossier
        user_analysis_data[current_user]['dossier'] = dossier
        
        return jsonify({
            'message': 'Dossier generated successfully',
            'dossier': dossier
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Dossier generation failed', 'error': str(e)}), 500

@bp.route('/download', methods=['GET'])
@token_required
def download_dossier(current_user):
    """Download dossier as PDF (simulated)"""
    try:
        if current_user not in user_analysis_data:
            return jsonify({'message': 'No dossier found'}), 404
        
        user_data = user_analysis_data[current_user]
        dossier = user_data.get('dossier', {})
        
        if not dossier:
            return jsonify({'message': 'Dossier must be generated first'}), 400
        
        # In production, this would generate an actual PDF
        return jsonify({
            'message': 'PDF generation simulated',
            'download_url': f'/downloads/dossier-{dossier.get("document_id", "unknown")}.pdf',
            'file_size': '2.5 MB',
            'pages': 4
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Download failed', 'error': str(e)}), 500

@bp.route('/share', methods=['POST'])
@token_required
def share_dossier(current_user):
    """Generate shareable link for dossier"""
    try:
        if current_user not in user_analysis_data:
            return jsonify({'message': 'No dossier found'}), 404
        
        user_data = user_analysis_data[current_user]
        dossier = user_data.get('dossier', {})
        
        if not dossier:
            return jsonify({'message': 'Dossier must be generated first'}), 400
        
        # Generate shareable link (simulated)
        share_token = f"share-{dossier.get('document_id', 'unknown')}"
        share_url = f"https://gradalyze.com/shared/{share_token}"
        
        return jsonify({
            'message': 'Share link generated',
            'share_url': share_url,
            'expires_in': '30 days',
            'access_type': 'view_only'
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Share link generation failed', 'error': str(e)}), 500

@bp.route('/preview', methods=['GET'])
@token_required
def preview_dossier(current_user):
    """Get dossier preview data"""
    try:
        if current_user not in user_analysis_data:
            return jsonify({'message': 'No analysis data found'}), 404
        
        user_data = user_analysis_data[current_user]
        
        # Return preview data or full dossier if available
        if 'dossier' in user_data:
            return jsonify({
                'message': 'Dossier preview',
                'dossier': user_data['dossier']
            }), 200
        else:
            # Return partial data for preview
            results = user_data.get('results', {})
            return jsonify({
                'message': 'Dossier preview (partial)',
                'preview': {
                    'archetype': results.get('archetype', {}),
                    'academic_metrics': results.get('academic_metrics', {}),
                    'career_paths': results.get('career_paths', [])[:2],  # Top 2 only
                    'status': 'preview'
                }
            }), 200
        
    except Exception as e:
        return jsonify({'message': 'Preview generation failed', 'error': str(e)}), 500


