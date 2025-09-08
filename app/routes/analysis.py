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
from datetime import datetime, timezone

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
def validate_grades():
    """Validate and confirm extracted grades"""
    try:
        data = request.get_json()
        validated_grades = data.get('grades', [])
        
        if not validated_grades:
            return jsonify({'message': 'No grades provided for validation'}), 400
        
        # For now, just return success without storing (since we removed user context)
        # In production, you'd store this in a database with proper user association
        
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
def compute_archetype():
    """Compute learning archetype using K-Means clustering simulation"""
    try:
        data = request.get_json() or {}
        validated_grades = data.get('grades', [])
        email = data.get('email', '')
        
        if not validated_grades:
            return jsonify({'message': 'No validated grades found'}), 400
        
        if not email:
            return jsonify({'message': 'Email is required for database storage'}), 400
        
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
        
        # Generate archetype percentages (simulated)
        archetype_percentages = {
            'realistic': 25.0,
            'investigative': 30.0,
            'artistic': 15.0,
            'social': 10.0,
            'enterprising': 12.0,
            'conventional': 8.0
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
        
        # Save to database
        try:
            supabase = get_supabase_client()
            
            # Prepare update data
            update_data = {
                'archetype_analyzed_at': datetime.now(timezone.utc).isoformat(),
                'primary_archetype': archetype['type'],
                'archetype_realistic_percentage': archetype_percentages['realistic'],
                'archetype_investigative_percentage': archetype_percentages['investigative'],
                'archetype_artistic_percentage': archetype_percentages['artistic'],
                'archetype_social_percentage': archetype_percentages['social'],
                'archetype_enterprising_percentage': archetype_percentages['enterprising'],
                'archetype_conventional_percentage': archetype_percentages['conventional'],
                'tor_notes': json.dumps(results)  # Store all results including career_paths in tor_notes
            }
            
            # Update user record
            response = supabase.table('users').update(update_data).eq('email', email).execute()
            
            if response.data:
                return jsonify({
                    'message': 'Archetype computation completed and saved to database',
                    'results': results,
                    'saved_to_db': True
                }), 200
            else:
                return jsonify({
                    'message': 'Archetype computation completed but failed to save to database',
                    'results': results,
                    'saved_to_db': False
                }), 200
                
        except Exception as db_error:
            return jsonify({
                'message': 'Archetype computation completed but database save failed',
                'results': results,
                'saved_to_db': False,
                'db_error': str(db_error)
            }), 200
        
    except Exception as e:
        return jsonify({'message': 'Archetype computation failed', 'error': str(e)}), 500

@bp.route('/save-existing-results', methods=['POST'])
def save_existing_results():
    """Save existing analysis results to database"""
    try:
        data = request.get_json() or {}
        email = data.get('email', '')
        analysis_results = data.get('analysisResults', {})
        
        if not email:
            return jsonify({'message': 'Email is required for database storage'}), 400
        
        if not analysis_results:
            return jsonify({'message': 'No analysis results provided'}), 400
        
        # Extract archetype data from existing results
        archetype = analysis_results.get('archetype', {})
        archetype_percentages = analysis_results.get('learning_archetype', {}).get('archetype_percentages', {})
        career_paths = analysis_results.get('career_paths', [])
        
        # Save to database
        try:
            supabase = get_supabase_client()
            
            # Prepare update data
            update_data = {
                'archetype_analyzed_at': datetime.now(timezone.utc).isoformat(),
                'primary_archetype': archetype.get('type', 'Unknown'),
                'archetype_realistic_percentage': archetype_percentages.get('realistic', 0.0),
                'archetype_investigative_percentage': archetype_percentages.get('investigative', 0.0),
                'archetype_artistic_percentage': archetype_percentages.get('artistic', 0.0),
                'archetype_social_percentage': archetype_percentages.get('social', 0.0),
                'archetype_enterprising_percentage': archetype_percentages.get('enterprising', 0.0),
                'archetype_conventional_percentage': archetype_percentages.get('conventional', 0.0),
                'tor_notes': json.dumps(analysis_results)  # Store all results including career_paths in tor_notes
            }
            
            # Update user record
            response = supabase.table('users').update(update_data).eq('email', email).execute()
            
            if response.data:
                return jsonify({
                    'message': 'Analysis results saved to database successfully',
                    'saved_to_db': True
                }), 200
            else:
                return jsonify({
                    'message': 'Failed to save analysis results to database',
                    'saved_to_db': False
                }), 200
                
        except Exception as db_error:
            return jsonify({
                'message': 'Database save failed',
                'saved_to_db': False,
                'db_error': str(db_error)
            }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to save results', 'error': str(e)}), 500

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

@bp.route('/process-analysis', methods=['POST'])
@token_required
def process_analysis(current_user):
    """Process analysis using SoP objectives: Career Path Forecasting and Archetype Classification"""
    try:
        data = request.get_json()
        grades = data.get('grades', [])
        email = data.get('email', '')
        
        if not grades:
            return jsonify({'message': 'No grades provided for analysis'}), 400
        
        # Initialize AcademicAnalyzer
        analyzer = AcademicAnalyzer()
        
        # SoP 1 / Obj 1: Career Path Forecasting using Linear Regression
        career_forecast = analyzer.generate_career_recommendations(grades)
        
        # SoP 2 / Obj 2: Student Archetype Classification using K-Means
        archetype_analysis = analyzer.analyze_transcript(grades)
        
        # Store results in database
        supabase = get_supabase_client()
        
        # Update user profile with analysis results
        update_data = {
            'archetype_analyzed_at': datetime.now(timezone.utc).isoformat(),
            'primary_archetype': archetype_analysis.get('primary_archetype', 'unknown'),
            'archetype_realistic_percentage': archetype_analysis.get('learning_archetype', {}).get('archetype_percentages', {}).get('realistic', 0.0),
            'archetype_investigative_percentage': archetype_analysis.get('learning_archetype', {}).get('archetype_percentages', {}).get('investigative', 0.0),
            'archetype_artistic_percentage': archetype_analysis.get('learning_archetype', {}).get('archetype_percentages', {}).get('artistic', 0.0),
            'archetype_social_percentage': archetype_analysis.get('learning_archetype', {}).get('archetype_percentages', {}).get('social', 0.0),
            'archetype_enterprising_percentage': archetype_analysis.get('learning_archetype', {}).get('archetype_percentages', {}).get('enterprising', 0.0),
            'archetype_conventional_percentage': archetype_analysis.get('learning_archetype', {}).get('archetype_percentages', {}).get('conventional', 0.0),
            'tor_notes': json.dumps({
                'archetype_analysis': archetype_analysis,
                'career_forecast': career_forecast,
                'academic_metrics': {
                    'total_subjects': len(grades),
                    'total_units': sum(g.get('units', 0) for g in grades),
                    'overall_gpa': sum(g.get('grade', 0) for g in grades) / len(grades) if grades else 0,
                    'semester_breakdown': data.get('semester_breakdown', [])
                }
            })
        }
        
        # Update user record
        supabase.table('users').update(update_data).eq('email', email).execute()
        
        return jsonify({
            'message': 'Analysis processing completed successfully',
            'results': {
                'archetype_analysis': archetype_analysis,
                'career_forecast': career_forecast,
                'sop_objectives': {
                    'sop1_obj1': {
                        'name': 'Career Path Forecasting',
                        'theory': 'Predictive analytics in career guidance',
                        'method': 'Linear Regression applied to academic subject grades',
                        'tool': 'Scikit-learn regression models',
                        'status': 'completed'
                    },
                    'sop2_obj2': {
                        'name': 'Student Archetype Classification',
                        'theory': 'Educational psychology and career archetypes',
                        'method': 'K-Means Clustering based on subject-specific grades',
                        'tool': 'Scikit-learn clustering module',
                        'status': 'completed'
                    }
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Analysis processing failed', 'error': str(e)}), 500

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
            "primary_archetype, archetype_realistic_percentage, archetype_investigative_percentage, "
            "archetype_artistic_percentage, archetype_social_percentage, archetype_enterprising_percentage, "
            "archetype_conventional_percentage, tor_notes"
        ).eq("email", email).execute()
        
        if not user_result.data:
            return jsonify({"error": "User not found"}), 404
        
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
            "primary_archetype, archetype_realistic_percentage, archetype_investigative_percentage, "
            "archetype_artistic_percentage, archetype_social_percentage, archetype_enterprising_percentage, "
            "archetype_conventional_percentage"
        ).eq("email", email).execute()
        
        if not user_result.data:
            return jsonify({"error": "User not found"}), 404
        
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

@bp.route('/seed-jobs', methods=['POST'])
def seed_jobs():
    """Seed the jobs table with realistic sample job data"""
    try:
        from app.services.job_scraper import JobScraper
        supabase = get_supabase_client()
        
        # Create job scraper instance to use its URL generation methods
        scraper = JobScraper()
        
        # Sample job data with improved URLs using the scraper's URL generation
        sample_jobs = [
            {
                "title": "Software Developer",
                "company": "Accenture Philippines",
                "location": "Makati City, Philippines",
                "employment_type": "Full-time",
                "remote": False,
                "salary_min": 45000,
                "salary_max": 80000,
                "currency": "PHP",
                "url": scraper._generate_realistic_job_url("Software Developer", "software developer", 0),
                "source": "LinkedIn Jobs",
                "posted_at": "2025-08-20T10:00:00Z",
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "tags": ["software", "development", "entry-level"],
                "description": "Join our dynamic team as a Software Developer. Work on cutting-edge projects and develop your skills in a collaborative environment."
            },
            {
                "title": "Data Analyst",
                "company": "Concentrix",
                "location": "BGC, Taguig, Philippines",
                "employment_type": "Full-time",
                "remote": True,
                "salary_min": 40000,
                "salary_max": 70000,
                "currency": "PHP",
                "url": scraper._generate_realistic_job_url("Data Analyst", "data analyst", 1),
                "source": "LinkedIn Jobs",
                "posted_at": "2025-08-19T14:30:00Z",
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "tags": ["data", "analytics", "entry-level"],
                "description": "We're looking for a Data Analyst to help us make sense of complex data and drive business decisions."
            },
            {
                "title": "UI/UX Designer",
                "company": "IBM Philippines",
                "location": "Quezon City, Philippines",
                "employment_type": "Full-time",
                "remote": False,
                "salary_min": 50000,
                "salary_max": 90000,
                "currency": "PHP",
                "url": scraper._generate_realistic_job_url("UI/UX Designer", "ui ux designer", 2),
                "source": "LinkedIn Jobs",
                "posted_at": "2025-08-18T09:15:00Z",
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "tags": ["design", "ui", "ux", "creative"],
                "description": "Create beautiful and intuitive user experiences. Join our design team and help shape the future of our products."
            },
            {
                "title": "System Analyst",
                "company": "Cognizant",
                "location": "Manila, Philippines",
                "employment_type": "Full-time",
                "remote": False,
                "salary_min": 55000,
                "salary_max": 85000,
                "currency": "PHP",
                "url": scraper._generate_realistic_job_url("System Analyst", "system analyst", 3),
                "source": "LinkedIn Jobs",
                "posted_at": "2025-08-17T16:45:00Z",
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "tags": ["system", "analysis", "technical"],
                "description": "Analyze business requirements and design system solutions. Work with stakeholders to deliver high-quality systems."
            },
            {
                "title": "Junior Project Manager",
                "company": "Deloitte Philippines",
                "location": "Makati City, Philippines",
                "employment_type": "Full-time",
                "remote": False,
                "salary_min": 60000,
                "salary_max": 95000,
                "currency": "PHP",
                "url": scraper._generate_realistic_job_url("Junior Project Manager", "junior project manager", 4),
                "source": "LinkedIn Jobs",
                "posted_at": "2025-08-16T11:20:00Z",
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "tags": ["project", "management", "leadership"],
                "description": "Start your project management career with us. Learn from experienced professionals and manage exciting projects."
            },
            {
                "title": "Business Analyst",
                "company": "PwC Philippines",
                "location": "BGC, Taguig, Philippines",
                "employment_type": "Full-time",
                "remote": True,
                "salary_min": 50000,
                "salary_max": 80000,
                "currency": "PHP",
                "url": scraper._generate_realistic_job_url("Business Analyst", "business analyst", 5),
                "source": "LinkedIn Jobs",
                "posted_at": "2025-08-15T13:10:00Z",
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "tags": ["business", "analysis", "consulting"],
                "description": "Help businesses optimize their processes and achieve their goals. Join our consulting team."
            },
            {
                "title": "Frontend Developer",
                "company": "Globe Telecom",
                "location": "Taguig, Philippines",
                "employment_type": "Full-time",
                "remote": False,
                "salary_min": 45000,
                "salary_max": 75000,
                "currency": "PHP",
                "url": scraper._generate_realistic_job_url("Frontend Developer", "frontend developer", 6),
                "source": "LinkedIn Jobs",
                "posted_at": "2025-08-14T08:30:00Z",
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "tags": ["frontend", "web", "development"],
                "description": "Build amazing user interfaces for our digital products. Work with modern technologies and frameworks."
            },
            {
                "title": "Quality Assurance Engineer",
                "company": "PLDT",
                "location": "Makati City, Philippines",
                "employment_type": "Full-time",
                "remote": False,
                "salary_min": 40000,
                "salary_max": 70000,
                "currency": "PHP",
                "url": scraper._generate_realistic_job_url("Quality Assurance Engineer", "quality assurance engineer", 7),
                "source": "LinkedIn Jobs",
                "posted_at": "2025-08-13T15:45:00Z",
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "tags": ["qa", "testing", "quality"],
                "description": "Ensure the quality of our software products. Work with development teams to deliver bug-free applications."
            }
        ]
        
        # Insert jobs into the database
        for job in sample_jobs:
            try:
                supabase.table('jobs').insert(job).execute()
            except Exception as e:
                print(f"Error inserting job {job['title']}: {e}")
                continue
        
        return jsonify({
            'message': f'Successfully seeded {len(sample_jobs)} jobs',
            'jobs_added': len(sample_jobs)
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to seed jobs', 'error': str(e)}), 500

@bp.route('/dev-compute-archetype', methods=['POST'])
def dev_compute_archetype():
    """Development endpoint: Compute archetype for any user by email"""
    try:
        data = request.get_json() or {}
        email = data.get('email', '')
        
        if not email:
            return jsonify({'message': 'Email is required'}), 400
        
        # Simulate processing delay
        time.sleep(2)
        
        # Simulate archetype computation (in production, use actual ML algorithms)
        archetype = {
            'type': 'Analytical Thinker',
            'description': 'Strong in logical reasoning and systematic problem-solving',
            'strengths': ['Analytical Skills', 'Problem Solving', 'Technical Excellence'],
            'score': 8.5,
            'confidence': 0.92
        }
        
        # Generate archetype percentages (simulated)
        archetype_percentages = {
            'realistic': 25.0,
            'investigative': 30.0,
            'artistic': 15.0,
            'social': 10.0,
            'enterprising': 12.0,
            'conventional': 8.0
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
                'total_subjects': 15,
                'average_grade': 1.45,
                'major_subjects_count': 12,
                'major_average': 1.42,
                'total_units': 45
            }
        }
        
        # Save to database
        try:
            supabase = get_supabase_client()
            
            # Prepare update data
            update_data = {
                'archetype_analyzed_at': datetime.now(timezone.utc).isoformat(),
                'primary_archetype': archetype['type'],
                'archetype_realistic_percentage': archetype_percentages['realistic'],
                'archetype_investigative_percentage': archetype_percentages['investigative'],
                'archetype_artistic_percentage': archetype_percentages['artistic'],
                'archetype_social_percentage': archetype_percentages['social'],
                'archetype_enterprising_percentage': archetype_percentages['enterprising'],
                'archetype_conventional_percentage': archetype_percentages['conventional'],
                'tor_notes': json.dumps(results)  # Store all results including career_paths in tor_notes
            }
            
            # Update user record
            response = supabase.table('users').update(update_data).eq('email', email).execute()
            
            if response.data:
                return jsonify({
                    'message': 'Archetype computation completed and saved to database',
                    'results': results,
                    'saved_to_db': True,
                    'email': email
                }), 200
            else:
                return jsonify({
                    'message': 'Archetype computation completed but failed to save to database',
                    'results': results,
                    'saved_to_db': False,
                    'email': email
                }), 200
                
        except Exception as db_error:
            return jsonify({
                'message': 'Archetype computation completed but database save failed',
                'results': results,
                'saved_to_db': False,
                'db_error': str(db_error),
                'email': email
            }), 200
        
    except Exception as e:
        return jsonify({'message': 'Archetype computation failed', 'error': str(e)}), 500

def get_archetype_keywords(archetype):
    """Get relevant keywords for each RIASEC archetype"""
    keywords = {
        'realistic': ['hardware', 'network', 'systems', 'technical', 'infrastructure', 'support', 'engineering'],
        'investigative': ['data', 'analyst', 'research', 'scientist', 'machine learning', 'ai', 'statistics'],
        'artistic': ['design', 'creative', 'ui', 'ux', 'frontend', 'visual', 'multimedia', 'graphic'],
        'social': ['support', 'training', 'communication', 'help desk', 'documentation', 'teaching'],
        'enterprising': ['manager', 'lead', 'director', 'project', 'product', 'business', 'strategic'],
        'conventional': ['database', 'audit', 'qa', 'compliance', 'documentation', 'quality assurance']
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
    """Get skill recommendations based on RIASEC archetype percentages"""
    # Default skills for each RIASEC archetype
    archetype_skills = {
        'realistic': [
            {'name': 'Network Administration', 'relevance': 85.0, 'demand': 'High'},
            {'name': 'Systems Engineering', 'relevance': 80.0, 'demand': 'High'},
            {'name': 'Hardware Maintenance', 'relevance': 75.0, 'demand': 'Medium'},
            {'name': 'Technical Support', 'relevance': 70.0, 'demand': 'High'}
        ],
        'investigative': [
            {'name': 'Data Analysis', 'relevance': 90.0, 'demand': 'High'},
            {'name': 'Python', 'relevance': 85.0, 'demand': 'High'},
            {'name': 'Machine Learning', 'relevance': 80.0, 'demand': 'High'},
            {'name': 'Statistical Analysis', 'relevance': 75.0, 'demand': 'Medium'}
        ],
        'artistic': [
            {'name': 'UI/UX Design', 'relevance': 90.0, 'demand': 'High'},
            {'name': 'JavaScript', 'relevance': 85.0, 'demand': 'High'},
            {'name': 'Graphic Design', 'relevance': 80.0, 'demand': 'Medium'},
            {'name': 'Creative Development', 'relevance': 75.0, 'demand': 'Medium'}
        ],
        'social': [
            {'name': 'Technical Training', 'relevance': 85.0, 'demand': 'High'},
            {'name': 'Communication', 'relevance': 80.0, 'demand': 'High'},
            {'name': 'Documentation', 'relevance': 75.0, 'demand': 'Medium'},
            {'name': 'Customer Support', 'relevance': 70.0, 'demand': 'High'}
        ],
        'enterprising': [
            {'name': 'Project Management', 'relevance': 90.0, 'demand': 'High'},
            {'name': 'Leadership', 'relevance': 85.0, 'demand': 'High'},
            {'name': 'Strategic Planning', 'relevance': 80.0, 'demand': 'High'},
            {'name': 'Business Analysis', 'relevance': 75.0, 'demand': 'Medium'}
        ],
        'conventional': [
            {'name': 'Database Management', 'relevance': 85.0, 'demand': 'High'},
            {'name': 'Quality Assurance', 'relevance': 80.0, 'demand': 'High'},
            {'name': 'Compliance', 'relevance': 75.0, 'demand': 'Medium'},
            {'name': 'Process Analysis', 'relevance': 70.0, 'demand': 'Medium'}
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
