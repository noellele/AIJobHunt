from fastapi import APIRouter, HTTPException
from bson import ObjectId
from typing import List
from backend.db.mongo import get_db
from backend.models.user import (
    UserProfile,
    UserProfileUpdate,
    UserInDB,
    user_helper,
)
from datetime import datetime, timezone

router = APIRouter()


@router.post("/", response_model=UserInDB, status_code=201)
async def create_user(user: UserProfile):
    db = get_db()
    result = await db.users.insert_one(user.model_dump())

    new_user = await db.users.find_one(
        {"_id": result.inserted_id}
    )

    # Initialize user stats for the new user
    await db.user_stats.insert_one({
        "user_id": result.inserted_id,
        "jobs_viewed": 0,
        "jobs_saved": 0,
        "top_missing_skill": None,
        "created_at": datetime.now(timezone.utc),
        "last_calculated": None,
    })

    return user_helper(new_user)


@router.get("/", response_model=List[UserInDB])
async def get_users():
    db = get_db()
    users = []

    async for user in db.users.find():
        users.append(user_helper(user))

    return users


@router.get("/{user_id}", response_model=UserInDB)
async def get_user(user_id: str):
    db = get_db()
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    user = await db.users.find_one(
        {"_id": ObjectId(user_id)}
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user_helper(user)


@router.put("/{user_id}", response_model=UserInDB)
async def update_user(user_id: str, updates: UserProfileUpdate):
    db = get_db()

    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    raw_updates = updates.model_dump(exclude_unset=True)

    if not raw_updates:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update",
        )

    update_data = {}

    for key, value in raw_updates.items():
        if key == "preferences" and isinstance(value, dict):
            for pref_key, pref_val in value.items():
                update_data[f"preferences.{pref_key}"] = pref_val
        else:
            update_data[key] = value

    update_data["updated_at"] = datetime.now(timezone.utc)

    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data},
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = await db.users.find_one(
        {"_id": ObjectId(user_id)}
    )

    return user_helper(updated_user)


@router.patch("/{user_id}", response_model=UserInDB)
async def patch_user(user_id: str, updates: UserProfileUpdate):
    db = get_db()

    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    raw_updates = updates.model_dump(exclude_unset=True)

    if not raw_updates:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update",
        )

    update_data: dict = {}

    for key, value in raw_updates.items():
        if key == "preferences" and isinstance(value, dict):
            for pref_key, pref_val in value.items():
                update_data[f"preferences.{pref_key}"] = pref_val
        else:
            update_data[key] = value

    update_data["updated_at"] = datetime.now(timezone.utc)

    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data},
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = await db.users.find_one(
        {"_id": ObjectId(user_id)}
    )

    return user_helper(updated_user)


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: str):
    db = get_db()

    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    # Cascading delete on user stats
    await db.user_stats.delete_one(
        {"user_id": ObjectId(user_id)}
    )

    # Cascading delete on saved searches
    await db.saved_searches.delete_many(
        {"user_id": ObjectId(user_id)}
    )

    # Cascading delete on user-job interactions
    await db.user_job_interactions.delete_many(
        {"user_id": ObjectId(user_id)}
    )

    # Then delete user
    result = await db.users.delete_one(
        {"_id": ObjectId(user_id)}
    )

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return
