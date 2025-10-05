import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import numpy as np


class CertificateAnalyzer:
    """Analyze certificates to extract keywords and enhance career/archetype analysis"""
    
    def __init__(self):
        # Certificate keyword mapping to career paths and personality traits
        self.certificate_keywords = {
            # Technical Skills Certificates
            'programming': {
                'keywords': ['python', 'java', 'javascript', 'programming', 'coding', 'software development', 'web development', 'mobile development', 'api development'],
                'career_boost': ['Software Engineer', 'Full Stack Developer', 'Mobile Developer', 'API Developer', 'DevOps Engineer'],
                'archetype_boost': ['investigative', 'realistic'],
                'weight': 0.8
            },
            'data_science': {
                'keywords': ['data science', 'machine learning', 'artificial intelligence', 'analytics', 'statistics', 'data analysis', 'big data', 'sql', 'pandas', 'numpy'],
                'career_boost': ['Data Scientist', 'Machine Learning Engineer', 'Data Analyst', 'Business Intelligence Analyst', 'AI Engineer'],
                'archetype_boost': ['investigative', 'conventional'],
                'weight': 0.9
            },
            'cloud_computing': {
                'keywords': ['aws', 'azure', 'google cloud', 'cloud computing', 'devops', 'kubernetes', 'docker', 'microservices', 'serverless'],
                'career_boost': ['Cloud Engineer', 'DevOps Engineer', 'Solutions Architect', 'Cloud Security Engineer', 'Site Reliability Engineer'],
                'archetype_boost': ['realistic', 'conventional'],
                'weight': 0.8
            },
            'cybersecurity': {
                'keywords': ['cybersecurity', 'information security', 'ethical hacking', 'penetration testing', 'security audit', 'risk assessment', 'compliance', 'gdpr', 'iso 27001'],
                'career_boost': ['Cybersecurity Analyst', 'Security Engineer', 'Penetration Tester', 'Security Consultant', 'Compliance Officer'],
                'archetype_boost': ['investigative', 'conventional'],
                'weight': 0.9
            },
            'project_management': {
                'keywords': ['project management', 'pmp', 'agile', 'scrum', 'kanban', 'leadership', 'team management', 'stakeholder management', 'risk management'],
                'career_boost': ['Project Manager', 'Product Manager', 'Scrum Master', 'Program Manager', 'Operations Manager'],
                'archetype_boost': ['enterprising', 'social'],
                'weight': 0.7
            },
            'ui_ux_design': {
                'keywords': ['ui design', 'ux design', 'user experience', 'user interface', 'figma', 'adobe', 'prototyping', 'wireframing', 'usability testing'],
                'career_boost': ['UI/UX Designer', 'Product Designer', 'User Researcher', 'Interaction Designer', 'Visual Designer'],
                'archetype_boost': ['artistic', 'social'],
                'weight': 0.8
            },
            'digital_marketing': {
                'keywords': ['digital marketing', 'seo', 'sem', 'social media marketing', 'content marketing', 'email marketing', 'analytics', 'google ads', 'facebook ads'],
                'career_boost': ['Digital Marketing Specialist', 'SEO Specialist', 'Content Marketing Manager', 'Social Media Manager', 'Marketing Analyst'],
                'archetype_boost': ['enterprising', 'artistic'],
                'weight': 0.7
            },
            'leadership': {
                'keywords': ['leadership', 'team leadership', 'management', 'mentoring', 'coaching', 'public speaking', 'presentation', 'communication', 'negotiation'],
                'career_boost': ['Team Lead', 'Engineering Manager', 'Technical Lead', 'Department Head', 'Director'],
                'archetype_boost': ['enterprising', 'social'],
                'weight': 0.6
            },
            'entrepreneurship': {
                'keywords': ['entrepreneurship', 'startup', 'business development', 'innovation', 'venture capital', 'fundraising', 'business plan', 'market research'],
                'career_boost': ['Entrepreneur', 'Startup Founder', 'Business Development Manager', 'Innovation Manager', 'Venture Capitalist'],
                'archetype_boost': ['enterprising', 'artistic'],
                'weight': 0.8
            },
            'research': {
                'keywords': ['research', 'academic research', 'scientific method', 'data collection', 'analysis', 'publication', 'peer review', 'methodology'],
                'career_boost': ['Research Scientist', 'Research Engineer', 'Academic Researcher', 'Research Analyst', 'Data Scientist'],
                'archetype_boost': ['investigative', 'conventional'],
                'weight': 0.9
            }
        }
        
        # Personality trait keywords from certificates
        self.personality_keywords = {
            'realistic': ['hands-on', 'technical', 'practical', 'implementation', 'building', 'construction', 'maintenance'],
            'investigative': ['analysis', 'research', 'problem-solving', 'logical', 'systematic', 'methodical', 'scientific'],
            'artistic': ['creative', 'design', 'innovation', 'artistic', 'aesthetic', 'visual', 'imagination', 'expression'],
            'social': ['communication', 'teaching', 'helping', 'collaboration', 'teamwork', 'mentoring', 'support', 'service'],
            'enterprising': ['leadership', 'management', 'entrepreneurship', 'sales', 'marketing', 'negotiation', 'influence', 'persuasion'],
            'conventional': ['organization', 'systematic', 'detail-oriented', 'compliance', 'regulation', 'documentation', 'process', 'structure']
        }
    
    def analyze_certificate(self, certificate_text: str) -> Dict[str, Any]:
        """Analyze certificate text and extract relevant keywords and boosts"""
        
        if not certificate_text or not certificate_text.strip():
            return {
                'certificate_analysis': {},
                'career_boosts': {},
                'archetype_boosts': {},
                'extracted_keywords': [],
                'confidence_score': 0.0
            }
        
        # Clean and normalize text
        text = certificate_text.lower().strip()
        
        # Extract keywords and calculate boosts
        career_boosts = {}
        archetype_boosts = {}
        extracted_keywords = []
        confidence_scores = []
        
        # Analyze each certificate category
        for category, data in self.certificate_keywords.items():
            keyword_matches = []
            
            # Check for keyword matches
            for keyword in data['keywords']:
                if keyword.lower() in text:
                    keyword_matches.append(keyword)
                    extracted_keywords.append(keyword)
            
            if keyword_matches:
                # Calculate confidence based on keyword matches
                confidence = min(len(keyword_matches) / len(data['keywords']), 1.0) * data['weight']
                confidence_scores.append(confidence)
                
                # Apply career boosts
                for career in data['career_boost']:
                    if career not in career_boosts:
                        career_boosts[career] = 0
                    career_boosts[career] += confidence * 0.01  # 1% boost per match
                
                # Apply archetype boosts
                for archetype in data['archetype_boost']:
                    if archetype not in archetype_boosts:
                        archetype_boosts[archetype] = 0
                    archetype_boosts[archetype] += confidence * 0.01  # 1% boost per match
        
        # Analyze personality keywords
        personality_boosts = {}
        for trait, keywords in self.personality_keywords.items():
            matches = sum(1 for keyword in keywords if keyword.lower() in text)
            if matches > 0:
                personality_boosts[trait] = min(matches * 0.005, 0.02)  # Max 2% boost per trait
        
        # Merge personality boosts with archetype boosts
        for trait, boost in personality_boosts.items():
            if trait not in archetype_boosts:
                archetype_boosts[trait] = 0
            archetype_boosts[trait] += boost
        
        # Calculate overall confidence
        overall_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
        
        return {
            'certificate_analysis': {
                'total_keywords_found': len(extracted_keywords),
                'categories_identified': len(confidence_scores),
                'confidence_scores': confidence_scores
            },
            'career_boosts': career_boosts,
            'archetype_boosts': archetype_boosts,
            'extracted_keywords': list(set(extracted_keywords)),
            'confidence_score': overall_confidence
        }
    
    def extract_certificate_text(self, certificate_path: str) -> str:
        """Extract text from certificate document (PDF, image, etc.)"""
        try:
            import pdfplumber
            import io
            
            # For now, assume it's a PDF - can be extended for images
            with pdfplumber.open(certificate_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text.strip()
        except Exception as e:
            print(f"Error extracting certificate text: {e}")
            return ""
    
    def combine_with_tor_analysis(self, tor_analysis: Dict[str, Any], certificate_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Combine TOR analysis with certificate analysis for enhanced results"""
        
        # Get original career scores from TOR
        original_career_scores = tor_analysis.get('career_forecast', {}).get('career_scores', {})
        if not original_career_scores:
            original_career_scores = tor_analysis.get('career_forecast', {})
        
        # Get original archetype scores from TOR
        original_archetype_scores = tor_analysis.get('learning_archetype', {}).get('archetype_percentages', {})
        if not original_archetype_scores:
            original_archetype_scores = tor_analysis.get('archetype_scores', {})
        
        # Apply certificate boosts
        enhanced_career_scores = original_career_scores.copy()
        certificate_career_boosts = certificate_analysis.get('career_boosts', {})
        
        for career, boost in certificate_career_boosts.items():
            if career in enhanced_career_scores:
                enhanced_career_scores[career] = min(enhanced_career_scores[career] + boost, 1.0)
            else:
                enhanced_career_scores[career] = boost
        
        # Apply archetype boosts
        enhanced_archetype_scores = original_archetype_scores.copy()
        certificate_archetype_boosts = certificate_analysis.get('archetype_boosts', {})
        
        for archetype, boost in certificate_archetype_boosts.items():
            if archetype in enhanced_archetype_scores:
                enhanced_archetype_scores[archetype] = min(enhanced_archetype_scores[archetype] + boost, 1.0)
            else:
                enhanced_archetype_scores[archetype] = boost
        
        # Normalize archetype scores to sum to 100%
        total_archetype = sum(enhanced_archetype_scores.values())
        if total_archetype > 0:
            for archetype in enhanced_archetype_scores:
                enhanced_archetype_scores[archetype] = (enhanced_archetype_scores[archetype] / total_archetype) * 100
        
        # Create enhanced analysis
        enhanced_analysis = tor_analysis.copy()
        
        # Update career forecast
        if 'career_forecast' in enhanced_analysis:
            enhanced_analysis['career_forecast']['career_scores'] = enhanced_career_scores
            enhanced_analysis['career_forecast']['certificate_enhanced'] = True
            enhanced_analysis['career_forecast']['certificate_boosts'] = certificate_career_boosts
        
        # Update archetype analysis
        if 'learning_archetype' in enhanced_analysis:
            enhanced_analysis['learning_archetype']['archetype_percentages'] = enhanced_archetype_scores
            enhanced_analysis['learning_archetype']['certificate_enhanced'] = True
            enhanced_analysis['learning_archetype']['certificate_boosts'] = certificate_archetype_boosts
        
        # Add certificate analysis metadata
        enhanced_analysis['certificate_enhancement'] = {
            'certificate_analysis': certificate_analysis,
            'enhancement_applied': True,
            'enhancement_timestamp': datetime.utcnow().isoformat()
        }
        
        return enhanced_analysis


# Helper function for easy integration
def analyze_certificate_text(certificate_text: str) -> Dict[str, Any]:
    """
    Analyze certificate text and return enhancement data
    
    Args:
        certificate_text: Extracted text from certificate document
        
    Returns:
        Certificate analysis results
    """
    analyzer = CertificateAnalyzer()
    return analyzer.analyze_certificate(certificate_text)


def enhance_analysis_with_certificates(tor_analysis: Dict[str, Any], certificate_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Enhance TOR analysis with multiple certificate analyses
    
    Args:
        tor_analysis: Original TOR analysis results
        certificate_analyses: List of certificate analysis results
        
    Returns:
        Enhanced analysis combining TOR and certificate data
    """
    analyzer = CertificateAnalyzer()
    
    # Combine all certificate analyses
    combined_certificate_analysis = {
        'career_boosts': {},
        'archetype_boosts': {},
        'extracted_keywords': [],
        'confidence_score': 0.0
    }
    
    for cert_analysis in certificate_analyses:
        # Merge career boosts
        for career, boost in cert_analysis.get('career_boosts', {}).items():
            if career not in combined_certificate_analysis['career_boosts']:
                combined_certificate_analysis['career_boosts'][career] = 0
            combined_certificate_analysis['career_boosts'][career] += boost
        
        # Merge archetype boosts
        for archetype, boost in cert_analysis.get('archetype_boosts', {}).items():
            if archetype not in combined_certificate_analysis['archetype_boosts']:
                combined_certificate_analysis['archetype_boosts'][archetype] = 0
            combined_certificate_analysis['archetype_boosts'][archetype] += boost
        
        # Merge keywords
        combined_certificate_analysis['extracted_keywords'].extend(cert_analysis.get('extracted_keywords', []))
        
        # Average confidence
        combined_certificate_analysis['confidence_score'] += cert_analysis.get('confidence_score', 0)
    
    # Average the confidence score
    if certificate_analyses:
        combined_certificate_analysis['confidence_score'] /= len(certificate_analyses)
    
    # Remove duplicate keywords
    combined_certificate_analysis['extracted_keywords'] = list(set(combined_certificate_analysis['extracted_keywords']))
    
    # Apply enhancements
    return analyzer.combine_with_tor_analysis(tor_analysis, combined_certificate_analysis)
