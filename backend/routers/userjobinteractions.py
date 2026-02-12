from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError
from pymongo import ReturnDocument

from backend.db.mongo import get_db
from backend.utils.validation import validate_object_id
from backend.models.userjobinteraction import (
    UserJobInteractionCreate,
    UserJobInteractionUpdate,
    UserJobInteractionInDB,
    userjobinteraction_helper,
)

router = APIRouter()


@router.post("/", response_model=UserJobInteractionInDB, status_code=201)
async def create_interaction(payload: UserJobInteractionCreate):
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
    doc["timestamp"] = datetime.now(timezone.utc)

    try:
        result = await db.user_job_interactions.insert_one(doc)
        doc["_id"] = result.inserted_id
        return userjobinteraction_helper(doc)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=409,
            detail="Interaction already exists",
        )


@router.get("/user/{user_id}")
async def get_user_interactions(user_id: str):
    user_oid = validate_object_id(user_id, "user ID")
    db = get_db()

    cursor = db.user_job_interactions.find({"user_id": user_oid})

    return [
        userjobinteraction_helper(doc)
        async for doc in cursor
    ]


@router.get("/job/{job_id}")
async def get_job_interactions(job_id: str):
    job_oid = validate_object_id(job_id, "job ID")
    db = get_db()

    cursor = db.user_job_interactions.find({"job_id": job_oid})

    return [
        userjobinteraction_helper(doc)
        async for doc in cursor
    ]


@router.patch("/{interaction_id}")
async def update_interaction(
    interaction_id: str,
    payload: UserJobInteractionUpdate,
):
    interaction_oid = validate_object_id(interaction_id, "interaction ID")

    updates = payload.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(400, "No fields provided")

    db = get_db()

    updated = await db.user_job_interactions.find_one_and_update(
        {"_id": interaction_oid},
        {"$set": updates},
        return_document=ReturnDocument.AFTER
    )

    if not updated:
        raise HTTPException(404, "Interaction not found")

    return userjobinteraction_helper(updated)


@router.delete("/{interaction_id}", status_code=204)
async def delete_interaction(interaction_id: str):
    interaction_oid = validate_object_id(interaction_id, "interaction ID")
    db = get_db()

    result = await db.user_job_interactions.delete_one(
        {"_id": interaction_oid}
    )

    if result.deleted_count == 0:
        raise HTTPException(404, "Interaction not found")
