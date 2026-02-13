"""
Shared MongoDB ingestion helpers for API → MongoDB scripts.

All values must come from .env (no hardcoded defaults):
- MONGODB_CONNECT_STRING (required)
- PROD_DB (required) — database name
- MONGO_JOBS_COLLECTION (required) — collection name

Documents are written in canonical Job Posting schema (see job_schema.py):
external_id, title, company, description, location, remote_type, skills_required,
posted_date, source_url, source_platform, salary_range, source, ingested_at.
"""

import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Callable

from pymongo import MongoClient
from pymongo.collection import Collection

try:
    from backend.app.api.job_schema import to_canonical_document
except ImportError:
    from job_schema import to_canonical_document


def _ensure_env_loaded():
    """Load .env from backend folder if MongoDB vars are missing (handles different cwds)."""
    if os.getenv("MONGO_JOBS_COLLECTION") and os.getenv("MONGODB_CONNECT_STRING"):
        return
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    # Try paths: backend/.env (from this file: api/mongo_ingestion_utils.py -> ../../.env = backend/.env)
    this_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(this_dir, "..", "..", ".env"),  # backend/.env
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.getcwd(), "backend", ".env"),
    ]
    for path in candidates:
        path = os.path.abspath(path)
        if os.path.isfile(path):
            load_dotenv(dotenv_path=path)
            break


def get_mongo_collection() -> Collection:
    """
    Build MongoDB client and return the jobs collection (sync).
    All three values must be set in .env for security and explicit configuration.
    """
    _ensure_env_loaded()
    uri = os.getenv("MONGODB_CONNECT_STRING")
    if not uri:
        raise ValueError(
            "MONGODB_CONNECT_STRING is not set. Add it to your .env file."
        )
    db_name = os.getenv("PROD_DB")
    if not db_name:
        raise ValueError(
            "PROD_DB is not set. Add the database name to your .env file."
        )
    collection_name = os.getenv("MONGO_JOBS_COLLECTION")
    if not collection_name:
        raise ValueError(
            "MONGO_JOBS_COLLECTION is not set. Add the collection name to your .env file."
        )

    client = MongoClient(uri)
    db = client[db_name]
    return db[collection_name]


def insert_jobs_into_mongo(
    jobs: List[Dict[str, Any]],
    collection: Collection,
    source: str,
    normalizer: Callable[[Dict[str, Any]], Dict[str, Any]],
) -> int:
    """
    Normalize job records, map to canonical schema, and append to MongoDB (insert only).

    Pipeline: raw job -> normalizer(job) -> to_canonical_document(..., source) -> add ingested_at.
    Written document schema: _id (Mongo), external_id, title, company, description, location,
    remote_type, skills_required, posted_date, source_url, source_platform, salary_range { min, max, currency }, ingested_at.

    Args:
        jobs: Raw job records from the API.
        collection: MongoDB collection to insert into.
        source: Source label (e.g. "Adzuna", "SerpAPI"); becomes source_platform.
        normalizer: Function that takes one raw job dict and returns a normalized dict
                    (e.g. Company, Position, Location, Tags, URL, Salary_Min, Date, ID).

    Returns:
        Number of documents inserted.
    """
    if not jobs:
        return 0

    now = datetime.now(timezone.utc)
    docs = []
    for job in jobs:
        normalized = normalizer(job)
        doc = to_canonical_document(normalized, source)
        doc["ingested_at"] = now  # optional audit field; rest matches Job Posting schema
        docs.append(doc)

    # Append only: insert_many adds new documents. Add unique index on external_id to reject duplicates.
    result = collection.insert_many(docs)
    return len(result.inserted_ids)
