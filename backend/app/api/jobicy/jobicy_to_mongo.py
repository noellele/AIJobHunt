"""
Jobicy API → MongoDB ingestion.

Fetches job postings from the Jobicy API for each title in TOP_JOBS (top_jobs.py),
normalizes them, maps to the canonical job schema (job_schema.to_canonical_document
via mongo_ingestion_utils), and appends to a MongoDB collection.

Env: MONGODB_CONNECT_STRING, PROD_DB, MONGO_JOBS_COLLECTION (optional).
Data source label: "Jobicy".

Run from backend: python app/api/jobicy/jobicy_to_mongo.py
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
    from backend.app.api.top_jobs import TOP_JOBS
except ImportError:
    import sys
    _api_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if _api_dir not in sys.path:
        sys.path.insert(0, _api_dir)
    from top_jobs import TOP_JOBS

try:
    from backend.app.api.jobicy.jobicy_fetch_top_jobs import fetch_all_top_jobs
except ImportError:
    from jobicy_fetch_top_jobs import fetch_all_top_jobs

try:
    from backend.app.api.jobicy.test_jobicy_api import normalize_jobicy_job
except ImportError:
    from test_jobicy_api import normalize_jobicy_job


def run(
    job_titles: Optional[List[str]] = None,
    industry: Optional[str] = None,
    geo: Optional[str] = None,
    count_per_tag: Optional[int] = 100,
) -> int:
    """Fetch jobs from Jobicy for each title in TOP_JOBS (or given list), dedupe, and insert into MongoDB.
    Documents are normalized then mapped to the canonical schema (job_schema) by insert_jobs_into_mongo.
    Returns count inserted."""
    titles = job_titles or TOP_JOBS
    print("Jobicy → MongoDB (Top Jobs)")
    print("=" * 50)
    all_jobs = fetch_all_top_jobs(
        job_titles=titles,
        industry=industry,
        geo=geo,
        count_per_tag=count_per_tag or 100,
    )
    print(f"Retrieved {len(all_jobs)} unique job postings from Jobicy.")
    count_inserted = run_ingestion(
        source="Jobicy",
        normalizer=normalize_jobicy_job,
        fetch_jobs=lambda: all_jobs,
    )
    print(f"Inserted {count_inserted} documents into MongoDB.")
    return count_inserted


if __name__ == "__main__":
    try:
        run()
        print("Done.")
    except ValueError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"Error: {e}")
        raise
