import os
from typing import Optional
from pymongo import MongoClient
import motor.motor_asyncio
from dotenv import load_dotenv

#Singletons to prevent connection leaks
_sync_client: Optional[MongoClient] = None
_async_client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None

def _ensure_env_loaded():
    """
    Loads .env across different working directories
    Returns:
    """

    if os.getenv("MONGODB_CONNECT_STRING") and os.getenv("PROD_DB"):
        return

    this_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(this_dir, "..", "..", "..", ".env"),
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.getcwd(), "backend", ".env"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            load_dotenv(dotenv_path=path)
            break

def get_sync_jobs_collection():
    """
    For offline scripts (train.py)
    Returns: Synchronous jobs collection
    """

    global _sync_client
    _ensure_env_loaded()

    uri = os.getenv("MONGODB_CONNECT_STRING")
    db_name = os.getenv("PROD_DB")

    if not uri or not db_name:
        raise ValueError("MONGODB_CONNECT_STRING or PROD_DB missing from .env")

    if _sync_client is None:
        _sync_client = MongoClient(uri, serverSelectionTimeoutMS=5000)

    return _sync_client[db_name]["jobs"]

def get_async_matches_collection():
    """
    For FASTAPI (routes_ml.py)
    Returns: Asynchronous job_matches collection
    """

    global _async_client
    _ensure_env_loaded()

    uri = os.getenv("MONGODB_CONNECT_STRING")
    db_name = os.getenv("PROD_DB")

    if not uri or not db_name:
        raise ValueError("MONGODB_CONNECT_STRING or PROD_DB missing from .env")

    if _async_client is None:
        _async_client = motor.motor_asyncio.AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)

    return _async_client[db_name]["job_matches"]
