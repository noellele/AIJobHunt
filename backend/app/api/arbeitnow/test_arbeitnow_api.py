"""
Test API Call for Arbeitnow
Endpoint: GET https://www.arbeitnow.com/api/job-board-api

This file demonstrates how to make a test API call to Arbeitnow
and includes sample response data with all required fields.
Type: Job aggregator API
Auth: None
Coverage: European companies and remote roles
"""

import requests
import json
import csv
import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional


def test_arbeitnow_api(page: Optional[int] = None, 
                       remote_only: bool = True,
                       keywords: Optional[str] = None,
                       salary_min: Optional[int] = None,
                       salary_max: Optional[int] = None) -> Dict[str, Any]:
    """
    Make a test API call to Arbeitnow endpoint.
    
    Args:
        page: Optional page number for pagination
        remote_only: Filter to only return remote jobs (default: True)
        keywords: Optional search keywords (default: "Software Engineer")
        salary_min: Minimum salary filter (default: 50000)
        salary_max: Maximum salary filter (default: 150000)
    
    Returns:
        Dictionary containing job postings from Arbeitnow API (filtered to remote only if requested)
    """
    try:
        url = 'https://www.arbeitnow.com/api/job-board-api'
        params = {}
        if page:
            params['page'] = page
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Filter for remote jobs, keywords, and salary range
        if 'data' in data:
            filtered_jobs = []
            search_term = (keywords or "Software Engineer").lower()
            min_salary = salary_min or 50000
            max_salary = salary_max or 150000
            
            for job in data['data']:
                # Filter by remote
                if remote_only and not job.get('remote', False):
                    continue
                
                # Filter by keywords in title
                title = job.get('title', '').lower()
                if search_term not in title and 'software engineer' not in title:
                    continue
                
                # Filter by salary if available (Arbeitnow may not have salary in all jobs)
                # If salary info is not available, include the job
                job_salary = job.get('salary_min') or job.get('salary_max')
                if job_salary:
                    if job_salary < min_salary or job_salary > max_salary:
                        continue
                
                filtered_jobs.append(job)
            
            data['data'] = filtered_jobs
        
        return data
    except requests.exceptions.RequestException as error:
        print(f'Error calling Arbeitnow API: {error}')
        raise


def normalize_arbeitnow_job(job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize Arbeitnow job data to include all mapped fields.
    
    Args:
        job: Raw job data from Arbeitnow API
    
    Returns:
        Normalized job data with all required fields
    """
    # Normalize tags
    tags = job.get('tags', [])
    tags_str = '; '.join(tags) if isinstance(tags, list) else str(tags)
    
    # Clean description
    description = job.get('description', '')
    clean_description = re.sub(r'<[^>]+>', '', description)
    clean_description = ' '.join(clean_description.split())
    
    return {
        'Company': job.get('company_name', 'N/A'),
        'Position': job.get('title', 'N/A'),
        'Location': job.get('location', 'Remote'),
        'Tags': tags_str,
        'Description': clean_description,
        'URL': job.get('url', 'N/A'),
        'Salary_Min': job.get('salary_min', ''),
        'Salary_Max': job.get('salary_max', ''),
        'Date': job.get('published_at', 'N/A'),
        'ID': job.get('id', 'N/A')
    }


def export_to_csv(jobs: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
    """
    Export job postings to a CSV file.
    
    Args:
        jobs: List of job postings (raw API response)
        filename: Optional filename (default: arbeitnow_jobs_YYYYMMDD_HHMMSS.csv)
    
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
        filename = f"arbeitnow_{timestamp}.csv"
    
    # Save to csv subfolder
    filepath = os.path.join(csv_dir, filename)
    
    # Normalize all jobs
    normalized_jobs = [normalize_arbeitnow_job(job) for job in jobs]
    
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
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(normalized_jobs)
    
    print(f"Exported {len(normalized_jobs)} job postings to {filepath}")
    return filepath


# Sample test data structure (mapped from API response)
# Search criteria: Software Engineer, Remote, $50,000 - $150,000
sample_arbeitnow_response = {
    "data": [
        {
            "id": "arbeitnow-001",
            "title": "Software Engineer",
            "company_name": "TechFlow Solutions",
            "location": "Remote",
            "remote": True,
            "tags": ["software-engineer", "python", "javascript", "remote", "full-time"],
            "description": "We are seeking a Software Engineer to design and build scalable software applications. You will work with modern programming languages and frameworks to create robust systems. Experience with software development best practices, version control, and cloud platforms preferred. This is a fully remote position with competitive salary.",
            "url": "https://www.arbeitnow.com/view/job/software-engineer-techflow-001",
            "salary_min": 70000,
            "salary_max": 110000,
            # Normalized fields for testing
            "company": "TechFlow Solutions",
            "position": "Software Engineer",
            "location": "Remote",
            "tags": ["software-engineer", "python", "javascript", "remote", "full-time"]
        },
        {
            "id": "arbeitnow-002",
            "title": "Senior Software Engineer",
            "company_name": "WebTech Pro",
            "location": "Remote",
            "remote": True,
            "tags": ["software-engineer", "senior", "react", "node.js", "remote"],
            "description": "Join our engineering team as a Senior Software Engineer. You will design and develop complex software systems, mentor junior engineers, and contribute to architectural decisions. Strong experience with software engineering principles and modern development practices required. Fully remote position with excellent compensation.",
            "url": "https://www.arbeitnow.com/view/job/senior-software-engineer-webtech-002",
            "salary_min": 100000,
            "salary_max": 150000,
            # Normalized fields for testing
            "company": "WebTech Pro",
            "position": "Senior Software Engineer",
            "location": "Remote",
            "tags": ["software-engineer", "senior", "react", "node.js", "remote"]
        }
    ]
}


if __name__ == "__main__":
    # Example usage: Software Engineer, Remote, $50,000 - $150,000
    try:
        result = test_arbeitnow_api(
            page=1,
            remote_only=True,
            keywords="Software Engineer",
            salary_min=50000,
            salary_max=150000
        )
        jobs = result.get("data", [])
        print(f"Retrieved {len(jobs)} Software Engineer remote job postings ($50k-$150k)")
        
        # Export to CSV
        if jobs:
            csv_file = export_to_csv(jobs)
            if csv_file:
                print(f"\nCSV file created: {csv_file}")
        
        print(json.dumps(jobs[:2], indent=2))  # Print first 2 jobs
    except Exception as e:
        print(f"Test failed: {e}")

