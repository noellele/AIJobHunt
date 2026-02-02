"""
Test API Call for Remotive - Full Dataset Version
Endpoint: GET https://remotive.com/api/remote-jobs

This version fetches ALL currently active remote job listings in one response.
The Remotive API is designed to return all active jobs in a single call.

Type: Job aggregator API
Auth: None
Coverage: Remote jobs aggregated from multiple ATS job boards
"""

import requests
import json
import csv
import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional


def fetch_all_remotive_jobs(category: Optional[str] = None, 
                           search: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch ALL active remote job listings from Remotive API in one request.
    
    According to Remotive API documentation, the endpoint returns all currently
    active remote job listings in one response (subject to their internal cap).
    
    Args:
        category: Optional job category filter (e.g., "software-dev")
        search: Optional search term to filter jobs
    
    Returns:
        Dictionary containing all active job postings from Remotive API
        Structure: {"jobs": [list of all active jobs]}
    """
    try:
        url = 'https://remotive.com/api/remote-jobs'
        params = {}
        
        if category:
            params['category'] = category
        if search:
            params['search'] = search
        
        print(f"Fetching all active remote jobs from Remotive API...")
        print(f"URL: {url}")
        if params:
            print(f"Filters: {params}")
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        total_jobs = len(data.get('jobs', []))
        print(f"✓ Successfully retrieved {total_jobs} total active job postings")
        
        return data
    except requests.exceptions.RequestException as error:
        print(f'Error calling Remotive API: {error}')
        raise


def filter_software_engineer_jobs(jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter jobs to only include those with "Software Engineer" in the title.
    
    Args:
        jobs: List of all job postings from API
    
    Returns:
        Filtered list containing only Software Engineer positions
    """
    filtered = []
    for job in jobs:
        job_title = job.get('title', '').upper()
        if 'SOFTWARE ENGINEER' in job_title:
            filtered.append(job)
    
    print(f"✓ Filtered to {len(filtered)} Software Engineer positions")
    return filtered


def normalize_remotive_job(job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize Remotive job data to include all mapped fields.
    
    Args:
        job: Raw job data from Remotive API
    
    Returns:
        Normalized job data with all required fields
    """
    # Extract salary from API response
    # API provides 'salary' as a string field (e.g., "$180k + bonus up to 100%", "$120k - $160k", "$120,000 - $160,000")
    salary_min = job.get('salary_min')  # Usually not present in API response
    salary_max = job.get('salary_max')  # Usually not present in API response
    
    if not salary_min or not salary_max:
        salary_str = job.get('salary', '')
        if salary_str:
            # Pattern 1: Range format "$120k - $160k" or "$120,000 - $160,000"
            range_patterns = [
                r'\$(\d+)k?\s*-\s*\$(\d+)k?',
                r'\$(\d{1,3}(?:,\d{3})*)\s*-\s*\$(\d{1,3}(?:,\d{3})*)',
            ]
            for pattern in range_patterns:
                match = re.search(pattern, salary_str, re.IGNORECASE)
                if match:
                    min_val = match.group(1).replace(',', '')
                    max_val = match.group(2).replace(',', '')
                    salary_min = int(min_val) * 1000 if 'k' in match.group(0).lower() else int(min_val)
                    salary_max = int(max_val) * 1000 if 'k' in match.group(0).lower() else int(max_val)
                    break
            
            # Pattern 2: Single value with 'k' like "$180k" or "$180k + bonus"
            if not salary_min:
                single_k_pattern = r'\$(\d+)k'
                match = re.search(single_k_pattern, salary_str, re.IGNORECASE)
                if match:
                    val = int(match.group(1)) * 1000
                    salary_min = val
                    salary_max = val
            
            # Pattern 3: Single value with full number like "$180000"
            if not salary_min:
                single_full_pattern = r'\$(\d{1,3}(?:,\d{3})*)'
                match = re.search(single_full_pattern, salary_str, re.IGNORECASE)
                if match:
                    val = int(match.group(1).replace(',', ''))
                    salary_min = val
                    salary_max = val
    
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
        'Location': job.get('candidate_required_location', 'Remote'),
        'Tags': tags_str,
        'Description': clean_description,
        'URL': job.get('url', 'N/A'),
        'Salary_Min': salary_min if salary_min else '',
        'Salary_Max': salary_max if salary_max else '',
        'Date': job.get('publication_date', 'N/A'),
        'ID': job.get('id', 'N/A')
    }


def export_to_csv(jobs: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
    """
    Export job postings to a CSV file.
    
    Args:
        jobs: List of job postings (raw API response)
        filename: Optional filename (default: remotive_jobs_full_YYYYMMDD_HHMMSS.csv)
    
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
        filename = f"remotive_full_{timestamp}.csv"
    
    # Save to csv subfolder
    filepath = os.path.join(csv_dir, filename)
    
    print(f"Normalizing {len(jobs)} jobs for CSV export...")
    # Normalize all jobs
    normalized_jobs = [normalize_remotive_job(job) for job in jobs]
    
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
    Print statistics about the retrieved jobs.
    
    Args:
        jobs: List of job postings
    """
    if not jobs:
        print("No jobs to analyze")
        return
    
    print("\n" + "="*50)
    print("JOB STATISTICS")
    print("="*50)
    
    total = len(jobs)
    print(f"Total jobs: {total}")
    
    # Count jobs with salary information
    jobs_with_salary = sum(1 for job in jobs if job.get('salary') or job.get('salary_min') or job.get('salary_max'))
    print(f"Jobs with salary info: {jobs_with_salary} ({jobs_with_salary/total*100:.1f}%)")
    
    # Count unique companies
    companies = set(job.get('company_name', '') for job in jobs)
    print(f"Unique companies: {len(companies)}")
    
    # Count by location
    locations = {}
    for job in jobs:
        loc = job.get('candidate_required_location', 'Unknown')
        locations[loc] = locations.get(loc, 0) + 1
    
    print(f"\nTop locations:")
    sorted_locations = sorted(locations.items(), key=lambda x: x[1], reverse=True)[:5]
    for loc, count in sorted_locations:
        print(f"  {loc}: {count}")
    
    print("="*50 + "\n")


if __name__ == "__main__":
    # Fetch ALL active remote jobs, then filter for Software Engineer positions
    try:
        # Step 1: Fetch all active jobs (no limit - gets everything)
        result = fetch_all_remotive_jobs()
        all_jobs = result.get("jobs", [])
        
        # Step 2: Filter for Software Engineer positions
        software_engineer_jobs = filter_software_engineer_jobs(all_jobs)
        
        # Step 3: Print statistics
        print_statistics(software_engineer_jobs)
        
        # Step 4: Export to CSV
        if software_engineer_jobs:
            csv_file = export_to_csv(software_engineer_jobs)
            if csv_file:
                print(f"\n✓ CSV file created: {csv_file}")
        
        # Step 5: Show sample jobs
        print("\nSample jobs (first 2):")
        print(json.dumps(software_engineer_jobs[:2], indent=2))
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

