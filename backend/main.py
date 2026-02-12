import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from backend.db.indexes import ensure_indexes
from backend.db.mongo import mongo
from backend.routers import (
    users,
    jobs,
    jobmatches,
    auth,
    savedsearches,
    userstats,
    userjobinteractions
)

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await mongo.connect(os.getenv("PROD_DB"))
    await ensure_indexes()
    yield
    await mongo.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(userstats.router, prefix="/users", tags=["User Stats"])
app.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(
    userjobinteractions.router,
    prefix="/interactions",
    tags=["User-Job Interactions"]
)
app.include_router(
    savedsearches.router,
    prefix="/saved-searches",
    tags=["Saved Searches"],
)
app.include_router(
    jobmatches.router,
    prefix="/job-matches",
    tags=["Job Matches"],
)
