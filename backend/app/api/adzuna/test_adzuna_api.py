"""
Test API Call for Adzuna
Endpoint: GET https://api.adzuna.com/v1/api/jobs/us/search/{page}

This file demonstrates how to make a test API call to Adzuna.
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


def test_adzuna_api(page: int = 1, keywords: Optional[str] = None, 
                    app_id: Optional[str] = None,
                    app_key: Optional[str] = None,
                    results_per_page: int = 50) -> Dict[str, Any]:
    """
    Make a test API call to Adzuna endpoint.
    
    Args:
        page: Page number for pagination (default: 1)
        keywords: Optional search keywords (default: "Software Engineer")
        app_id: Adzuna App ID (required - defaults to ADZUNA_APP_ID)
        app_key: Adzuna App Key (defaults to ADZUNA_API_KEY)
        results_per_page: Number of results per page (default: 50)
    
    Returns:
        Dictionary containing job postings from Adzuna API
        Returns all jobs with "Software Engineer" in the title
    
    Raises:
        ValueError: If app_id is not provided
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
            'results_per_page': results_per_page
        }
        
        # Search for Software Engineer
        params['what'] = keywords or "Software Engineer"
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Post-process to filter by job title
        if 'results' in data:
            filtered_results = []
            for job in data['results']:
                job_title = job.get('title', '').upper()
                # Filter by job title - must contain "SOFTWARE ENGINEER"
                if 'SOFTWARE ENGINEER' not in job_title:
                    continue
                
                filtered_results.append(job)
            data['results'] = filtered_results
        
        return data
    except requests.exceptions.RequestException as error:
        print(f'Error calling Adzuna API: {error}')
        if hasattr(error.response, 'text'):
            print(f'Response: {error.response.text}')
        raise


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
        filename: Optional filename (default: adzuna_jobs_YYYYMMDD_HHMMSS.csv)
    
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
        filename = f"adzuna_{timestamp}.csv"
    
    # Save to csv subfolder
    filepath = os.path.join(csv_dir, filename)
    
    # Normalize all jobs
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
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(normalized_jobs)
    
    print(f"Exported {len(normalized_jobs)} job postings to {filepath}")
    return filepath


if __name__ == "__main__":
    # Example usage: Software Engineer
    try:
        result = test_adzuna_api(
            page=1,
            keywords="Software Engineer",
            results_per_page=50
        )
        jobs = result.get("results", [])
        print(f"Retrieved {len(jobs)} Software Engineer job postings")
        
        # Export to CSV
        if jobs:
            csv_file = export_to_csv(jobs)
            if csv_file:
                print(f"\nCSV file created: {csv_file}")
        
        print(json.dumps(jobs[:2], indent=2))  # Print first 2 jobs
    except ValueError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"Test failed: {e}")

