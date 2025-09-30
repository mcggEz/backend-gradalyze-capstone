"""
Course-to-RIASEC Mapping System for BSIT Program
Based on comprehensive curriculum analysis for accurate archetype classification
"""

from typing import Dict, List, Tuple, Any
import json

class CourseRIASECMapper:
    """Maps courses to RIASEC archetypes based on curriculum analysis"""
    
    def __init__(self):
        # Comprehensive course-to-RIASEC mapping for BSIT program
        self.course_mapping = {
            # Year 1, Semester 1
            'STS 0002': {
                'primary': 'social',
                'secondary': 'investigative',
                'weight': 1.0,
                'justification': 'Encourages critical thinking about science\'s role in society and its impact on people.'
            },
            'AAP 0007': {
                'primary': 'artistic',
                'secondary': None,
                'weight': 1.0,
                'justification': 'Focuses on creativity, expression, and visual interpretation.'
            },
            'PCM 0006': {
                'primary': 'social',
                'secondary': 'enterprising',
                'weight': 1.0,
                'justification': 'Develops communication and presentation skills useful in teamwork and leadership.'
            },
            'MMW 0001': {
                'primary': 'investigative',
                'secondary': None,
                'weight': 1.0,
                'justification': 'Emphasizes logical reasoning and problem-solving.'
            },
            'IPP 0010': {
                'primary': 'social',
                'secondary': 'conventional',
                'weight': 1.0,
                'justification': 'Strengthens academic reading/writing; aligns with structured communication.'
            },
            'ICC 0101': {
                'primary': 'investigative',
                'secondary': 'conventional',
                'weight': 1.0,
                'justification': 'Builds logical and systematic foundations in IT.'
            },
            'ICC 0102': {
                'primary': 'investigative',
                'secondary': 'conventional',
                'weight': 1.0,
                'justification': 'Involves problem-solving and structured programming logic.'
            },
            'PED 0001': {
                'primary': 'realistic',
                'secondary': 'social',
                'weight': 0.8,
                'justification': 'Involves physical activity and collaboration in sports.'
            },
            'NSTP 01': {
                'primary': 'social',
                'secondary': 'enterprising',
                'weight': 0.8,
                'justification': 'Focuses on civic engagement, leadership, and teamwork.'
            },
            
            # Year 1, Semester 2
            'CET 0111': {
                'primary': 'investigative',
                'secondary': None,
                'weight': 1.0,
                'justification': 'Strengthens analytical and mathematical problem-solving skills.'
            },
            'CET 0114': {
                'primary': 'investigative',
                'secondary': 'realistic',
                'weight': 1.0,
                'justification': 'Combines scientific investigation with hands-on lab work.'
            },
            'EIT 0121': {
                'primary': 'artistic',
                'secondary': 'social',
                'weight': 1.0,
                'justification': 'Emphasizes user-centered design and usability principles.'
            },
            'EIT 0122': {
                'primary': 'investigative',
                'secondary': None,
                'weight': 1.0,
                'justification': 'Strengthens formal logic, proofs, and abstract reasoning.'
            },
            'EIT 0123': {
                'primary': 'artistic',
                'secondary': 'conventional',
                'weight': 1.0,
                'justification': 'Balances creative web design with technical implementation.'
            },
            'ICC 0103': {
                'primary': 'investigative',
                'secondary': 'conventional',
                'weight': 1.0,
                'justification': 'Builds on programming foundations, requiring logical structuring.'
            },
            'GTB 121': {
                'primary': 'social',
                'secondary': 'artistic',
                'weight': 0.8,
                'justification': 'Encourages cultural appreciation and reflective thinking.'
            },
            'PED 0013': {
                'primary': 'realistic',
                'secondary': 'social',
                'weight': 0.8,
                'justification': 'Physical activity with team participation.'
            },
            'NSTP 02': {
                'primary': 'social',
                'secondary': 'enterprising',
                'weight': 0.8,
                'justification': 'Builds leadership, civic responsibility, and social engagement.'
            },
            
            # Year 2, Semester 1
            'CET 0121': {
                'primary': 'investigative',
                'secondary': None,
                'weight': 1.0,
                'justification': 'Focuses on analytical and mathematical reasoning.'
            },
            'CET 0225': {
                'primary': 'investigative',
                'secondary': 'realistic',
                'weight': 1.0,
                'justification': 'Applies scientific and physical principles with hands-on lab components.'
            },
            'TCW 0005': {
                'primary': 'social',
                'secondary': 'enterprising',
                'weight': 0.8,
                'justification': 'Encourages global awareness, civic engagement, and critical reflection.'
            },
            'ICC 0104': {
                'primary': 'investigative',
                'secondary': 'conventional',
                'weight': 1.0,
                'justification': 'Involves structured problem-solving and abstract logical design.'
            },
            'EIT 0211': {
                'primary': 'investigative',
                'secondary': 'conventional',
                'weight': 1.0,
                'justification': 'Focuses on modular thinking and structured programming concepts.'
            },
            'PPC 122': {
                'primary': 'social',
                'secondary': 'artistic',
                'weight': 0.8,
                'justification': 'Engages with culture and creativity while fostering reflective understanding.'
            },
            'EIT ELECTIVE 1': {
                'primary': 'investigative',  # Default, varies by elective
                'secondary': None,
                'weight': 0.9,
                'justification': 'Specialized topics may align with Investigative, Artistic, or Enterprising traits.'
            },
            'PED 0054': {
                'primary': 'realistic',
                'secondary': 'social',
                'weight': 0.8,
                'justification': 'Physical activity requiring teamwork and coordination.'
            },
            
            # Year 2, Semester 2
            'UTS 0003': {
                'primary': 'social',
                'secondary': 'enterprising',
                'weight': 0.8,
                'justification': 'Focuses on personal growth, self-awareness, and interpersonal development.'
            },
            'RPH 0004': {
                'primary': 'social',
                'secondary': 'conventional',
                'weight': 0.8,
                'justification': 'Builds contextual understanding and systematic historical analysis.'
            },
            'EIT 0212A': {
                'primary': 'realistic',
                'secondary': 'conventional',
                'weight': 1.0,
                'justification': 'Hands-on systems knowledge requiring structured technical practice.'
            },
            'ICC 0105': {
                'primary': 'conventional',
                'secondary': 'investigative',
                'weight': 1.0,
                'justification': 'Emphasizes database organization, storage, and systematic data handling.'
            },
            'EIT 0221': {
                'primary': 'investigative',
                'secondary': None,
                'weight': 1.0,
                'justification': 'Applies mathematical/statistical tools for problem-solving.'
            },
            'EIT 0222': {
                'primary': 'realistic',
                'secondary': 'investigative',
                'weight': 1.0,
                'justification': 'Practical network setup and troubleshooting with technical problem-solving.'
            },
            'ENS 111': {
                'primary': 'investigative',
                'secondary': 'social',
                'weight': 0.8,
                'justification': 'Examines scientific and societal issues related to sustainability.'
            },
            'EIT ELECTIVE 2': {
                'primary': 'investigative',  # Default, varies by elective
                'secondary': None,
                'weight': 0.9,
                'justification': 'May align with technical (I/C), design (A), or managerial (E/S) fields.'
            },
            'PED 0074': {
                'primary': 'realistic',
                'secondary': 'social',
                'weight': 0.8,
                'justification': 'Physical activity that requires collaboration.'
            },
            
            # Year 3, Semester 1
            'ICC 0335': {
                'primary': 'investigative',
                'secondary': 'enterprising',
                'weight': 1.0,
                'justification': 'Involves exploring innovative IT trends and applying them to real-world contexts.'
            },
            'EIT 0311': {
                'primary': 'conventional',
                'secondary': 'investigative',
                'weight': 1.0,
                'justification': 'Focuses on structured data management, optimization, and complex queries.'
            },
            'EIT ELECTIVE 3': {
                'primary': 'investigative',  # Default, varies by elective
                'secondary': None,
                'weight': 0.9,
                'justification': 'Specialized electives can emphasize Investigative, Artistic, or Enterprising traits.'
            },
            'EIT 0312': {
                'primary': 'realistic',
                'secondary': 'investigative',
                'weight': 1.0,
                'justification': 'Requires hands-on configuration of networks and advanced troubleshooting.'
            },
            'LWR 0009': {
                'primary': 'social',
                'secondary': 'enterprising',
                'weight': 0.8,
                'justification': 'Encourages civic responsibility, leadership, and reflective learning from historical context.'
            },
            
            # Year 3, Semester 2
            'EIT 0321': {
                'primary': 'realistic',
                'secondary': 'conventional',
                'weight': 1.0,
                'justification': 'Involves system protection, security protocols, and structured compliance practices.'
            },
            'EIT 0322': {
                'primary': 'realistic',
                'secondary': 'conventional',
                'weight': 1.0,
                'justification': 'Hands-on integration of hardware/software systems with structured planning.'
            },
            'EIT 0323': {
                'primary': 'investigative',
                'secondary': 'conventional',
                'weight': 1.0,
                'justification': 'Combines different technologies into cohesive solutions, requiring logical integration.'
            },
            'ETH 0008': {
                'primary': 'social',
                'secondary': 'conventional',
                'weight': 0.8,
                'justification': 'Focuses on moral reasoning, professional practice, and systematic application of values.'
            },
            
            # Year 3, Summer
            'EIT 0331': {
                'primary': 'realistic',
                'secondary': 'conventional',
                'weight': 1.0,
                'justification': 'Continuation of system-level design and integration with structured methods.'
            },
            'CAP 0101': {
                'primary': 'enterprising',
                'secondary': 'investigative',
                'weight': 1.2,
                'justification': 'Requires innovation, teamwork, and research application to solve real-world IT problems.'
            },
            
            # Year 4, Semester 1
            'EIT ELECTIVE 4': {
                'primary': 'investigative',  # Default, varies by elective
                'secondary': None,
                'weight': 0.9,
                'justification': 'Can emphasize Investigative (research/technical), Artistic (design/UI), or Enterprising (management/innovation).'
            },
            'EIT ELECTIVE 5': {
                'primary': 'investigative',  # Default, varies by elective
                'secondary': None,
                'weight': 0.9,
                'justification': 'Same as above; mapping varies based on specialization.'
            },
            'EIT ELECTIVE 6': {
                'primary': 'investigative',  # Default, varies by elective
                'secondary': None,
                'weight': 0.9,
                'justification': 'Same as above; mapping varies based on specialization.'
            },
            'CAP 0102': {
                'primary': 'enterprising',
                'secondary': 'investigative',
                'weight': 1.2,
                'justification': 'Focuses on implementation, leadership, and teamwork in solving real-world IT challenges.'
            },
            
            # Year 4, Semester 2
            'IIP 0101A': {
                'primary': 'realistic',
                'secondary': 'enterprising',
                'weight': 1.1,
                'justification': 'Prepares students for workplace immersion, focusing on applied skills and professional practice.'
            },
            'IIP 0101.1': {
                'primary': 'realistic',
                'secondary': 'social',
                'weight': 1.1,
                'justification': 'Hands-on industry training requiring teamwork, adaptability, and leadership.'
            }
        }
        
        # RIASEC archetype definitions
        self.riasec_definitions = {
            'realistic': {
                'name': 'Applied Practitioner',
                'description': 'Practical, hands-on, technical problem-solving',
                'traits': ['hands-on', 'technical', 'practical', 'systematic']
            },
            'investigative': {
                'name': 'Analytical Thinker', 
                'description': 'Logical, analytical, research-oriented, problem-solving',
                'traits': ['analytical', 'logical', 'research', 'problem-solving']
            },
            'artistic': {
                'name': 'Creative Innovator',
                'description': 'Creative, innovative, design-oriented, expressive',
                'traits': ['creative', 'innovative', 'design', 'expressive']
            },
            'social': {
                'name': 'Collaborative Supporter',
                'description': 'People-oriented, helpful, communicative, team-focused',
                'traits': ['people-oriented', 'helpful', 'communicative', 'teamwork']
            },
            'enterprising': {
                'name': 'Strategic Leader',
                'description': 'Leadership, management, entrepreneurial, goal-oriented',
                'traits': ['leadership', 'management', 'entrepreneurial', 'goal-oriented']
            },
            'conventional': {
                'name': 'Methodical Organizer',
                'description': 'Organized, detail-oriented, systematic, structured',
                'traits': ['organized', 'detail-oriented', 'systematic', 'structured']
            }
        }
    
    def get_course_riasec_mapping(self, course_code: str) -> Dict[str, Any]:
        """Get RIASEC mapping for a specific course"""
        return self.course_mapping.get(course_code.upper(), {
            'primary': 'investigative',  # Default for unknown courses
            'secondary': None,
            'weight': 0.5,
            'justification': 'Unknown course - defaulting to investigative archetype'
        })
    
    def calculate_archetype_scores(self, grades_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate RIASEC archetype scores based on course grades and mappings
        
        Args:
            grades_data: List of course grades with course codes and scores
            
        Returns:
            Dictionary with RIASEC archetype percentages
        """
        archetype_scores = {
            'realistic': 0.0,
            'investigative': 0.0,
            'artistic': 0.0,
            'social': 0.0,
            'enterprising': 0.0,
            'conventional': 0.0
        }
        
        total_weighted_score = 0.0
        
        for course in grades_data:
            course_code = course.get('course_code', '').strip()
            grade = course.get('grade', 0)
            
            if not course_code or grade == 0:
                continue
                
            # Get course mapping
            mapping = self.get_course_riasec_mapping(course_code)
            
            # Convert grade to score (Philippine system: 1.0 = 100%, 5.0 = 0%)
            # Higher grades (lower numbers) = better performance
            grade_score = max(0, (5.0 - grade) / 4.0)  # Normalize to 0-1 scale
            
            # Apply course weight
            weighted_score = grade_score * mapping['weight']
            
            # Add to primary archetype
            primary_archetype = mapping['primary']
            archetype_scores[primary_archetype] += weighted_score
            
            # Add to secondary archetype if exists
            if mapping['secondary']:
                archetype_scores[mapping['secondary']] += weighted_score * 0.5  # Secondary gets half weight
            
            total_weighted_score += weighted_score
        
        # Normalize scores to percentages
        if total_weighted_score > 0:
            for archetype in archetype_scores:
                archetype_scores[archetype] = (archetype_scores[archetype] / total_weighted_score) * 100
        
        return archetype_scores
    
    def get_primary_archetype(self, archetype_scores: Dict[str, float]) -> str:
        """Get the primary archetype based on highest score"""
        return max(archetype_scores.items(), key=lambda x: x[1])[0]
    
    def get_archetype_analysis(self, grades_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get comprehensive archetype analysis based on course grades
        
        Args:
            grades_data: List of course grades
            
        Returns:
            Complete archetype analysis with scores, primary archetype, and insights
        """
        # Calculate archetype scores
        archetype_scores = self.calculate_archetype_scores(grades_data)
        
        # Get primary archetype
        primary_archetype = self.get_primary_archetype(archetype_scores)
        
        # Get archetype definition
        primary_definition = self.riasec_definitions[primary_archetype]
        
        # Sort archetypes by score for ranking
        sorted_archetypes = sorted(archetype_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Generate insights
        insights = self._generate_archetype_insights(archetype_scores, grades_data)
        
        return {
            'primary_archetype': primary_archetype,
            'archetype_name': primary_definition['name'],
            'archetype_description': primary_definition['description'],
            'archetype_traits': primary_definition['traits'],
            'archetype_scores': archetype_scores,
            'archetype_ranking': sorted_archetypes,
            'insights': insights,
            'total_courses_analyzed': len(grades_data),
            'analysis_method': 'course_riasec_mapping'
        }
    
    def _generate_archetype_insights(self, archetype_scores: Dict[str, float], grades_data: List[Dict[str, Any]]) -> List[str]:
        """Generate insights based on archetype analysis"""
        insights = []
        
        # Find top 3 archetypes
        top_archetypes = sorted(archetype_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Primary archetype insight
        primary = top_archetypes[0]
        primary_name = self.riasec_definitions[primary[0]]['name']
        insights.append(f"Your primary learning archetype is {primary_name} ({primary[1]:.1f}%), indicating strong {self.riasec_definitions[primary[0]]['description'].lower()} tendencies.")
        
        # Secondary archetype insight
        if len(top_archetypes) > 1 and top_archetypes[1][1] > 15:  # Only mention if significant
            secondary = top_archetypes[1]
            secondary_name = self.riasec_definitions[secondary[0]]['name']
            insights.append(f"You also show strong {secondary_name} characteristics ({secondary[1]:.1f}%), suggesting a balanced learning approach.")
        
        # Performance insight
        total_courses = len(grades_data)
        if total_courses > 0:
            avg_grade = sum(course.get('grade', 0) for course in grades_data) / total_courses
            if avg_grade <= 2.0:
                insights.append("Your strong academic performance across diverse subjects demonstrates excellent learning adaptability.")
            elif avg_grade <= 3.0:
                insights.append("Your consistent academic performance shows good learning potential with room for growth in specific areas.")
            else:
                insights.append("Focus on improving performance in core subjects to better align with your learning archetype.")
        
        return insights

# Helper function for easy integration
def analyze_student_archetype(grades_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze student archetype using course-based RIASEC mapping
    
    Args:
        grades_data: List of course grades with course_code and grade fields
        
    Returns:
        Complete archetype analysis
    """
    mapper = CourseRIASECMapper()
    return mapper.get_archetype_analysis(grades_data)
