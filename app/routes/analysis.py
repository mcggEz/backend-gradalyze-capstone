"""
Analysis routes for academic processing and archetype computation
"""

from flask import Blueprint, request, jsonify
from app.routes.auth import token_required
from app.services.supabase_client import get_supabase_client
from app.services.features import build_feature_vector_from_grades
from app.services.ml_models import predict_career_scores, predict_archetype_kmeans
import json
import re
from collections import Counter
from datetime import datetime, timezone

bp = Blueprint('analysis', __name__, url_prefix='/api/analysis')

## Removed demo endpoints: upload/extract/validate/admin-review (kept production analysis routes only)


@bp.route('/process', methods=['POST'])
def process_analysis_v1():
    """Compute Obj1 (career forecast) + Obj2 (archetype) from provided grades and persist to users.

    Body JSON: { email: str, grades: [{ subject, units, grade, semester } ...] }
    """
    try:
        data = request.get_json(silent=True) or {}
        email = (data.get('email') or '').strip().lower()
        grades = data.get('grades') or []
        if not email or not isinstance(grades, list):
            return jsonify({'message': 'email and grades are required'}), 400

        supabase = get_supabase_client()
        res_user = supabase.table('users').select('id, tor_notes').eq('email', email).limit(1).execute()
        if not res_user.data:
            return jsonify({'message': 'User not found'}), 404
        user = res_user.data[0]

        # Build features and run models
        vec = build_feature_vector_from_grades(grades)
        career_scores = predict_career_scores(vec)
        cluster_id, km_perc = predict_archetype_kmeans(vec)

        import json as _json
        try:
            notes = _json.loads(user.get('tor_notes') or '{}')
        except Exception:
            notes = {}
        ar = notes.get('analysis_results') or {}
        ar['career_forecast'] = career_scores
        notes['analysis_results'] = ar
        notes['grades'] = grades

        from datetime import datetime, timezone
        update = {
            'tor_notes': _json.dumps(notes),
                'archetype_analyzed_at': datetime.now(timezone.utc).isoformat(),
            'primary_archetype': max(km_perc, key=km_perc.get) if km_perc else None,
            'archetype_realistic_percentage': km_perc.get('realistic'),
            'archetype_investigative_percentage': km_perc.get('investigative'),
            'archetype_artistic_percentage': km_perc.get('artistic'),
            'archetype_social_percentage': km_perc.get('social'),
            'archetype_enterprising_percentage': km_perc.get('enterprising'),
            'archetype_conventional_percentage': km_perc.get('conventional'),
        }
        supabase.table('users').update(update).eq('id', user['id']).execute()

        return jsonify({
            'message': 'Analysis processed',
            'career_forecast': career_scores,
            'archetype': {
                'primary': update.get('primary_archetype'),
                'percentages': km_perc,
                'cluster_id': cluster_id
            }
        }), 200
    except Exception as e:
        return jsonify({'message': 'Process analysis failed', 'error': str(e)}), 500

## Removed legacy placeholder endpoint: /compute-archetype

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

## Removed legacy in-memory /results endpoint

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

## Removed dev-only endpoint: /dev-compute-archetype

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


@bp.route('/process-v2', methods=['POST'])
def process_analysis_v2():
    """Compute Obj1 (career forecast) + Obj2 (archetype) from provided grades and persist to users.

    Body JSON: { email: str, grades: [{ subject, units, grade, semester } ...] }
    """
    try:
        data = request.get_json(silent=True) or {}
        email = (data.get('email') or '').strip().lower()
        grades = data.get('grades') or []
        if not email or not isinstance(grades, list):
            return jsonify({'message': 'email and grades are required'}), 400

        supabase = get_supabase_client()
        res_user = supabase.table('users').select('id, tor_notes').eq('email', email).limit(1).execute()
        if not res_user.data:
            return jsonify({'message': 'User not found'}), 404
        user = res_user.data[0]

        # Build features and run models
        from app.services.features import build_feature_vector_from_grades
        from app.services.ml_models import predict_career_scores, predict_archetype_kmeans
        vec = build_feature_vector_from_grades(grades)
        career_scores = predict_career_scores(vec)
        cluster_id, km_perc = predict_archetype_kmeans(vec)

        import json as _json
        try:
            notes = _json.loads(user.get('tor_notes') or '{}')
        except Exception:
            notes = {}
        ar = notes.get('analysis_results') or {}
        ar['career_forecast'] = career_scores
        notes['analysis_results'] = ar
        notes['grades'] = grades

        from datetime import datetime, timezone
        update = {
            'tor_notes': _json.dumps(notes),
            'archetype_analyzed_at': datetime.now(timezone.utc).isoformat(),
            'primary_archetype': max(km_perc, key=km_perc.get) if km_perc else None,
            'archetype_realistic_percentage': km_perc.get('realistic'),
            'archetype_investigative_percentage': km_perc.get('investigative'),
            'archetype_artistic_percentage': km_perc.get('artistic'),
            'archetype_social_percentage': km_perc.get('social'),
            'archetype_enterprising_percentage': km_perc.get('enterprising'),
            'archetype_conventional_percentage': km_perc.get('conventional'),
        }
        supabase.table('users').update(update).eq('id', user['id']).execute()

        return jsonify({
            'message': 'Analysis processed',
            'career_forecast': career_scores,
            'archetype': {
                'primary': update.get('primary_archetype'),
                'percentages': km_perc,
                'cluster_id': cluster_id
            }
        }), 200
    except Exception as e:
        return jsonify({'message': 'Process analysis failed', 'error': str(e)}), 500
