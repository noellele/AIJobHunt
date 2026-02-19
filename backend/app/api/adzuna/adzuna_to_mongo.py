"""
Adzuna API → MongoDB ingestion (single keyword).

Fetches job postings from the Adzuna API for a given keyword (e.g. "Software Engineer"),
normalizes them, and inserts into a MongoDB collection.

Uses MONGODB_CONNECT_STRING and PROD_DB from environment (.env).
Collection name defaults to data-ingestion-api_adzuna (override with MONGO_JOBS_COLLECTION).

Run from project root:
  python -m backend.app.api.adzuna.adzuna_to_mongo
Or from backend/app/api/adzuna:
  python adzuna_to_mongo.py
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
    from backend.app.api.adzuna.test_adzuna_api import test_adzuna_api, normalize_adzuna_job
except ImportError:
    from test_adzuna_api import test_adzuna_api, normalize_adzuna_job


def run(
    keywords: Optional[str] = "Software Engineer",
    page: int = 1,
    results_per_page: int = 50,
) -> int:
    """
    Fetch jobs from Adzuna for the given keyword, then insert into MongoDB.
    Returns the number of documents inserted.
    """
    print("Adzuna → MongoDB (single keyword)")
    print("=" * 50)

    def fetch_jobs():
        result = test_adzuna_api(
            page=page,
            keywords=keywords,
            results_per_page=results_per_page,
        )
        return result.get("results", [])

    jobs = fetch_jobs()
    print(f"Retrieved {len(jobs)} job postings from Adzuna.")
    count = run_ingestion(
        source="Adzuna",
        normalizer=normalize_adzuna_job,
        fetch_jobs=lambda: jobs,
    )
    print(f"Inserted {count} documents into MongoDB.")
    return count


if __name__ == "__main__":
    try:
        run(
            keywords="Software Engineer",
            page=1,
            results_per_page=50,
        )
        print("Done.")
    except ValueError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"Error: {e}")
        raise
