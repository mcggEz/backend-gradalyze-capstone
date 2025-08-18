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


@bp.route("/upload-tor", methods=["POST"])
def upload_tor():
    """Upload a PDF Transcript of Records and associate it with the user.

    Dev mode (no auth): expects form-data with fields:
      - email: user's email
      - file (or tor): the PDF file
    """
    try:
        # Accept either 'file' or 'tor' as the field name
        uploaded_file = request.files.get('file') or request.files.get('tor')
        email = (request.form.get('email') or '').strip().lower()
        user_id_form = request.form.get('user_id')
        kind = (request.form.get('kind') or 'tor').strip().lower()  # 'tor' | 'certificate'

        if not uploaded_file:
            return jsonify({'message': 'file is required (multipart/form-data)'}), 400

        if uploaded_file.mimetype not in ('application/pdf', 'application/x-pdf'):
            return jsonify({'message': 'Only PDF files are allowed'}), 400

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
        object_path = f"{user_id}/{prefix}-{timestamp}.pdf"
        file_bytes = uploaded_file.read()

        # Upload to storage
        storage.from_(bucket).upload(object_path, file_bytes, {
            'contentType': 'application/pdf',
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
                'tor_verified': False,
                'tor_verified_at': None,
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
    """Read a stored PDF (via storage path) and extract simple text features.

    Body JSON:
      - email: user email
      - storage_path: transcripts/<user_id>/tor-xxxx.pdf

    Returns extracted text sample and a trivial ML-based clustering label (demo).
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
        # Download the file bytes from storage
        file_bytes = supabase.storage.from_(bucket).download(storage_path)

        # Parse PDF text
        import io
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages_text = [page.extract_text() or '' for page in pdf.pages]
        full_text = '\n'.join(pages_text)

        # Try to extract rough grade rows using a simple regex heuristic
        import re
        grade_rows = []
        pattern = re.compile(r"^\s*(?P<subject>[A-Za-z].*?)\s+(?P<grade>(?:[1-5](?:\.\d{2})?))\s+(?P<units>[1-6])\s*(?:units?)?\s*$")
        for line in full_text.splitlines():
            m = pattern.match(line)
            if m:
                try:
                    subject = m.group('subject').strip()
                    grade_val = float(m.group('grade'))
                    units_val = int(m.group('units'))
                    grade_rows.append({
                        'subject': subject[:120],
                        'grade': grade_val,
                        'units': units_val,
                        'semester': '',
                        'category': 'Major'
                    })
                except Exception:
                    continue

        # Fallback sample if nothing parsed
        if not grade_rows:
            grade_rows = [
                {
                    'subject': 'Unparsed Transcript Line',
                    'grade': 1.50,
                    'units': 3,
                    'semester': '',
                    'category': 'Major'
                }
            ]

        # Very simple text featurization + clustering demo
        # In a real system, you'd OCR tables and parse grade rows.
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.cluster import KMeans

        vectorizer = TfidfVectorizer(stop_words='english', max_features=500)
        X = vectorizer.fit_transform([full_text if full_text else 'empty'])
        model = KMeans(n_clusters=1, n_init='auto', random_state=42)
        labels = model.fit_predict(X)

        # Store a minimal extraction result back to the user row for demo
        supabase.table('users').update({
            'tor_notes': f'Extracted {len(full_text)} chars; parsed_rows={len(grade_rows)}; cluster={int(labels[0])}'
        }).eq('email', email).execute()

        return jsonify({
            'message': 'Extraction complete',
            'characters': len(full_text),
            'cluster': int(labels[0]),
            'text': full_text,
            'grades': grade_rows
        }), 200
    except Exception as error:
        current_app.logger.exception('Extract grades failed: %s', error)
        return jsonify({'message': 'Extraction failed', 'error': str(error)}), 500

