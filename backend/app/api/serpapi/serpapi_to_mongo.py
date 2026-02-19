"""
SerpAPI (Google Jobs) → MongoDB ingestion.

Fetches job postings from SerpAPI Google Jobs for the same TOP_JOBS list as Adzuna,
normalizes them, and appends to a MongoDB collection. Uses shared data_ingestor and mongo_ingestion_utils.

Env: MONGODB_CONNECT_STRING, PROD_DB, MONGO_JOBS_COLLECTION (optional), SERPAPI_API_KEY.
Data source label: "SerpAPI".

Run from backend dir (use venv Python so dotenv/packages are available):
  .\\venv\\Scripts\\python.exe app\\api\\serpapi\\serpapi_to_mongo.py
Or activate venv first, then:  python app\\api\\serpapi\\serpapi_to_mongo.py
Run from project root:  python backend\\app\\api\\serpapi\\serpapi_to_mongo.py  (use backend venv)
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
    from backend.app.api.serpapi.serpapi_fetch_top_jobs import fetch_all_top_jobs
except ImportError:
    from serpapi_fetch_top_jobs import fetch_all_top_jobs

try:
    from backend.app.api.serpapi.test_serp_api import normalize_serpapi_job
except ImportError:
    from test_serp_api import normalize_serpapi_job

try:
    from backend.app.api.top_jobs import TOP_JOBS
except ImportError:
    import sys
    _api_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if _api_dir not in sys.path:
        sys.path.insert(0, _api_dir)
    from top_jobs import TOP_JOBS


def run(
    job_titles: Optional[List[str]] = None,
    location: str = "United States",
    num: int = 100,
) -> int:
    """Fetch jobs from SerpAPI for each title in TOP_JOBS (or given list), dedupe, and insert into MongoDB."""
    titles = job_titles or TOP_JOBS
    print("SerpAPI (Google Jobs) → MongoDB (Top Jobs)")
    print("=" * 50)
    all_jobs = fetch_all_top_jobs(job_titles=titles, location=location, num=num)
    print(f"Retrieved {len(all_jobs)} unique job postings from SerpAPI.")
    count = run_ingestion(
        source="SerpAPI",
        normalizer=normalize_serpapi_job,
        fetch_jobs=lambda: all_jobs,
    )
    print(f"Inserted {count} documents into MongoDB.")
    return count


if __name__ == "__main__":
    try:
        run()
        print("Done.")
    except ValueError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"Error: {e}")
        raise
