"""
USAJobs API → MongoDB ingestion.

Fetches job postings from the USAJobs API, normalizes them,
and appends to a MongoDB collection. Uses shared data_ingestor and mongo_ingestion_utils.

Env: MONGODB_CONNECT_STRING, PROD_DB, MONGO_JOBS_COLLECTION (optional), USAJOBS_API_KEY.
Data source label: "USAJobs".

Run from backend: python app/api/usajobs/usajobs_to_mongo.py
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
    from backend.app.api.usajobs.test_usajobs_api import test_usajobs_api, normalize_usajobs_job
except ImportError:
    from test_usajobs_api import test_usajobs_api, normalize_usajobs_job


def run(
    keywords: Optional[str] = "Software Engineer",
    page: Optional[int] = None,
) -> int:
    """Fetch jobs from USAJobs and insert into MongoDB. Returns count inserted."""
    print("USAJobs → MongoDB")
    print("=" * 50)

    def fetch_jobs():
        data = test_usajobs_api(keywords=keywords, page=page)
        return data.get("SearchResult", {}).get("SearchResultItems", [])

    items = fetch_jobs()
    print(f"Retrieved {len(items)} job postings from USAJobs.")
    count = run_ingestion(
        source="USAJobs",
        normalizer=normalize_usajobs_job,
        fetch_jobs=lambda: items,
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
