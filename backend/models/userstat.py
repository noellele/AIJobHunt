from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import Optional


class UserStatsBase(BaseModel):
    user_id: str  # FK for UserProfile._id (stored as ObjectId in Mongo)
    jobs_viewed: int = Field(0, ge=0)
    jobs_saved: int = Field(0, ge=0)
    top_missing_skill: Optional[str] = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    last_calculated: Optional[datetime] = None


class UserStatsCreate(BaseModel):
    user_id: str


class UserStatsUpdate(BaseModel):
    jobs_viewed: Optional[int] = Field(None, ge=0)
    jobs_saved: Optional[int] = Field(None, ge=0)
    top_missing_skill: Optional[str] = None
    last_calculated: Optional[datetime] = None


class UserStatsInDB(UserStatsBase):
    id: str
    user_id: str
    top_missing_skill: Optional[str] = None
    jobs_viewed: Optional[int] = 0
    last_calculated: Optional[datetime] = None


def userstats_helper(doc) -> dict:
    return {
        "id": str(doc["_id"]),
        "user_id": str(doc["user_id"]),
        "jobs_viewed": doc.get("jobs_viewed", 0),
        "jobs_saved": doc.get("jobs_saved", 0),
        "top_missing_skill": doc.get("top_missing_skill"),
        "created_at": doc.get("created_at") or datetime.now(timezone.utc),
        "last_calculated": doc.get("last_calculated"),
    }