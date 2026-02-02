"""
Test API Call for The Muse
Endpoint: GET https://www.themuse.com/api/public/v2/jobs

This file demonstrates how to make a test API call to The Muse API.
Type: Job aggregator API
Auth: API key required (X-Muse-Api-Key header)
Coverage: Tech and professional job postings from various companies
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

# The Muse API Credentials
# Loaded from environment variables
MUSE_API_KEY = os.getenv("MUSE_API_KEY")


def test_muse_api(page: int = 1,
                  keywords: Optional[str] = None,
                  locations: Optional[str] = None,
                  company: Optional[str] = None,
                  level: Optional[str] = None,
                  categories: Optional[List[str]] = None,
                  descending: Optional[str] = None,
                  api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Make a test API call to The Muse endpoint.
    
    Based on actual API structure from The Muse website:
    https://www.themuse.com/api/public/jobs?category=Software%20Engineering&page=1&descending=descending
    
    Args:
        page: Page number for pagination (default: 1)
        keywords: Optional search keywords (filtered client-side after API call)
        locations: Optional location filter (e.g., "San Francisco Bay Area", "United States", "Culver City, CA")
                   Default: "United States" if not provided
        company: Optional company filter (e.g., "Google")
        level: Optional job level filter (e.g., "Internship", "Entry Level", "Mid Level", "Senior Level")
        categories: Optional list of job categories (e.g., ["Software Engineering", "IT"])
                   Default: All 9 tech categories if not provided
        descending: Optional sort order - use "descending" for descending order
        api_key: The Muse API key (defaults to MUSE_API_KEY)
    
    Returns:
        Dictionary containing job postings from The Muse API
        Returns all jobs with "Software Engineer" in the title (filtered client-side)
    
    Raises:
        ValueError: If api_key is not provided
    """
    try:
        # Use provided API key or default
        api_key_value = api_key or MUSE_API_KEY
        
        if not api_key_value:
            raise ValueError(
                "The Muse API requires an API key. "
                "Please provide an api_key parameter or set MUSE_API_KEY in the .env file."
            )
        
        # Set headers with API key
        headers = {
            'X-Muse-Api-Key': api_key_value
        }
        
        # Use the actual API endpoint (not v2)
        url = 'https://www.themuse.com/api/public/jobs'
        
        # Build query parameters based on actual API structure
        # The API supports multiple category parameters
        params = []
        
        # Add page parameter
        params.append(('page', page))
        
        # Add categories - API supports multiple category parameters
        # Based on: https://www.themuse.com/api/public/jobs?category=Computer%20and%20IT&category=Data%20and%20Analytics&category=Data%20Science&category=Design%20and%20UX&category=IT&category=Science%20and%20Engineering&category=Software%20Engineer&category=Software%20Engineering&category=UX&page=20&descending=descending
        if categories:
            for cat in categories:
                params.append(('category', cat))
        else:
            # Default categories matching the example URL
            default_categories = [
                "Computer and IT",
                "Data and Analytics",
                "Data Science",
                "Design and UX",
                "IT",
                "Science and Engineering",
                "Software Engineer",
                "Software Engineering",
                "UX"
            ]
            for cat in default_categories:
                params.append(('category', cat))
        
        # Add descending parameter if specified
        if descending:
            params.append(('descending', descending))
        else:
            # Default to descending order (newest first)
            params.append(('descending', 'descending'))
        
        # Add location parameter - default to United States if not specified
        if locations:
            params.append(('location', locations))
        else:
            # Default to United States to filter for US-based jobs
            params.append(('location', 'United States'))
        
        # Add other optional parameters
        if company:
            params.append(('company', company))
        if level:
            params.append(('level', level))
        
        # Make the request - use params as list of tuples to allow multiple category params
        response = requests.get(url, params=params, headers=headers)
        
        response.raise_for_status()
        data = response.json()
        
        # Post-process to filter by job title if keywords provided
        # Handle both 'results' array and direct array response
        jobs_list = data.get('results', []) if isinstance(data, dict) else data
        
        # Filter by keywords if provided
        if keywords:
            filtered_results = []
            search_term = keywords.lower()
            
            for job in jobs_list:
                # Job title is in the 'name' field based on API structure
                job_title = str(job.get('name', '')).lower()
                # Filter by job title - must contain search term
                if search_term in job_title:
                    filtered_results.append(job)
            
            # Return filtered results
            if isinstance(data, dict):
                data['results'] = filtered_results
                return data
            else:
                return {'results': filtered_results}
        
        # Return all results if no keyword filter
        return data if isinstance(data, dict) else {'results': jobs_list}
    except requests.exceptions.RequestException as error:
        print(f'Error calling The Muse API: {error}')
        if hasattr(error, 'response') and error.response is not None:
            print(f'Response: {error.response.text}')
        raise


def normalize_muse_job(job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize The Muse job data to include all mapped fields.
    
    Args:
        job: Raw job data from The Muse API
    
    Returns:
        Normalized job data with all required fields
    """
    # Extract company name
    company = job.get('company', {})
    if isinstance(company, dict):
        company = company.get('name', 'N/A')
    
    # Extract location
    locations = job.get('locations', [])
    location = 'Remote'
    if locations:
        # Get the first location's name
        first_location = locations[0]
        if isinstance(first_location, dict):
            location = first_location.get('name', 'Remote')
        else:
            location = str(first_location)
    
    # Extract tags/categories
    categories = job.get('categories', [])
    tags = []
    for cat in categories:
        if isinstance(cat, dict):
            tags.append(cat.get('name', ''))
        else:
            tags.append(str(cat))
    
    # Add level if available
    level = job.get('levels', [])
    if level:
        for lvl in level:
            if isinstance(lvl, dict):
                tags.append(lvl.get('name', ''))
            else:
                tags.append(str(lvl))
    
    tags_str = '; '.join([tag for tag in tags if tag]) if tags else ''
    
    # Extract description
    contents = job.get('contents', '')
    description = ''
    if isinstance(contents, str):
        description = contents
    elif isinstance(contents, dict):
        description = contents.get('description', '')
    
    # Clean description
    clean_description = re.sub(r'<[^>]+>', '', description)
    clean_description = ' '.join(clean_description.split())
    
    # Extract publication date
    publication_date = job.get('publication_date', 'N/A')
    
    # Extract URL
    refs = job.get('refs', {})
    url = refs.get('landing_page', 'N/A') if isinstance(refs, dict) else 'N/A'
    
    # Extract salary information (if available)
    salary_min = job.get('salary_min', '')
    salary_max = job.get('salary_max', '')
    
    return {
        'Company': company,
        'Position': job.get('name', 'N/A'),
        'Location': location,
        'Tags': tags_str,
        'Description': clean_description,
        'URL': url,
        'Salary_Min': salary_min if salary_min else '',
        'Salary_Max': salary_max if salary_max else '',
        'Date': publication_date,
        'ID': job.get('id', 'N/A')
    }


def export_to_csv(jobs: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
    """
    Export job postings to a CSV file.
    
    Args:
        jobs: List of job postings (raw API response)
        filename: Optional filename (default: muse_jobs_YYYYMMDD_HHMMSS.csv)
    
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
        filename = f"muse_{timestamp}.csv"
    
    # Save to csv subfolder
    filepath = os.path.join(csv_dir, filename)
    
    # Normalize all jobs
    normalized_jobs = [normalize_muse_job(job) for job in jobs]
    
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
        print("The Muse API - Software Engineer Jobs Search")
        print("=" * 60)
        
        # Use the actual API structure with multiple categories
        # Categories match: https://www.themuse.com/api/public/jobs?category=Computer%20and%20IT&category=Data%20and%20Analytics&category=Data%20Science&category=Design%20and%20UX&category=IT&category=Science%20and%20Engineering&category=Software%20Engineer&category=Software%20Engineering&category=UX&page=20&descending=descending
        # Location defaults to "United States" to filter for US-based jobs
        print("Fetching jobs from The Muse API (United States only)...")
        result = test_muse_api(
            page=1,
            keywords=None,  # Don't filter - get all results first
            locations="United States",  # Filter for United States jobs
            # Using default categories (all 9 categories from the example URL)
            # Or specify custom: categories=["Software Engineering", "IT"]
            descending="descending"  # Newest first
        )
        all_jobs = result.get("results", [])
        print(f"Retrieved {len(all_jobs)} total job postings from categories")
        
        # Now filter for Software Engineer
        if all_jobs:
            software_jobs = []
            for job in all_jobs:
                # Job title is in the 'name' field
                job_title = str(job.get('name', '')).lower()
                if 'software engineer' in job_title:
                    software_jobs.append(job)
            
            jobs = software_jobs
            print(f"Filtered to {len(jobs)} Software Engineer job postings")
            
            # If no exact matches but we have jobs, show what we got
            if not jobs and all_jobs:
                print(f"\nNote: Found {len(all_jobs)} jobs in selected categories, but none with 'Software Engineer' in title.")
                print("You may want to:")
                print("  - Try different pages (there are more results available)")
                print("  - Adjust the category filters")
                print("  - Search through more pages to find Software Engineer positions")
        else:
            jobs = []
            print("No jobs found on this page.")
        
        # Export to CSV (export all jobs from categories, not just filtered)
        if all_jobs:
            csv_file = export_to_csv(all_jobs)
            if csv_file:
                print(f"\nCSV file created with {len(all_jobs)} jobs: {csv_file}")
        
        # Show sample jobs
        if jobs:
            print("\nSample Software Engineer jobs (first 2):")
            print(json.dumps(jobs[:2], indent=2))
        elif all_jobs:
            print("\nSample jobs from categories (first 2):")
            print(json.dumps(all_jobs[:2], indent=2))
    except ValueError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

