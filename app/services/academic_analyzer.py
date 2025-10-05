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
        
        self.riasec_archetypes = {
            'realistic': {
                'name': 'Applied Practitioner',
                'traits': ['practical', 'hands-on', 'technical', 'systematic'],
                'careers': ['Hardware Technician', 'Network Engineer', 'Systems Administrator', 'IT Support Specialist'],
                'description': 'Practical and hands-on approach to technology. Excels in hardware, networking, and systems.',
                'academic_indicators': ['hardware courses', 'networking', 'systems installation', 'applied technical labs', 'practical projects'],
                'keywords': ['hardware', 'networking', 'systems', 'technical', 'installation', 'maintenance', 'infrastructure']
            },
            'investigative': {
                'name': 'Analytical Thinker',
                'traits': ['analytical', 'logical', 'research-oriented', 'problem-solving'],
                'careers': ['Data Scientist', 'AI/ML Engineer', 'Systems Analyst', 'Research Engineer', 'Software Architect'],
                'description': 'Analytical and research-focused. Excels in mathematics, algorithms, and complex problem-solving.',
                'academic_indicators': ['mathematics', 'algorithms', 'programming', 'data structures', 'machine learning', 'research projects', 'analytical thinking'],
                'keywords': ['data science', 'machine learning', 'algorithms', 'research', 'analytics', 'mathematics', 'statistics']
            },
            'artistic': {
                'name': 'Creative Innovator',
                'traits': ['creative', 'innovative', 'artistic', 'expressive'],
                'careers': ['UI/UX Designer', 'Game Developer', 'Digital Media Specialist', 'Creative Developer', 'Frontend Engineer'],
                'description': 'Creative and innovative approach to technology. Excels in design, multimedia, and creative coding.',
                'academic_indicators': ['UI/UX design', 'multimedia applications', 'creative coding', 'human-computer interaction', 'design principles', 'visual arts'],
                'keywords': ['design', 'creative', 'ui/ux', 'multimedia', 'visual', 'artistic', 'innovation', 'frontend']
            },
            'social': {
                'name': 'Collaborative Supporter',
                'traits': ['collaborative', 'supportive', 'communicative', 'helpful'],
                'careers': ['IT Support Specialist', 'Systems Trainer', 'Academic Tutor', 'Community IT Facilitator', 'Technical Writer'],
                'description': 'Collaborative and supportive approach. Excels in communication, training, and helping others.',
                'academic_indicators': ['communication-intensive subjects', 'teamwork-driven projects', 'IT support', 'training modules', 'group work', 'presentation skills'],
                'keywords': ['support', 'training', 'communication', 'collaboration', 'help', 'teaching', 'documentation']
            },
            'enterprising': {
                'name': 'Strategic Leader',
                'traits': ['leadership', 'strategic', 'entrepreneurial', 'persuasive'],
                'careers': ['IT Project Manager', 'Tech Entrepreneur', 'Product Manager', 'Team Lead', 'Business Analyst'],
                'description': 'Strategic and leadership-oriented. Excels in project management, entrepreneurship, and business planning.',
                'academic_indicators': ['project management', 'entrepreneurship subjects', 'software business planning', 'leadership tasks', 'business courses', 'management'],
                'keywords': ['management', 'leadership', 'entrepreneurship', 'strategy', 'business', 'project management', 'product']
            },
            'conventional': {
                'name': 'Methodical Organizer',
                'traits': ['organized', 'methodical', 'systematic', 'detail-oriented'],
                'careers': ['Database Administrator', 'Systems Auditor', 'QA Tester', 'Technical Writer', 'Compliance Specialist'],
                'description': 'Methodical and organized approach. Excels in database management, documentation, and structured processes.',
                'academic_indicators': ['database management', 'information systems', 'documentation', 'structured coding practices', 'quality assurance', 'compliance'],
                'keywords': ['database', 'documentation', 'quality assurance', 'compliance', 'organization', 'systems', 'audit']
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
            'grades': grades_data,
            'academic_metrics': academic_metrics,
            'subject_analysis': subject_analysis,
            'learning_archetype': learning_archetype,
            'skills': skills,
            'career_recommendations': career_recommendations,
            'analysis_timestamp': datetime.utcnow().isoformat()
        }
    
    def extract_grades_and_subjects(self, text: str) -> List[Dict[str, Any]]:
        """Extract grades and subjects from transcript text - Enhanced for PLM TOR format"""
        subjects = []
        seen_subjects = set()  # Track seen subjects to avoid duplicates
        
        # Split text into sections by semester headers
        semester_sections = self.split_text_by_semesters(text)
        
        for section_text, semester in semester_sections:
            # Enhanced patterns specifically for PLM TOR format
            grade_patterns = [
                # A) Course code + title + UNITS + GRADE
                (r'([A-Z]{2,4}\s+\d{4}(?:\.\d+[A-Z]?)?)\s+([A-Za-z\s,()]+?)\s+(\d{1,2})\s+(\d+\.\d{2})', 'units_then_grade'),
                (r'([A-Z]{2,4}\s+\d{4}\.\d+[A-Z]?)\s+([A-Za-z\s,()]+?)\s+(\d{1,2})\s+(\d+\.\d{2})', 'units_then_grade'),
                (r'([A-Z]{2,4}\s+\d{4})\s+([A-Za-z\s,()]+?)\s+(\d{1,2})\s+(\d+\.\d{2})', 'units_then_grade'),
                (r'([A-Z]{2,4}\s+\d{4}\.\d+[A-Z])\s+([A-Za-z\s,()]+?)\s+(\d{1,2})\s+(\d+\.\d{2})', 'units_then_grade'),
                # B) Course code + title + GRADE + UNITS (PLM TOR layout)
                (r'([A-Z]{2,4}\s+\d{4}(?:\.\d+[A-Z]?)?)\s+([A-Za-z\s,()]+?)\s+(\d+\.\d{2})\s+(\d{1,2})', 'grade_then_units'),
                (r'([A-Z]{2,4}\s+\d{4}\.\d+[A-Z]?)\s+([A-Za-z\s,()]+?)\s+(\d+\.\d{2})\s+(\d{1,2})', 'grade_then_units'),
                (r'([A-Z]{2,4}\s+\d{4})\s+([A-Za-z\s,()]+?)\s+(\d+\.\d{2})\s+(\d{1,2})', 'grade_then_units'),
                (r'([A-Z]{2,4}\s+\d{4}\.\d+[A-Z])\s+([A-Za-z\s,()]+?)\s+(\d+\.\d{2})\s+(\d{1,2})', 'grade_then_units'),
            ]
            
            # Process patterns in order (most specific first)
            for pattern, pattern_type in grade_patterns:
                matches = re.findall(pattern, section_text, re.IGNORECASE)
                for match in matches:
                    if len(match) == 4:
                        if pattern_type == 'units_then_grade':
                            course_code, course_title, units, grade = match
                        else:  # grade_then_units
                            course_code, course_title, grade, units = match
                        
                        # Clean and validate the data
                        course_code = course_code.strip()
                        course_title = course_title.strip()
                        
                        # Enhanced validation for PLM format
                        if self.is_valid_plm_course_code(course_code):
                            # Clean course title (fix OCR typos and remove extra spaces)
                            course_title = self.clean_course_title(course_title)
                            
                            # Create unique subject key
                            subject_key = f"{course_code}-{course_title}-{semester}"
                            
                            # Skip if we've already seen this subject
                            if subject_key in seen_subjects:
                                continue
                            
                            # Validate units and grade
                            units_num = self.parse_units(units)
                            grade_num = self.normalize_grade(grade)
                            
                            # Enhanced validation for PLM format
                            if self.is_valid_grade_data(units_num, grade_num):
                                seen_subjects.add(subject_key)
                                
                                # Determine course category based on course code
                                category = self.categorize_plm_course(course_code)
                                
                                subjects.append({
                                    'subject': f"{course_code} - {course_title}",
                                    'course_code': course_code,
                                    'units': units_num,
                                    'grade': grade_num,
                                    'semester': semester,
                                    'category': category
                                })
            
            # Fallback patterns for non-standard formats
            if not any(subject.get('semester') == semester for subject in subjects):
                fallback_patterns = [
                    # Pattern: Subject Name + Units + Grade
                    (r'([A-Z][a-zA-Z\s&()]+(?:I{1,3}|IV|V)?)\s+(\d{1,2})\s+(\d+\.\d{2})', 'fallback_format'),
                    # Pattern: Subject Name + Grade (assume 3 units)
                    (r'([A-Z][a-zA-Z\s&()]+(?:I{1,3}|IV|V)?)\s+(\d+\.\d{2})', 'fallback_format'),
                ]
                
                for pattern, pattern_type in fallback_patterns:
                    matches = re.findall(pattern, section_text, re.IGNORECASE)
                    for match in matches:
                        if len(match) == 3:
                            subject_name, units, grade = match
                            subject_key = f"{subject_name.strip()}-{semester}"
                            
                            if subject_key in seen_subjects:
                                continue
                            
                            seen_subjects.add(subject_key)
                            subjects.append({
                                'subject': subject_name.strip(),
                                'course_code': 'N/A',
                                'units': self.parse_units(units),
                                'grade': self.normalize_grade(grade),
                                'semester': semester,
                                'category': 'General'
                            })
                        elif len(match) == 2:
                            subject_name, grade = match
                            subject_key = f"{subject_name.strip()}-{semester}"
                            
                            if subject_key in seen_subjects:
                                continue
                            
                            seen_subjects.add(subject_key)
                            subjects.append({
                                'subject': subject_name.strip(),
                                'course_code': 'N/A',
                                'units': 3,  # Default units
                                'grade': self.normalize_grade(grade),
                                'semester': semester,
                                'category': 'General'
                            })
        
        # Do not fabricate data; return empty if nothing parsed
        
        return subjects
    
    def split_text_by_semesters(self, text: str) -> List[Tuple[str, str]]:
        """Split text into sections based on semester headers - Enhanced for PLM format"""
        sections = []
        
        # Enhanced patterns for PLM TOR semester headers
        semester_patterns = [
            # Pattern 1: "1st Semester, 2020-2021", "2nd Semester, 2021-2022"
            r'(\d+(?:st|nd|rd|th)\s+Semester,\s+\d{4}-\d{4})',
            # Pattern 2: "First Semester, 2020-2021", "Second Semester, 2021-2022"
            r'(First|Second|Third|Fourth)\s+Semester,\s+\d{4}-\d{4}',
            # Pattern 3: "MidYear Term, 2022-2023"
            r'(MidYear\s+Term,\s+\d{4}-\d{4})',
            # Pattern 4: Legacy format "First Year, First Semester"
            r'(First|Second|Third|Fourth)\s+(Year|Semester).*?(First|Second|Third|Fourth)?\s*(Year|Semester)?'
        ]
        
        # Find all semester headers using multiple patterns
        semester_matches = []
        for pattern in semester_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            semester_matches.extend(matches)
        
        # Sort matches by position
        semester_matches.sort(key=lambda x: x.start())
        
        if not semester_matches:
            # If no semester headers found, treat entire text as one section
            sections.append((text, 'N/A'))
        else:
            # Split text by semester headers
            for i, match in enumerate(semester_matches):
                semester_name = match.group(0).strip()
                
                if i == 0:
                    # First section: from start to first semester header
                    section_text = text[:match.start()]
                else:
                    # Middle sections: from previous header to current header
                    prev_match = semester_matches[i-1]
                    section_text = text[prev_match.end():match.start()]
                
                # Clean up the section text
                section_text = section_text.strip()
                if section_text:
                    sections.append((section_text, semester_name))
            
            # Last section: from last header to end
            if semester_matches:
                last_match = semester_matches[-1]
                last_section_text = text[last_match.end():].strip()
                if last_section_text and len(last_section_text) > 50:
                    sections.append((last_section_text, semester_matches[-1].group(0).strip()))
        
        return sections
    
    def create_sample_academic_data(self) -> List[Dict[str, Any]]:
        """Deprecated: samples removed to avoid non-real outputs."""
        return []
    
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
            return 2.5  # Default
    
    def is_valid_plm_course_code(self, course_code: str) -> bool:
        """Validate PLM course code format"""
        if not course_code or len(course_code) < 3:
            return False
        
        # Skip invalid patterns
        invalid_patterns = [
            'COURSE', 'CODE', 'TITLE', 'UNITS', 'GRADE', 'FINAL', 'COMPLETION',
            'DESCRIPTIVE', 'OF CREDIT', 'GRADES', 'FINAL', 'COMPLETION'
        ]
        
        course_code_upper = course_code.upper()
        for pattern in invalid_patterns:
            if pattern in course_code_upper:
                return False
        
        # Check for valid PLM course code patterns
        # ICC 0101, CET 0114.1, EIT 0211.1A, etc.
        plm_pattern = r'^[A-Z]{2,4}\s+\d{4}(?:\.\d+[A-Z]?)?$'
        return bool(re.match(plm_pattern, course_code.strip()))
    
    def is_valid_grade_data(self, units: int, grade: float) -> bool:
        """Validate units and grade data"""
        return (1 <= units <= 10 and 1.0 <= grade <= 5.0 and units > 0 and grade > 0)
    
    def categorize_plm_course(self, course_code: str) -> str:
        """Categorize PLM course based on course code"""
        if not course_code:
            return 'General'
        
        course_code = course_code.upper().strip()
        
        # IT/CS Major courses
        if course_code.startswith('ICC') or course_code.startswith('EIT'):
            return 'Major'
        # Mathematics courses
        elif course_code.startswith('CET') or course_code.startswith('MMW'):
            return 'Mathematics'
        # General Education courses
        elif course_code.startswith('STS') or course_code.startswith('AAP') or course_code.startswith('PCM'):
            return 'General Education'
        # Physical Education
        elif course_code.startswith('PED'):
            return 'Physical Education'
        # NSTP
        elif course_code.startswith('NSTP'):
            return 'NSTP'
        # Capstone/Project courses
        elif course_code.startswith('CAP'):
            return 'Capstone'
        else:
            return 'General'
    
    def clean_course_title(self, title: str) -> str:
        """Clean and fix common OCR errors in course titles"""
        title = title.strip()
        
        # Fix common OCR typos specific to PLM format
        title_fixes = {
            'rt Appreciation': 'Art Appreciation',
            'undamentals of Programming': 'Fundamentals of Programming',
            'oundation of Physical Activities': 'Foundation of Physical Activities',
            'Interdisiplinaryong Pagbasa at Pagsulat': 'Interdisciplinary Pagbasa at Pagsulat',
            'echnology and Society': 'Technology and Society',
            'ntroduction to Computing': 'Introduction to Computing',
            'eneral Chemistry': 'General Chemistry',
            'latform Technology': 'Platform Technology',
            'uantitative Methods': 'Quantitative Methods',
            'etworking 1': 'Networking 1',
            'apstone Project': 'Capstone Project',
            'uman Computer Interaction': 'Human Computer Interaction',
            'ata Structures': 'Data Structures',
            'lgorithms': 'Algorithms',
            'oftware Engineering': 'Software Engineering',
            'atabase Management': 'Database Management',
            'achine Learning': 'Machine Learning',
            'rtificial Intelligence': 'Artificial Intelligence',
            'eb Development': 'Web Development',
            'obile Application Development': 'Mobile Application Development',
            # Fix double letters from OCR
            'IIntroduction': 'Introduction',
            'GGeneral': 'General',
            'AArt': 'Art',
            'FFundamentals': 'Fundamentals',
            'GGeneral': 'General',
            'HHuman': 'Human',
            'PPlatform': 'Platform',
            'DData': 'Data',
            'QQuantitative': 'Quantitative',
            'DDatabase': 'Database',
            'SSoftware': 'Software',
            'MMachine': 'Machine',
            'AArtificial': 'Artificial',
            'WWeb': 'Web',
            'MMobile': 'Mobile',
            'CCloud': 'Cloud',
            'CCybersecurity': 'Cybersecurity'
        }
        
        for typo, correct in title_fixes.items():
            if typo in title:
                title = title.replace(typo, correct)
        
        # Remove any remaining OCR artifacts and normalize spacing
        title = re.sub(r'\s+', ' ', title)  # Multiple spaces to single space
        title = title.strip()
        
        return title
    
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
        """Identify learning archetype based on academic performance using RIASEC archetypes with percentages"""
        # Initialize scores for all 6 RIASEC archetypes
        archetype_scores = {
            'realistic': 0,
            'investigative': 0,
            'artistic': 0,
            'social': 0,
            'enterprising': 0,
            'conventional': 0
        }
        
        gpa = academic_metrics.get('gpa', 3.0)
        total_subjects = academic_metrics.get('subjects_count', 0)
        
        # Analyze subject performance patterns
        strong_categories = [cat for cat, data in subject_analysis.items() 
                           if data['average_grade'] <= 2.0]
        weak_categories = [cat for cat, data in subject_analysis.items() 
                          if data['average_grade'] > 3.0]
        
        # Enhanced scoring system for RIASEC archetypes
        
        # Realistic (Applied Practitioner) - Practical, hands-on, technical
        if 'engineering' in strong_categories:
            archetype_scores['realistic'] += 3
        if 'programming' in strong_categories:
            archetype_scores['realistic'] += 2
        if gpa <= 2.5:
            archetype_scores['realistic'] += 2  # Practical approach
        if total_subjects >= 6:
            archetype_scores['realistic'] += 1  # Systematic approach
        
        # Investigative (Analytical Thinker) - Analytical, research-oriented
        if gpa <= 1.75:
            archetype_scores['investigative'] += 3
        if 'mathematics' in strong_categories:
            archetype_scores['investigative'] += 3
        if 'data_science' in strong_categories:
            archetype_scores['investigative'] += 3
        if 'science' in strong_categories:
            archetype_scores['investigative'] += 2
        if 'programming' in strong_categories:
            archetype_scores['investigative'] += 2
        
        # Artistic (Creative Innovator) - Creative, innovative, expressive
        if 'design' in strong_categories:
            archetype_scores['artistic'] += 3
        if 'communication' in strong_categories:
            archetype_scores['artistic'] += 2
        if len(strong_categories) >= 3:
            archetype_scores['artistic'] += 2  # Diverse creative abilities
        if 'programming' in strong_categories:
            archetype_scores['artistic'] += 1  # Creative coding
        
        # Social (Collaborative Supporter) - Collaborative, supportive, communicative
        if 'communication' in strong_categories:
            archetype_scores['social'] += 3
        if 'business' in strong_categories:
            archetype_scores['social'] += 2
        if gpa <= 2.5:
            archetype_scores['social'] += 2  # Good interpersonal skills
        if total_subjects >= 5:
            archetype_scores['social'] += 1  # Collaborative approach
        
        # Enterprising (Strategic Leader) - Leadership, strategic, entrepreneurial
        if 'business' in strong_categories:
            archetype_scores['enterprising'] += 3
        if gpa <= 2.0:
            archetype_scores['enterprising'] += 2
        if total_subjects >= 8:
            archetype_scores['enterprising'] += 2  # Managing many subjects
        if len(strong_categories) >= 2:
            archetype_scores['enterprising'] += 2  # Leadership across domains
        
        # Conventional (Methodical Organizer) - Organized, methodical, systematic
        if 'data_science' in strong_categories:
            archetype_scores['conventional'] += 2
        if gpa <= 2.0:
            archetype_scores['conventional'] += 2
        if total_subjects >= 6:
            archetype_scores['conventional'] += 2  # Systematic approach
        if len(weak_categories) == 0:
            archetype_scores['conventional'] += 2  # Consistent performance
        if 'mathematics' in strong_categories:
            archetype_scores['conventional'] += 1
        
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
                archetype_percentages[archetype] = round(100 / 6, 1)
        
        # Determine primary archetype
        primary_archetype = max(archetype_scores, key=archetype_scores.get)
        
        # Get archetype details
        archetype_info = self.riasec_archetypes[primary_archetype]
        
        return {
            'primary_archetype': primary_archetype,
            'archetype_scores': archetype_scores,
            'archetype_percentages': archetype_percentages,
            'traits': archetype_info['traits'],
            'description': archetype_info['description'],
            'academic_indicators': archetype_info['academic_indicators'],
            'archetype_name': archetype_info['name']
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
        base_careers = self.riasec_archetypes[primary_archetype]['careers']
        
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
