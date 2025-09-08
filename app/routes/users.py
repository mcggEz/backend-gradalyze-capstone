from flask import Blueprint, jsonify, request, current_app
from app.routes.auth import token_required
from app.services.supabase_client import get_supabase_client
import os
import time
from datetime import datetime, timezone


bp = Blueprint("users", __name__, url_prefix="/api/users")


@bp.route("/", methods=["GET"])
@token_required
def list_users(current_user):
    try:
        supabase = get_supabase_client()
        response = supabase.table("users").select("*").execute()
        return jsonify(response.data), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500


@bp.route("/", methods=["POST"])
@token_required
def add_user(current_user):
    try:
        payload = request.get_json(silent=True) or {}
        if not payload:
            payload = {"name": "John Doe", "email": "john@example.com"}

        supabase = get_supabase_client()
        response = supabase.table("users").insert(payload).execute()
        return jsonify(response.data), 201
    except Exception as error:
        return jsonify({"error": str(error)}), 500


@bp.route("/upload-tor", methods=["POST", "DELETE"])
def upload_tor():
    """Upload a PDF Transcript of Records and associate it with the user.

    Dev mode (no auth): expects form-data with fields:
      - email: user's email
      - file (or tor): the PDF file
    """
    try:
        # Handle DELETE request for certificate deletion
        if request.method == "DELETE":
            data = request.get_json()
            email = (data.get('email') or '').strip().lower()
            certificate_path = data.get('certificate_path')
            
            if not email or not certificate_path:
                return jsonify({'message': 'email and certificate_path are required'}), 400
            
            supabase = get_supabase_client()
            
            # Get user by email
            res_user = supabase.table('users').select('id,certificate_paths,certificate_urls,certificates_count').eq('email', email).limit(1).execute()
            if not res_user.data:
                return jsonify({'message': 'User not found'}), 404
            
            user_data = res_user.data[0]
            user_id = user_data['id']
            
            # Remove certificate from arrays
            certificate_paths = list(user_data.get('certificate_paths', []))
            certificate_urls = list(user_data.get('certificate_urls', []))
            
            if certificate_path in certificate_paths:
                index = certificate_paths.index(certificate_path)
                certificate_paths.pop(index)
                if index < len(certificate_urls):
                    certificate_urls.pop(index)
                
                # Update user record
                supabase.table('users').update({
                    'certificates_count': max(0, user_data.get('certificates_count', 0) - 1),
                    'certificate_paths': certificate_paths,
                    'certificate_urls': certificate_urls,
                }).eq('id', user_id).execute()
                
                # Delete from storage
                try:
                    bucket = os.getenv('SUPABASE_CERT_BUCKET', 'certificates')
                    storage = supabase.storage
                    storage.from_(bucket).remove([certificate_path])
                except Exception as e:
                    print(f"Warning: Could not delete from storage: {e}")
                
                return jsonify({'message': 'Certificate deleted successfully'}), 200
            else:
                return jsonify({'message': 'Certificate not found'}), 404
        
        # Handle POST request for file upload
        # Accept either 'file' or 'tor' as the field name
        uploaded_file = request.files.get('file') or request.files.get('tor')
        email = (request.form.get('email') or '').strip().lower()
        user_id_form = request.form.get('user_id')
        kind = (request.form.get('kind') or 'tor').strip().lower()  # 'tor' | 'certificate'

        if not uploaded_file:
            return jsonify({'message': 'file is required (multipart/form-data)'}), 400

        # Allow more file types for certificates
        allowed_mimetypes = ['application/pdf', 'application/x-pdf']
        if kind == 'certificate':
            allowed_mimetypes.extend([
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'image/jpeg',
                'image/png',
                'image/jpg'
            ])
        
        if uploaded_file.mimetype not in allowed_mimetypes:
            return jsonify({'message': f'File type {uploaded_file.mimetype} not allowed. For certificates, only PDF, DOC, DOCX, JPG, and PNG files are allowed.'}), 400

        supabase = get_supabase_client()
        # Resolve user id from form user_id or email
        user_id = None
        if user_id_form and str(user_id_form).isdigit():
            user_id = int(user_id_form)
        elif email:
            res_user = supabase.table('users').select('id,email').eq('email', email).limit(1).execute()
            if res_user.data:
                user_id = res_user.data[0]['id']

        if user_id is None:
            return jsonify({'message': 'user_id or email is required to link the upload'}), 400

        # Choose bucket by kind
        bucket = os.getenv('SUPABASE_BUCKET')  # legacy fallback
        if not bucket:
            if kind == 'certificate':
                bucket = os.getenv('SUPABASE_CERT_BUCKET', 'certificates')
            else:
                bucket = os.getenv('SUPABASE_TOR_BUCKET', 'tor')
        storage = supabase.storage

        # Ensure bucket exists (ignore errors if it already exists)
        try:
            storage.create_bucket(bucket, public=True)
        except Exception:
            pass

        # Compute storage path and read bytes
        timestamp = int(time.time())
        prefix = 'tor' if kind == 'tor' else 'cert'
        
        # Get file extension
        filename = uploaded_file.filename
        file_extension = os.path.splitext(filename)[1] if filename else '.pdf'
        if not file_extension:
            file_extension = '.pdf'
        
        object_path = f"{user_id}/{prefix}-{timestamp}{file_extension}"
        file_bytes = uploaded_file.read()

        # Upload to storage
        storage.from_(bucket).upload(object_path, file_bytes, {
            'contentType': uploaded_file.mimetype,
            'upsert': 'true'
        })

        # Build public URL (bucket must be public)
        base_url = os.getenv('SUPABASE_URL', '').rstrip('/')
        public_url = f"{base_url}/storage/v1/object/public/{bucket}/{object_path}"

        # Update user record
        now_iso = datetime.now(timezone.utc).isoformat()
        if kind == 'certificate':
            # Increment certificates_count and append to arrays
            cert_count = 0
            certificate_paths: list[str] = []
            certificate_urls: list[str] = []
            try:
                q = supabase.table('users').select('certificates_count, certificate_paths, certificate_urls').eq('id', user_id).limit(1).execute()
                if q.data:
                    row = q.data[0]
                    if isinstance(row.get('certificates_count'), (int, float)):
                        cert_count = int(row['certificates_count'])
                    if isinstance(row.get('certificate_paths'), list):
                        certificate_paths = list(row['certificate_paths'])
                    if isinstance(row.get('certificate_urls'), list):
                        certificate_urls = list(row['certificate_urls'])
            except Exception:
                pass

            certificate_paths.append(object_path)
            certificate_urls.append(public_url)

            supabase.table('users').update({
                'latest_certificate_url': public_url,
                'latest_certificate_path': object_path,
                'certificates_count': cert_count + 1,
                'certificate_paths': certificate_paths,
                'certificate_urls': certificate_urls,
            }).eq('id', user_id).execute()
        else:
            supabase.table('users').update({
                'tor_url': public_url,
                'tor_storage_path': object_path,
                'tor_notes': None,
                'tor_uploaded_at': now_iso
            }).eq('id', user_id).execute()

        current_app.logger.info('Uploaded TOR for user %s (id=%s) to %s', email, user_id, object_path)
        return jsonify({
            'message': 'Upload successful',
            'user_id': user_id,
            'url': public_url,
            'storage_path': object_path,
            'kind': kind,
            'bucket': bucket
        }), 200
    except Exception as error:
        current_app.logger.exception('Upload TOR failed: %s', error)
        return jsonify({'message': 'Upload failed', 'error': str(error)}), 500


@bp.route("/extract-grades", methods=["POST"])
def extract_grades_from_pdf():
    """Read a stored PDF and perform comprehensive academic analysis.

    Body JSON:
      - email: user email
      - storage_path: transcripts/<user_id>/tor-xxxx.pdf

    Returns comprehensive academic analysis including grades, GPA, learning archetype, skills, and career recommendations.
    """
    try:
        data = request.get_json(silent=True) or {}
        email = (data.get('email') or '').strip().lower()
        storage_path = data.get('storage_path')

        if not email or not storage_path:
            return jsonify({'message': 'email and storage_path are required'}), 400

        supabase = get_supabase_client()
        # Fetch user for id and to validate ownership
        res_user = supabase.table('users').select('id').eq('email', email).limit(1).execute()
        if not res_user.data:
            return jsonify({'message': 'User not found'}), 404

        # Use TOR bucket for transcript extraction (fallback to legacy var or default)
        bucket = os.getenv('SUPABASE_TOR_BUCKET') or os.getenv('SUPABASE_BUCKET') or 'tor'
        
        # Download and parse PDF
        try:
            file_bytes = supabase.storage.from_(bucket).download(storage_path)
            import io
            import pdfplumber
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                pages_text = [page.extract_text() or '' for page in pdf.pages]
            full_text = '\n'.join(pages_text)
            current_app.logger.info(f'Extracted {len(full_text)} characters from PDF')
            current_app.logger.info(f'First 500 characters: {full_text[:500]}')
        except Exception as e:
            # If file download fails, use empty text (will generate sample data)
            current_app.logger.error(f'PDF extraction failed: {e}')
            full_text = ""

        # Use the new Academic Analyzer for comprehensive analysis
        from app.services.academic_analyzer import AcademicAnalyzer
        analyzer = AcademicAnalyzer()
        academic_analysis = analyzer.analyze_transcript(full_text)
        
        # Debug logging
        current_app.logger.info(f'Academic analysis result: {academic_analysis}')
        current_app.logger.info(f'Grades extracted: {len(academic_analysis.get("grades", []))}')
        if academic_analysis.get("grades"):
            current_app.logger.info(f'First grade: {academic_analysis["grades"][0]}')
            current_app.logger.info(f'All grades: {academic_analysis["grades"]}')
            
            # Log semester breakdown
            semesters = {}
            for grade in academic_analysis["grades"]:
                semester = grade.get('semester', 'Unknown')
                if semester not in semesters:
                    semesters[semester] = []
                semesters[semester].append(grade.get('subject', 'Unknown'))
            
            for semester, subjects in semesters.items():
                current_app.logger.info(f'Semester {semester}: {len(subjects)} subjects')
                current_app.logger.info(f'Subjects: {subjects}')

        # Store the comprehensive analysis in the user record
        import json
        
        # Extract archetype data for database storage
        learning_archetype = academic_analysis.get('learning_archetype', {})
        archetype_percentages = learning_archetype.get('archetype_percentages', {})
        primary_archetype = learning_archetype.get('primary_archetype', '')
        
        # Prepare update data with archetype percentages
        update_data = {
            'tor_notes': json.dumps(academic_analysis),
            'primary_archetype': primary_archetype,
            'archetype_analyzed_at': datetime.now(timezone.utc).isoformat()
        }
        
        # Add individual archetype percentages
        archetype_mapping = {
            'realistic': 'archetype_realistic_percentage',
            'investigative': 'archetype_investigative_percentage',
            'artistic': 'archetype_artistic_percentage',
            'social': 'archetype_social_percentage',
            'enterprising': 'archetype_enterprising_percentage',
            'conventional': 'archetype_conventional_percentage'
        }
        
        for archetype_key, percentage in archetype_percentages.items():
            if archetype_key in archetype_mapping:
                column_name = archetype_mapping[archetype_key]
                update_data[column_name] = percentage
        
        supabase.table('users').update(update_data).eq('email', email).execute()

        return jsonify({
            'message': 'Academic analysis complete',
            'analysis': academic_analysis,
            'text': full_text,
            'grades': academic_analysis.get('grades', []),
            'extracted_text_length': len(full_text),
            'debug_info': {
                'text_preview': full_text[:200] + '...' if len(full_text) > 200 else full_text,
                'grades_count': len(academic_analysis.get('grades', [])),
                'has_grades': bool(academic_analysis.get('grades'))
            }
        }), 200
        
    except Exception as error:
        current_app.logger.exception('Academic analysis failed: %s', error)
        return jsonify({'message': 'Analysis failed', 'error': str(error)}), 500


@bp.route("/job-matches/<email>", methods=["GET"])
def get_job_matches(email):
    """Get personalized job matches for a user based on their academic profile.
    
    Path parameter:
      - email: user's email address
      
    Query parameters:
      - limit: number of matches to return (default: 10)
    """
    try:
        email = email.strip().lower()
        limit = int(request.args.get('limit', 10))
        
        from app.services.job_matcher import JobMatcher
        matcher = JobMatcher()
        
        job_matches = matcher.match_jobs_for_user(email, limit)
        
        if 'error' in job_matches:
            return jsonify({'message': job_matches['error']}), 404
        
        return jsonify(job_matches), 200
        
    except Exception as error:
        current_app.logger.exception('Job matching failed: %s', error)
        return jsonify({'message': 'Job matching failed', 'error': str(error)}), 500


@bp.route("/profile-summary/<email>", methods=["GET"])
def get_profile_summary(email):
    """Get a summary of user's academic profile and career recommendations.
    
    Path parameter:
      - email: user's email address
    """
    try:
        email = email.strip().lower()
        
        from app.services.job_matcher import JobMatcher
        matcher = JobMatcher()
        
        user_profile = matcher.get_user_academic_profile(email)
        if not user_profile:
            return jsonify({'message': 'User profile not found'}), 404
        
        profile_summary = matcher.get_profile_summary(user_profile)
        academic_analysis = user_profile['academic_analysis']
        
        return jsonify({
            'profile_summary': profile_summary,
            'learning_archetype': academic_analysis.get('learning_archetype', {}),
            'academic_metrics': academic_analysis.get('academic_metrics', {}),
            'career_recommendations': academic_analysis.get('career_recommendations', []),
            'skills': academic_analysis.get('skills', [])
        }), 200
        
    except Exception as error:
        current_app.logger.exception('Profile summary failed: %s', error)
        return jsonify({'message': 'Profile summary failed', 'error': str(error)}), 500


@bp.route('/delete-tor', methods=['DELETE'])
def delete_tor():
    """Delete user's TOR and analysis data"""
    try:
        email = request.args.get('email')
        
        if not email:
            return jsonify({'message': 'Email parameter is required'}), 400
        
        supabase = get_supabase_client()
        
        # Clear TOR-related fields
        update_data = {
            'tor_url': None,
            'tor_notes': None,
            'tor_uploaded_at': None,
            'archetype_analyzed_at': None,
            'primary_archetype': None,
            'archetype_realistic_percentage': None,
            'archetype_investigative_percentage': None,
            'archetype_artistic_percentage': None,
            'archetype_social_percentage': None,
            'archetype_enterprising_percentage': None,
            'archetype_conventional_percentage': None,
            'career_recommendations': None,
            'analysis_results': None
        }
        
        response = supabase.table('users').update(update_data).eq('email', email).execute()
        
        if response.data:
            return jsonify({
                'message': 'TOR and analysis data deleted successfully',
                'deleted': True
            }), 200
        else:
            return jsonify({
                'message': 'Failed to delete TOR data',
                'deleted': False
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Error deleting TOR: {str(e)}")
        return jsonify({'message': 'Failed to delete TOR data', 'error': str(e)}), 500

