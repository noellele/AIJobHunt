"""
Test API Call for Adzuna - Top 25 Computer Science Jobs (2026)
Endpoint: GET https://api.adzuna.com/v1/api/jobs/us/search/{page}

This file searches for the top 25 most popular computer science job titles in 2026.
Type: Job aggregator API
Auth: API key required
"""

import requests
import json
import csv
import os
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Load environment variables from .env file in backend directory
env_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env')
load_dotenv(dotenv_path=env_path)

# Adzuna API Credentials
# Note: Adzuna requires BOTH app_id and app_key for authentication
# Loaded from environment variables
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_API_KEY = os.getenv("ADZUNA_API_KEY")

# Top 25 Computer Science Job Titles (2026)
TOP_25_JOBS = [
    "AI Engineer",
    "Machine Learning Engineer",
    "Cybersecurity Analyst",
    "Software Engineer",
    "Data Scientist",
    "Cloud Architect",
    "Data Engineer",
    "DevOps Engineer",
    "AI Consultant",
    "Technical Product Manager",
    "Full-Stack Developer",
    "AI/ML Researcher",
    "Data Architect",
    "Security Engineer",
    "Network Engineer",
    "Blockchain Developer",
    "Systems Analyst",
    "UX/UI Designer",
    "Datacenter Technician",
    "Quantitative Researcher",
    "Mobile App Developer",
    "Ethical Hacker",
    "Database Administrator",
    "SRE",
    "Solutions Architect"
]


def search_adzuna_jobs(keywords: str, page: int = 1,
                       app_id: Optional[str] = None,
                       app_key: Optional[str] = None,
                       results_per_page: int = 50) -> Dict[str, Any]:
    """
    Make a single API call to Adzuna endpoint for a specific job title.
    
    Args:
        keywords: Search keywords (job title)
        page: Page number for pagination (default: 1)
        app_id: Adzuna App ID (defaults to ADZUNA_APP_ID)
        app_key: Adzuna App Key (defaults to ADZUNA_API_KEY)
        results_per_page: Number of results per page (default: 50)
    
    Returns:
        Dictionary containing job postings from Adzuna API
    """
    try:
        # Adzuna API endpoint format - page number goes in the URL path
        url = f'https://api.adzuna.com/v1/api/jobs/us/search/{page}'
        
        # Use provided credentials or defaults from environment variables
        api_key = app_key or ADZUNA_API_KEY
        api_app_id = app_id or ADZUNA_APP_ID
        
        if not api_app_id:
            raise ValueError(
                "Adzuna API requires both app_id and app_key. "
                "Please provide an app_id parameter or set ADZUNA_APP_ID in the .env file."
            )
        if not api_key:
            raise ValueError(
                "Adzuna API requires both app_id and app_key. "
                "Please provide an app_key parameter or set ADZUNA_API_KEY in the .env file."
            )
        
        params = {
            'app_id': api_app_id,
            'app_key': api_key,
            'results_per_page': results_per_page,
            'what': keywords
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        return data
    except requests.exceptions.RequestException as error:
        print(f'Error calling Adzuna API for "{keywords}": {error}')
        if hasattr(error.response, 'text'):
            print(f'Response: {error.response.text}')
        return {'results': []}


def filter_jobs_by_top_titles(jobs: List[Dict[str, Any]], job_titles: List[str]) -> List[Dict[str, Any]]:
    """
    Filter jobs to only include those matching the top job titles.
    
    Args:
        jobs: List of job postings from API
        job_titles: List of job titles to match against
    
    Returns:
        Filtered list of jobs matching the top titles
    """
    filtered = []
    title_keywords = [title.upper() for title in job_titles]
    
    for job in jobs:
        job_title = job.get('title', '').upper()
        # Check if job title contains any of the top job title keywords
        for keyword in title_keywords:
            # Split keyword to check for main terms (e.g., "AI Engineer" -> check for "AI" and "ENGINEER")
            keyword_parts = keyword.split()
            # For multi-word titles, check if all significant parts are present
            if len(keyword_parts) > 1:
                # Check if all main parts are in the job title
                if all(part in job_title for part in keyword_parts if len(part) > 2):
                    filtered.append(job)
                    break
            else:
                # Single word - direct match
                if keyword in job_title:
                    filtered.append(job)
                    break
    
    return filtered


def fetch_all_top_jobs(job_titles: List[str] = None,
                       app_id: Optional[str] = None,
                       app_key: Optional[str] = None,
                       results_per_page: int = 50,
                       max_pages_per_job: int = 1) -> List[Dict[str, Any]]:
    """
    Fetch jobs for all top 25 job titles.
    
    Args:
        job_titles: List of job titles to search (defaults to TOP_25_JOBS)
        app_id: Adzuna App ID
        app_key: Adzuna App Key
        results_per_page: Number of results per page (default: 50)
        max_pages_per_job: Maximum pages to fetch per job title (default: 1)
    
    Returns:
        Combined list of all job postings
    """
    if job_titles is None:
        job_titles = TOP_25_JOBS
    
    all_jobs = []
    total_jobs = len(job_titles)
    
    print(f"Searching for {total_jobs} top job titles...")
    print("=" * 60)
    
    for idx, job_title in enumerate(job_titles, 1):
        print(f"[{idx}/{total_jobs}] Searching for: {job_title}")
        
        try:
            # Search for this job title
            for page in range(1, max_pages_per_job + 1):
                result = search_adzuna_jobs(
                    keywords=job_title,
                    page=page,
                    app_id=app_id,
                    app_key=app_key,
                    results_per_page=results_per_page
                )
                
                jobs = result.get('results', [])
                if jobs:
                    # Filter to ensure jobs match the title
                    filtered = filter_jobs_by_top_titles(jobs, [job_title])
                    all_jobs.extend(filtered)
                    print(f"  ✓ Found {len(filtered)} jobs (page {page})")
                else:
                    if page == 1:
                        print(f"  ✗ No jobs found")
                    break
                
                # If we got fewer results than requested, no more pages
                if len(jobs) < results_per_page:
                    break
        
        except Exception as e:
            print(f"  ✗ Error: {e}")
            continue
    
    print("=" * 60)
    print(f"Total jobs retrieved: {len(all_jobs)}")
    
    return all_jobs


def normalize_adzuna_job(job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize Adzuna job data to include all mapped fields.
    
    Args:
        job: Raw job data from Adzuna API
    
    Returns:
        Normalized job data with all required fields
    """
    # Extract company name
    company = job.get('company', {})
    if isinstance(company, dict):
        company = company.get('display_name', 'N/A')
    
    # Extract location
    location = job.get('location', {})
    if isinstance(location, dict):
        location = location.get('display_name', 'Remote')
    
    # Extract tags (Adzuna may not have tags, create from title/description)
    tags = job.get('tags', [])
    if not tags:
        title = job.get('title', '').lower()
        tags = [tag for tag in ['software-engineer', 'remote', 'full-time'] if tag in title]
    tags_str = '; '.join(tags) if isinstance(tags, list) else str(tags)
    
    # Clean description
    description = job.get('description', '')
    clean_description = re.sub(r'<[^>]+>', '', description)
    clean_description = ' '.join(clean_description.split())
    
    return {
        'Company': company,
        'Position': job.get('title', 'N/A'),
        'Location': location,
        'Tags': tags_str,
        'Description': clean_description,
        'URL': job.get('redirect_url', job.get('url', 'N/A')),
        'Salary_Min': job.get('salary_min', ''),
        'Salary_Max': job.get('salary_max', ''),
        'Date': job.get('created', 'N/A'),
        'ID': job.get('id', 'N/A')
    }


def export_to_csv(jobs: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
    """
    Export job postings to a CSV file.
    
    Args:
        jobs: List of job postings (raw API response)
        filename: Optional filename (default: adzuna_top25_YYYYMMDD_HH_MM_SS.csv)
    
    Returns:
        Path to the created CSV file
    """
    if not jobs:
        print("No jobs to export")
        return ""
    
    # Create csv directory if it doesn't exist
    csv_dir = os.path.join(os.path.dirname(__file__), 'csv')
    os.makedirs(csv_dir, exist_ok=True)
    
    # Generate filename if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H_%M_%S")
        filename = f"adzuna_top25_{timestamp}.csv"
    
    # Save to csv subfolder
    filepath = os.path.join(csv_dir, filename)
    
    # Normalize all jobs
    print(f"\nNormalizing {len(jobs)} jobs for CSV export...")
    normalized_jobs = [normalize_adzuna_job(job) for job in jobs]
    
    # Define CSV columns in order
    fieldnames = [
        'Company',
        'Position',
        'Location',
        'Tags',
        'Description',
        'URL',
        'Salary_Min',
        'Salary_Max',
        'Date',
        'ID'
    ]
    
    # Write to CSV
    print(f"Writing to CSV file...")
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(normalized_jobs)
    
    print(f"✓ Exported {len(normalized_jobs)} job postings to {filepath}")
    return filepath


def print_statistics(jobs: List[Dict[str, Any]]):
    """
    Print statistics about the retrieved jobs by job title.
    
    Args:
        jobs: List of job postings
    """
    if not jobs:
        print("No jobs to analyze")
        return
    
    print("\n" + "=" * 60)
    print("JOB STATISTICS BY TITLE")
    print("=" * 60)
    
    # Count jobs by title category
    title_counts = {}
    for job in jobs:
        title = job.get('title', 'Unknown')
        # Find which top job title it matches
        for top_title in TOP_25_JOBS:
            if top_title.upper() in title.upper():
                title_counts[top_title] = title_counts.get(top_title, 0) + 1
                break
        else:
            title_counts['Other'] = title_counts.get('Other', 0) + 1
    
    # Sort by count
    sorted_titles = sorted(title_counts.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\nTotal jobs: {len(jobs)}")
    print(f"\nJobs by title category:")
    for title, count in sorted_titles[:15]:  # Show top 15
        print(f"  {title}: {count}")
    
    # Count jobs with salary information
    jobs_with_salary = sum(1 for job in jobs if job.get('salary_min') or job.get('salary_max'))
    print(f"\nJobs with salary info: {jobs_with_salary} ({jobs_with_salary/len(jobs)*100:.1f}%)")
    
    print("=" * 60 + "\n")


if __name__ == "__main__":
    # Fetch jobs for all top 25 job titles
    try:
        print("Adzuna API - Top 25 Computer Science Jobs Search")
        print("=" * 60)
        
        # Fetch all jobs
        all_jobs = fetch_all_top_jobs(
            job_titles=TOP_25_JOBS,
            results_per_page=50,
            max_pages_per_job=1  # Adjust if you want more pages per job title
        )
        
        # Print statistics
        print_statistics(all_jobs)
        
        # Export to CSV
        if all_jobs:
            csv_file = export_to_csv(all_jobs)
            if csv_file:
                print(f"\n✓ CSV file created: {csv_file}")
        
        # Show sample jobs
        print("\nSample jobs (first 3):")
        print(json.dumps(all_jobs[:3], indent=2))
        
    except ValueError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

