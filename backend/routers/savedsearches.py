from fastapi import APIRouter, HTTPException
from bson import ObjectId
from typing import List

from backend.db.mongo import get_db
from backend.models.savedsearch import (
    SavedSearch,
    SavedSearchUpdate,
    SavedSearchInDB,
    saved_search_helper,
)

router = APIRouter()


@router.post("/", response_model=SavedSearchInDB, status_code=201)
async def create_saved_search(search: SavedSearch):
    db = get_db()

    # validate user id
    if not ObjectId.is_valid(search.user_id):
        raise HTTPException(status_code=400, detail="Invalid user_id")

    payload = search.model_dump()
    payload["user_id"] = ObjectId(payload["user_id"])

    result = await db.saved_searches.insert_one(payload)

    created = await db.saved_searches.find_one(
        {"_id": result.inserted_id}
    )

    return saved_search_helper(created)


@router.get(
    "/user/{user_id}",
    response_model=List[SavedSearchInDB],
)
async def get_saved_searches_for_user(user_id: str):
    db = get_db()

    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user_id")

    searches = []

    async for search in db.saved_searches.find(
        {"user_id": ObjectId(user_id)}
    ):
        searches.append(saved_search_helper(search))

    return searches


@router.get("/{search_id}", response_model=SavedSearchInDB)
async def get_saved_search(search_id: str):
    db = get_db()

    if not ObjectId.is_valid(search_id):
        raise HTTPException(status_code=400, detail="Invalid search ID")

    search = await db.saved_searches.find_one(
        {"_id": ObjectId(search_id)}
    )

    if not search:
        raise HTTPException(status_code=404, detail="SavedSearch not found")

    return saved_search_helper(search)


@router.put("/{search_id}", response_model=SavedSearchInDB)
async def update_saved_search(
    search_id: str,
    updates: SavedSearchUpdate,
):
    return await _apply_saved_search_update(search_id, updates)


@router.patch("/{search_id}", response_model=SavedSearchInDB)
async def patch_saved_search(
    search_id: str,
    updates: SavedSearchUpdate,
):
    return await _apply_saved_search_update(search_id, updates)


# -----------------------------
# SHARED UPDATE LOGIC
# -----------------------------

async def _apply_saved_search_update(
    search_id: str,
    updates: SavedSearchUpdate,
):
    db = get_db()

    if not ObjectId.is_valid(search_id):
        raise HTTPException(status_code=400, detail="Invalid search ID")

    raw_updates = updates.model_dump(exclude_unset=True)

    if not raw_updates:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update",
        )

    result = await db.saved_searches.update_one(
        {"_id": ObjectId(search_id)},
        {"$set": raw_updates},
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="SavedSearch not found")

    updated = await db.saved_searches.find_one(
        {"_id": ObjectId(search_id)}
    )

    return saved_search_helper(updated)


@router.delete("/{search_id}", status_code=204)
async def delete_saved_search(search_id: str):
    db = get_db()

    if not ObjectId.is_valid(search_id):
        raise HTTPException(status_code=400, detail="Invalid search ID")

    result = await db.saved_searches.delete_one(
        {"_id": ObjectId(search_id)}
    )

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="SavedSearch not found")

    return
