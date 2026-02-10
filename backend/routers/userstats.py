from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime, timezone
from backend.db.mongo import get_db
from backend.models.userstat import (
    UserStatsUpdate,
    UserStatsInDB,
    userstats_helper,
)

router = APIRouter()


@router.get("/{user_id}/stats", response_model=UserStatsInDB)
async def get_user_stats(user_id: str):
    db = get_db()

    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    stats = await db.user_stats.find_one(
        {"user_id": ObjectId(user_id)}
    )

    if not stats:
        raise HTTPException(status_code=404, detail="UserStats not found")

    return userstats_helper(stats)


@router.patch("/{user_id}/stats", response_model=UserStatsInDB)
async def patch_user_stats(user_id: str, updates: UserStatsUpdate):
    db = get_db()

    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    update_data = {
        k: v for k, v in updates.model_dump(exclude_unset=True).items()
    }

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update",
        )

    update_data["last_calculated"] = datetime.now(timezone.utc)

    result = await db.user_stats.update_one(
        {"user_id": ObjectId(user_id)},
        {"$set": update_data},
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="UserStats not found")

    updated = await db.user_stats.find_one(
        {"user_id": ObjectId(user_id)}
    )

    return userstats_helper(updated)
