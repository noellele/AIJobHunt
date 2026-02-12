from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError
from pymongo import ReturnDocument

from backend.db.mongo import get_db
from backend.utils.validation import validate_object_id
from backend.models.jobmatch import (
    JobMatchCreate,
    JobMatchUpdate,
    JobMatchInDB,
    jobmatch_helper,
)

router = APIRouter()


@router.post("/", response_model=JobMatchInDB, status_code=201)
async def create_job_match(payload: JobMatchCreate):
    db = get_db()

    user_oid = validate_object_id(payload.user_id, "user ID")
    job_oid = validate_object_id(payload.job_id, "job ID")

    if not await db.users.find_one({"_id": user_oid}):
        raise HTTPException(404, "User not found")

    if not await db.jobs.find_one({"_id": job_oid}):
        raise HTTPException(404, "Job not found")

    doc = payload.model_dump()
    doc["user_id"] = user_oid
    doc["job_id"] = job_oid
    doc["matched_at"] = datetime.now(timezone.utc)

    try:
        result = await db.job_matches.insert_one(doc)
        doc["_id"] = result.inserted_id
        return jobmatch_helper(doc)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=409,
            detail="Job match already exists for this user and job",
        )


@router.get("/user/{user_id}", response_model=List[JobMatchInDB])
async def get_matches_for_user(user_id: str):
    db = get_db()
    user_oid = validate_object_id(user_id, "user ID")

    matches = []
    async for doc in db.job_matches.find({"user_id": user_oid}):
        matches.append(jobmatch_helper(doc))

    return matches


@router.patch("/{match_id}", response_model=JobMatchInDB)
async def update_job_match(match_id: str, updates: JobMatchUpdate):
    db = get_db()
    match_oid = validate_object_id(match_id, "match ID")

    update_data = {
        k: v for k, v in updates.model_dump(exclude_unset=True).items()
    }

    if not update_data:
        raise HTTPException(400, "No fields provided for update")

    updated = await db.job_matches.find_one_and_update(
        {"_id": match_oid},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER
    )

    if not updated:
        raise HTTPException(404, "Match not found")

    return jobmatch_helper(updated)


@router.delete("/{match_id}", status_code=204)
async def delete_job_match(match_id: str):
    db = get_db()
    match_oid = validate_object_id(match_id, "match ID")

    result = await db.job_matches.delete_one({"_id": match_oid})

    if result.deleted_count == 0:
        raise HTTPException(404, "Match not found")
