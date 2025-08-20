"""
Authentication routes for Gradalyze API
"""

from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from app.services.supabase_client import get_supabase_client
import jwt
import datetime
from functools import wraps

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Sample users (in production, this would be from a database)
USERS = {}

def token_required(f):
    """Decorator to require JWT token for protected routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            secret = current_app.config.get('SECRET_KEY', 'dev-secret-key-change-in-production')
            data = jwt.decode(token, secret, algorithms=['HS256'])
            current_user = data['email']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated


@bp.route('/register', methods=['POST'])
def register():
    """Register a new user in Supabase 'users' table."""
    try:
        data = request.get_json() or {}

        required_fields = ['firstName', 'lastName', 'studentNumber', 'course', 'email', 'password']
        missing = [f for f in required_fields if not data.get(f)]
        if missing:
            return jsonify({'message': 'Missing required fields', 'missing': missing}), 400

        if len(data['password']) < 6:
            return jsonify({'message': 'Password must be at least 6 characters'}), 400

        # Hash password
        password_hash = generate_password_hash(data['password'])

        # Map to DB columns
        record = {
            'first_name': data.get('firstName', '').strip(),
            'middle_name': data.get('middleName', '').strip() if data.get('middleName') else None,
            'last_name': data.get('lastName', '').strip(),
            'extension': data.get('extension', '').strip() if data.get('extension') else None,
            'student_number': data.get('studentNumber', '').strip(),
            'course': data.get('course', '').strip(),
            'email': data.get('email', '').strip().lower(),
            'password_hash': password_hash,
        }

        supabase = get_supabase_client()
        response = supabase.table('users').insert(record).execute()

        created = response.data[0] if response.data else {}
        if 'password_hash' in created:
            del created['password_hash']

        return jsonify({'message': 'Registration successful', 'user': created}), 201
    except Exception as e:
        return jsonify({'message': 'Registration failed', 'error': str(e)}), 500

@bp.route('/login', methods=['POST'])
def login():
    """User login endpoint using Supabase users table."""
    try:
        data = request.get_json() or {}
        email = (data.get('email') or '').strip().lower()
        password = data.get('password') or ''

        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400

        # Fetch user from Supabase
        supabase = get_supabase_client()
        current_app.logger.info('Login attempt for %s', email)
        # Select only columns guaranteed to exist; fill optional fields in code
        response = supabase.table('users').select(
            'id, email, first_name, last_name, course, student_number, password_hash'
        ).eq('email', email).limit(1).execute()

        if not response.data:
            current_app.logger.info('Login failed: user not found for %s', email)
            return jsonify({'message': 'Invalid credentials'}), 401

        db_user = response.data[0]
        if not check_password_hash(db_user.get('password_hash', ''), password):
            current_app.logger.info('Login failed: password mismatch for %s', email)
            return jsonify({'message': 'Invalid credentials'}), 401

        # Shape user payload without password_hash (JWT disabled for now)
        safe_user = {
            'id': db_user.get('id'),
            'email': db_user.get('email'),
            'name': f"{db_user.get('first_name','')} {db_user.get('last_name','')}".strip(),
            'course': db_user.get('course'),
            'student_number': db_user.get('student_number'),
        }

        current_app.logger.info('Login successful for %s (id=%s)', email, safe_user.get('id'))
        return jsonify({'message': 'Login successful', 'user': safe_user}), 200

    except Exception as e:
        current_app.logger.exception('Login error for %s: %s', request.json.get('email') if request.is_json else 'unknown', e)
        return jsonify({'message': 'Login failed', 'error': str(e)}), 500

@bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """Get user profile from Supabase."""
    try:
        supabase = get_supabase_client()
        res = supabase.table('users').select(
            'id, email, first_name, last_name, course, student_number, created_at'
        ).eq('email', current_user).limit(1).execute()
        if not res.data:
            return jsonify({'message': 'User not found'}), 404
        row = res.data[0]
        return jsonify({
            'id': row.get('id'),
            'email': row.get('email'),
            'name': f"{row.get('first_name','')} {row.get('last_name','')}".strip(),
            'course': row.get('course'),
            'student_number': row.get('student_number'),
            'created_at': row.get('created_at')
        }), 200
    except Exception as e:
        return jsonify({'message': 'Failed to fetch profile', 'error': str(e)}), 500


@bp.route('/profile-by-email', methods=['GET'])
def profile_by_email():
    """Development helper: fetch profile by email without JWT.

    Query param: ?email=<email>
    """
    try:
        email = (request.args.get('email') or '').strip().lower()
        if not email:
            return jsonify({'message': 'email is required'}), 400

        supabase = get_supabase_client()
        res = supabase.table('users').select(
            'id, email, first_name, last_name, course, student_number, created_at'
        ).eq('email', email).limit(1).execute()
        if not res.data:
            return jsonify({'message': 'User not found'}), 404
        row = res.data[0]
        return jsonify({
            'id': row.get('id'),
            'email': row.get('email'),
            'name': f"{row.get('first_name','')} {row.get('last_name','')}".strip(),
            'course': row.get('course'),
            'student_number': row.get('student_number'),
            'created_at': row.get('created_at')
        }), 200
    except Exception as e:
        return jsonify({'message': 'Failed to fetch profile', 'error': str(e)}), 500


