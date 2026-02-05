from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from typing import List
from pydantic import model_validator


class UserPreferences(BaseModel):
    desired_locations: List[str] = []
    target_roles: List[str] = []
    skills: List[str] = []

    experience_level: Optional[str] = None

    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)

    @model_validator(mode="after")
    def validate_salary_range(self):
        if (
            self.salary_min is not None
            and self.salary_max is not None
            and self.salary_min > self.salary_max
        ):
            raise ValueError(
                "salary_min must be less than or equal to salary_max"
                )

        return self


class UserPreferencesUpdate(BaseModel):
    desired_locations: Optional[List[str]] = None
    target_roles: Optional[List[str]] = None
    skills: Optional[List[str]] = None

    experience_level: Optional[str] = None

    salary_min: Optional[int] = None
    salary_max: Optional[int] = None

    @model_validator(mode="after")
    def validate_salary_range(self):
        if (
            self.salary_min is not None
            and self.salary_max is not None
            and self.salary_min > self.salary_max
        ):
            raise ValueError(
                "salary_min must be less than or equal to salary_max"
                )

        return self


class UserProfile(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    preferences: Optional[UserPreferences] = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        )
    updated_at: Optional[datetime] = None  # Set default to None


class UserProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    preferences: Optional[UserPreferencesUpdate] = None
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        )


class UserInDB(UserProfile):
    id: str


def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "preferences": user.get("preferences"),
        "created_at": user["created_at"],
        "updated_at": user.get("updated_at"),
    }
