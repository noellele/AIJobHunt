from fastapi import APIRouter, HTTPException
from typing import List
from pymongo import ReturnDocument
from backend.services.userstats_service import (
    recalculate_top_missing_skill_for_user
)
from backend.services.jobmatches_service import (
    upsert_job_match
)

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

    updated = await upsert_job_match(
        db=db,
        user_id=payload.user_id,
        job_id=payload.job_id,
        score=payload.score,
        missing_skills=payload.missing_skills,
    )

    return jobmatch_helper(updated)


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

    update_data = updates.model_dump(exclude_unset=True)

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
    doc = await db.job_matches.find_one({"_id": match_oid})

    if not doc:
        raise HTTPException(status_code=404, detail="Match not found")

    user_oid = doc["user_id"]

    # Delete the job match
    await db.job_matches.delete_one({"_id": match_oid})

    # Automatically recalculate top missing skill
    await recalculate_top_missing_skill_for_user(db, user_oid)

    # 204 means no response body
    return
