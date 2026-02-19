"""
SerpAPI (Google Jobs): fetch all jobs for a list of job titles.

Core utility (non-test) that loops over job_titles, calls the SerpAPI Google Jobs API per query,
aggregates results and dedupes by a stable id. No default job list; callers pass job_titles
(e.g. from top_jobs.TOP_JOBS).
"""

from typing import List, Dict, Any

try:
    from backend.app.api.serpapi.test_serp_api import test_serpapi_google_jobs
except ImportError:
    from test_serp_api import test_serpapi_google_jobs


def fetch_all_top_jobs(
    job_titles: List[str],
    location: str = "United States",
    num: int = 100,
) -> List[Dict[str, Any]]:
    """
    Fetch jobs from SerpAPI Google Jobs for each title in job_titles and dedupe by stable id.

    Args:
        job_titles: List of job title/query strings (no default; from top_jobs.TOP_JOBS).
        location: Location string for the search (default "United States").
        num: Number of results per query (default 100).

    Returns:
        Combined, deduplicated list of raw SerpAPI job dicts.
    """
    all_jobs: List[Dict[str, Any]] = []
    seen_ids: set = set()

    for query in job_titles:
        try:
            result = test_serpapi_google_jobs(query=query, location=location, num=num)
        except Exception:
            continue
        jobs = result.get("jobs_results", [])
        for job in jobs:
            job_id = job.get("job_id") or (
                (job.get("title") or "") + "|" + (job.get("company_name") or "")
            )
            if job_id not in seen_ids:
                seen_ids.add(job_id)
                all_jobs.append(job)

    return all_jobs
