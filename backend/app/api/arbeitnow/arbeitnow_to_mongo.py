"""
Arbeitnow API → MongoDB ingestion.

Fetches job postings from the Arbeitnow API, normalizes them,
and appends to a MongoDB collection. Uses shared data_ingestor and mongo_ingestion_utils.

Env: MONGODB_CONNECT_STRING, PROD_DB, MONGO_JOBS_COLLECTION (optional).
Data source label: "Arbeitnow".

Run from backend: python app/api/arbeitnow/arbeitnow_to_mongo.py
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
    from backend.app.api.arbeitnow.test_arbeitnow_api import test_arbeitnow_api, normalize_arbeitnow_job
except ImportError:
    from test_arbeitnow_api import test_arbeitnow_api, normalize_arbeitnow_job


def run(
    page: Optional[int] = None,
    remote_only: bool = True,
    keywords: Optional[str] = "Software Engineer",
    salary_min: Optional[int] = None,
    salary_max: Optional[int] = None,
) -> int:
    """Fetch jobs from Arbeitnow and insert into MongoDB. Returns count inserted."""
    print("Arbeitnow → MongoDB")
    print("=" * 50)

    def fetch_jobs():
        data = test_arbeitnow_api(
            page=page,
            remote_only=remote_only,
            keywords=keywords,
            salary_min=salary_min,
            salary_max=salary_max,
        )
        return data.get("data", [])

    jobs = fetch_jobs()
    print(f"Retrieved {len(jobs)} job postings from Arbeitnow.")
    count = run_ingestion(
        source="Arbeitnow",
        normalizer=normalize_arbeitnow_job,
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
