"""
Jobicy: fetch all jobs for a list of job titles.

Core utility (non-test) that loops over job_titles, calls the Jobicy API per title,
aggregates results and dedupes by job id. No default job list; callers pass job_titles
(e.g. from top_jobs.TOP_JOBS).
"""

from typing import List, Dict, Any, Optional

try:
    from backend.app.api.jobicy.test_jobicy_api import test_jobicy_api
except ImportError:
    from test_jobicy_api import test_jobicy_api


def fetch_all_top_jobs(
    job_titles: List[str],
    industry: Optional[str] = None,
    geo: Optional[str] = None,
    count_per_tag: int = 100,
) -> List[Dict[str, Any]]:
    """
    Fetch jobs from Jobicy for each title in job_titles and dedupe by job id.

    Args:
        job_titles: List of job title strings to search for (no default; from top_jobs.TOP_JOBS).
        industry: Optional job category filter (e.g. "engineering", "marketing").
        geo: Optional geographic filter (e.g. "usa", "canada", "emea").
        count_per_tag: Number of listings per tag (default 100, range 1-100).

    Returns:
        Combined, deduplicated list of raw Jobicy job dicts.
    """
    all_jobs: List[Dict[str, Any]] = []
    seen_ids: set = set()

    for tag in job_titles:
        try:
            data = test_jobicy_api(tag=tag, industry=industry, geo=geo, count=count_per_tag)
        except Exception:
            continue
        jobs = data.get("jobs", [])
        for job in jobs:
            job_id = job.get("id")
            if job_id is not None and job_id not in seen_ids:
                seen_ids.add(job_id)
                all_jobs.append(job)

    return all_jobs
