"""
Remotive API → MongoDB ingestion.

Fetches job postings from the Remotive API, normalizes them,
and appends to a MongoDB collection. Uses shared data_ingestor and mongo_ingestion_utils.

Env: MONGODB_CONNECT_STRING, PROD_DB, MONGO_JOBS_COLLECTION (optional).
Data source label: "Remotive".

Run from backend: python app/api/remotive/remotive_to_mongo.py
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
    from backend.app.api.remotive.test_remotive_api import test_remotive_api, normalize_remotive_job
except ImportError:
    from test_remotive_api import test_remotive_api, normalize_remotive_job


def run(
    category: Optional[str] = "software-dev",
    search: Optional[str] = "Software Engineer",
    limit: Optional[int] = None,
) -> int:
    """Fetch jobs from Remotive and insert into MongoDB. Returns count inserted."""
    print("Remotive → MongoDB")
    print("=" * 50)

    def fetch_jobs():
        data = test_remotive_api(category=category, search=search, limit=limit)
        return data.get("jobs", [])

    jobs = fetch_jobs()
    print(f"Retrieved {len(jobs)} job postings from Remotive.")
    count = run_ingestion(
        source="Remotive",
        normalizer=normalize_remotive_job,
        fetch_jobs=lambda: jobs,
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
