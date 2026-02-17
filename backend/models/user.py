from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator, BeforeValidator
from typing import Optional, List, Annotated
from bson import ObjectId


# This helper converts ObjectId to string for Pydantic validation
PyObjectId = Annotated[str, BeforeValidator(str)]

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
    preferences: UserPreferences = Field(default_factory=UserPreferences)
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
    id: PyObjectId = Field(..., alias="_id")
    # map '_id' from Mongo to 'id' in API
    model_config = ConfigDict(
        # allows Pydantic to accept the raw MongoDB dictionary
        from_attributes=True, 
        # ensures that 'id' and '_id' can be used interchangeably
        populate_by_name=True
    )


class UserAuthBase(BaseModel):
    """Common fields & logic for Auth models"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    @field_validator('email')
    @classmethod
    def normalize_email(cls, v):
        return v.lower().strip()


class UserCreate(UserAuthBase):
    name: str = Field(..., min_length=1, max_length=100)


class UserLogin(UserAuthBase):
    pass


def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        # returns an empty dict if the key is missing
        "preferences": user.get("preferences", {
            "desired_locations": [],
            "target_roles": [],
            "skills": [],
            "salary_min": 0,
            "salary_max": 0
        }),
        "created_at": user["created_at"],
        "updated_at": user.get("updated_at"),
    }
