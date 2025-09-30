"""
Gemini AI Integration for Company Recommendations and Job Openings
Uses Gemini AI to provide personalized company and job recommendations
"""

from typing import Dict, List, Any, Optional
import json
import os
import google.generativeai as genai
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
import re

class GeminiRecommendationEngine:
    """Gemini AI-powered recommendation system for companies and jobs"""
    
    def __init__(self):
        # Configure Gemini API - REQUIRED
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required but not found in environment variables")
        
        try:
            genai.configure(api_key=api_key)
            # Use the latest stable model
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            print("✅ Gemini AI configured successfully")
        except Exception as e:
            print(f"⚠️ Gemini AI not available, will use fallback: {e}")
            self.model = None
        
    
    def generate_company_recommendations(self, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate company recommendations using Gemini AI
        
        Args:
            user_profile: User's academic profile with archetype and career data
            
        Returns:
            List of recommended companies with details
        """
        if not self.model:
            raise ValueError("Gemini AI model is required but not available. Please configure GEMINI_API_KEY.")
            
        try:
            # Simple prompt for Gemini
            archetype = user_profile.get('primary_archetype', 'investigative')
            course = user_profile.get('course', 'BS Information Technology')
            
            prompt = f"""
            Recommend 20 CURRENT and REAL companies in the Philippines for a {course} student with {archetype} personality type.
            
            Requirements:
            - Use REAL, CURRENT company names (not generic placeholders)
            - Include ACTUAL current job roles and positions available
            - Provide REAL locations in the Philippines
            - Match scores should vary realistically (75-95%)
            - Include diverse company types (multinational, local tech, startup, fintech, etc.)
            - Focus on companies actively hiring in 2024-2025
            - Include current industry trends and technologies
            - Mention recent company growth and opportunities
            
            Return as JSON array:
            [
                {{
                    "name": "Current Real Company Name",
                    "category": "multinational",
                    "match_score": 92,
                    "reasoning": "Specific reason why this current company fits the student's profile and current market trends",
                    "location": "Makati City, Philippines",
                    "website": "https://realcompany.com",
                    "career_page": "https://realcompany.com/careers",
                    "job_roles": ["Software Engineer", "Data Analyst", "IT Consultant", "Cloud Engineer"],
                    "company_size": "5000+ employees",
                    "industry": "Technology",
                    "recent_growth": "Expanding AI/ML teams in 2024",
                    "hiring_status": "Actively hiring"
                }}
            ]
            """
            
            response = self.model.generate_content(prompt)
            
            # Clean the response text to extract JSON
            response_text = response.text.strip()
            
            # Try to find JSON array in the response
            if '[' in response_text and ']' in response_text:
                start = response_text.find('[')
                end = response_text.rfind(']') + 1
                json_text = response_text[start:end]
            else:
                json_text = response_text
            
            print(f"DEBUG: Gemini response: {response_text[:200]}...")
            print(f"DEBUG: Extracted JSON: {json_text[:200]}...")
            
            result = json.loads(json_text)
            
            return result[:20]  # Return top 20
            
        except Exception as e:
            print(f"Error generating company recommendations: {e}")
            raise e
    
    def generate_job_openings(self, user_profile: Dict[str, Any], companies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate job openings using Gemini AI
        
        Args:
            user_profile: User's academic profile
            companies: List of recommended companies
            
        Returns:
            List of job openings with links
        """
        if not self.model:
            raise ValueError("Gemini AI model is required but not available. Please configure GEMINI_API_KEY.")
            
        try:
            # Simple prompt for Gemini
            archetype = user_profile.get('primary_archetype', 'investigative')
            company_names = [c['name'] for c in companies[:5]]
            
            prompt = f"""
            Suggest 10 CURRENT and REAL entry-level job openings in the Philippines for a {archetype} personality type at these companies: {', '.join(company_names)}
            
            Requirements:
            - Use REAL, CURRENT job titles (not generic placeholders)
            - Provide ACTUAL salary ranges for Philippines market (2024-2025 rates)
            - Include REAL job descriptions and requirements
            - Use ACTUAL company career page URLs
            - Use RECENT posted dates (within last 3 months)
            - Match scores should vary realistically (70-95%)
            - Include diverse job types (remote, hybrid, on-site)
            - Focus on entry-level positions for fresh graduates
            
            Return as JSON array:
            [
                {{
                    "title": "Current Real Job Title",
                    "company": "Real Company Name",
                    "location": "Real City, Philippines",
                    "employment_type": "Full-time",
                    "experience_level": "Entry-level",
                    "salary_range": "PHP 35,000 - 50,000",
                    "description": "Current detailed job description with specific responsibilities and recent requirements",
                    "requirements": ["Bachelor's degree in IT/CS", "Programming skills", "Problem-solving ability", "Recent technologies"],
                    "benefits": ["Health insurance", "13th month pay", "Training opportunities", "Remote work options"],
                    "application_url": "https://realcompany.com/careers/current-job-opening",
                    "posted_date": "2024-12-15",
                    "match_score": 88,
                    "reasoning": "Specific reason why this current job matches the student's profile and skills"
                }}
            ]
            """
            
            response = self.model.generate_content(prompt)
            
            # Clean the response text to extract JSON
            response_text = response.text.strip()
            
            # Try to find JSON array in the response
            if '[' in response_text and ']' in response_text:
                start = response_text.find('[')
                end = response_text.rfind(']') + 1
                json_text = response_text[start:end]
            else:
                json_text = response_text
            
            print(f"DEBUG: Gemini job response: {response_text[:200]}...")
            print(f"DEBUG: Extracted job JSON: {json_text[:200]}...")
            
            result = json.loads(json_text)
            
            return result[:10]  # Return top 10
            
        except Exception as e:
            print(f"Error generating job openings: {e}")
            raise e
    

# Helper function for easy integration
def get_company_recommendations(user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Get company recommendations using Gemini AI
    
    Args:
        user_profile: User's academic profile
        
    Returns:
        List of recommended companies
    """
    try:
        engine = GeminiRecommendationEngine()
        return engine.generate_company_recommendations(user_profile)
    except Exception as e:
        print(f"Error getting company recommendations: {e}")
        return []

def get_job_openings(user_profile: Dict[str, Any], companies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Get job openings using Gemini AI
    
    Args:
        user_profile: User's academic profile
        companies: List of recommended companies
        
    Returns:
        List of job openings
    """
    try:
        engine = GeminiRecommendationEngine()
        return engine.generate_job_openings(user_profile, companies)
    except Exception as e:
        print(f"Error getting job openings: {e}")
        return []
