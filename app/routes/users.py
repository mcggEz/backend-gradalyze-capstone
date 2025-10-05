from flask import Blueprint, jsonify, request, current_app
from app.routes.auth import token_required
from app.services.supabase_client import get_supabase_client
from app.services.ml_models import build_feature_vector_from_grades
from app.services.ml_models import predict_career_scores, predict_archetype_kmeans
import os
import time
from datetime import datetime, timezone
import json


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
            data = request.get_json(silent=True) or {}
            email = (data.get('email') or '').strip().lower()
            certificate_path = (data.get('certificate_path') or '').strip()
            certificate_url = (data.get('certificate_url') or '').strip()

            if not email or (not certificate_path and not certificate_url):
                return jsonify({'message': 'email and certificate_path or certificate_url are required'}), 400

            supabase = get_supabase_client()

            # Get user by email
            res_user = supabase.table('users').select('*').eq('email', email).limit(1).execute()
            if not res_user.data:
                return jsonify({'message': 'User not found'}), 404

            user_data = res_user.data[0]
            user_id = user_data.get('id')

            # Normalize arrays (handle null/strings)
            def to_list(v):
                if v is None:
                    return []
                if isinstance(v, list):
                    return list(v)
                if isinstance(v, str):
                    try:
                        parsed = json.loads(v)
                        if isinstance(parsed, list):
                            return parsed
                    except Exception:
                        pass
                    return [s.strip() for s in v.split(',') if s.strip()]
                return []

            certificate_paths = to_list(user_data.get('certificate_paths'))
            certificate_urls = to_list(user_data.get('certificate_urls'))

            # If only URL provided, try to match by URL or by trailing path segment
            target_index = -1
            if certificate_path:
                if certificate_path in certificate_paths:
                    target_index = certificate_paths.index(certificate_path)
                else:
                    # sometimes frontend sends full URL as path
                    for i, p in enumerate(certificate_paths):
                        if p and (p == certificate_path or certificate_path.endswith('/' + p)):
                            target_index = i
                            break
            elif certificate_url:
                if certificate_url in certificate_urls:
                    target_index = certificate_urls.index(certificate_url)
                else:
                    # map URL to path by suffix
                    for i, u in enumerate(certificate_urls):
                        if u and certificate_url and (u == certificate_url or certificate_url.endswith('/' + (certificate_paths[i] if i < len(certificate_paths) else ''))):
                            target_index = i
                            break

            if target_index == -1:
                return jsonify({'message': 'Certificate not found'}), 404

            # Values to remove
            removed_path = certificate_paths[target_index] if target_index < len(certificate_paths) else None
            if target_index < len(certificate_paths):
                certificate_paths.pop(target_index)
            if target_index < len(certificate_urls):
                certificate_urls.pop(target_index)

            # Build update only for existing columns, also clear latest if needed
            existing_columns = set(user_data.keys())
            potential_updates = {
                'certificates_count': max(0, int(user_data.get('certificates_count') or 0) - 1),
                'certificate_paths': certificate_paths,
                'certificate_urls': certificate_urls,
            }
            # Clear latest fields if they match removed
            latest_path = (user_data.get('latest_certificate_path') or '').strip()
            latest_url = (user_data.get('latest_certificate_url') or '').strip()
            if removed_path and latest_path and (removed_path == latest_path or latest_path.endswith('/' + removed_path)):
                potential_updates['latest_certificate_path'] = None
            if certificate_url and latest_url and (certificate_url == latest_url or latest_url.endswith('/' + (removed_path or ''))):
                potential_updates['latest_certificate_url'] = None
            # If arrays are now empty, clear latest fields if present
            if not certificate_paths:
                potential_updates['latest_certificate_path'] = None
            if not certificate_urls:
                potential_updates['latest_certificate_url'] = None
            update_data = {k: v for k, v in potential_updates.items() if k in existing_columns}
            if update_data:
                current_app.logger.info('[CERT_DELETE] updating user %s with %s', user_id, update_data)
                supabase.table('users').update(update_data).eq('id', user_id).execute()

            # Delete from storage if we have a path
            if removed_path:
                try:
                    bucket = os.getenv('SUPABASE_CERT_BUCKET', 'certificates')
                    supabase.storage.from_(bucket).remove([removed_path])
                except Exception as e:
                    current_app.logger.warning('Certificate storage delete warning: %s', e)

            return jsonify({'message': 'Certificate deleted successfully'}), 200
        
        # Handle POST request for file upload
        # Accept either 'file' or 'tor' as the field name
        uploaded_file = request.files.get('file') or request.files.get('tor')
        email = (request.form.get('email') or '').strip().lower()
        user_id_form = request.form.get('user_id')
        kind = (request.form.get('kind') or 'tor').strip().lower()  # 'tor' | 'certificate'

        if not uploaded_file:
            return jsonify({'message': 'file is required (multipart/form-data)'}), 400

        # Debug file info
        current_app.logger.info(f"Upload attempt - File: {uploaded_file.filename}, MIME: {uploaded_file.mimetype}, Size: {uploaded_file.content_length}, Kind: {kind}")

        # Allow more file types for certificates
        allowed_mimetypes = [
            'application/pdf', 
            'application/x-pdf',
            'application/octet-stream',  # Some PDFs have this MIME type
            'text/pdf'  # Some systems use this
        ]
        if kind == 'certificate':
            allowed_mimetypes.extend([
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'image/jpeg',
                'image/png',
                'image/jpg'
            ])
        
        if uploaded_file.mimetype not in allowed_mimetypes:
            error_msg = f'File type {uploaded_file.mimetype} not allowed. '
            if kind == 'tor':
                error_msg += 'For transcripts, only PDF files are allowed.'
            else:
                error_msg += 'For certificates, only PDF, DOC, DOCX, JPG, and PNG files are allowed.'
            current_app.logger.warning(f"File type rejected: {uploaded_file.mimetype} for {kind}")
            return jsonify({'message': error_msg}), 400

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

        # For TOR enforce exactly one file per user; preserve original filename
        if kind == 'tor':
            # Determine previous TOR path
            try:
                prev_q = supabase.table('users').select('tor_storage_path').eq('id', user_id).limit(1).execute()
                prev_path = prev_q.data[0].get('tor_storage_path') if prev_q.data else None
            except Exception:
                prev_path = None

            # Preserve original file name (sanitize)
            original_base = os.path.basename(filename) if filename else f"tor{file_extension}"
            safe_name = ''.join(ch if ch.isalnum() or ch in ['.', '-', '_'] else '-' for ch in original_base).strip('-')
            if not safe_name:
                safe_name = f"tor{file_extension}"
            object_path = f"{user_id}/{safe_name}"

            # If previous path exists and is different, remove it to keep only one TOR in storage
            if prev_path and prev_path != object_path:
                try:
                    bucket_del = os.getenv('SUPABASE_TOR_BUCKET') or os.getenv('SUPABASE_BUCKET') or 'tor'
                    supabase.storage.from_(bucket_del).remove([prev_path])
                except Exception as e:
                    current_app.logger.warning('Could not delete previous TOR from storage: %s', e)
        else:
            # For certificates, preserve original file name (sanitize)
            original_base = os.path.basename(filename) if filename else f"{prefix}{file_extension}"
            safe_name = ''.join(ch if ch.isalnum() or ch in ['.', '-', '_'] else '-' for ch in original_base).strip('-')
            if not safe_name:
                safe_name = f"{prefix}{file_extension}"
            object_path = f"{user_id}/{safe_name}"
        file_bytes = uploaded_file.read()

        # Upload to storage with robust error handling
        try:
            storage.from_(bucket).upload(object_path, file_bytes, {
                'contentType': uploaded_file.mimetype,
                'upsert': 'true'
            })
        except Exception as e:
            # Retry with service role client; also ensure bucket exists (public)
            current_app.logger.warning('[UPLOAD] primary upload failed, retrying with service role: %s', e)
            try:
                from app.services.supabase_client import create_supabase_client
                sr_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
                if sr_key:
                    sr_client = create_supabase_client(sr_key)
                    # Ensure bucket exists and is public
                    try:
                        sr_client.storage.create_bucket(bucket, public=True)
                    except Exception:
                        pass
                    sr_client.storage.from_(bucket).upload(object_path, file_bytes, {
                        'contentType': uploaded_file.mimetype,
                        'upsert': 'true'
                    })
                else:
                    raise RuntimeError('Service role key not configured')
            except Exception as e2:
                current_app.logger.exception('[UPLOAD] storage upload failed (both attempts): bucket=%s path=%s mime=%s err=%s', bucket, object_path, uploaded_file.mimetype, e2)
                return jsonify({'message': 'Storage upload failed', 'error': str(e2), 'bucket': bucket, 'path': object_path}), 500

        # Build public URL (bucket must be public)
        base_url = os.getenv('SUPABASE_URL', '').rstrip('/')
        public_url = f"{base_url}/storage/v1/object/public/{bucket}/{object_path}"

        # Update user record
        now_iso = datetime.now(timezone.utc).isoformat()
        if kind == 'certificate':
            current_app.logger.info('[CERT_UPLOAD] processing certificate for user_id=%s', user_id)
            # Read full row so we can update only columns that exist in this environment
            try:
                q = supabase.table('users').select('*').eq('id', user_id).limit(1).execute()
                row = q.data[0] if q.data else {}
            except Exception as e:
                current_app.logger.warning('[CERT_UPLOAD] failed to read user row: %s', e)
                row = {}

            # Determine existing values
            cert_count = 0
            if isinstance(row.get('certificates_count'), (int, float)):
                cert_count = int(row['certificates_count'])

            certificate_paths: list[str] = []
            if isinstance(row.get('certificate_paths'), list):
                certificate_paths = list(row['certificate_paths'])

            certificate_urls: list[str] = []
            if isinstance(row.get('certificate_urls'), list):
                certificate_urls = list(row['certificate_urls'])

            current_app.logger.info('[CERT_UPLOAD] existing data: count=%s, paths=%s, urls=%s', cert_count, certificate_paths, certificate_urls)

            # Append new (dedupe by path); keep arrays aligned
            if object_path in certificate_paths:
                idx = certificate_paths.index(object_path)
                if idx < len(certificate_urls):
                    certificate_urls[idx] = public_url
                else:
                    while len(certificate_urls) < idx:
                        certificate_urls.append('')
                    certificate_urls.append(public_url)
            else:
                certificate_paths.append(object_path)
                certificate_urls.append(public_url)

            # Prepare full set of potential updates
            potential_updates = {
                'latest_certificate_url': public_url,
                'latest_certificate_path': object_path,
                'latest_certificate_uploaded_at': now_iso,
                'certificates_count': len(certificate_paths) if certificate_paths else cert_count + 1,
                'certificate_paths': certificate_paths,
                'certificate_urls': certificate_urls,
            }

            # Only include columns that actually exist in this schema
            existing_columns = set(row.keys())
            update_data = {k: v for k, v in potential_updates.items() if k in existing_columns}

            # If none of the cert columns exist (unlikely), fall back to no-op safe update on id to avoid 500
            if not update_data:
                current_app.logger.warning('[CERT_UPLOAD] No matching certificate columns found in schema; skipping user row update')
            else:
                current_app.logger.info('[CERT_UPLOAD] updating with data: %s', update_data)
                try:
                    result = supabase.table('users').update(update_data).eq('id', user_id).execute()
                    current_app.logger.info('[CERT_UPLOAD] update result: %s', result.data)
                except Exception as e:
                    current_app.logger.exception('[CERT_UPLOAD] update failed: %s', e)
                    return jsonify({'message': 'Certificate metadata update failed', 'error': str(e)}), 500
        else:
            # Update TOR pointers
            supabase.table('users').update({
                'tor_url': public_url,
                'tor_storage_path': object_path,
                'tor_notes': None,
                'tor_uploaded_at': now_iso,
                # Reset prior analysis so UI doesn't render stale results
                'primary_archetype': None,
                'archetype_analyzed_at': None,
                'archetype_realistic_percentage': None,
                'archetype_investigative_percentage': None,
                'archetype_artistic_percentage': None,
                'archetype_social_percentage': None,
                'archetype_enterprising_percentage': None,
                'archetype_conventional_percentage': None,
            }).eq('id', user_id).execute()
            # NOTE: Analysis is triggered via explicit frontend action.

        current_app.logger.info('Uploaded file for user %s (id=%s) to %s (kind=%s)', email, user_id, object_path, kind)
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
        
        # IMPORTANT: Do not persist archetype/career results here.
        # OCR endpoint should only extract grades. Full processing happens
        # when the user clicks "Process & Analyze".

        # Return only numeric grades array
        def _to_numeric_grades(raw_list):
            def to_float(v):
                if v is None:
                    return None
                if isinstance(v, (int, float)):
                    return float(v)
                if isinstance(v, str):
                    try:
                        return float(v.strip())
                    except Exception:
                        return None
                return None

            def is_quarter_grade(x: float) -> bool:
                if x is None:
                    return False
                if x < 1.0 or x > 3.0:
                    return False
                q = round((x - 1.0) * 4)
                return abs(x - (1.0 + q / 4.0)) < 1e-6

            nums = []
            if not isinstance(raw_list, list):
                return nums
            for g in raw_list:
                try:
                    if not isinstance(g, dict):
                        val = to_float(g)
                        if val is not None:
                            nums.append(round(val, 2))
                        continue

                    candidates = []
                    for key in ('grade', 'final_grade', 'final', 'rating', 'score'):
                        candidates.append(to_float(g.get(key)))
                    # Prefer proper quarter-step grade between 1.00 and 3.00
                    grade_val = next((x for x in candidates if x is not None and is_quarter_grade(x)), None)

                    # Avoid confusing units (1,2,3) as grade when no decimal present
                    units_val = to_float(g.get('units'))
                    if (grade_val is None or (grade_val in (1.0, 2.0, 3.0))) and units_val in (1.0, 2.0, 3.0):
                        # If there is a text field containing a decimal like 1.25/1.50/2.75, extract that
                        txt_fields = [str(g.get(k) or '') for k in ('raw', 'line', 'subject', 'title')]
                        import re as _re
                        m = _re.findall(r"(?:(?<!\d)(?:1|2|3))(?:\.00|\.25|\.50|\.75)", ' '.join(txt_fields))
                        if m:
                            try:
                                grade_val = float(m[0])
                            except Exception:
                                pass

                    if grade_val is None:
                        # Fallback: use any numeric that looks like a grade and not the units
                        for x in candidates:
                            if x is not None and is_quarter_grade(x):
                                grade_val = x
                                break

                    if grade_val is not None:
                        nums.append(round(float(grade_val), 2))
                except Exception:
                    continue
            return nums

        numeric_grades = _to_numeric_grades(academic_analysis.get('grades', []))

        # Do NOT synthesize or override with derived data; return only what analyzer extracted

        return jsonify({
            'message': 'Academic analysis complete',
            'grades': numeric_grades
        }), 200
        
    except Exception as error:
        current_app.logger.exception('Academic analysis failed: %s', error)
        return jsonify({'message': 'Analysis failed', 'error': str(error)}), 500


@bp.route("/profile-summary/<email>", methods=["GET"])
def get_profile_summary(email):
    """Get a summary of user's academic profile and career recommendations.
    
    Path parameter:
      - email: user's email address
    """
    try:
        email = email.strip().lower()
        
        supabase = get_supabase_client()
        
        # Get user data
        user_result = supabase.table("users").select(
            "primary_archetype, archetype_realistic_percentage, archetype_investigative_percentage, "
            "archetype_artistic_percentage, archetype_social_percentage, archetype_enterprising_percentage, "
            "archetype_conventional_percentage, tor_notes"
        ).eq("email", email).execute()
        
        if not user_result.data:
            return jsonify({'message': 'User profile not found'}), 404
        
        user = user_result.data[0]
        
        # Get archetype percentages
        archetype_percentages = {
            'realistic': user.get('archetype_realistic_percentage', 0.0),
            'investigative': user.get('archetype_investigative_percentage', 0.0),
            'artistic': user.get('archetype_artistic_percentage', 0.0),
            'social': user.get('archetype_social_percentage', 0.0),
            'enterprising': user.get('archetype_enterprising_percentage', 0.0),
            'conventional': user.get('archetype_conventional_percentage', 0.0)
        }
        
        # Get TOR notes for career forecast
        tor_notes = user.get('tor_notes', {})
        career_forecast = tor_notes.get('analysis_results', {}).get('career_forecast', {})
        
        return jsonify({
            'primary_archetype': user.get('primary_archetype', ''),
            'archetype_percentages': archetype_percentages,
            'career_forecast': career_forecast
        }), 200
        
    except Exception as error:
        current_app.logger.exception('Profile summary failed: %s', error)
        return jsonify({'message': 'Profile summary failed', 'error': str(error)}), 500


@bp.route('/delete-tor', methods=['DELETE'])
def delete_tor():
    """Delete user's TOR and analysis data"""
    try:
        email = (request.args.get('email') or '').strip().lower()
        current_app.logger.info('[DELETE_TOR] incoming request for email=%s', email)
        if not email and request.is_json:
            body = request.get_json(silent=True) or {}
            email = (body.get('email') or '').strip().lower()
        
        if not email:
            return jsonify({'message': 'Email parameter is required'}), 400
        
        supabase = get_supabase_client()

        # Simple approach - just clear the core TOR fields (avoid non-existent columns)
        update_data = {
            'tor_url': None,
            'tor_storage_path': None,
            'tor_notes': None,
            'tor_uploaded_at': None,
            'archetype_analyzed_at': None,
            'primary_archetype': None,
            'archetype_realistic_percentage': None,
            'archetype_investigative_percentage': None,
            'archetype_artistic_percentage': None,
            'archetype_social_percentage': None,
            'archetype_enterprising_percentage': None,
            'archetype_conventional_percentage': None
        }

        current_app.logger.info('[DELETE_TOR] update payload=%s', update_data)
        # Direct update - same as test code
        result = supabase.table('users').update(update_data).eq('email', email).execute()
        current_app.logger.info('[DELETE_TOR] update result=%s', result.data)

        # Verify
        verify = supabase.table('users').select('tor_url, tor_storage_path').eq('email', email).limit(1).execute()
        current_app.logger.info('[DELETE_TOR] verify after update=%s', verify.data)
        if verify.data:
            row = verify.data[0]
            cleared = ((row.get('tor_url') in (None, '')) and (row.get('tor_storage_path') in (None, '')))
            if not cleared:
                return jsonify({'message': 'Failed to clear TOR data', 'verify': row}), 500
        
        return jsonify({
            'message': 'TOR and analysis data deleted successfully',
            'deleted': True,
            'cleared': True
        }), 200
            
    except Exception as e:
        current_app.logger.exception('[DELETE_TOR] error for %s: %s', email if 'email' in locals() else 'unknown', e)
        return jsonify({'message': 'Failed to delete TOR data', 'error': str(e)}), 500

