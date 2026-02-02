"""
Test API Call for USAJobs
Endpoint: GET https://data.usajobs.gov/api/Search

This file demonstrates how to make a test API call to USAJobs.
Type: Government job aggregator API
Auth: API Key required
Coverage: United States federal government roles
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


def test_usajobs_api(keywords: Optional[str] = None,
                     page: Optional[int] = None,
                     api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Make a test API call to USAJobs endpoint.
    
    Args:
        keywords: Optional search keywords (default: "Software Engineer")
        page: Optional page number for pagination
        api_key: USAJobs API key (default: uses hardcoded key)
    
    Returns:
        Dictionary containing job postings from USAJobs API
        Returns all jobs with "Software Engineer" in the title
    """
    # USAJobs API key - loaded from environment variables
    if not api_key:
        api_key = os.getenv("USAJOBS_API_KEY")
        if not api_key:
            raise ValueError(
                "USAJobs API requires an API key. "
                "Please provide an api_key parameter or set USAJOBS_API_KEY in the .env file."
            )
    
    try:
        url = 'https://data.usajobs.gov/api/Search'
        params = {}
        params['Keyword'] = keywords or "Software Engineer"
        if page:
            params['Page'] = page
        
        # USAJobs API requires specific headers
        headers = {
            'Host': 'data.usajobs.gov',
            'User-Agent': 'OSU Job Search Application',
            'Authorization-Key': api_key
        }
        
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Post-process to filter by job title
        if 'SearchResult' in data and 'SearchResultItems' in data['SearchResult']:
            filtered_items = []
            
            for item in data['SearchResult']['SearchResultItems']:
                descriptor = item.get('MatchedObjectDescriptor', {})
                position_title = descriptor.get('PositionTitle', '').upper()
                
                # Filter by job title - must contain "SOFTWARE ENGINEER"
                if 'SOFTWARE ENGINEER' not in position_title:
                    continue
                
                filtered_items.append(item)
            
            data['SearchResult']['SearchResultItems'] = filtered_items
        
        return data
    except requests.exceptions.RequestException as error:
        print(f'Error calling USAJobs API: {error}')
        raise


def normalize_usajobs_job(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize USAJobs job data to include all mapped fields.
    
    Args:
        item: Raw job item from USAJobs API (SearchResultItems entry)
    
    Returns:
        Normalized job data with all required fields
    """
    descriptor = item.get('MatchedObjectDescriptor', {})
    user_area = descriptor.get('UserArea', {})
    details = user_area.get('Details', {})
    
    # Extract location
    locations = descriptor.get('PositionLocation', [])
    location = 'Remote'
    location_display = descriptor.get('PositionLocationDisplay', '')
    if locations:
        location = locations[0].get('LocationName', 'Remote')
    elif location_display:
        location = location_display
    
    # Extract salary
    remuneration = descriptor.get('PositionRemuneration', [])
    salary_min = None
    salary_max = None
    salary_rate = ''
    if remuneration:
        rem = remuneration[0]
        salary_min = rem.get('MinimumRange')
        salary_max = rem.get('MaximumRange')
        salary_rate = rem.get('Description', '')
    
    # Extract description from multiple sources
    descriptions = descriptor.get('PositionFormattedDescription', [])
    description = ''
    if descriptions:
        description = descriptions[0].get('Content', '')
    
    # Get JobSummary from UserArea.Details
    job_summary = details.get('JobSummary', '')
    
    # Combine description sources
    full_description = description
    if job_summary and job_summary not in description:
        full_description = f"{job_summary}\n\n{description}" if description else job_summary
    
    # Clean description
    clean_description = re.sub(r'<[^>]+>', '', full_description)
    clean_description = ' '.join(clean_description.split())
    
    # Extract Major Duties
    major_duties = details.get('MajorDuties', [])
    major_duties_str = ' | '.join(major_duties) if isinstance(major_duties, list) else str(major_duties)
    
    # Extract Job Category
    job_categories = descriptor.get('JobCategory', [])
    job_category_str = '; '.join([cat.get('Name', '') for cat in job_categories if isinstance(cat, dict)]) if job_categories else ''
    
    # Extract URL
    apply_uris = descriptor.get('ApplyURI', [])
    url = apply_uris[0] if apply_uris else descriptor.get('PositionURI', 'N/A')
    
    # Create tags from position and organization
    tags = ['government', 'federal']
    position_title = descriptor.get('PositionTitle', '').lower()
    if 'software' in position_title and 'engineer' in position_title:
        tags.append('software-engineering')
    if 'remote' in location.lower() or details.get('RemoteIndicator', False):
        tags.append('remote')
    if details.get('TeleworkEligible', False):
        tags.append('telework')
    tags_str = '; '.join(tags)
    
    # Extract additional fields
    education = details.get('Education', '')
    requirements = details.get('Requirements', '')
    how_to_apply = details.get('HowToApply', '')
    benefits = details.get('Benefits', '')
    security_clearance = details.get('SecurityClearance', '')
    
    # Clean text fields
    def clean_text(text):
        if not text:
            return ''
        cleaned = re.sub(r'<[^>]+>', '', str(text))
        return ' '.join(cleaned.split())
    
    return {
        'Company': descriptor.get('OrganizationName', 'N/A'),
        'Department': descriptor.get('DepartmentName', 'N/A'),
        'Position': descriptor.get('PositionTitle', 'N/A'),
        'PositionID': descriptor.get('PositionID', 'N/A'),
        'Location': location,
        'LocationDisplay': location_display,
        'JobCategory': job_category_str,
        'Tags': tags_str,
        'Description': clean_description[:5000] if len(clean_description) > 5000 else clean_description,  # Limit length
        'MajorDuties': clean_text(major_duties_str)[:2000] if len(major_duties_str) > 2000 else clean_text(major_duties_str),
        'Education': clean_text(education),
        'Requirements': clean_text(requirements)[:2000] if len(requirements) > 2000 else clean_text(requirements),
        'HowToApply': clean_text(how_to_apply),
        'Benefits': clean_text(benefits),
        'URL': url,
        'Salary_Min': salary_min if salary_min else '',
        'Salary_Max': salary_max if salary_max else '',
        'Salary_Rate': salary_rate,
        'StartDate': descriptor.get('PositionStartDate', 'N/A'),
        'EndDate': descriptor.get('PositionEndDate', 'N/A'),
        'ApplicationCloseDate': descriptor.get('ApplicationCloseDate', 'N/A'),
        'SecurityClearance': security_clearance,
        'TeleworkEligible': 'Yes' if details.get('TeleworkEligible', False) else 'No',
        'RemoteIndicator': 'Yes' if details.get('RemoteIndicator', False) else 'No',
        'ID': item.get('MatchedObjectId', 'N/A')
    }


def export_to_csv(items: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
    """
    Export job postings to a CSV file.
    
    Args:
        items: List of job items from USAJobs API (SearchResultItems)
        filename: Optional filename (default: usajobs_jobs_YYYYMMDD_HHMMSS.csv)
    
    Returns:
        Path to the created CSV file
    """
    if not items:
        print("No jobs to export")
        return ""
    
    # Create csv directory if it doesn't exist
    csv_dir = os.path.join(os.path.dirname(__file__), 'csv')
    os.makedirs(csv_dir, exist_ok=True)
    
    # Generate filename if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H_%M_%S")
        filename = f"usajobs_{timestamp}.csv"
    
    # Save to csv subfolder
    filepath = os.path.join(csv_dir, filename)
    
    # Normalize all jobs
    normalized_jobs = [normalize_usajobs_job(item) for item in items]
    
    # Define CSV columns in order
    fieldnames = [
        'Company',
        'Department',
        'Position',
        'PositionID',
        'Location',
        'LocationDisplay',
        'JobCategory',
        'Tags',
        'Description',
        'MajorDuties',
        'Education',
        'Requirements',
        'HowToApply',
        'Benefits',
        'URL',
        'Salary_Min',
        'Salary_Max',
        'Salary_Rate',
        'StartDate',
        'EndDate',
        'ApplicationCloseDate',
        'SecurityClearance',
        'TeleworkEligible',
        'RemoteIndicator',
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
        result = test_usajobs_api(
            keywords="Software Engineer"
        )
        items = result.get("SearchResult", {}).get("SearchResultItems", [])
        print(f"Retrieved {len(items)} Software Engineer job postings")
        
        # Export to CSV
        if items:
            csv_file = export_to_csv(items)
            if csv_file:
                print(f"\nCSV file created: {csv_file}")
        
        print(json.dumps(items[:2], indent=2))  # Print first 2 jobs
    except Exception as e:
        print(f"Test failed: {e}")

