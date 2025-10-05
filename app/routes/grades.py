from flask import Blueprint, request, jsonify
from app.services.supabase_client import get_supabase_client

# Expose under /api/grades/*
grades_bp = Blueprint('grades', __name__, url_prefix='/api/grades')

@grades_bp.route('/get/<int:user_id>', methods=['GET'])
def get_user_grades(user_id):
    """Get user grades array"""
    try:
        supabase = get_supabase_client()
        res = supabase.table('users').select('grades').eq('id', user_id).limit(1).execute()
        if not res.data:
            return jsonify({'error': 'User not found'}), 404
        row = res.data[0]
        grades = row.get('grades') or []
        return jsonify({
            'success': True,
            'grades': grades
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@grades_bp.route('/update/<int:user_id>', methods=['POST'])
def update_user_grades(user_id):
    """Update user grades array"""
    try:
        data = request.get_json()
        grades = data.get('grades', [])
        # Basic validation
        for g in grades:
            for field in ['id','subject','units','grade','semester']:
                if field not in g:
                    return jsonify({'error': f'Missing required field: {field}'}), 400

        supabase = get_supabase_client()
        res = supabase.table('users').update({'grades': grades}).eq('id', user_id).execute()
        if not res.data:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({
            'success': True,
            'message': 'Grades updated successfully',
            'grades': (res.data[0].get('grades') if res.data else grades) or grades
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@grades_bp.route('/add/<int:user_id>', methods=['POST'])
def add_user_grade(user_id):
    """Add a single grade to user's grades array"""
    try:
        data = request.get_json()
        new_grade = data.get('grade')
        
        if not new_grade:
            return jsonify({'error': 'Grade data is required'}), 400
            
        # Validate required fields
        required_fields = ['id', 'subject', 'units', 'grade', 'semester']
        for field in required_fields:
            if field not in new_grade:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        supabase = get_supabase_client()
        # Fetch current grades
        res_get = supabase.table('users').select('grades').eq('id', user_id).limit(1).execute()
        if not res_get.data:
            return jsonify({'error': 'User not found'}), 404
        current_grades = res_get.data[0].get('grades') or []
        # Replace by id
        gid = new_grade['id']
        updated = [g for g in current_grades if (g or {}).get('id') != gid]
        updated.append(new_grade)
        # Save
        res_upd = supabase.table('users').update({'grades': updated}).eq('id', user_id).execute()
        return jsonify({
            'success': True,
            'message': 'Grade added successfully',
            'grades': (res_upd.data[0].get('grades') if res_upd.data else updated) or updated
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@grades_bp.route('/delete/<int:user_id>', methods=['POST'])
def delete_user_grade(user_id):
    """Delete a grade from user's grades array"""
    try:
        data = request.get_json()
        grade_id = data.get('grade_id')
        
        if not grade_id:
            return jsonify({'error': 'Grade ID is required'}), 400
        supabase = get_supabase_client()
        res_get = supabase.table('users').select('grades').eq('id', user_id).limit(1).execute()
        if not res_get.data:
            return jsonify({'error': 'User not found'}), 404
        current = res_get.data[0].get('grades') or []
        updated = [g for g in current if (g or {}).get('id') != grade_id]
        res_upd = supabase.table('users').update({'grades': updated}).eq('id', user_id).execute()
        return jsonify({
            'success': True,
            'message': 'Grade deleted successfully',
            'grades': (res_upd.data[0].get('grades') if res_upd.data else updated) or updated
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
