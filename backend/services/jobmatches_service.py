from datetime import datetime, timezone
from pymongo import ReturnDocument
from fastapi import HTTPException

from backend.services.userstats_service import (
    recalculate_top_missing_skill_for_user
)
from backend.utils.validation import validate_object_id


async def upsert_job_match(
    db,
    user_id: str,
    job_id: str,
    score: float,
    missing_skills: list[str],
    recalc: bool = True,
):
    """
    Create or update a job match and automatically
    recalculate the user's top missing skill.
    """

    user_oid = validate_object_id(user_id, "user ID")
    job_oid = validate_object_id(job_id, "job ID")

    # Validate user exists
    if not await db.users.find_one({"_id": user_oid}):
        raise HTTPException(404, "User not found")

    # Validate job exists
    if not await db.jobs.find_one({"_id": job_oid}):
        raise HTTPException(404, "Job not found")

    updated = await db.job_matches.find_one_and_update(
        {
            "user_id": user_oid,
            "job_id": job_oid,
        },
        {
            "$set": {
                "score": score,
                "missing_skills": missing_skills,
                "match_date": datetime.now(timezone.utc),
            }
        },
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )

    # Recalculate top missing skill
    if recalc:
        await recalculate_top_missing_skill_for_user(db, user_oid)

    return updated
