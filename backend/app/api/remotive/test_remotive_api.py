"""
Test API Call for Remotive
Endpoint: GET https://remotive.com/api/remote-jobs

This file demonstrates how to make a test API call to Remotive.
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


def test_remotive_api(category: Optional[str] = None, 
                      search: Optional[str] = None,
                      limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Make a test API call to Remotive endpoint.
    
    Args:
        category: Optional job category filter (default: "software-dev")
        search: Optional search term (default: "Software Engineer")
        limit: Optional limit for number of results
    
    Returns:
        Dictionary containing job postings from Remotive API (all jobs are remote)
        Returns all jobs with "Software Engineer" in the title
    """
    try:
        url = 'https://remotive.com/api/remote-jobs'
        params = {}
        params['category'] = category or "software-dev"
        params['search'] = search or "Software Engineer"
        if limit:
            params['limit'] = limit
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Post-process to filter by job title
        if 'jobs' in data:
            filtered_jobs = []
            for job in data['jobs']:
                # Filter by job title - must contain "Software Engineer"
                job_title = job.get('title', '').upper()
                if 'SOFTWARE ENGINEER' not in job_title:
                    continue
                
                filtered_jobs.append(job)
            
            data['jobs'] = filtered_jobs
        
        return data
    except requests.exceptions.RequestException as error:
        print(f'Error calling Remotive API: {error}')
        raise


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
                    # For single values, set max to min (or could leave empty)
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
        filename: Optional filename (default: remotive_jobs_YYYYMMDD_HHMMSS.csv)
    
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
        filename = f"remotive_{timestamp}.csv"
    
    # Save to csv subfolder
    filepath = os.path.join(csv_dir, filename)
    
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
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(normalized_jobs)
    
    print(f"Exported {len(normalized_jobs)} job postings to {filepath}")
    return filepath


if __name__ == "__main__":
    # Example usage: Software Engineer
    try:
        result = test_remotive_api(
            category="software-dev",
            search="Software Engineer",
            limit=10
        )
        jobs = result.get("jobs", [])
        print(f"Retrieved {len(jobs)} Software Engineer remote job postings")
        
        # Export to CSV
        if jobs:
            csv_file = export_to_csv(jobs)
            if csv_file:
                print(f"\nCSV file created: {csv_file}")
        
        print(json.dumps(jobs[:2], indent=2))  # Print first 2 jobs
    except Exception as e:
        print(f"Test failed: {e}")

