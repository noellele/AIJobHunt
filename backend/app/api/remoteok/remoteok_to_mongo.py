"""
RemoteOK API → MongoDB ingestion.

Fetches job postings from the RemoteOK API, normalizes them,
and appends to a MongoDB collection. Uses shared data_ingestor and mongo_ingestion_utils.

Env: MONGODB_CONNECT_STRING, PROD_DB, MONGO_JOBS_COLLECTION (optional).
Data source label: "RemoteOK".

Run from backend: python app/api/remoteok/remoteok_to_mongo.py
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
    from backend.app.api.remoteok.test_remoteok_api import test_remoteok_api, normalize_job_data
except ImportError:
    from test_remoteok_api import test_remoteok_api, normalize_job_data


def run(
    keywords: Optional[str] = "Software Engineer",
    salary_min: Optional[int] = None,
    salary_max: Optional[int] = None,
    limit: Optional[int] = None,
    require_salary: bool = True,
) -> int:
    """Fetch jobs from RemoteOK and insert into MongoDB. Returns count inserted."""
    print("RemoteOK → MongoDB")
    print("=" * 50)

    def fetch_jobs():
        return test_remoteok_api(
            keywords=keywords,
            salary_min=salary_min,
            salary_max=salary_max,
            limit=limit,
            require_salary=require_salary,
        )

    jobs = fetch_jobs()
    print(f"Retrieved {len(jobs)} job postings from RemoteOK.")
    count = run_ingestion(
        source="RemoteOK",
        normalizer=normalize_job_data,
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
