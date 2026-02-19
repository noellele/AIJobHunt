"""
Adzuna API → MongoDB ingestion (Top Jobs).

Fetches job postings from the Adzuna API for the TOP_JOBS list,
normalizes them, and inserts into a MongoDB collection.

Env: MONGODB_CONNECT_STRING, PROD_DB, MONGO_JOBS_COLLECTION (from .env).
Data source label: "Adzuna (Top Jobs)".

Run from backend: python app/api/adzuna/adzuna_top_jobs_to_mongo.py
"""

import os
from typing import List, Dict, Any, Optional

try:
    from backend.app.api.data_ingestor import run_ingestion
except ImportError:
    import sys
    _api_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if _api_dir not in sys.path:
        sys.path.insert(0, _api_dir)
    from data_ingestor import run_ingestion

try:
    from backend.app.api.adzuna.adzuna_fetch_top_jobs import fetch_all_top_jobs
    from backend.app.api.adzuna.test_adzuna_api import normalize_adzuna_job
    from backend.app.api.top_jobs import TOP_JOBS
except ImportError:
    from adzuna_fetch_top_jobs import fetch_all_top_jobs
    from test_adzuna_api import normalize_adzuna_job
    import sys
    _api_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if _api_dir not in sys.path:
        sys.path.insert(0, _api_dir)
    from top_jobs import TOP_JOBS


def run(
    job_titles: Optional[List[str]] = None,
    results_per_page: int = 50,
    max_pages_per_job: int = 1,
) -> int:
    """Fetch jobs from Adzuna for the top jobs list (or given titles), then insert into MongoDB."""
    print("Adzuna → MongoDB (Top Jobs)")
    print("=" * 50)
    titles = job_titles or TOP_JOBS
    all_jobs = fetch_all_top_jobs(
        job_titles=titles,
        results_per_page=results_per_page,
        max_pages_per_job=max_pages_per_job,
    )
    print(f"Retrieved {len(all_jobs)} job postings from Adzuna.")
    count = run_ingestion(
        source="Adzuna",
        normalizer=normalize_adzuna_job,
        fetch_jobs=lambda: all_jobs,
    )
    print(f"Inserted {count} documents into MongoDB.")
    return count


if __name__ == "__main__":
    try:
        run(
            job_titles=TOP_JOBS,
            results_per_page=50,
            max_pages_per_job=1,
        )
        print("Done.")
    except ValueError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"Error: {e}")
        raise
