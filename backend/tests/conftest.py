import os
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.db.indexes import ensure_indexes
from backend.db.mongo import mongo, get_db


@pytest_asyncio.fixture
async def client():
    await mongo.connect(os.getenv("TEST_DB"))
    await ensure_indexes()

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as ac:
        yield ac

    await mongo.close()


@pytest_asyncio.fixture(autouse=True)
async def clean_collections(client):

    db = get_db()

    # Clean BEFORE
    await db.users.delete_many({})
    await db.jobs.delete_many({})
    await db.saved_searches.delete_many({})
    await db.user_stats.delete_many({})
    await db.user_job_interactions.delete_many({})
    await db.job_matches.delete_many({})

    yield

    # Clean AFTER
    await db.users.delete_many({})
    await db.jobs.delete_many({})
    await db.saved_searches.delete_many({})
    await db.user_stats.delete_many({})
    await db.user_job_interactions.delete_many({})
    await db.job_matches.delete_many({})
