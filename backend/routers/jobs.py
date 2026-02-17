from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from typing import List
from datetime import datetime, timezone

from backend.db.mongo import get_db
from backend.models.job import (
    JobPosting,
    JobPostingUpdate,
    JobInDB,
    job_helper,
)
from backend.models.user import UserPreferencesUpdate

router = APIRouter()


@router.post("/", response_model=JobInDB, status_code=201)
async def create_job(job: JobPosting):
    db = get_db()

    existing = await db.jobs.find_one(
        {"external_id": job.external_id}
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Job with this external_id already exists",
        )

    result = await db.jobs.insert_one(job.model_dump())

    new_job = await db.jobs.find_one(
        {"_id": result.inserted_id}
    )

    return job_helper(new_job)


@router.get("/", response_model=List[JobInDB])
async def get_jobs():
    db = get_db()

    jobs = []

    async for job in db.jobs.find():
        jobs.append(job_helper(job))

    return jobs


@router.get("/{job_id}", response_model=JobInDB)
async def get_job(job_id: str):
    db = get_db()

    if not ObjectId.is_valid(job_id):
        raise HTTPException(status_code=400, detail="Invalid job ID")

    job = await db.jobs.find_one(
        {"_id": ObjectId(job_id)}
    )

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job_helper(job)


def flatten_job_updates(raw_updates: dict) -> dict:
    update_data: dict = {}

    for key, value in raw_updates.items():
        if key in {"salary_range", "ml_features"} and isinstance(value, dict):
            for sub_key, sub_val in value.items():
                update_data[f"{key}.{sub_key}"] = sub_val
        else:
            update_data[key] = value

    return update_data


@router.put("/{job_id}", response_model=JobInDB)
async def update_job(job_id: str, updates: JobPostingUpdate):
    return await _apply_job_update(job_id, updates)


@router.patch("/{job_id}", response_model=JobInDB)
async def patch_job(job_id: str, updates: JobPostingUpdate):
    return await _apply_job_update(job_id, updates)


async def _apply_job_update(job_id: str, updates: JobPostingUpdate):
    db = get_db()

    if not ObjectId.is_valid(job_id):
        raise HTTPException(status_code=400, detail="Invalid job ID")

    raw_updates = updates.model_dump(exclude_unset=True)

    if not raw_updates:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update",
        )

    update_data: dict = {}

    for field, value in raw_updates.items():
        update_data[field] = value

    update_data["updated_at"] = datetime.now(timezone.utc)

    result = await db.jobs.update_one(
        {"_id": ObjectId(job_id)},
        {"$set": update_data},
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")

    updated = await db.jobs.find_one(
        {"_id": ObjectId(job_id)},
    )

    return job_helper(updated)


@router.delete("/{job_id}", status_code=204)
async def delete_job(job_id: str):
    db = get_db()

    if not ObjectId.is_valid(job_id):
        raise HTTPException(status_code=400, detail="Invalid job ID")

    result = await db.jobs.delete_one(
        {"_id": ObjectId(job_id)}
    )

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")

    # Cascading delete on user-job interactions
    await db.user_job_interactions.delete_many(
        {"job_id": ObjectId(job_id)}
    )

    return


@router.post("/search", response_model=List[JobInDB])
async def search_jobs(
    criteria: UserPreferencesUpdate, 
    db = Depends(get_db)
):
    query = {}
    if criteria.skills:
        # "$in" checks if ANY element in the job's skills_required list 
        # is present in the user's skills list
        query["skills_required"] = {"$in": criteria.skills}

    # Match Target Roles (Regex search on job title)
    if criteria.target_roles:
        query["$or"] = [
            {"title": {"$regex": role, "$options": "i"}} 
            for role in criteria.target_roles
        ]

    # Match Salary >= user's min request
    if criteria.salary_min is not None:
        query["salary_range.min"] = {"$gte": criteria.salary_min}

    # Match Location
    if criteria.desired_locations:
        location_queries = [
            {"location": {"$regex": loc, "$options": "i"}} 
            for loc in criteria.desired_locations
        ]
        if "$or" in query:
            query = {"$and": [
                {"$or": query.pop("$or")},
                {"$or": location_queries}
            ]}
        else:
            query["$or"] = location_queries

    try:
        cursor = db.jobs.find(query).limit(50)
        jobs = await cursor.to_list(length=50)
        
        # Format for JobInDB
        formatted_jobs = []
        for job in jobs:
            job["id"] = str(job["_id"]) # Maps _id to id for the response model
            formatted_jobs.append(job)
            
        return formatted_jobs

    except Exception as e:
        print(f"Search error: {e}")
        raise HTTPException(status_code=500, detail="Database search failed")