from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class MatchDetails(BaseModel):
    skills_matched: List[str] = []
    skills_missing: List[str] = []
    overall_compatibility: float = Field(..., ge=0.0, le=1.0)


class UserSnapshot(BaseModel):
    preferences_at_match: Dict[str, Any]
    credentials_at_match: Dict[str, Any]


class JobMatchBase(BaseModel):
    user_id: str
    job_id: str
    relevancy_score: float = Field(..., ge=0.0, le=1.0)
    match_reason: Optional[str] = None
    is_active: bool = True
    matched_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    match_details: MatchDetails
    user_snapshot: UserSnapshot


class JobMatchCreate(JobMatchBase):
    pass


class JobMatchUpdate(BaseModel):
    relevancy_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    match_reason: Optional[str] = None
    is_active: Optional[bool] = None


class JobMatchInDB(JobMatchBase):
    id: str


def jobmatch_helper(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "user_id": str(doc["user_id"]),
        "job_id": str(doc["job_id"]),
        "relevancy_score": doc["relevancy_score"],
        "match_reason": doc.get("match_reason"),
        "is_active": doc["is_active"],
        "matched_at": doc["matched_at"],
        "match_details": doc["match_details"],
        "user_snapshot": doc["user_snapshot"],
    }
