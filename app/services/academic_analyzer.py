import re
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


class AcademicAnalyzer:
    """Comprehensive academic analysis for career recommendations"""
    
    def __init__(self):
        self.subject_categories = {
            'programming': ['programming', 'software', 'algorithm', 'data structure', 'coding', 'python', 'java', 'javascript', 'web development'],
            'mathematics': ['mathematics', 'calculus', 'statistics', 'algebra', 'geometry', 'discrete math', 'probability'],
            'science': ['physics', 'chemistry', 'biology', 'laboratory', 'research', 'experiment'],
            'business': ['business', 'management', 'economics', 'finance', 'marketing', 'accounting'],
            'communication': ['english', 'communication', 'writing', 'presentation', 'literature', 'public speaking'],
            'design': ['design', 'graphics', 'art', 'creative', 'visual', 'ui', 'ux'],
            'engineering': ['engineering', 'systems', 'hardware', 'circuits', 'mechanics', 'electrical'],
            'data_science': ['data science', 'machine learning', 'artificial intelligence', 'analytics', 'database']
        }
        
        self.learning_archetypes = {
            'the_innocent': {
                'traits': ['optimism', 'trust', 'simplicity', 'safety-seeking'],
                'careers': ['Customer Service Representative', 'Teacher', 'Counselor', 'Healthcare Worker'],
                'description': 'Values safety, simplicity, and optimism. Seeks to be good and do the right thing.',
                'academic_indicators': ['consistent performance', 'follows rules', 'collaborative work', 'positive attitude']
            },
            'the_everyman': {
                'traits': ['belonging', 'equality', 'realism', 'down-to-earth'],
                'careers': ['Administrative Assistant', 'Sales Representative', 'Team Member', 'Support Specialist'],
                'description': 'Seeks belonging and connection. Values equality and being part of a community.',
                'academic_indicators': ['team projects', 'average performance', 'social subjects', 'practical courses']
            },
            'the_hero': {
                'traits': ['courage', 'mastery', 'overcoming challenges', 'determination'],
                'careers': ['Entrepreneur', 'Military Officer', 'Emergency Responder', 'Athlete'],
                'description': 'Driven by courage and mastery. Seeks to prove worth through courageous acts.',
                'academic_indicators': ['overcoming difficult subjects', 'leadership roles', 'competitive spirit', 'high achievement']
            },
            'the_caregiver': {
                'traits': ['compassion', 'service', 'selflessness', 'nurturing'],
                'careers': ['Nurse', 'Social Worker', 'Teacher', 'Human Resources Manager'],
                'description': 'Motivated by compassion and service. Seeks to help and protect others.',
                'academic_indicators': ['helping others', 'service-oriented projects', 'healthcare subjects', 'communication skills']
            },
            'the_explorer': {
                'traits': ['freedom', 'discovery', 'self-fulfillment', 'adventure'],
                'careers': ['Travel Writer', 'Researcher', 'Consultant', 'Freelancer'],
                'description': 'Seeks freedom and discovery. Values exploration and new experiences.',
                'academic_indicators': ['diverse course selection', 'independent study', 'research projects', 'creative thinking']
            },
            'the_rebel': {
                'traits': ['revolution', 'nonconformity', 'change', 'disruption'],
                'careers': ['Innovation Consultant', 'Startup Founder', 'Activist', 'Creative Director'],
                'description': 'Driven by revolution and change. Seeks to disrupt the status quo.',
                'academic_indicators': ['challenging conventional methods', 'innovative projects', 'questioning authority', 'creative solutions']
            },
            'the_lover': {
                'traits': ['passion', 'relationships', 'intimacy', 'connection'],
                'careers': ['Marketing Specialist', 'Event Planner', 'Public Relations', 'Sales Manager'],
                'description': 'Motivated by passion and relationships. Seeks connection and intimacy.',
                'academic_indicators': ['group work', 'communication courses', 'relationship-building', 'emotional intelligence']
            },
            'the_creator': {
                'traits': ['innovation', 'imagination', 'lasting value', 'artistic expression'],
                'careers': ['Artist', 'Designer', 'Writer', 'Architect', 'Software Developer'],
                'description': 'Driven by innovation and imagination. Seeks to create something of lasting value.',
                'academic_indicators': ['creative projects', 'design courses', 'artistic expression', 'innovative thinking']
            },
            'the_jester': {
                'traits': ['fun', 'joy', 'lightheartedness', 'entertainment'],
                'careers': ['Entertainer', 'Comedian', 'Event Host', 'Content Creator', 'Teacher'],
                'description': 'Seeks fun and joy. Values lightheartedness and bringing happiness to others.',
                'academic_indicators': ['enjoyment in learning', 'humor in presentations', 'engaging others', 'positive atmosphere']
            },
            'the_sage': {
                'traits': ['wisdom', 'knowledge', 'truth', 'understanding'],
                'careers': ['Professor', 'Researcher', 'Analyst', 'Consultant', 'Data Scientist'],
                'description': 'Driven by wisdom and knowledge. Seeks truth and understanding.',
                'academic_indicators': ['excellent academic performance', 'research focus', 'analytical thinking', 'knowledge pursuit']
            },
            'the_magician': {
                'traits': ['vision', 'transformation', 'possibility', 'influence'],
                'careers': ['Life Coach', 'Therapist', 'Innovation Leader', 'Change Manager', 'Product Manager'],
                'description': 'Seeks transformation and possibility. Has the vision to make things happen.',
                'academic_indicators': ['transformative projects', 'visionary thinking', 'influencing others', 'change management']
            },
            'the_ruler': {
                'traits': ['control', 'order', 'leadership', 'responsibility'],
                'careers': ['CEO', 'Manager', 'Project Manager', 'Team Lead', 'Government Official'],
                'description': 'Driven by control and order. Seeks leadership and responsibility.',
                'academic_indicators': ['leadership roles', 'organizational skills', 'management courses', 'taking charge']
            }
        }
    
    def analyze_transcript(self, transcript_text: str) -> Dict[str, Any]:
        """Comprehensive analysis of academic transcript"""
        
        # Extract grades and subjects
        grades_data = self.extract_grades_and_subjects(transcript_text)
        
        # Calculate academic metrics
        academic_metrics = self.calculate_academic_metrics(grades_data)
        
        # Analyze subject performance
        subject_analysis = self.analyze_subject_performance(grades_data)
        
        # Identify learning archetype
        learning_archetype = self.identify_learning_archetype(subject_analysis, academic_metrics)
        
        # Extract skills
        skills = self.extract_skills_from_subjects(grades_data)
        
        # Generate career recommendations
        career_recommendations = self.generate_career_recommendations(learning_archetype, skills, subject_analysis)
        
        return {
            'academic_metrics': academic_metrics,
            'subject_analysis': subject_analysis,
            'learning_archetype': learning_archetype,
            'skills': skills,
            'career_recommendations': career_recommendations,
            'analysis_timestamp': datetime.utcnow().isoformat()
        }
    
    def extract_grades_and_subjects(self, text: str) -> List[Dict[str, Any]]:
        """Extract grades and subjects from transcript text"""
        subjects = []
        
        # Common grade patterns
        grade_patterns = [
            r'([A-Z][a-z\s]+(?:I{1,3}|IV|V)?)\s+(\d+(?:\.\d+)?)\s+([A-F][+-]?|\d+(?:\.\d+)?)',  # Subject Units Grade
            r'([A-Z][a-z\s]+(?:I{1,3}|IV|V)?)\s+([A-F][+-]?|\d+(?:\.\d+)?)',  # Subject Grade
        ]
        
        for pattern in grade_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) == 3:
                    subject_name, units, grade = match
                    subjects.append({
                        'subject': subject_name.strip(),
                        'units': self.parse_units(units),
                        'grade': self.normalize_grade(grade)
                    })
                elif len(match) == 2:
                    subject_name, grade = match
                    subjects.append({
                        'subject': subject_name.strip(),
                        'units': 3,  # Default units
                        'grade': self.normalize_grade(grade)
                    })
        
        # If no structured data found, create sample data for demonstration
        if not subjects:
            subjects = self.create_sample_academic_data()
        
        return subjects
    
    def create_sample_academic_data(self) -> List[Dict[str, Any]]:
        """Create sample academic data for demonstration"""
        return [
            {'subject': 'Data Structures and Algorithms', 'units': 3, 'grade': 1.5},
            {'subject': 'Web Development', 'units': 3, 'grade': 1.25},
            {'subject': 'Database Systems', 'units': 3, 'grade': 1.75},
            {'subject': 'Software Engineering', 'units': 3, 'grade': 1.5},
            {'subject': 'Mathematics', 'units': 3, 'grade': 2.0},
            {'subject': 'Statistics', 'units': 3, 'grade': 1.75},
            {'subject': 'Programming Fundamentals', 'units': 3, 'grade': 1.25},
            {'subject': 'Computer Networks', 'units': 3, 'grade': 2.0},
            {'subject': 'Human Computer Interaction', 'units': 3, 'grade': 1.5},
            {'subject': 'Project Management', 'units': 3, 'grade': 1.75}
        ]
    
    def parse_units(self, units_str: str) -> int:
        """Parse units from string"""
        try:
            return int(float(units_str))
        except:
            return 3  # Default
    
    def normalize_grade(self, grade_str: str) -> float:
        """Convert grade to numerical format (Philippine grading system: 1.0-5.0, 1.0 = highest)"""
        grade_str = str(grade_str).strip().upper()
        
        # Letter grades to numerical
        letter_to_num = {
            'A+': 1.0, 'A': 1.25, 'A-': 1.5,
            'B+': 1.75, 'B': 2.0, 'B-': 2.25,
            'C+': 2.5, 'C': 2.75, 'C-': 3.0,
            'D': 4.0, 'F': 5.0
        }
        
        if grade_str in letter_to_num:
            return letter_to_num[grade_str]
        
        try:
            grade_num = float(grade_str)
            # Ensure grade is in valid range
            return max(1.0, min(5.0, grade_num))
        except:
            return 2.5  # Default grade
    
    def calculate_academic_metrics(self, grades_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate GPA and other academic metrics"""
        if not grades_data:
            return {'gpa': 0.0, 'total_units': 0, 'subjects_count': 0}
        
        total_grade_points = sum(subject['grade'] * subject['units'] for subject in grades_data)
        total_units = sum(subject['units'] for subject in grades_data)
        
        gpa = total_grade_points / total_units if total_units > 0 else 0.0
        
        # Academic standing (Philippine system)
        if gpa <= 1.5:
            standing = "Summa Cum Laude"
        elif gpa <= 1.75:
            standing = "Magna Cum Laude"
        elif gpa <= 2.0:
            standing = "Cum Laude"
        elif gpa <= 3.0:
            standing = "Good Standing"
        else:
            standing = "Fair Standing"
        
        return {
            'gpa': round(gpa, 2),
            'total_units': total_units,
            'subjects_count': len(grades_data),
            'academic_standing': standing,
            'grade_distribution': self.calculate_grade_distribution(grades_data)
        }
    
    def calculate_grade_distribution(self, grades_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate distribution of grades"""
        distribution = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
        
        for subject in grades_data:
            grade = subject['grade']
            if grade <= 1.5:
                distribution['A'] += 1
            elif grade <= 2.25:
                distribution['B'] += 1
            elif grade <= 3.0:
                distribution['C'] += 1
            elif grade <= 4.0:
                distribution['D'] += 1
            else:
                distribution['F'] += 1
        
        return distribution
    
    def analyze_subject_performance(self, grades_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance by subject categories"""
        category_performance = {}
        
        for category, keywords in self.subject_categories.items():
            category_subjects = []
            
            for subject in grades_data:
                subject_name = subject['subject'].lower()
                if any(keyword in subject_name for keyword in keywords):
                    category_subjects.append(subject)
            
            if category_subjects:
                avg_grade = sum(s['grade'] for s in category_subjects) / len(category_subjects)
                category_performance[category] = {
                    'average_grade': round(avg_grade, 2),
                    'subject_count': len(category_subjects),
                    'subjects': [s['subject'] for s in category_subjects],
                    'performance_level': self.grade_to_performance_level(avg_grade)
                }
        
        return category_performance
    
    def grade_to_performance_level(self, grade: float) -> str:
        """Convert grade to performance level"""
        if grade <= 1.5:
            return "Excellent"
        elif grade <= 2.0:
            return "Very Good"
        elif grade <= 2.5:
            return "Good"
        elif grade <= 3.0:
            return "Satisfactory"
        else:
            return "Needs Improvement"
    
    def identify_learning_archetype(self, subject_analysis: Dict[str, Any], academic_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Identify learning archetype based on academic performance using 12 Jungian archetypes with percentages"""
        # Initialize scores for all 12 archetypes
        archetype_scores = {
            'the_innocent': 0,
            'the_everyman': 0,
            'the_hero': 0,
            'the_caregiver': 0,
            'the_explorer': 0,
            'the_rebel': 0,
            'the_lover': 0,
            'the_creator': 0,
            'the_jester': 0,
            'the_sage': 0,
            'the_magician': 0,
            'the_ruler': 0
        }
        
        gpa = academic_metrics.get('gpa', 3.0)
        total_subjects = academic_metrics.get('subjects_count', 0)
        
        # Analyze subject performance patterns
        strong_categories = [cat for cat, data in subject_analysis.items() 
                           if data['average_grade'] <= 2.0]
        weak_categories = [cat for cat, data in subject_analysis.items() 
                          if data['average_grade'] > 3.0]
        
        # Enhanced scoring system for all archetypes
        
        # The Sage - Excellent academic performance, analytical subjects
        if gpa <= 1.75:
            archetype_scores['the_sage'] += 3
        if gpa <= 2.0:
            archetype_scores['the_sage'] += 2
        if 'mathematics' in strong_categories:
            archetype_scores['the_sage'] += 2
        if 'data_science' in strong_categories:
            archetype_scores['the_sage'] += 2
        if 'science' in strong_categories:
            archetype_scores['the_sage'] += 1
        
        # The Hero - Overcoming challenges, high achievement
        if gpa <= 2.0:
            archetype_scores['the_hero'] += 2
        if len(weak_categories) > 0 and gpa <= 2.5:
            archetype_scores['the_hero'] += 3  # Overcoming challenges
        if 'programming' in strong_categories:
            archetype_scores['the_hero'] += 1
        if 'engineering' in strong_categories:
            archetype_scores['the_hero'] += 1
        
        # The Creator - Creative subjects, innovative thinking
        if 'design' in strong_categories:
            archetype_scores['the_creator'] += 3
        if 'communication' in strong_categories:
            archetype_scores['the_creator'] += 2
        if 'programming' in strong_categories:
            archetype_scores['the_creator'] += 2
        if len(strong_categories) >= 3:
            archetype_scores['the_creator'] += 1  # Diverse creative abilities
        
        # The Ruler - Leadership, management, organizational skills
        if 'business' in strong_categories:
            archetype_scores['the_ruler'] += 3
        if gpa <= 2.0:
            archetype_scores['the_ruler'] += 2
        if total_subjects >= 8:
            archetype_scores['the_ruler'] += 1  # Managing many subjects
        if len(strong_categories) >= 2:
            archetype_scores['the_ruler'] += 1  # Leadership across domains
        
        # The Explorer - Diverse course selection, research focus
        if total_subjects >= 8:
            archetype_scores['the_explorer'] += 3
        if 'science' in strong_categories:
            archetype_scores['the_explorer'] += 2
        if 'data_science' in strong_categories:
            archetype_scores['the_explorer'] += 2
        if len(strong_categories) >= 4:
            archetype_scores['the_explorer'] += 2  # Very diverse interests
        
        # The Rebel - Challenging conventional methods, innovative projects
        if len(strong_categories) >= 3:
            archetype_scores['the_rebel'] += 2
        if 'programming' in strong_categories:
            archetype_scores['the_rebel'] += 2
        if 'engineering' in strong_categories:
            archetype_scores['the_rebel'] += 1
        if len(weak_categories) > 0:
            archetype_scores['the_rebel'] += 1  # Challenging conventional methods
        
        # The Lover - Communication, relationship-building
        if 'communication' in strong_categories:
            archetype_scores['the_lover'] += 3
        if 'business' in strong_categories:
            archetype_scores['the_lover'] += 1
        if gpa <= 2.5:
            archetype_scores['the_lover'] += 1  # Good interpersonal skills
        
        # The Magician - Transformative thinking, visionary projects
        if 'engineering' in strong_categories:
            archetype_scores['the_magician'] += 2
        if 'programming' in strong_categories:
            archetype_scores['the_magician'] += 2
        if 'data_science' in strong_categories:
            archetype_scores['the_magician'] += 2
        if gpa <= 2.0:
            archetype_scores['the_magician'] += 1
        
        # The Caregiver - Service-oriented, helping others
        if 'communication' in strong_categories:
            archetype_scores['the_caregiver'] += 2
        if gpa <= 2.5:
            archetype_scores['the_caregiver'] += 1
        if 'business' in strong_categories:
            archetype_scores['the_caregiver'] += 1  # People management
        
        # The Innocent - Consistent, rule-following, positive attitude
        if gpa <= 2.5:
            archetype_scores['the_innocent'] += 2
        if len(weak_categories) == 0:
            archetype_scores['the_innocent'] += 2  # Consistent performance
        if total_subjects >= 5:
            archetype_scores['the_innocent'] += 1  # Follows academic structure
        
        # The Everyman - Average performance, practical courses
        if 2.0 <= gpa <= 3.0:
            archetype_scores['the_everyman'] += 2
        if total_subjects >= 5:
            archetype_scores['the_everyman'] += 2
        if len(strong_categories) >= 2:
            archetype_scores['the_everyman'] += 1  # Practical across domains
        
        # The Jester - Enjoyment in learning, engaging others
        if 'communication' in strong_categories:
            archetype_scores['the_jester'] += 2
        if gpa <= 2.5:
            archetype_scores['the_jester'] += 1
        if 'design' in strong_categories:
            archetype_scores['the_jester'] += 1  # Creative expression
        
        # Calculate percentages for all archetypes
        total_score = sum(archetype_scores.values())
        archetype_percentages = {}
        
        if total_score > 0:
            for archetype, score in archetype_scores.items():
                percentage = round((score / total_score) * 100, 1)
                archetype_percentages[archetype] = percentage
        else:
            # If no scores, distribute evenly
            for archetype in archetype_scores:
                archetype_percentages[archetype] = round(100 / 12, 1)
        
        # Determine primary archetype
        primary_archetype = max(archetype_scores, key=archetype_scores.get)
        
        # Get archetype details
        archetype_info = self.learning_archetypes[primary_archetype]
        
        return {
            'primary_archetype': primary_archetype,
            'archetype_scores': archetype_scores,
            'archetype_percentages': archetype_percentages,
            'traits': archetype_info['traits'],
            'description': archetype_info['description'],
            'academic_indicators': archetype_info['academic_indicators'],
            'archetype_name': primary_archetype.replace('_', ' ').title()
        }
    
    def extract_skills_from_subjects(self, grades_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract and rate skills based on subject performance"""
        skills = []
        
        skill_mapping = {
            'programming': ['Python', 'Java', 'JavaScript', 'Web Development', 'Software Development'],
            'mathematics': ['Statistical Analysis', 'Mathematical Modeling', 'Problem Solving'],
            'data_science': ['Data Analysis', 'Machine Learning', 'Database Management'],
            'business': ['Project Management', 'Business Analysis', 'Strategic Planning'],
            'communication': ['Technical Writing', 'Presentation Skills', 'Documentation'],
            'design': ['UI/UX Design', 'Visual Design', 'User Experience'],
            'engineering': ['Systems Design', 'Technical Architecture', 'Engineering Principles']
        }
        
        for subject in grades_data:
            subject_name = subject['subject'].lower()
            grade = subject['grade']
            
            # Determine skill proficiency based on grade
            if grade <= 1.5:
                proficiency = "Expert"
                score = 90
            elif grade <= 2.0:
                proficiency = "Advanced"
                score = 80
            elif grade <= 2.5:
                proficiency = "Intermediate"
                score = 70
            else:
                proficiency = "Beginner"
                score = 60
            
            # Map subjects to skills
            for category, skill_list in skill_mapping.items():
                if any(keyword in subject_name for keyword in self.subject_categories[category]):
                    for skill in skill_list:
                        skills.append({
                            'skill': skill,
                            'proficiency': proficiency,
                            'score': score,
                            'source_subject': subject['subject']
                        })
        
        # Remove duplicates and average scores
        unique_skills = {}
        for skill_data in skills:
            skill_name = skill_data['skill']
            if skill_name in unique_skills:
                # Average the scores
                existing_score = unique_skills[skill_name]['score']
                new_score = (existing_score + skill_data['score']) / 2
                unique_skills[skill_name]['score'] = new_score
            else:
                unique_skills[skill_name] = skill_data
        
        return list(unique_skills.values())
    
    def generate_career_recommendations(self, learning_archetype: Dict[str, Any], 
                                      skills: List[Dict[str, Any]], 
                                      subject_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate personalized career recommendations based on 12 Jungian archetypes"""
        recommendations = []
        
        # Get archetype-based careers
        primary_archetype = learning_archetype['primary_archetype']
        base_careers = self.learning_archetypes[primary_archetype]['careers']
        
        # Enhanced career skill mapping for all archetype careers
        career_skill_mapping = {
            # The Sage careers
            'Professor': ['Research', 'Analytical Thinking', 'Knowledge Pursuit', 'Teaching'],
            'Researcher': ['Data Analysis', 'Statistical Analysis', 'Research Methods', 'Critical Thinking'],
            'Analyst': ['Data Analysis', 'Statistical Analysis', 'Problem Solving', 'Reporting'],
            'Consultant': ['Problem Solving', 'Communication', 'Strategic Thinking', 'Analysis'],
            'Data Scientist': ['Data Analysis', 'Statistical Analysis', 'Machine Learning', 'Python'],
            
            # The Creator careers
            'Artist': ['Creative Thinking', 'Visual Design', 'Artistic Expression', 'Innovation'],
            'Designer': ['UI/UX Design', 'Visual Design', 'Creative Thinking', 'User Experience'],
            'Writer': ['Communication', 'Creative Writing', 'Content Creation', 'Storytelling'],
            'Architect': ['Design', 'Technical Drawing', 'Creative Thinking', 'Project Management'],
            'Software Developer': ['Programming', 'Problem Solving', 'Software Development', 'Technical Skills'],
            
            # The Ruler careers
            'CEO': ['Leadership', 'Strategic Planning', 'Decision Making', 'Management'],
            'Manager': ['Leadership', 'Project Management', 'Team Management', 'Communication'],
            'Project Manager': ['Project Management', 'Leadership', 'Organization', 'Communication'],
            'Team Lead': ['Leadership', 'Team Management', 'Technical Skills', 'Communication'],
            'Government Official': ['Leadership', 'Public Policy', 'Communication', 'Management'],
            
            # The Hero careers
            'Entrepreneur': ['Leadership', 'Risk Taking', 'Innovation', 'Business Acumen'],
            'Military Officer': ['Leadership', 'Discipline', 'Strategic Thinking', 'Physical Fitness'],
            'Emergency Responder': ['Quick Thinking', 'Problem Solving', 'Physical Fitness', 'Courage'],
            'Athlete': ['Physical Fitness', 'Discipline', 'Competitive Spirit', 'Teamwork'],
            
            # The Explorer careers
            'Travel Writer': ['Writing', 'Communication', 'Adventure', 'Cultural Awareness'],
            'Researcher': ['Research Methods', 'Analytical Thinking', 'Curiosity', 'Data Analysis'],
            'Consultant': ['Problem Solving', 'Communication', 'Strategic Thinking', 'Analysis'],
            'Freelancer': ['Self Management', 'Time Management', 'Technical Skills', 'Communication'],
            
            # The Rebel careers
            'Innovation Consultant': ['Innovation', 'Creative Thinking', 'Problem Solving', 'Change Management'],
            'Startup Founder': ['Leadership', 'Innovation', 'Risk Taking', 'Business Acumen'],
            'Activist': ['Communication', 'Passion', 'Leadership', 'Social Awareness'],
            'Creative Director': ['Creative Thinking', 'Leadership', 'Artistic Vision', 'Innovation'],
            
            # The Lover careers
            'Marketing Specialist': ['Communication', 'Creative Thinking', 'Market Analysis', 'Relationship Building'],
            'Event Planner': ['Organization', 'Communication', 'Attention to Detail', 'Customer Service'],
            'Public Relations': ['Communication', 'Relationship Building', 'Media Relations', 'Crisis Management'],
            'Sales Manager': ['Communication', 'Leadership', 'Relationship Building', 'Sales Skills'],
            
            # The Magician careers
            'Life Coach': ['Communication', 'Psychology', 'Motivation', 'Empathy'],
            'Therapist': ['Psychology', 'Communication', 'Empathy', 'Problem Solving'],
            'Innovation Leader': ['Leadership', 'Innovation', 'Strategic Thinking', 'Change Management'],
            'Change Manager': ['Change Management', 'Leadership', 'Communication', 'Strategic Planning'],
            'Product Manager': ['Product Management', 'Leadership', 'Strategic Thinking', 'Communication'],
            
            # The Caregiver careers
            'Nurse': ['Healthcare', 'Compassion', 'Patient Care', 'Medical Knowledge'],
            'Social Worker': ['Social Work', 'Compassion', 'Communication', 'Problem Solving'],
            'Teacher': ['Teaching', 'Communication', 'Patience', 'Knowledge Sharing'],
            'Human Resources Manager': ['HR Management', 'Communication', 'Employee Relations', 'Leadership'],
            
            # The Innocent careers
            'Customer Service Representative': ['Customer Service', 'Communication', 'Patience', 'Problem Solving'],
            'Teacher': ['Teaching', 'Communication', 'Patience', 'Knowledge Sharing'],
            'Counselor': ['Counseling', 'Communication', 'Empathy', 'Active Listening'],
            'Healthcare Worker': ['Healthcare', 'Compassion', 'Patient Care', 'Medical Knowledge'],
            
            # The Everyman careers
            'Administrative Assistant': ['Organization', 'Communication', 'Time Management', 'Attention to Detail'],
            'Sales Representative': ['Sales', 'Communication', 'Relationship Building', 'Product Knowledge'],
            'Team Member': ['Teamwork', 'Communication', 'Collaboration', 'Technical Skills'],
            'Support Specialist': ['Technical Support', 'Communication', 'Problem Solving', 'Customer Service'],
            
            # The Jester careers
            'Entertainer': ['Performance', 'Creativity', 'Communication', 'Entertainment'],
            'Comedian': ['Humor', 'Communication', 'Creativity', 'Performance'],
            'Event Host': ['Communication', 'Entertainment', 'Organization', 'Public Speaking'],
            'Content Creator': ['Content Creation', 'Creativity', 'Communication', 'Digital Skills'],
            'Teacher': ['Teaching', 'Communication', 'Engagement', 'Knowledge Sharing']
        }
        
        # Score careers based on skills and archetype alignment
        career_scores = {}
        
        for career in base_careers:
            score = 70  # Base score for archetype alignment
            
            # Boost score based on matching skills
            if career in career_skill_mapping:
                required_skills = career_skill_mapping[career]
                user_skills = [s['skill'] for s in skills]
                
                matching_skills = set(required_skills).intersection(set(user_skills))
                score += len(matching_skills) * 5
            
            # Additional boost for archetype-specific traits
            archetype_traits = learning_archetype.get('traits', [])
            if any(trait in career.lower() for trait in archetype_traits):
                score += 10
            
            career_scores[career] = min(100, score)
        
        # Create recommendations with enhanced reasoning
        for career, score in sorted(career_scores.items(), key=lambda x: x[1], reverse=True):
            archetype_name = learning_archetype.get('archetype_name', 'Your Profile')
            reasoning = f"Perfect match for your {archetype_name} archetype. Your academic performance shows strong alignment with {career} requirements."
            
            recommendations.append({
                'career': career,
                'match_score': score,
                'reasoning': reasoning,
                'required_skills': career_skill_mapping.get(career, []),
                'growth_potential': "High" if score >= 85 else "Medium" if score >= 70 else "Low",
                'archetype_alignment': f"Strong {archetype_name} characteristics"
            })
        
        return recommendations[:5]  # Top 5 recommendations
