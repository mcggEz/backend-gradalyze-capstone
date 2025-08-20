"""
Analysis routes for academic processing and archetype computation
"""

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import time
from app.routes.auth import token_required
from app.services.supabase_client import get_supabase_client
from app.services.academic_analyzer import AcademicAnalyzer
import json
import re
from collections import Counter

bp = Blueprint('analysis', __name__, url_prefix='/api/analysis')

# Temporary storage for demo (in production, use proper database)
user_analysis_data = {}

@bp.route('/upload', methods=['POST'])
@token_required
def upload_documents(current_user):
    """Upload transcript and certificates"""
    try:
        if 'transcript' not in request.files:
            return jsonify({'message': 'Transcript file is required'}), 400
        
        transcript = request.files['transcript']
        certificates = request.files.getlist('certificates')
        
        if transcript.filename == '':
            return jsonify({'message': 'No transcript file selected'}), 400
        
        # Simulate file processing
        uploaded_files = {
            'transcript': {
                'filename': secure_filename(transcript.filename),
                'size': len(transcript.read()),
                'uploaded_at': time.time()
            },
            'certificates': []
        }
        
        for cert in certificates:
            if cert.filename:
                uploaded_files['certificates'].append({
                    'filename': secure_filename(cert.filename),
                    'size': len(cert.read()),
                    'uploaded_at': time.time()
                })
        
        # Store user data
        if current_user not in user_analysis_data:
            user_analysis_data[current_user] = {}
        
        user_analysis_data[current_user]['uploaded_files'] = uploaded_files
        user_analysis_data[current_user]['status'] = 'uploaded'
        
        return jsonify({
            'message': 'Files uploaded successfully',
            'files': uploaded_files
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Upload failed', 'error': str(e)}), 500

@bp.route('/extract-grades', methods=['POST'])
@token_required
def extract_grades(current_user):
    """Simulate grade extraction from transcript"""
    try:
        # Simulate OCR processing delay
        time.sleep(2)
        
        # Sample extracted grades (in production, this would use OCR)
        extracted_grades = [
            {
                'subject': 'Data Structures & Algorithms',
                'grade': 1.25,
                'units': 3,
                'semester': '1st Sem 2023',
                'category': 'Major'
            },
            {
                'subject': 'Database Systems',
                'grade': 1.50,
                'units': 3,
                'semester': '1st Sem 2023',
                'category': 'Major'
            },
            {
                'subject': 'Software Engineering',
                'grade': 1.75,
                'units': 3,
                'semester': '2nd Sem 2023',
                'category': 'Major'
            },
            {
                'subject': 'Computer Networks',
                'grade': 1.25,
                'units': 3,
                'semester': '2nd Sem 2023',
                'category': 'Major'
            },
            {
                'subject': 'Mathematics for CS',
                'grade': 2.00,
                'units': 3,
                'semester': '1st Sem 2022',
                'category': 'Minor'
            }
        ]
        
        # Store extracted grades
        user_analysis_data[current_user]['extracted_grades'] = extracted_grades
        user_analysis_data[current_user]['status'] = 'extracted'
        
        return jsonify({
            'message': 'Grades extracted successfully',
            'grades': extracted_grades
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Grade extraction failed', 'error': str(e)}), 500

@bp.route('/validate-grades', methods=['POST'])
@token_required
def validate_grades(current_user):
    """Validate and confirm extracted grades"""
    try:
        data = request.get_json()
        validated_grades = data.get('grades', [])
        
        if not validated_grades:
            return jsonify({'message': 'No grades provided for validation'}), 400
        
        # Store validated grades
        user_analysis_data[current_user]['validated_grades'] = validated_grades
        user_analysis_data[current_user]['status'] = 'validated'
        
        return jsonify({
            'message': 'Grades validated successfully',
            'grades': validated_grades
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Grade validation failed', 'error': str(e)}), 500

@bp.route('/admin-review', methods=['POST'])
@token_required
def admin_review(current_user):
    """Simulate admin review process"""
    try:
        # Simulate admin review delay
        time.sleep(2)
        
        user_analysis_data[current_user]['status'] = 'admin_approved'
        user_analysis_data[current_user]['admin_review'] = {
            'approved_by': 'admin@gradalyze.com',
            'approved_at': time.time(),
            'notes': 'Academic records verified and approved'
        }
        
        return jsonify({
            'message': 'Admin review completed',
            'status': 'approved'
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Admin review failed', 'error': str(e)}), 500

@bp.route('/compute-archetype', methods=['POST'])
@token_required
def compute_archetype(current_user):
    """Compute learning archetype using K-Means clustering simulation"""
    try:
        if current_user not in user_analysis_data:
            return jsonify({'message': 'No analysis data found'}), 404
        
        user_data = user_analysis_data[current_user]
        validated_grades = user_data.get('validated_grades', [])
        
        if not validated_grades:
            return jsonify({'message': 'No validated grades found'}), 400
        
        # Simulate processing delay
        time.sleep(3)
        
        # Calculate basic metrics
        total_grades = len(validated_grades)
        average_grade = sum(g['grade'] for g in validated_grades) / total_grades
        major_subjects = [g for g in validated_grades if g['category'] == 'Major']
        major_average = sum(g['grade'] for g in major_subjects) / len(major_subjects) if major_subjects else 0
        
        # Simulate archetype computation (in production, use actual ML algorithms)
        archetype = {
            'type': 'Analytical Thinker',
            'description': 'Strong in logical reasoning and systematic problem-solving',
            'strengths': ['Analytical Skills', 'Problem Solving', 'Technical Excellence'],
            'score': 8.5,
            'confidence': 0.92
        }
        
        # Career path predictions
        career_paths = [
            {
                'title': 'Software Engineer',
                'match': 92,
                'demand': 'High',
                'salary': '₱45,000 - ₱80,000',
                'description': 'Design and develop software applications'
            },
            {
                'title': 'Data Scientist',
                'match': 88,
                'demand': 'High',
                'salary': '₱50,000 - ₱90,000',
                'description': 'Analyze complex data to derive insights'
            },
            {
                'title': 'System Analyst',
                'match': 85,
                'demand': 'Medium',
                'salary': '₱40,000 - ₱70,000',
                'description': 'Design and improve computer systems'
            }
        ]
        
        # Company recommendations
        companies = [
            {
                'name': 'Accenture Philippines',
                'position': 'Junior Software Developer',
                'posted': '2 days ago',
                'type': 'Full-time',
                'location': 'Makati City'
            },
            {
                'name': 'Concentrix',
                'position': 'Data Analyst',
                'posted': '1 week ago',
                'type': 'Full-time',
                'location': 'BGC, Taguig'
            },
            {
                'name': 'IBM Philippines',
                'position': 'System Analyst Trainee',
                'posted': '3 days ago',
                'type': 'Full-time',
                'location': 'Quezon City'
            }
        ]
        
        # Store results
        results = {
            'archetype': archetype,
            'career_paths': career_paths,
            'companies': companies,
            'academic_metrics': {
                'total_subjects': total_grades,
                'average_grade': round(average_grade, 2),
                'major_subjects_count': len(major_subjects),
                'major_average': round(major_average, 2),
                'total_units': sum(g['units'] for g in validated_grades)
            }
        }
        
        user_analysis_data[current_user]['results'] = results
        user_analysis_data[current_user]['status'] = 'completed'
        
        return jsonify({
            'message': 'Archetype computation completed',
            'results': results
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Archetype computation failed', 'error': str(e)}), 500

@bp.route('/results', methods=['GET'])
@token_required
def get_results(current_user):
    """Get analysis results"""
    try:
        if current_user not in user_analysis_data:
            return jsonify({'message': 'No analysis data found'}), 404
        
        user_data = user_analysis_data[current_user]
        
        return jsonify({
            'status': user_data.get('status', 'not_started'),
            'results': user_data.get('results', {})
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to retrieve results', 'error': str(e)}), 500

@bp.route("/recommended-skills", methods=["GET"])
def get_recommended_skills():
    """Get personalized skill recommendations based on user's archetype and job market"""
    try:
        email = request.args.get('email')
        if not email:
            return jsonify({"error": "Email parameter required"}), 400
        
        supabase = get_supabase_client()
        
        # Get user's archetype data
        user_result = supabase.table("users").select(
            "primary_archetype, archetype_innocent_percentage, archetype_everyman_percentage, "
            "archetype_hero_percentage, archetype_caregiver_percentage, archetype_explorer_percentage, "
            "archetype_rebel_percentage, archetype_lover_percentage, archetype_creator_percentage, "
            "archetype_jester_percentage, archetype_sage_percentage, archetype_magician_percentage, "
            "archetype_ruler_percentage, tor_notes"
        ).eq("email", email).execute()
        
        if not user_result.data:
            return jsonify({"error": "User not found"}), 404
        
        user = user_result.data[0]
        
        # Get archetype percentages
        archetype_percentages = {
            'the_innocent': user.get('archetype_innocent_percentage', 0.0),
            'the_everyman': user.get('archetype_everyman_percentage', 0.0),
            'the_hero': user.get('archetype_hero_percentage', 0.0),
            'the_caregiver': user.get('archetype_caregiver_percentage', 0.0),
            'the_explorer': user.get('archetype_explorer_percentage', 0.0),
            'the_rebel': user.get('archetype_rebel_percentage', 0.0),
            'the_lover': user.get('archetype_lover_percentage', 0.0),
            'the_creator': user.get('archetype_creator_percentage', 0.0),
            'the_jester': user.get('archetype_jester_percentage', 0.0),
            'the_sage': user.get('archetype_sage_percentage', 0.0),
            'the_magician': user.get('archetype_magician_percentage', 0.0),
            'the_ruler': user.get('archetype_ruler_percentage', 0.0)
        }
        
        # Get relevant jobs based on archetype
        jobs_result = supabase.table("jobs").select("*").execute()
        relevant_jobs = []
        
        # Filter jobs based on user's top archetypes
        top_archetypes = sorted(archetype_percentages.items(), key=lambda x: x[1], reverse=True)[:3]
        
        for archetype, percentage in top_archetypes:
            if percentage > 10:  # Only consider archetypes with >10% match
                # Filter jobs that match the archetype's typical roles
                archetype_keywords = get_archetype_keywords(archetype)
                for job in jobs_result.data:
                    if any(keyword.lower() in job.get('title', '').lower() or 
                           keyword.lower() in job.get('description', '').lower() 
                           for keyword in archetype_keywords):
                        relevant_jobs.append(job)
        
        # Extract skills from job descriptions
        all_skills = []
        for job in relevant_jobs:
            description = job.get('description', '')
            skills = extract_skills_from_text(description)
            all_skills.extend(skills)
        
        # Count and rank skills
        skill_counts = Counter(all_skills)
        
        # Get top skills with relevance scores
        top_skills = []
        for skill, count in skill_counts.most_common(8):
            relevance_score = min(100, (count / len(relevant_jobs)) * 100 + 10)
            top_skills.append({
                "name": skill,
                "relevance": round(relevance_score, 1),
                "demand": "High" if relevance_score > 70 else "Medium" if relevance_score > 40 else "Low"
            })
        
        # If no relevant skills found, provide archetype-based recommendations
        if not top_skills:
            top_skills = get_archetype_based_skills(archetype_percentages)
        
        return jsonify({
            "skills": top_skills[:4],  # Return top 4 skills
            "user_archetype": user.get('primary_archetype'),
            "total_relevant_jobs": len(relevant_jobs)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route("/companies-for-user", methods=["GET"])
def get_companies_for_user():
    """Get companies hiring for roles relevant to user's archetype"""
    try:
        email = request.args.get('email')
        if not email:
            return jsonify({"error": "Email parameter required"}), 400
        
        supabase = get_supabase_client()
        
        # Get user's archetype data
        user_result = supabase.table("users").select(
            "primary_archetype, archetype_innocent_percentage, archetype_everyman_percentage, "
            "archetype_hero_percentage, archetype_caregiver_percentage, archetype_explorer_percentage, "
            "archetype_rebel_percentage, archetype_lover_percentage, archetype_creator_percentage, "
            "archetype_jester_percentage, archetype_sage_percentage, archetype_magician_percentage, "
            "archetype_ruler_percentage"
        ).eq("email", email).execute()
        
        if not user_result.data:
            return jsonify({"error": "User not found"}), 404
        
        user = user_result.data[0]
        
        # Get archetype percentages
        archetype_percentages = {
            'the_innocent': user.get('archetype_innocent_percentage', 0.0),
            'the_everyman': user.get('archetype_everyman_percentage', 0.0),
            'the_hero': user.get('archetype_hero_percentage', 0.0),
            'the_caregiver': user.get('archetype_caregiver_percentage', 0.0),
            'the_explorer': user.get('archetype_explorer_percentage', 0.0),
            'the_rebel': user.get('archetype_rebel_percentage', 0.0),
            'the_lover': user.get('archetype_lover_percentage', 0.0),
            'the_creator': user.get('archetype_creator_percentage', 0.0),
            'the_jester': user.get('archetype_jester_percentage', 0.0),
            'the_sage': user.get('archetype_sage_percentage', 0.0),
            'the_magician': user.get('archetype_magician_percentage', 0.0),
            'the_ruler': user.get('archetype_ruler_percentage', 0.0)
        }
        
        # Get all jobs
        jobs_result = supabase.table("jobs").select("*").execute()
        
        # Filter relevant jobs based on archetype
        relevant_jobs = []
        top_archetypes = sorted(archetype_percentages.items(), key=lambda x: x[1], reverse=True)[:3]
        
        for archetype, percentage in top_archetypes:
            if percentage > 10:
                archetype_keywords = get_archetype_keywords(archetype)
                for job in jobs_result.data:
                    if any(keyword.lower() in job.get('title', '').lower() or 
                           keyword.lower() in job.get('description', '').lower() 
                           for keyword in archetype_keywords):
                        relevant_jobs.append(job)
        
        # Group jobs by company
        company_jobs = {}
        for job in relevant_jobs:
            company = job.get('company', 'Unknown Company')
            if company not in company_jobs:
                company_jobs[company] = []
            company_jobs[company].append(job)
        
        # Create company list with job counts
        companies = []
        for company, jobs in company_jobs.items():
            companies.append({
                "name": company,
                "job_count": len(jobs),
                "latest_job": max(jobs, key=lambda x: x.get('posted_at', '')) if jobs else None
            })
        
        # Sort by job count and take top 3
        companies.sort(key=lambda x: x['job_count'], reverse=True)
        top_companies = companies[:3]
        
        return jsonify({
            "companies": top_companies,
            "user_archetype": user.get('primary_archetype'),
            "total_relevant_jobs": len(relevant_jobs)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_archetype_keywords(archetype):
    """Get relevant keywords for each archetype"""
    keywords = {
        'the_sage': ['data', 'analyst', 'research', 'scientist', 'statistics', 'business intelligence', 'machine learning'],
        'the_creator': ['developer', 'designer', 'creative', 'software', 'ui', 'ux', 'frontend', 'backend', 'full stack'],
        'the_ruler': ['manager', 'lead', 'director', 'project', 'product', 'operations', 'executive', 'team lead'],
        'the_hero': ['entrepreneur', 'founder', 'startup', 'business development', 'sales', 'consultant', 'strategic'],
        'the_explorer': ['consultant', 'researcher', 'analyst', 'strategist', 'business consultant', 'policy'],
        'the_rebel': ['innovation', 'creative', 'disruptive', 'startup', 'change management', 'transformation'],
        'the_lover': ['marketing', 'sales', 'customer', 'public relations', 'brand', 'relationship', 'client'],
        'the_magician': ['product', 'change', 'transformation', 'strategic', 'innovation', 'visionary'],
        'the_caregiver': ['human resources', 'teacher', 'trainer', 'mentor', 'coach', 'hr', 'learning'],
        'the_innocent': ['customer service', 'administrative', 'receptionist', 'office', 'support', 'help desk'],
        'the_everyman': ['administrative', 'support', 'coordinator', 'assistant', 'team member', 'operations'],
        'the_jester': ['content', 'social media', 'entertainment', 'event', 'creative', 'digital', 'media']
    }
    return keywords.get(archetype, [])

def extract_skills_from_text(text):
    """Extract skills from job description text"""
    # Common tech skills
    tech_skills = [
        'JavaScript', 'Python', 'Java', 'React', 'Angular', 'Vue', 'Node.js', 'PHP', 'C#', 'C++',
        'SQL', 'MongoDB', 'PostgreSQL', 'MySQL', 'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes',
        'Git', 'Jenkins', 'Jira', 'Agile', 'Scrum', 'DevOps', 'CI/CD', 'REST API', 'GraphQL',
        'Machine Learning', 'Data Science', 'AI', 'TensorFlow', 'PyTorch', 'Pandas', 'NumPy',
        'HTML', 'CSS', 'SASS', 'TypeScript', 'Redux', 'Express.js', 'Django', 'Flask', 'Spring',
        'Salesforce', 'SAP', 'Oracle', 'Tableau', 'Power BI', 'Excel', 'PowerPoint', 'Word'
    ]
    
    found_skills = []
    text_lower = text.lower()
    
    for skill in tech_skills:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    return found_skills

def get_archetype_based_skills(archetype_percentages):
    """Get skill recommendations based on archetype percentages"""
    # Default skills for each archetype
    archetype_skills = {
        'the_sage': [
            {'name': 'Data Analysis', 'relevance': 85.0, 'demand': 'High'},
            {'name': 'Python', 'relevance': 78.0, 'demand': 'High'},
            {'name': 'SQL', 'relevance': 72.0, 'demand': 'High'},
            {'name': 'Machine Learning', 'relevance': 68.0, 'demand': 'Medium'}
        ],
        'the_creator': [
            {'name': 'JavaScript', 'relevance': 88.0, 'demand': 'High'},
            {'name': 'React.js', 'relevance': 82.0, 'demand': 'High'},
            {'name': 'UI/UX Design', 'relevance': 75.0, 'demand': 'High'},
            {'name': 'Node.js', 'relevance': 70.0, 'demand': 'Medium'}
        ],
        'the_ruler': [
            {'name': 'Project Management', 'relevance': 90.0, 'demand': 'High'},
            {'name': 'Agile/Scrum', 'relevance': 85.0, 'demand': 'High'},
            {'name': 'Leadership', 'relevance': 80.0, 'demand': 'High'},
            {'name': 'Strategic Planning', 'relevance': 75.0, 'demand': 'Medium'}
        ]
    }
    
    # Get top archetype
    top_archetype = max(archetype_percentages.items(), key=lambda x: x[1])[0]
    
    return archetype_skills.get(top_archetype, [
        {'name': 'Problem Solving', 'relevance': 75.0, 'demand': 'High'},
        {'name': 'Communication', 'relevance': 70.0, 'demand': 'High'},
        {'name': 'Teamwork', 'relevance': 65.0, 'demand': 'Medium'},
        {'name': 'Adaptability', 'relevance': 60.0, 'demand': 'Medium'}
    ])
