"""
The Muse API → MongoDB ingestion.

Fetches job postings from The Muse API, normalizes them,
and appends to a MongoDB collection. Uses shared data_ingestor and mongo_ingestion_utils.

Env: MONGODB_CONNECT_STRING, PROD_DB, MONGO_JOBS_COLLECTION (optional), MUSE_API_KEY.
Data source label: "The Muse".

Run from backend: python app/api/muse/muse_to_mongo.py
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
    from backend.app.api.muse.test_muse_api import test_muse_api, normalize_muse_job
except ImportError:
    from test_muse_api import test_muse_api, normalize_muse_job


def run(
    page: int = 1,
    keywords: Optional[str] = None,
    locations: Optional[str] = "United States",
    categories: Optional[List[str]] = None,
    descending: Optional[str] = "descending",
) -> int:
    """Fetch jobs from The Muse and insert into MongoDB. Returns count inserted."""
    print("The Muse → MongoDB")
    print("=" * 50)

    def fetch_jobs():
        data = test_muse_api(
            page=page,
            keywords=keywords,
            locations=locations,
            categories=categories,
            descending=descending,
        )
        return data.get("results", [])

    jobs = fetch_jobs()
    print(f"Retrieved {len(jobs)} job postings from The Muse.")
    count = run_ingestion(
        source="The Muse",
        normalizer=normalize_muse_job,
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
