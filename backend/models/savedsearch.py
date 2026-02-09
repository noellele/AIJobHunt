from datetime import datetime, timezone
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field


class SavedSearch(BaseModel):
    user_id: str = Field(..., description="UserProfile _id")
    search_name: str = Field(..., min_length=1, max_length=150)
    search_query: Dict[str, Any]

    total_matches: int = 0
    new_matches: int = 0

    last_viewed: Optional[datetime] = None
    last_match_check: Optional[datetime] = None

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class SavedSearchUpdate(BaseModel):
    search_name: Optional[str] = None
    search_query: Optional[Dict[str, Any]] = None

    total_matches: Optional[int] = None
    new_matches: Optional[int] = None

    last_viewed: Optional[datetime] = None
    last_match_check: Optional[datetime] = None


class SavedSearchInDB(SavedSearch):
    id: str


def saved_search_helper(search) -> dict:
    return {
        "id": str(search["_id"]),
        "user_id": str(search["user_id"]),
        "search_name": search["search_name"],
        "search_query": search["search_query"],
        "total_matches": search.get("total_matches", 0),
        "new_matches": search.get("new_matches", 0),
        "last_viewed": search.get("last_viewed"),
        "last_match_check": search.get("last_match_check"),
        "created_at": search["created_at"],
    }
