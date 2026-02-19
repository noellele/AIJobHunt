"""
Adzuna: fetch all jobs for a list of job titles.

Core utility (non-test) that loops over job_titles, calls the Adzuna API per title/page,
aggregates results and dedupes by job id. No default job list; callers pass job_titles
(e.g. from top_jobs.TOP_JOBS).
"""

from typing import List, Dict, Any, Optional

try:
    from backend.app.api.adzuna.test_adzuna_api import test_adzuna_api
except ImportError:
    from test_adzuna_api import test_adzuna_api


def fetch_all_top_jobs(
    job_titles: List[str],
    results_per_page: int = 50,
    max_pages_per_job: int = 1,
) -> List[Dict[str, Any]]:
    """
    Fetch jobs from Adzuna for each title in job_titles, across pages, and dedupe by job id.

    Args:
        job_titles: List of job title strings to search for (no default; from top_jobs.TOP_JOBS).
        results_per_page: Number of results per API page (default 50).
        max_pages_per_job: Max pages to fetch per job title (default 1).

    Returns:
        Combined, deduplicated list of raw Adzuna job dicts.
    """
    all_jobs: List[Dict[str, Any]] = []
    seen_ids: set = set()

    for title in job_titles:
        for page in range(1, max_pages_per_job + 1):
            try:
                data = test_adzuna_api(
                    page=page,
                    keywords=title,
                    results_per_page=results_per_page,
                )
            except Exception:
                continue
            results = data.get("results") or []
            for job in results:
                job_id = job.get("id")
                if job_id is not None and job_id not in seen_ids:
                    seen_ids.add(job_id)
                    all_jobs.append(job)

    return all_jobs
