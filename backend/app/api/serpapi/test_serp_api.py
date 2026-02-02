"""
Test API Call for SerpAPI (Google Jobs)
Endpoint: GET https://serpapi.com/search.json?engine=google_jobs

This file demonstrates how to make a test API call to SerpAPI for Google Jobs search.
Type: Job search API (aggregates Google Jobs results)
Auth: API key required
Coverage: Google Jobs search results from various sources

Note: Requires the google-search-results package
Install with: pip install google-search-results
"""

try:
    from serpapi import GoogleSearch
except ImportError:
    print("Error: serpapi library not found.")
    print("Please install it with: pip install google-search-results")
    raise
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

# SerpAPI Credentials
# Loaded from environment variables
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")


def test_serpapi_google_jobs(query: str = "Software Engineer",
                             location: str = "United States",
                             api_key: Optional[str] = None,
                             num: int = 100,
                             next_page_token: Optional[str] = None) -> Dict[str, Any]:
    """
    Make a test API call to SerpAPI Google Jobs endpoint.
    
    Args:
        query: Search query (job title/keywords) (default: "Software Engineer")
        location: Location filter (default: "United States")
        api_key: SerpAPI API key (defaults to SERPAPI_API_KEY)
        num: Number of results to return (default: 100, max typically 100)
        next_page_token: Token for pagination (from previous response)
    
    Returns:
        Dictionary containing job postings from SerpAPI Google Jobs
        Structure: {"jobs_results": [list of jobs], "next_page_token": token for next page}
    
    Raises:
        ValueError: If api_key is not provided
    """
    try:
        # Use provided API key or default
        api_key_value = api_key or SERPAPI_API_KEY
        
        if not api_key_value:
            raise ValueError(
                "SerpAPI requires an API key. "
                "Please provide an api_key parameter or set SERPAPI_API_KEY in the .env file."
            )
        
        # Build search parameters
        # Note: Google Jobs API no longer supports 'start' parameter, use 'next_page_token' instead
        params = {
            "engine": "google_jobs",
            "q": query,
            "location": location,
            "google_domain": "google.com",
            "hl": "en",
            "gl": "us",
            "api_key": api_key_value,
            "num": num
        }
        
        # Add next_page_token if provided (for pagination)
        if next_page_token:
            params["next_page_token"] = next_page_token
        
        # Perform the search
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Debug: Check what we got back
        if "error" in results:
            error_msg = results.get("error", "Unknown error")
            print(f"SerpAPI Error: {error_msg}")
            if "Invalid API key" in error_msg:
                raise ValueError("Invalid SerpAPI API key. Please check your API key.")
            raise Exception(f"SerpAPI API error: {error_msg}")
        
        # Extract jobs results
        jobs_results = results.get("jobs_results", [])
        
        # Extract pagination token - check multiple possible locations
        next_page_token = None
        if "pagination" in results:
            pagination = results.get("pagination", {})
            next_page_token = pagination.get("next_page_token") or pagination.get("next")
        elif "serpapi_pagination" in results:
            next_page_token = results.get("serpapi_pagination", {}).get("next_page_token")
        
        # Debug output
        if not jobs_results:
            print(f"Warning: No jobs_results found in response.")
            print(f"Response keys: {list(results.keys())}")
            if "search_information" in results:
                print(f"Search info: {results.get('search_information', {})}")
        
        return {
            "jobs_results": jobs_results,
            "search_metadata": results.get("search_metadata", {}),
            "search_parameters": results.get("search_parameters", {}),
            "next_page_token": next_page_token,
            "raw_response": results  # Include full response for debugging
        }
    except Exception as error:
        print(f'Error calling SerpAPI: {error}')
        import traceback
        traceback.print_exc()
        raise


def normalize_serpapi_job(job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize SerpAPI Google Jobs data to include all mapped fields.
    
    Args:
        job: Raw job data from SerpAPI Google Jobs API
    
    Returns:
        Normalized job data with all required fields
    """
    # Extract job title
    job_title = job.get('title', 'N/A')
    
    # Extract company name
    company = job.get('company_name', 'N/A')
    
    # Extract location
    location = job.get('location', 'N/A')
    
    # Extract description
    description = job.get('description', '')
    if not description:
        # Try alternative description fields
        description = job.get('snippet', '') or job.get('job_highlights', {}).get('description', '')
    
    # Clean description - remove HTML tags and normalize whitespace
    if isinstance(description, str):
        clean_description = re.sub(r'<[^>]+>', '', description)
        clean_description = ' '.join(clean_description.split())
    elif isinstance(description, list):
        # If description is a list, join it
        clean_description = ' '.join([str(d) for d in description])
    else:
        clean_description = str(description) if description else ''
    
    # Extract URL
    url = job.get('apply_options', [{}])[0].get('link', '') if job.get('apply_options') else ''
    if not url:
        url = job.get('related_links', [{}])[0].get('link', '') if job.get('related_links') else ''
    if not url:
        url = job.get('link', 'N/A')
    
    # Extract salary/pay information
    salary_min = ''
    salary_max = ''
    
    # Try multiple sources for salary information
    salary_sources = [
        job.get('detected_extensions', {}).get('salary'),
        job.get('salary'),
        job.get('compensation', {}).get('base_salary', {}).get('value', {}).get('min_value'),
    ]
    
    for salary_data in salary_sources:
        if salary_data:
            salary_str = str(salary_data)
            # Try to parse salary range (e.g., "$100,000 - $150,000", "$100k - $150k")
            # Pattern 1: Full numbers with commas
            salary_range = re.findall(r'\$?([\d,]+)', salary_str)
            if len(salary_range) >= 2:
                salary_min = salary_range[0].replace(',', '')
                salary_max = salary_range[1].replace(',', '')
                break
            elif len(salary_range) == 1:
                salary_min = salary_range[0].replace(',', '')
                salary_max = salary_min
                break
            # Pattern 2: Numbers with 'k' suffix (e.g., "$100k - $150k")
            k_range = re.findall(r'\$?(\d+)k', salary_str, re.IGNORECASE)
            if len(k_range) >= 2:
                salary_min = str(int(k_range[0]) * 1000)
                salary_max = str(int(k_range[1]) * 1000)
                break
            elif len(k_range) == 1:
                salary_min = str(int(k_range[0]) * 1000)
                salary_max = salary_min
                break
    
    # Extract job highlights/tags
    job_highlights = job.get('job_highlights', [])
    tags = []
    if isinstance(job_highlights, list):
        for highlight in job_highlights:
            if isinstance(highlight, dict):
                tags.append(highlight.get('title', ''))
            else:
                tags.append(str(highlight))
    tags_str = '; '.join([tag for tag in tags if tag]) if tags else ''
    
    # Extract date (if available)
    date = job.get('posted_at', job.get('schedule_type', 'N/A'))
    
    # Extract job ID
    job_id = job.get('job_id', job.get('title', 'N/A'))
    
    return {
        'Company': company,
        'Position': job_title,
        'Location': location,
        'Tags': tags_str,
        'Description': clean_description,
        'URL': url,
        'Salary_Min': salary_min,
        'Salary_Max': salary_max,
        'Date': date,
        'ID': job_id
    }


def export_to_csv(jobs: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
    """
    Export job postings to a CSV file.
    
    Args:
        jobs: List of job postings (raw API response)
        filename: Optional filename (default: serpapi_jobs_YYYYMMDD_HHMMSS.csv)
    
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
        filename = f"serpapi_{timestamp}.csv"
    
    # Save to csv subfolder
    filepath = os.path.join(csv_dir, filename)
    
    # Normalize all jobs
    normalized_jobs = [normalize_serpapi_job(job) for job in jobs]
    
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


def export_to_json(jobs: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
    """
    Export raw job postings to a JSON file (same data shown in terminal).
    
    Args:
        jobs: List of job postings (raw API response)
        filename: Optional filename (default: serpapi_jobs_YYYYMMDD_HHMMSS.json)
    
    Returns:
        Path to the created JSON file
    """
    if not jobs:
        print("No jobs to export to JSON")
        return ""
    
    # Create csv directory if it doesn't exist (reuse same directory as CSV)
    json_dir = os.path.join(os.path.dirname(__file__), 'csv')
    os.makedirs(json_dir, exist_ok=True)
    
    # Generate filename if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H_%M_%S")
        filename = f"serpapi_{timestamp}.json"
    
    # Save to csv subfolder (same location as CSV files)
    filepath = os.path.join(json_dir, filename)
    
    # Write raw JSON data (same format as shown in terminal)
    with open(filepath, 'w', encoding='utf-8') as jsonfile:
        json.dump(jobs, jsonfile, indent=2, ensure_ascii=False)
    
    print(f"Exported {len(jobs)} job postings (raw JSON) to {filepath}")
    return filepath


if __name__ == "__main__":
    # Example usage: Software Engineer in United States
    try:
        print("SerpAPI Google Jobs - Software Engineer Search")
        print("=" * 60)
        
        # Fetch multiple pages to get up to 100 jobs
        # Google Jobs API returns ~10 jobs per page, so we need to paginate
        all_jobs = []
        next_token = None
        max_jobs = 100
        page_count = 0
        max_pages = 10  # Limit to prevent infinite loops
        
        print(f"Fetching up to {max_jobs} jobs (may require multiple pages)...")
        
        while len(all_jobs) < max_jobs and page_count < max_pages:
            page_count += 1
            print(f"  Fetching page {page_count}...", end=" ")
            
            result = test_serpapi_google_jobs(
                query="Software Engineer",
                location="United States",
                num=100,  # Request 100 per page (API may still limit to ~10)
                next_page_token=next_token
            )
            
            page_jobs = result.get("jobs_results", [])
            all_jobs.extend(page_jobs)
            next_token = result.get("next_page_token")
            
            print(f"Got {len(page_jobs)} jobs (Total: {len(all_jobs)})")
            
            # Debug: Check pagination info
            if not next_token and page_count == 1:
                raw_response = result.get("raw_response", {})
                print(f"    Debug: Checking for pagination token...")
                print(f"    Response keys: {list(raw_response.keys())}")
                if "pagination" in raw_response:
                    print(f"    Pagination data: {raw_response.get('pagination')}")
            
            # If no more pages or no next token, stop
            if not next_token or len(page_jobs) == 0:
                if not next_token:
                    print(f"    No more pages available (no next_page_token)")
                break
        
        jobs = all_jobs[:max_jobs]  # Limit to exactly max_jobs if we got more
        print(f"\nRetrieved {len(jobs)} job postings total")
        
        # Debug: Show response structure if no jobs
        if not jobs:
            print("\nDebugging information:")
            print(f"Search metadata: {result.get('search_metadata', {})}")
            print(f"Search parameters: {result.get('search_parameters', {})}")
            raw_response = result.get("raw_response", {})
            if "error" in raw_response:
                print(f"API Error: {raw_response.get('error')}")
            elif "jobs_results" not in raw_response:
                print(f"Available keys in response: {list(raw_response.keys())}")
                # Try to find jobs in alternative locations
                for key in raw_response.keys():
                    if 'job' in key.lower() or 'result' in key.lower():
                        print(f"  Found key '{key}': {type(raw_response[key])}")
        
        # Export to CSV and JSON
        if jobs:
            # Use same timestamp for both files to match them up
            timestamp = datetime.now().strftime("%Y%m%d_%H_%M_%S")
            
            csv_file = export_to_csv(jobs, filename=f"serpapi_{timestamp}.csv")
            if csv_file:
                print(f"\nCSV file created: {csv_file}")
            
            # Export raw JSON (all jobs, same format as shown in terminal)
            json_file = export_to_json(jobs, filename=f"serpapi_{timestamp}.json")
            if json_file:
                print(f"JSON file created: {json_file}")
                print(f"  (Contains all {len(jobs)} jobs in raw API format)")
        
        # Show sample jobs
        if jobs:
            print("\nSample jobs (first 2):")
            print(json.dumps(jobs[:2], indent=2))
        else:
            print("\nNo jobs found. This might indicate:")
            print("  - API key issue (check if key is valid)")
            print("  - Rate limit reached")
            print("  - No jobs match the search criteria")
            print("  - API response structure may be different")
    except ValueError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
