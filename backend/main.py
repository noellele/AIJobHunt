import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from backend.db.mongo import mongo
from backend.routers import users, jobs, savedsearches, userstats

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await mongo.connect(os.getenv("PROD_DB"))
    yield
    await mongo.close()


app = FastAPI(lifespan=lifespan)

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(userstats.router, prefix="/users", tags=["User Stats"])
app.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
app.include_router(
    savedsearches.router,
    prefix="/saved-searches",
    tags=["Saved Searches"],
)
