"""
Test API Call for Jobicy
Endpoint: GET https://jobicy.com/api/v2/remote-jobs

This file demonstrates how to make a test API call to Jobicy.
Type: Job aggregator API
Auth: None
Coverage: Remote jobs aggregated from multiple sources
"""

import requests
import json
import csv
import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional


def test_jobicy_api(tag: Optional[str] = None,
                    industry: Optional[str] = None,
                    geo: Optional[str] = None,
                    count: Optional[int] = None) -> Dict[str, Any]:
    """
    Make a test API call to Jobicy endpoint.
    
    Args:
        tag: Optional search by job title and description (default: "Software Engineer")
        industry: Optional job category filter (e.g., "engineering", "marketing")
        geo: Optional geographic filter (e.g., "usa", "canada", "emea")
        count: Optional number of listings to return (default: 100, range: 1-100)
    
    Returns:
        Dictionary containing job postings from Jobicy API (all jobs are remote)
    """
    try:
        url = 'https://jobicy.com/api/v2/remote-jobs'
        params = {}
        
        # Use tag parameter for search (searches job title and description)
        if tag:
            params['tag'] = tag
        else:
            params['tag'] = "Software Engineer"
        
        # Use industry parameter for job category filter
        if industry:
            params['industry'] = industry
        
        # Use geo parameter for geographic filter
        if geo:
            params['geo'] = geo
        
        # Use count parameter (default: 100, range: 1-100)
        if count:
            # Ensure count is within valid range
            count = max(1, min(100, count))
            params['count'] = count
        
        # Add headers to make request look like a browser (bypass Cloudflare protection)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://jobicy.com/',
            'Origin': 'https://jobicy.com',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        }
        
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        return data
    except requests.exceptions.RequestException as error:
        print(f'Error calling Jobicy API: {error}')
        if hasattr(error, 'response') and error.response is not None:
            print(f'Response: {error.response.text}')
        raise


def normalize_jobicy_job(job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize Jobicy job data to include all mapped fields.
    
    Args:
        job: Raw job data from Jobicy API
    
    Returns:
        Normalized job data with all required fields
    """
    # Extract salary from API response (salaryMin and salaryMax are provided directly)
    salary_min = job.get('salaryMin')
    salary_max = job.get('salaryMax')
    
    # Normalize jobIndustry (array) and jobType (array) into tags
    tags_list = []
    
    # Add jobIndustry to tags
    job_industry = job.get('jobIndustry', [])
    if isinstance(job_industry, list):
        tags_list.extend([str(industry) for industry in job_industry if industry])
    elif job_industry:
        tags_list.append(str(job_industry))
    
    # Add jobType to tags
    job_type = job.get('jobType', [])
    if isinstance(job_type, list):
        tags_list.extend([str(jt) for jt in job_type if jt])
    elif job_type:
        tags_list.append(str(job_type))
    
    # Add jobLevel to tags if available
    job_level = job.get('jobLevel', '')
    if job_level and job_level != 'Any':
        tags_list.append(str(job_level))
    
    tags_str = '; '.join(tags_list) if tags_list else ''
    
    # Clean description (jobDescription contains HTML)
    description = job.get('jobDescription', '')
    clean_description = re.sub(r'<[^>]+>', '', description)
    clean_description = ' '.join(clean_description.split())
    
    # Extract publication date (pubDate in UTC+00:00 format)
    publication_date = job.get('pubDate', '')
    
    # Extract location (jobGeo - geographic restriction or "Anywhere")
    location = job.get('jobGeo', 'Remote')
    if not location or location == 'Anywhere':
        location = 'Remote'
    
    return {
        'Company': job.get('companyName', 'N/A'),
        'Position': job.get('jobTitle', 'N/A'),
        'Location': location,
        'Tags': tags_str,
        'Description': clean_description,
        'URL': job.get('url', 'N/A'),
        'Salary_Min': salary_min if salary_min else '',
        'Salary_Max': salary_max if salary_max else '',
        'Date': publication_date,
        'ID': job.get('id', 'N/A')
    }


def fetch_top_cs_jobs(geo: str = "usa", 
                      min_count: int = 100,
                      use_top_25: bool = True) -> List[Dict[str, Any]]:
    """
    Fetch 100+ top Computer Science jobs by making multiple API calls with different search terms.
    Uses the top 25 most popular CS job titles from 2026.
    
    Args:
        geo: Geographic filter (default: "usa")
        min_count: Minimum number of jobs to fetch (default: 100)
        use_top_25: If True, use top 25 job titles; if False, use top 10 only
    
    Returns:
        List of unique job postings (deduplicated by ID)
    """
    # Top 25 Most Popular Computer Science Job Titles (2026)
    top_25_job_titles = [
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
    
    # Top 10 for faster searches
    top_10_job_titles = top_25_job_titles[:10]
    
    # Use top 25 or top 10 based on parameter
    search_terms = top_25_job_titles if use_top_25 else top_10_job_titles
    
    all_jobs = []
    seen_ids = set()
    
    print(f"Fetching Top {len(search_terms)} Computer Science jobs from {geo.upper()}...")
    print(f"Target: {min_count}+ jobs\n")
    
    for i, search_term in enumerate(search_terms, 1):
        try:
            print(f"[{i}/{len(search_terms)}] Searching for: '{search_term}'...")
            result = test_jobicy_api(
                tag=search_term,
                geo=geo,
                count=100  # Get max allowed per call
            )
            
            jobs = result.get("jobs", [])
            job_count = result.get("jobCount", len(jobs))
            
            # Deduplicate jobs by ID
            new_jobs = []
            for job in jobs:
                job_id = job.get('id')
                
                # Only include if we haven't seen this ID
                if job_id and job_id not in seen_ids:
                    seen_ids.add(job_id)
                    new_jobs.append(job)
            
            all_jobs.extend(new_jobs)
            print(f"  → Found {len(new_jobs)} new unique jobs (Total: {len(all_jobs)})\n")
            
            # Stop if we've reached our target
            if len(all_jobs) >= min_count:
                print(f"✓ Reached target of {min_count}+ jobs!\n")
                break
                
        except Exception as e:
            print(f"  ✗ Error fetching '{search_term}': {e}\n")
            continue
    
    # Final deduplication by ID (just to be safe)
    unique_jobs = {}
    for job in all_jobs:
        job_id = job.get('id')
        if job_id and job_id not in unique_jobs:
            unique_jobs[job_id] = job
    
    final_jobs = list(unique_jobs.values())
    
    print(f"Final count: {len(final_jobs)} unique Computer Science jobs from {geo.upper()}")
    return final_jobs


def export_to_csv(jobs: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
    """
    Export job postings to a CSV file.
    
    Args:
        jobs: List of job postings (raw API response)
        filename: Optional filename (default: jobicy_YYYYMMDD_HHMMSS.csv)
    
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
        filename = f"jobicy_{timestamp}.csv"
    
    # Save to csv subfolder
    filepath = os.path.join(csv_dir, filename)
    
    # Normalize all jobs
    normalized_jobs = [normalize_jobicy_job(job) for job in jobs]
    
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
    # Fetch 100+ Top Computer Science jobs from USA
    try:
        print("Jobicy API - Top Computer Science Jobs Search (100+ roles)")
        print("Using Top 25 Most Popular CS Job Titles (2026)")
        print("=" * 70)
        print()
        
        # Fetch multiple batches to get 100+ jobs using top 25 job titles
        jobs = fetch_top_cs_jobs(
            geo="usa",
            min_count=100,
            use_top_25=True  # Set to False to use only top 10 for faster results
        )
        
        if jobs:
            print(f"\n{'='*70}")
            print(f"Successfully retrieved {len(jobs)} unique Computer Science jobs from USA")
            print(f"{'='*70}\n")
            
            # Export to CSV
            csv_file = export_to_csv(jobs)
            if csv_file:
                print(f"\n✓ CSV file created: {csv_file}")
            
            # Show statistics
            print(f"\n{'='*70}")
            print("Job Statistics:")
            print(f"{'='*70}")
            
            # Count by job title (matching top 25)
            top_titles = [
                "AI Engineer", "Machine Learning Engineer", "Cybersecurity Analyst",
                "Software Engineer", "Data Scientist", "Cloud Architect", "Data Engineer",
                "DevOps Engineer", "AI Consultant", "Technical Product Manager",
                "Full-Stack Developer", "AI/ML Researcher", "Data Architect", "Security Engineer",
                "Network Engineer", "Blockchain Developer", "Systems Analyst", "UX/UI Designer",
                "Datacenter Technician", "Quantitative Researcher", "Mobile App Developer",
                "Ethical Hacker", "Database Administrator", "SRE", "Solutions Architect"
            ]
            
            title_counts = {}
            for job in jobs:
                job_title = job.get('jobTitle', '').upper()
                # Match against top titles
                for title in top_titles:
                    title_upper = title.upper()
                    # Check if job title contains the search term
                    if title_upper in job_title or any(word in job_title for word in title_upper.split() if len(word) > 3):
                        title_counts[title] = title_counts.get(title, 0) + 1
                        break
            
            if title_counts:
                print(f"\nBy Job Title (Top 25 Matches):")
                for title, count in sorted(title_counts.items(), key=lambda x: x[1], reverse=True):
                    print(f"  {title}: {count}")
            
            # Count by job level
            levels = {}
            for job in jobs:
                level = job.get('jobLevel', 'Any')
                levels[level] = levels.get(level, 0) + 1
            
            if levels:
                print(f"\nBy Seniority Level:")
                for level, count in sorted(levels.items(), key=lambda x: x[1], reverse=True):
                    print(f"  {level}: {count}")
            
            # Count by job type
            types = {}
            for job in jobs:
                job_types = job.get('jobType', [])
                if isinstance(job_types, list):
                    for jt in job_types:
                        types[jt] = types.get(jt, 0) + 1
                elif job_types:
                    types[job_types] = types.get(job_types, 0) + 1
            
            if types:
                print(f"\nBy Job Type:")
                for jt, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
                    print(f"  {jt}: {count}")
            
            # Show sample jobs
            print(f"\n{'='*70}")
            print("Sample jobs (first 3):")
            print(f"{'='*70}\n")
            for i, job in enumerate(jobs[:3], 1):
                print(f"{i}. {job.get('jobTitle', 'N/A')}")
                print(f"   Company: {job.get('companyName', 'N/A')}")
                print(f"   Location: {job.get('jobGeo', 'Remote')}")
                print(f"   Level: {job.get('jobLevel', 'Any')}")
                if job.get('salaryMin') and job.get('salaryMax'):
                    print(f"   Salary: ${job.get('salaryMin'):,} - ${job.get('salaryMax'):,} {job.get('salaryCurrency', 'USD')}")
                print(f"   URL: {job.get('url', 'N/A')}")
                print()
        else:
            print("\n✗ No jobs found matching the criteria.")
            
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()

