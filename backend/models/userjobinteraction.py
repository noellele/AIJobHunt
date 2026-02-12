from datetime import datetime, timezone
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field


class InteractionType(str, Enum):
    viewed = "viewed"
    saved = "saved"
    applied = "applied"
    rejected = "rejected"
    withdrawn = "withdrawn"


class UserJobInteractionBase(BaseModel):
    user_id: str    # FK for UserProfile._id (stored as ObjectId in Mongo)
    job_id: str     # FK for JobPosting._id (stored as ObjectId in Mongo)
    interaction_type: InteractionType
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class UserJobInteractionCreate(UserJobInteractionBase):
    user_id: str
    job_id: str
    interaction_type: InteractionType = InteractionType.viewed


class UserJobInteractionUpdate(BaseModel):
    interaction_type: Optional[InteractionType] = None


class UserJobInteractionInDB(UserJobInteractionBase):
    id: str


def userjobinteraction_helper(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "user_id": str(doc["user_id"]),
        "job_id": str(doc["job_id"]),
        "interaction_type": doc["interaction_type"],
        "timestamp": doc["timestamp"],
    }
