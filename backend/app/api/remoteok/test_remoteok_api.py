"""
Test API Call for Remote OK
Endpoint: GET https://remoteok.com/api

This file demonstrates how to make a test API call to Remote OK
and includes sample response data with all required fields.
Type: Job aggregator API
Auth: None
Coverage: Tech focused roles sourced from many ATS systems
"""

import requests
import json
import csv
import re
from datetime import datetime
from typing import List, Dict, Any, Optional


def extract_salary_from_job(job: Dict[str, Any]) -> tuple[Optional[int], Optional[int]]:
    """
    Extract salary information from a job posting.
    
    Args:
        job: Raw job data from Remote OK API
    
    Returns:
        Tuple of (salary_min, salary_max) or (None, None) if not found
    """
    # Check if salary is directly in the job data
    if 'salary_min' in job and 'salary_max' in job:
        return (job.get('salary_min'), job.get('salary_max'))
    
    # Try to extract from description
    description = job.get('description', '')
    salary_patterns = [
        r'\$(\d+)k?\s*-\s*\$(\d+)k?',  # $70k-$110k or $70-$110
        r'\$(\d{1,3}(?:,\d{3})*)\s*-\s*\$(\d{1,3}(?:,\d{3})*)',  # $70,000-$110,000
        r'(\d+)k?\s*-\s*(\d+)k?\s*(?:USD|dollars|per year|annually)',  # 70k-110k USD
    ]
    for pattern in salary_patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            min_val = match.group(1).replace(',', '')
            max_val = match.group(2).replace(',', '')
            # Handle 'k' suffix
            salary_min = int(min_val) * 1000 if 'k' in match.group(0).lower() else int(min_val)
            salary_max = int(max_val) * 1000 if 'k' in match.group(0).lower() else int(max_val)
            return (salary_min, salary_max)
    
    return (None, None)


def is_valid_location(location: str) -> bool:
    """
    Check if location is valid (US, LIKE US, or Remote).
    
    Args:
        location: Location string from job posting
    
    Returns:
        True if location is US, LIKE US, or Remote
    """
    location_lower = location.lower()
    # Check for US variations
    us_patterns = ['us', 'usa', 'united states', 'u.s.', 'u.s.a.']
    # Check for "like us" patterns (e.g., "US only", "US-based", "US timezone")
    like_us_patterns = ['us only', 'us-based', 'us timezone', 'us time', 'united states only']
    # Check for remote
    remote_patterns = ['remote', 'anywhere', 'worldwide', 'global']
    
    # Check if location contains US patterns
    if any(pattern in location_lower for pattern in us_patterns):
        return True
    
    # Check if location contains "like US" patterns
    if any(pattern in location_lower for pattern in like_us_patterns):
        return True
    
    # Check if location is remote
    if any(pattern in location_lower for pattern in remote_patterns):
        return True
    
    return False


def test_remoteok_api(keywords: Optional[str] = None,
                      salary_min: Optional[int] = None,
                      salary_max: Optional[int] = None,
                      limit: Optional[int] = None,
                      require_salary: bool = True) -> List[Dict[str, Any]]:
    """
    Make a test API call to Remote OK endpoint.
    
    Args:
        keywords: Optional search keywords to filter by (default: "Software Engineer")
        salary_min: Minimum salary filter (default: 50000)
        salary_max: Maximum salary filter (default: 150000)
        limit: Optional limit on number of results (None = no limit)
        require_salary: Only include jobs with salary information (default: True)
    
    Returns:
        List of job postings from Remote OK API (filtered by location and salary)
    """
    try:
        response = requests.get('https://remoteok.com/api')
        response.raise_for_status()
        data = response.json()
        
        # Filter by keywords, location, and salary
        search_term = (keywords or "Software Engineer").lower()
        min_salary = salary_min or 50000
        max_salary = salary_max or 150000
        
        filtered_jobs = []
        for job in data:
            # Skip invalid entries (Remote OK sometimes includes metadata)
            if not isinstance(job, dict) or 'position' not in job:
                continue
            
            # Filter by keywords in position or tags
            position = job.get('position', '').lower()
            tags = ' '.join(job.get('tags', [])).lower()
            
            if search_term not in position and 'software engineer' not in position:
                continue
            
            # Filter by location (US, LIKE US, or Remote)
            location = job.get('location', '')
            if not is_valid_location(location):
                continue
            
            # Filter by salary - only include jobs with salary information if required
            if require_salary:
                job_salary_min, job_salary_max = extract_salary_from_job(job)
                if job_salary_min is None or job_salary_max is None:
                    continue
                
                # Check if salary range overlaps with desired range
                if job_salary_max < min_salary or job_salary_min > max_salary:
                    continue
            
            filtered_jobs.append(job)
            
            # Apply limit if specified
            if limit and len(filtered_jobs) >= limit:
                break
        
        return filtered_jobs
    except requests.exceptions.RequestException as error:
        print(f'Error calling Remote OK API: {error}')
        raise


def normalize_job_data(job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize job data to include all mapped fields.
    
    Args:
        job: Raw job data from Remote OK API
    
    Returns:
        Normalized job data with all required fields
    """
    # Extract salary using the helper function
    salary_min, salary_max = extract_salary_from_job(job)
    
    # Normalize tags - join array into semicolon-separated string
    tags = job.get('tags', [])
    tags_str = '; '.join(tags) if isinstance(tags, list) else str(tags)
    
    # Clean description - remove HTML tags and normalize whitespace
    description = job.get('description', '')
    clean_description = re.sub(r'<[^>]+>', '', description)
    clean_description = ' '.join(clean_description.split())
    
    return {
        'Company': job.get('company', 'N/A'),
        'Position': job.get('position', 'N/A'),
        'Location': job.get('location', 'Remote'),
        'Tags': tags_str,
        'Description': clean_description,
        'URL': job.get('url', 'N/A'),
        'Salary_Min': salary_min if salary_min else '',
        'Salary_Max': salary_max if salary_max else '',
        'Date': job.get('date', 'N/A'),
        'ID': job.get('id', 'N/A')
    }


def export_to_csv(jobs: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
    """
    Export job postings to a CSV file.
    
    Args:
        jobs: List of job postings (raw API response)
        filename: Optional filename (default: remoteok_jobs_YYYYMMDD_HHMMSS.csv)
    
    Returns:
        Path to the created CSV file
    """
    if not jobs:
        print("No jobs to export")
        return ""
    
    # Create csv directory if it doesn't exist
    import os
    csv_dir = os.path.join(os.path.dirname(__file__), 'csv')
    os.makedirs(csv_dir, exist_ok=True)
    
    # Generate filename if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H_%M_%S")
        filename = f"remoteok_{timestamp}.csv"
    
    # Save to csv subfolder
    filepath = os.path.join(csv_dir, filename)
    
    # Normalize all jobs
    normalized_jobs = [normalize_job_data(job) for job in jobs]
    
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


# Sample test data structure (mapped from API response) - FOR REFERENCE ONLY
# Search criteria: Software Engineer, Remote, $50,000 - $150,000
# This is example data showing the expected API response structure
# Uncomment and use for testing when API is unavailable
"""
sample_remoteok_response = [
    {
        "id": 123456,
        "date": "2024-01-15T10:00:00Z",
        "company": "TechCorp Inc.",
        "position": "Software Engineer",
        "location": "Remote",
        "tags": ["software-engineer", "javascript", "python", "remote", "full-time"],
        "description": "We are looking for a Software Engineer to join our remote team. You will work on building scalable web applications using modern programming languages and frameworks. Experience with software development best practices, version control, and cloud platforms required. Competitive salary range $70k-$110k.",
        "url": "https://remoteok.com/remote-jobs/123456-software-engineer-techcorp",
        "salary_min": 70000,
        "salary_max": 110000
    },
    {
        "id": 123457,
        "date": "2024-01-16T09:30:00Z",
        "company": "TechSolutions Inc.",
        "position": "Senior Software Engineer",
        "location": "Remote",
        "tags": ["software-engineer", "senior", "react", "node.js", "remote"],
        "description": "Join our engineering team as a Senior Software Engineer. You will design and develop complex software systems, mentor junior engineers, and contribute to architectural decisions. Strong experience with software engineering principles required. Salary range $100k-$150k.",
        "url": "https://remoteok.com/remote-jobs/123457-senior-software-engineer-techsolutions",
        "salary_min": 100000,
        "salary_max": 150000
    }
]
"""


if __name__ == "__main__":
    # Example usage: Software Engineer, US/LIKE US/Remote, with salary information
    try:
        # Fetch all matching jobs with salary information
        # Location: US, LIKE US, or Remote
        # Only jobs with salary information will be included
        jobs = test_remoteok_api(
            keywords="Software Engineer",
            salary_min=50000,
            salary_max=150000,
            limit=None,  # Set to a number to limit results, or None for all
            require_salary=True  # Only include jobs with salary information
        )
        print(f"Retrieved {len(jobs)} Software Engineer jobs (US/LIKE US/Remote) with salary information ($50k-$150k)")
        
        # Export to CSV
        csv_file = export_to_csv(jobs)
        if csv_file:
            print(f"\nCSV file created: {csv_file}")
        
        # Optionally print first 2 jobs as JSON for preview
        if jobs:
            print("\nPreview of first job:")
            print(json.dumps(normalize_job_data(jobs[0]), indent=2))
            
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

