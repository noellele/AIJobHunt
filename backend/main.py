import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
    userjobinteractions,
    ingestion,
)
from backend.app.ml import routes_ml

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await mongo.connect(os.getenv("PROD_DB"))
    await ensure_indexes()
    yield
    await mongo.close()


app = FastAPI(lifespan=lifespan)

API_SECRET = os.getenv("API_SECRET").strip()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://main.d1lixpon0rveb3.amplifyapp.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def verify_secret_header(request: Request, call_next):
    if request.method == "OPTIONS":
        return await call_next(request)
    secret = request.headers.get("aijobhunt-api-secret")
    if secret != API_SECRET:
        print(f"Mismatch! Header: '{secret}' vs Env: '{API_SECRET}'")
        return JSONResponse(status_code=403, content={"detail": "Forbidden"})
    return await call_next(request)

app.include_router(userstats.router, prefix="/user-stats", tags=["User Stats"])
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
app.include_router(ingestion.router, prefix="/ingestion", tags=["Ingestion"])
app.include_router(routes_ml.router, prefix="/ml", tags=["Machine Learning"])
app.include_router(users.router, prefix="/users", tags=["Users"])