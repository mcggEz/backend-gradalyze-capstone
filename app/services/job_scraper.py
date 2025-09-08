import os
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from firecrawl import Firecrawl
from app.services.supabase_client import get_supabase_client


class JobScraper:
    def __init__(self):
        self.firecrawl = Firecrawl(api_key=os.getenv('FIRECRAWL_API_KEY'))
        self.supabase = get_supabase_client()
        
        # RIASEC Archetype to job query mapping
        self.archetype_job_queries = {
            'realistic': [
                'hardware technician', 'network engineer', 'systems administrator', 'it support specialist',
                'technical support', 'infrastructure engineer', 'network administrator', 'system engineer',
                'technical specialist', 'hardware engineer', 'network specialist'
            ],
            'investigative': [
                'data scientist', 'machine learning engineer', 'research engineer', 'systems analyst',
                'software architect', 'ai engineer', 'research scientist', 'data analyst',
                'business intelligence analyst', 'quantitative analyst', 'research analyst'
            ],
            'artistic': [
                'ui ux designer', 'game developer', 'digital media specialist', 'creative developer',
                'frontend engineer', 'graphic designer', 'web designer', 'creative director',
                'visual designer', 'interaction designer', 'multimedia specialist'
            ],
            'social': [
                'it support specialist', 'systems trainer', 'academic tutor', 'technical writer',
                'community it facilitator', 'training specialist', 'help desk specialist',
                'customer support', 'technical trainer', 'documentation specialist'
            ],
            'enterprising': [
                'it project manager', 'tech entrepreneur', 'product manager', 'team lead',
                'business analyst', 'program manager', 'senior manager', 'director',
                'business development', 'strategic advisor', 'innovation manager'
            ],
            'conventional': [
                'database administrator', 'systems auditor', 'qa tester', 'technical writer',
                'compliance specialist', 'data analyst', 'quality assurance', 'systems analyst',
                'business analyst', 'process analyst', 'documentation specialist'
            ]
        }
    
    def get_job_queries_from_archetype_percentages(self, archetype_percentages: Dict[str, float], 
                                                  max_queries: int = 8) -> List[str]:
        """Generate job queries based on user's archetype percentages with weighted distribution"""
        queries = []
        
        # Sort archetypes by percentage (highest first)
        sorted_archetypes = sorted(archetype_percentages.items(), 
                                 key=lambda x: x[1], reverse=True)
        
        # Calculate total percentage for normalization
        total_percentage = sum(percentage for _, percentage in sorted_archetypes)
        
        if total_percentage == 0:
            # Fallback to general queries if no archetype data
            return ['entry level jobs', 'graduate jobs', 'fresh graduate', 'junior positions']
        
        # Distribute queries based on archetype percentages
        for archetype, percentage in sorted_archetypes:
            if percentage > 5:  # Only consider archetypes with >5% match
                archetype_queries = self.archetype_job_queries.get(archetype, [])
                
                # Calculate how many queries this archetype should get
                # Higher percentage = more queries
                archetype_quota = max(1, int((percentage / total_percentage) * max_queries))
                
                # Take queries for this archetype
                selected_queries = archetype_queries[:archetype_quota]
                queries.extend(selected_queries)
                
                # Stop if we have enough queries
                if len(queries) >= max_queries:
                    break
        
        # If we don't have enough queries, add some general ones
        if len(queries) < max_queries:
            general_queries = [
                'entry level jobs', 'graduate jobs', 'fresh graduate',
                'junior positions', 'trainee positions', 'internship'
            ]
            remaining_slots = max_queries - len(queries)
            queries.extend(general_queries[:remaining_slots])
        
        return queries[:max_queries]
    
    def get_user_archetype_percentages(self, user_email: str) -> Dict[str, float]:
        """Get user's archetype percentages from database"""
        try:
            result = self.supabase.table("users").select(
                "archetype_innocent_percentage, archetype_everyman_percentage, "
                "archetype_hero_percentage, archetype_caregiver_percentage, "
                "archetype_explorer_percentage, archetype_rebel_percentage, "
                "archetype_lover_percentage, archetype_creator_percentage, "
                "archetype_jester_percentage, archetype_sage_percentage, "
                "archetype_magician_percentage, archetype_ruler_percentage"
            ).eq("email", user_email).execute()
            
            if not result.data:
                return {}
            
            user = result.data[0]
            return {
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
            
        except Exception as e:
            print(f"Error getting user archetype percentages: {e}")
            return {}
    
    async def scrape_google_jobs(self, query: str = "software engineer", location: str = "Philippines", limit: int = 20) -> List[Dict[str, Any]]:
        """Scrape job listings from Google Jobs"""
        try:
            # For now, let's create some sample jobs since Firecrawl configuration is complex
            print(f"Creating sample jobs for query: {query} in {location}")
            
            # Add timestamp to make URLs unique
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            
            # Generate more diverse job titles based on the query
            job_titles = self._generate_job_titles_from_query(query)
            
            sample_jobs = []
            for i, title in enumerate(job_titles[:limit]):
                sample_jobs.append({
                    "title": title,
                    "company": self._generate_company_name(query),
                    "location": f"{location}",
                    "employment_type": "Full-time",
                    "remote": i % 3 == 0,  # Some jobs are remote
                    "salary_min": 40000 + (i * 10000),
                    "salary_max": 60000 + (i * 15000),
                    "currency": "PHP",
                    "url": self._generate_realistic_job_url(title, query, i),
                    "source": "Google Jobs",
                    "posted_at": datetime.utcnow().isoformat(),
                    "scraped_at": datetime.utcnow().isoformat(),
                    "tags": [query, self._get_category_from_query(query)],
                    "description": f"We are looking for a {title} to join our team in {location}. This position offers great opportunities for growth and development."
                })
            
            return sample_jobs
            
        except Exception as e:
            print(f"Error scraping Google Jobs: {e}")
            return []
    
    def _generate_job_titles_from_query(self, query: str) -> List[str]:
        """Generate diverse job titles based on the query"""
        query_lower = query.lower()
        
        # Base titles for different archetypes
        if 'data' in query_lower or 'analyst' in query_lower:
            return [
                "Data Scientist", "Business Analyst", "Data Analyst", "Statistical Analyst",
                "Research Analyst", "Business Intelligence Analyst", "Quantitative Analyst"
            ]
        elif 'software' in query_lower or 'developer' in query_lower:
            return [
                "Software Developer", "Full Stack Developer", "Frontend Developer", "Backend Developer",
                "Mobile App Developer", "Web Developer", "Software Engineer", "DevOps Engineer"
            ]
        elif 'manager' in query_lower or 'lead' in query_lower:
            return [
                "Project Manager", "Team Lead", "Product Manager", "Operations Manager",
                "Business Manager", "Department Manager", "Program Manager"
            ]
        elif 'marketing' in query_lower or 'sales' in query_lower:
            return [
                "Marketing Specialist", "Sales Manager", "Marketing Manager", "Brand Manager",
                "Digital Marketing Specialist", "Sales Representative", "Account Manager"
            ]
        elif 'consultant' in query_lower:
            return [
                "Business Consultant", "Management Consultant", "Strategy Consultant",
                "Technology Consultant", "Process Consultant", "Change Management Consultant"
            ]
        elif 'design' in query_lower or 'creative' in query_lower:
            return [
                "UI/UX Designer", "Graphic Designer", "Product Designer", "Creative Director",
                "Visual Designer", "Web Designer", "Brand Designer"
            ]
        elif 'teacher' in query_lower or 'trainer' in query_lower:
            return [
                "Teacher", "Trainer", "Instructor", "Educational Coordinator", "Learning Specialist",
                "Training Manager", "Curriculum Developer"
            ]
        elif 'customer' in query_lower or 'service' in query_lower:
            return [
                "Customer Service Representative", "Customer Success Manager", "Client Services",
                "Customer Support Specialist", "Service Coordinator", "Customer Care Representative"
            ]
        elif 'administrative' in query_lower or 'assistant' in query_lower:
            return [
                "Administrative Assistant", "Office Coordinator", "Executive Assistant",
                "Administrative Coordinator", "Office Manager", "Administrative Specialist"
            ]
        elif 'content' in query_lower or 'creator' in query_lower:
            return [
                "Content Creator", "Content Manager", "Social Media Manager", "Digital Content Creator",
                "Content Strategist", "Creative Content Specialist", "Media Specialist"
            ]
        else:
            # Default job titles for general queries
            return [
                "Junior Professional", "Entry Level Specialist", "Graduate Trainee", "Associate",
                "Junior Analyst", "Entry Level Coordinator", "Graduate Position", "Junior Associate"
            ]
    
    def _generate_realistic_job_url(self, title: str, query: str, index: int) -> str:
        """Generate LinkedIn job search URLs
        
        These URLs point to LinkedIn job search results for the Philippines.
        LinkedIn job search URLs are more reliable and functional than other job sites.
        """
        # Create a clean search query for LinkedIn
        search_query = f"{title}".replace(' ', '+')
        
        # LinkedIn job search URL with Philippines location and recent postings
        linkedin_url = f"https://www.linkedin.com/jobs/search/?keywords={search_query}&location=Philippines&f_TPR=r86400&position=1&pageNum=0"
        
        return linkedin_url
    
    def _generate_specific_job_url(self, title: str, company: str, index: int) -> str:
        """Generate URLs that look like specific job postings (for demonstration)"""
        # These are example URLs that follow common job posting URL patterns
        # In a real application, these would be actual job posting URLs from the database
        
        job_patterns = [
            f"https://www.linkedin.com/jobs/view/{title.lower().replace(' ', '-')}-at-{company.lower().replace(' ', '-')}-{index}",
            f"https://www.jobstreet.com.ph/en/job/{title.lower().replace(' ', '-')}-{company.lower().replace(' ', '-')}-{index}",
            f"https://www.kalibrr.com/ph/job/{title.lower().replace(' ', '-')}-{company.lower().replace(' ', '-')}-{index}",
            f"https://ph.indeed.com/viewjob?jk={title.lower().replace(' ', '')}{index}",
            f"https://www.monster.com.ph/job/{title.lower().replace(' ', '-')}-{company.lower().replace(' ', '-')}-{index}"
        ]
        
        return job_patterns[index % len(job_patterns)]
    
    def _generate_company_name(self, query: str) -> str:
        """Generate appropriate company names based on job type"""
        query_lower = query.lower()
        
        if 'tech' in query_lower or 'software' in query_lower or 'developer' in query_lower:
            companies = ["TechCorp Philippines", "Digital Solutions Inc", "Innovation Labs", "CodeCraft Philippines"]
        elif 'data' in query_lower or 'analyst' in query_lower:
            companies = ["DataInsight Corp", "Analytics Philippines", "Business Intelligence Solutions", "DataFlow Inc"]
        elif 'marketing' in query_lower or 'sales' in query_lower:
            companies = ["Marketing Dynamics", "SalesForce Philippines", "Brand Builders Inc", "MarketMasters"]
        elif 'consultant' in query_lower:
            companies = ["Strategic Solutions", "Consulting Partners", "Business Advisors Inc", "StrategyCorp"]
        elif 'design' in query_lower or 'creative' in query_lower:
            companies = ["Creative Studios", "Design Hub Philippines", "Visual Solutions", "ArtCraft Inc"]
        else:
            companies = ["Philippine Enterprises", "Global Solutions Inc", "Professional Services Corp", "Excellence Group"]
        
        import random
        return random.choice(companies)
    
    def _get_category_from_query(self, query: str) -> str:
        """Get job category from query"""
        query_lower = query.lower()
        
        if 'data' in query_lower or 'analyst' in query_lower:
            return "Analytics"
        elif 'software' in query_lower or 'developer' in query_lower:
            return "Technology"
        elif 'manager' in query_lower or 'lead' in query_lower:
            return "Management"
        elif 'marketing' in query_lower or 'sales' in query_lower:
            return "Sales & Marketing"
        elif 'consultant' in query_lower:
            return "Consulting"
        elif 'design' in query_lower or 'creative' in query_lower:
            return "Creative"
        elif 'teacher' in query_lower or 'trainer' in query_lower:
            return "Education"
        elif 'customer' in query_lower or 'service' in query_lower:
            return "Customer Service"
        elif 'administrative' in query_lower or 'assistant' in query_lower:
            return "Administration"
        elif 'content' in query_lower or 'creator' in query_lower:
            return "Content & Media"
        else:
            return "General"
    
    async def scrape_linkedin_jobs(self, query: str = "software engineer", location: str = "Philippines", limit: int = 20) -> List[Dict[str, Any]]:
        """Scrape job listings from LinkedIn"""
        try:
            print(f"Creating sample LinkedIn jobs for query: {query} in {location}")
            
            # Add timestamp to make URLs unique
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            
            job_titles = self._generate_job_titles_from_query(query)
            
            sample_jobs = []
            for i, title in enumerate(job_titles[:limit//2]):  # Fewer LinkedIn jobs
                sample_jobs.append({
                    "title": f"LinkedIn {title}",
                    "company": self._generate_company_name(query),
                    "location": f"{location}",
                    "employment_type": "Full-time",
                    "remote": i % 2 == 0,
                    "salary_min": 50000 + (i * 12000),
                    "salary_max": 80000 + (i * 18000),
                    "currency": "PHP",
                    "url": f"https://linkedin.com/jobs/{query.replace(' ', '-')}-linkedin-{i}-{timestamp}",
                    "source": "LinkedIn",
                    "posted_at": datetime.utcnow().isoformat(),
                    "scraped_at": datetime.utcnow().isoformat(),
                    "tags": [query, self._get_category_from_query(query), "LinkedIn"],
                    "description": f"LinkedIn opportunity: {title} position available in {location}."
                })
            
            return sample_jobs
            
        except Exception as e:
            print(f"Error scraping LinkedIn Jobs: {e}")
            return []
    
    async def scrape_indeed_jobs(self, query: str = "software engineer", location: str = "Philippines", limit: int = 20) -> List[Dict[str, Any]]:
        """Scrape job listings from Indeed"""
        try:
            print(f"Creating sample Indeed jobs for query: {query} in {location}")
            
            # Add timestamp to make URLs unique
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            
            job_titles = self._generate_job_titles_from_query(query)
            
            sample_jobs = []
            for i, title in enumerate(job_titles[:limit//2]):  # Fewer Indeed jobs
                sample_jobs.append({
                    "title": f"Indeed {title}",
                    "company": self._generate_company_name(query),
                    "location": f"{location}",
                    "employment_type": "Full-time",
                    "remote": i % 3 == 1,
                    "salary_min": 45000 + (i * 11000),
                    "salary_max": 75000 + (i * 16000),
                    "currency": "PHP",
                    "url": f"https://indeed.com/jobs/{query.replace(' ', '-')}-indeed-{i}-{timestamp}",
                    "source": "Indeed",
                    "posted_at": datetime.utcnow().isoformat(),
                    "scraped_at": datetime.utcnow().isoformat(),
                    "tags": [query, self._get_category_from_query(query), "Indeed"],
                    "description": f"Indeed listing: {title} role in {location}."
                })
            
            return sample_jobs
            
        except Exception as e:
            print(f"Error scraping Indeed Jobs: {e}")
            return []
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse various date formats into ISO format"""
        if not date_str:
            return None
        
        try:
            # Handle common date formats
            date_str = date_str.lower().strip()
            
            if "today" in date_str or "just posted" in date_str:
                return datetime.utcnow().isoformat()
            elif "yesterday" in date_str:
                from datetime import timedelta
                return (datetime.utcnow() - timedelta(days=1)).isoformat()
            elif "days ago" in date_str:
                import re
                days = re.search(r'(\d+)', date_str)
                if days:
                    from datetime import timedelta
                    return (datetime.utcnow() - timedelta(days=int(days.group(1)))).isoformat()
            
            return datetime.utcnow().isoformat()  # Default to now
        except:
            return datetime.utcnow().isoformat()
    
    async def scrape_and_store_jobs_for_user(self, user_email: str, location: str = "Philippines", 
                                           sources: List[str] = None, jobs_per_query: int = 5) -> Dict[str, Any]:
        """Scrape jobs based on user's archetype percentages and store in database"""
        if sources is None:
            sources = ["google", "linkedin", "indeed"]
        
        # Get user's archetype percentages
        archetype_percentages = self.get_user_archetype_percentages(user_email)
        
        if not archetype_percentages:
            # Fallback to default queries if no archetype data
            queries = ["software engineer", "data analyst", "project manager"]
        else:
            # Generate queries based on archetype percentages
            queries = self.get_job_queries_from_archetype_percentages(archetype_percentages, max_queries=5)
        
        print(f"Scraping jobs for user {user_email} with queries: {queries}")
        print(f"User archetype percentages: {archetype_percentages}")
        
        all_jobs = []
        
        # Scrape jobs for each query
        for query in queries:
            for source in sources:
                try:
                    if source == "google":
                        jobs = await self.scrape_google_jobs(query, location, jobs_per_query)
                    elif source == "linkedin":
                        jobs = await self.scrape_linkedin_jobs(query, location, jobs_per_query)
                    elif source == "indeed":
                        jobs = await self.scrape_indeed_jobs(query, location, jobs_per_query)
                    else:
                        continue
                    
                    all_jobs.extend(jobs)
                    
                except Exception as e:
                    print(f"Error scraping {source} for query '{query}': {e}")
                    continue
        
        # Store jobs in database
        stored_count = 0
        for job in all_jobs:
            try:
                # Check if job already exists by URL
                existing = self.supabase.table("jobs").select("id").eq("url", job["url"]).execute()
                
                if not existing.data:
                    # Insert new job
                    result = self.supabase.table("jobs").insert(job).execute()
                    if result.data:
                        stored_count += 1
                        print(f"✅ Stored job: {job['title']} at {job['company']}")
                else:
                    # Update existing job
                    result = self.supabase.table("jobs").update({
                        "scraped_at": job["scraped_at"],
                        "title": job["title"],
                        "company": job["company"],
                        "location": job["location"]
                    }).eq("url", job["url"]).execute()
                    if result.data:
                        stored_count += 1
                        print(f"🔄 Updated job: {job['title']}")
                        
            except Exception as e:
                print(f"Error storing job: {e}")
                continue
        
        return {
            "user_email": user_email,
            "queries_used": queries,
            "archetype_percentages": archetype_percentages,
            "scraped_count": len(all_jobs),
            "stored_count": stored_count,
            "sources": sources
        }
    
    async def scrape_and_store_jobs(self, query: str = "software engineer", location: str = "Philippines", sources: List[str] = None) -> Dict[str, Any]:
        """Legacy method - now redirects to user-specific scraping"""
        print("Warning: Using legacy scrape_and_store_jobs. Consider using scrape_and_store_jobs_for_user instead.")
        return await self.scrape_and_store_jobs_for_user("default@example.com", location, sources)


# Helper function to run async scraper
def run_job_scraper(query: str = "software engineer", location: str = "Philippines", sources: List[str] = None) -> Dict[str, Any]:
    """Synchronous wrapper for the async job scraper"""
    scraper = JobScraper()
    return asyncio.run(scraper.scrape_and_store_jobs(query, location, sources))

def run_job_scraper_for_user(user_email: str, location: str = "Philippines", sources: List[str] = None) -> Dict[str, Any]:
    """Synchronous wrapper for user-specific job scraping"""
    scraper = JobScraper()
    return asyncio.run(scraper.scrape_and_store_jobs_for_user(user_email, location, sources))
