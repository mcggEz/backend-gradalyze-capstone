from typing import Dict, List, Any, Optional
import json
from datetime import datetime
from app.services.supabase_client import get_supabase_client
from app.services.academic_analyzer import AcademicAnalyzer


class JobMatcher:
    """Intelligent job matching based on academic profiles and career goals"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.academic_analyzer = AcademicAnalyzer()
        
        # Enhanced skill-to-job mapping with archetype alignment
        self.skill_job_mapping = {
            # The Sage archetype jobs
            'Data Scientist': {
                'required_skills': ['Data Analysis', 'Statistical Analysis', 'Machine Learning'],
                'preferred_skills': ['Python', 'Mathematical Modeling', 'Database Management'],
                'min_gpa': 2.0,
                'experience_level': 'entry',
                'archetype': 'the_sage'
            },
            'Research Analyst': {
                'required_skills': ['Research Methods', 'Analytical Thinking', 'Data Analysis'],
                'preferred_skills': ['Statistical Analysis', 'Critical Thinking', 'Reporting'],
                'min_gpa': 2.0,
                'experience_level': 'entry',
                'archetype': 'the_sage'
            },
            'Professor': {
                'required_skills': ['Teaching', 'Research', 'Knowledge Pursuit'],
                'preferred_skills': ['Communication', 'Analytical Thinking', 'Mentoring'],
                'min_gpa': 1.75,
                'experience_level': 'senior',
                'archetype': 'the_sage'
            },
            
            # The Creator archetype jobs
            'Software Developer': {
                'required_skills': ['Programming', 'Problem Solving', 'Software Development'],
                'preferred_skills': ['Web Development', 'Database Management', 'Creative Thinking'],
                'min_gpa': 2.5,
                'experience_level': 'entry',
                'archetype': 'the_creator'
            },
            'UI/UX Designer': {
                'required_skills': ['UI/UX Design', 'Visual Design', 'User Experience'],
                'preferred_skills': ['Creative Thinking', 'Presentation Skills', 'Problem Solving'],
                'min_gpa': 2.5,
                'experience_level': 'entry',
                'archetype': 'the_creator'
            },
            'Creative Director': {
                'required_skills': ['Creative Thinking', 'Leadership', 'Artistic Vision'],
                'preferred_skills': ['Innovation', 'Communication', 'Project Management'],
                'min_gpa': 2.0,
                'experience_level': 'senior',
                'archetype': 'the_creator'
            },
            
            # The Ruler archetype jobs
            'Project Manager': {
                'required_skills': ['Project Management', 'Leadership', 'Organization'],
                'preferred_skills': ['Communication', 'Strategic Planning', 'Team Management'],
                'min_gpa': 2.0,
                'experience_level': 'mid',
                'archetype': 'the_ruler'
            },
            'Team Lead': {
                'required_skills': ['Leadership', 'Team Management', 'Technical Skills'],
                'preferred_skills': ['Communication', 'Problem Solving', 'Mentoring'],
                'min_gpa': 2.0,
                'experience_level': 'mid',
                'archetype': 'the_ruler'
            },
            'Manager': {
                'required_skills': ['Leadership', 'Management', 'Communication'],
                'preferred_skills': ['Strategic Planning', 'Decision Making', 'Team Building'],
                'min_gpa': 2.0,
                'experience_level': 'mid',
                'archetype': 'the_ruler'
            },
            
            # The Hero archetype jobs
            'Entrepreneur': {
                'required_skills': ['Leadership', 'Risk Taking', 'Innovation'],
                'preferred_skills': ['Business Acumen', 'Strategic Thinking', 'Problem Solving'],
                'min_gpa': 2.5,
                'experience_level': 'entry',
                'archetype': 'the_hero'
            },
            'Startup Founder': {
                'required_skills': ['Leadership', 'Innovation', 'Risk Taking'],
                'preferred_skills': ['Business Acumen', 'Strategic Thinking', 'Vision'],
                'min_gpa': 2.5,
                'experience_level': 'entry',
                'archetype': 'the_hero'
            },
            
            # The Explorer archetype jobs
            'Consultant': {
                'required_skills': ['Problem Solving', 'Communication', 'Strategic Thinking'],
                'preferred_skills': ['Analysis', 'Research Methods', 'Adaptability'],
                'min_gpa': 2.0,
                'experience_level': 'mid',
                'archetype': 'the_explorer'
            },
            'Researcher': {
                'required_skills': ['Research Methods', 'Analytical Thinking', 'Curiosity'],
                'preferred_skills': ['Data Analysis', 'Critical Thinking', 'Innovation'],
                'min_gpa': 2.0,
                'experience_level': 'entry',
                'archetype': 'the_explorer'
            },
            
            # The Rebel archetype jobs
            'Innovation Consultant': {
                'required_skills': ['Innovation', 'Creative Thinking', 'Problem Solving'],
                'preferred_skills': ['Change Management', 'Strategic Thinking', 'Disruption'],
                'min_gpa': 2.5,
                'experience_level': 'mid',
                'archetype': 'the_rebel'
            },
            
            # The Lover archetype jobs
            'Marketing Specialist': {
                'required_skills': ['Communication', 'Creative Thinking', 'Market Analysis'],
                'preferred_skills': ['Relationship Building', 'Presentation Skills', 'Customer Focus'],
                'min_gpa': 2.5,
                'experience_level': 'entry',
                'archetype': 'the_lover'
            },
            'Sales Manager': {
                'required_skills': ['Communication', 'Leadership', 'Relationship Building'],
                'preferred_skills': ['Sales Skills', 'Customer Focus', 'Motivation'],
                'min_gpa': 2.5,
                'experience_level': 'mid',
                'archetype': 'the_lover'
            },
            
            # The Magician archetype jobs
            'Product Manager': {
                'required_skills': ['Product Management', 'Leadership', 'Strategic Thinking'],
                'preferred_skills': ['Communication', 'Vision', 'Change Management'],
                'min_gpa': 2.0,
                'experience_level': 'mid',
                'archetype': 'the_magician'
            },
            'Change Manager': {
                'required_skills': ['Change Management', 'Leadership', 'Communication'],
                'preferred_skills': ['Strategic Planning', 'Vision', 'Influence'],
                'min_gpa': 2.0,
                'experience_level': 'mid',
                'archetype': 'the_magician'
            },
            
            # The Caregiver archetype jobs
            'Human Resources Manager': {
                'required_skills': ['HR Management', 'Communication', 'Employee Relations'],
                'preferred_skills': ['Leadership', 'Compassion', 'Problem Solving'],
                'min_gpa': 2.5,
                'experience_level': 'mid',
                'archetype': 'the_caregiver'
            },
            'Teacher': {
                'required_skills': ['Teaching', 'Communication', 'Patience'],
                'preferred_skills': ['Knowledge Sharing', 'Empathy', 'Engagement'],
                'min_gpa': 2.5,
                'experience_level': 'entry',
                'archetype': 'the_caregiver'
            },
            
            # The Innocent archetype jobs
            'Customer Service Representative': {
                'required_skills': ['Customer Service', 'Communication', 'Patience'],
                'preferred_skills': ['Problem Solving', 'Empathy', 'Positive Attitude'],
                'min_gpa': 3.0,
                'experience_level': 'entry',
                'archetype': 'the_innocent'
            },
            
            # The Everyman archetype jobs
            'Administrative Assistant': {
                'required_skills': ['Organization', 'Communication', 'Time Management'],
                'preferred_skills': ['Attention to Detail', 'Teamwork', 'Adaptability'],
                'min_gpa': 3.0,
                'experience_level': 'entry',
                'archetype': 'the_everyman'
            },
            'Support Specialist': {
                'required_skills': ['Technical Support', 'Communication', 'Problem Solving'],
                'preferred_skills': ['Customer Service', 'Technical Skills', 'Patience'],
                'min_gpa': 3.0,
                'experience_level': 'entry',
                'archetype': 'the_everyman'
            },
            
            # The Jester archetype jobs
            'Content Creator': {
                'required_skills': ['Content Creation', 'Creativity', 'Communication'],
                'preferred_skills': ['Digital Skills', 'Entertainment', 'Engagement'],
                'min_gpa': 2.5,
                'experience_level': 'entry',
                'archetype': 'the_jester'
            }
        }
    
    def match_jobs_for_user(self, user_email: str, limit: int = 20) -> Dict[str, Any]:
        """Find and rank job matches for a specific user"""
        try:
            # Get user's academic profile
            user_profile = self.get_user_academic_profile(user_email)
            if not user_profile:
                return {'error': 'User profile not found or not analyzed'}
            
            # Get available jobs
            jobs = self.get_available_jobs(limit * 2)  # Get more to filter
            
            # Score each job for the user
            job_matches = []
            for job in jobs:
                match_score = self.calculate_job_match_score(user_profile, job)
                if match_score > 50:  # Only include decent matches
                    job_matches.append({
                        'job': job,
                        'match_score': match_score,
                        'match_reasons': self.generate_match_reasons(user_profile, job, match_score)
                    })
            
            # Sort by match score
            job_matches.sort(key=lambda x: x['match_score'], reverse=True)
            
            return {
                'user_email': user_email,
                'total_matches': len(job_matches),
                'matches': job_matches[:limit],
                'user_profile_summary': self.get_profile_summary(user_profile),
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {'error': f'Error matching jobs: {str(e)}'}
    
    def get_user_academic_profile(self, user_email: str) -> Optional[Dict[str, Any]]:
        """Get user's academic analysis from the database"""
        try:
            # First get the user
            user_result = self.supabase.table("users").select("*").eq("email", user_email).execute()
            if not user_result.data:
                return None
            
            user = user_result.data[0]
            
            # If we don't have tor_notes (academic analysis), generate it
            if not user.get('tor_notes'):
                # Create sample analysis for demonstration
                sample_analysis = self.academic_analyzer.analyze_transcript("")
                return {
                    'user_data': user,
                    'academic_analysis': sample_analysis
                }
            
            # Parse existing tor_notes as academic analysis
            try:
                academic_analysis = json.loads(user['tor_notes'])
            except:
                # If tor_notes isn't valid JSON, create sample analysis
                academic_analysis = self.academic_analyzer.analyze_transcript("")
            
            return {
                'user_data': user,
                'academic_analysis': academic_analysis
            }
            
        except Exception as e:
            print(f"Error getting user profile: {e}")
            return None
    
    def get_available_jobs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get available jobs from the database"""
        try:
            result = self.supabase.table("jobs").select("*").order("scraped_at", desc=True).limit(limit).execute()
            return result.data or []
        except Exception as e:
            print(f"Error getting jobs: {e}")
            return []
    
    def calculate_job_match_score(self, user_profile: Dict[str, Any], job: Dict[str, Any]) -> int:
        """Calculate match score between user profile and job (0-100)"""
        score = 0
        academic_analysis = user_profile['academic_analysis']
        user_data = user_profile['user_data']
        
        # Job title matching
        job_title = job.get('title', '').lower()
        
        # Get job requirements if we have them mapped
        job_requirements = None
        for mapped_title, requirements in self.skill_job_mapping.items():
            if mapped_title.lower() in job_title:
                job_requirements = requirements
                break
        
        # Base score from job title matching user's archetype
        archetype = academic_analysis.get('learning_archetype', {})
        career_recommendations = academic_analysis.get('career_recommendations', [])
        user_archetype = archetype.get('primary_archetype', '')
        
        # Check if this job matches recommended careers
        for recommendation in career_recommendations:
            if recommendation['career'].lower() in job_title:
                score += recommendation.get('match_score', 70)
                break
        else:
            score += 40  # Base score if no direct match
        
        # Archetype alignment bonus
        if job_requirements and job_requirements.get('archetype') == user_archetype:
            score += 15  # Strong archetype alignment
        elif job_requirements and job_requirements.get('archetype'):
            # Check for complementary archetypes
            complementary_archetypes = {
                'the_sage': ['the_creator', 'the_explorer'],
                'the_creator': ['the_sage', 'the_rebel'],
                'the_ruler': ['the_hero', 'the_magician'],
                'the_hero': ['the_ruler', 'the_rebel'],
                'the_explorer': ['the_sage', 'the_creator'],
                'the_rebel': ['the_creator', 'the_hero'],
                'the_lover': ['the_caregiver', 'the_jester'],
                'the_magician': ['the_ruler', 'the_sage'],
                'the_caregiver': ['the_lover', 'the_innocent'],
                'the_innocent': ['the_caregiver', 'the_everyman'],
                'the_everyman': ['the_innocent', 'the_lover'],
                'the_jester': ['the_lover', 'the_creator']
            }
            
            if user_archetype in complementary_archetypes and job_requirements['archetype'] in complementary_archetypes[user_archetype]:
                score += 8  # Complementary archetype
        
        # Skills matching
        user_skills = [skill['skill'].lower() for skill in academic_analysis.get('skills', [])]
        
        if job_requirements:
            # Required skills
            required_skills = [skill.lower() for skill in job_requirements['required_skills']]
            required_matches = len(set(user_skills).intersection(set(required_skills)))
            score += required_matches * 8  # 8 points per required skill match
            
            # Preferred skills
            preferred_skills = [skill.lower() for skill in job_requirements['preferred_skills']]
            preferred_matches = len(set(user_skills).intersection(set(preferred_skills)))
            score += preferred_matches * 4  # 4 points per preferred skill match
            
            # GPA requirement
            user_gpa = academic_analysis.get('academic_metrics', {}).get('gpa', 3.0)
            min_gpa = job_requirements.get('min_gpa', 3.0)
            if user_gpa <= min_gpa:  # Lower GPA is better in Philippine system
                score += 10
        
        # Company and location matching
        job_location = job.get('location', '').lower()
        if 'philippines' in job_location:
            score += 5
        
        # Remote work bonus for certain archetypes
        if job.get('remote') and archetype.get('primary_archetype') in ['technical_specialist', 'analytical_thinker']:
            score += 5
        
        # Salary matching (bonus for reasonable ranges)
        salary_min = job.get('salary_min', 0)
        if 40000 <= salary_min <= 150000:  # Reasonable salary range
            score += 5
        
        # Cap the score at 100
        return min(100, max(0, score))
    
    def generate_match_reasons(self, user_profile: Dict[str, Any], job: Dict[str, Any], match_score: int) -> List[str]:
        """Generate human-readable reasons for the job match"""
        reasons = []
        academic_analysis = user_profile['academic_analysis']
        
        # Archetype matching
        archetype = academic_analysis.get('learning_archetype', {})
        primary_archetype = archetype.get('primary_archetype', '').replace('_', ' ').title()
        reasons.append(f"Matches your {primary_archetype} profile")
        
        # Skills matching
        user_skills = [skill['skill'] for skill in academic_analysis.get('skills', [])]
        job_title = job.get('title', '').lower()
        
        matching_skills = []
        for skill_data in academic_analysis.get('skills', []):
            skill = skill_data['skill'].lower()
            if any(keyword in job_title for keyword in skill.split()):
                matching_skills.append(skill_data['skill'])
        
        if matching_skills:
            reasons.append(f"Your skills match: {', '.join(matching_skills[:3])}")
        
        # Academic performance
        gpa = academic_analysis.get('academic_metrics', {}).get('gpa', 3.0)
        if gpa <= 2.0:
            reasons.append("Your excellent academic performance (GPA: {:.2f})".format(gpa))
        elif gpa <= 2.5:
            reasons.append("Your strong academic performance (GPA: {:.2f})".format(gpa))
        
        # Job specifics
        if job.get('remote'):
            reasons.append("Offers remote work flexibility")
        
        company = job.get('company', '')
        if company:
            reasons.append(f"Opportunity at {company}")
        
        # Salary
        salary_min = job.get('salary_min')
        salary_max = job.get('salary_max')
        if salary_min and salary_max:
            reasons.append(f"Competitive salary: ₱{salary_min:,} - ₱{salary_max:,}")
        
        return reasons[:5]  # Limit to top 5 reasons
    
    def get_profile_summary(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Get a summary of the user's profile for display"""
        academic_analysis = user_profile['academic_analysis']
        user_data = user_profile['user_data']
        
        return {
            'name': f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip(),
            'course': user_data.get('course', ''),
            'gpa': academic_analysis.get('academic_metrics', {}).get('gpa'),
            'academic_standing': academic_analysis.get('academic_metrics', {}).get('academic_standing'),
            'primary_archetype': academic_analysis.get('learning_archetype', {}).get('primary_archetype', '').replace('_', ' ').title(),
            'top_skills': [skill['skill'] for skill in academic_analysis.get('skills', [])[:5]],
            'career_recommendations': [rec['career'] for rec in academic_analysis.get('career_recommendations', [])[:3]]
        }
    
    def update_job_match_scores(self) -> Dict[str, Any]:
        """Update match scores for all users and jobs (batch processing)"""
        try:
            # Get all users with academic analysis
            users_result = self.supabase.table("users").select("email, tor_notes").execute()
            users = [user for user in users_result.data if user.get('tor_notes')]
            
            # Get all jobs
            jobs = self.get_available_jobs(100)
            
            total_matches = 0
            for user in users:
                user_email = user['email']
                user_matches = self.match_jobs_for_user(user_email, 10)
                if 'matches' in user_matches:
                    total_matches += len(user_matches['matches'])
            
            return {
                'processed_users': len(users),
                'processed_jobs': len(jobs),
                'total_matches': total_matches,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {'error': f'Error updating match scores: {str(e)}'}
