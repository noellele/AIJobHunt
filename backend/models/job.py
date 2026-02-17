from datetime import datetime, timezone
from typing import List, Optional, Annotated
from pydantic import BaseModel, Field, model_validator, ConfigDict, BeforeValidator


# This helper converts ObjectId to string for Pydantic validation
PyObjectId = Annotated[str, BeforeValidator(str)]

class SalaryRange(BaseModel):
    min: Optional[int] = Field(None, ge=0)
    max: Optional[int] = Field(None, ge=0)
    currency: Optional[str] = "USD"

    @model_validator(mode="after")
    def validate_range(self):
        if (
            self.min is not None
            and self.max is not None
            and self.min > self.max
        ):
            raise ValueError("salary_range.min must be <= salary_range.max")
        return self


class SalaryRangeUpdate(BaseModel):
    min: Optional[int] = None
    max: Optional[int] = None
    currency: Optional[str] = None

    @model_validator(mode="after")
    def validate_range(self):
        if (
            self.min is not None
            and self.max is not None
            and self.min > self.max
        ):
            raise ValueError("salary_range.min must be <= salary_range.max")
        return self


class MLFeatures(BaseModel):
    processed_text: Optional[str] = None
    keyword_vector: Optional[List[float]] = None


class MLFeaturesUpdate(BaseModel):
    processed_text: Optional[str] = None
    keyword_vector: Optional[List[float]] = None


class JobPosting(BaseModel):
    external_id: str
    title: str
    company: str
    description: str
    location: str

    remote_type: Optional[str] = None

    skills_required: List[str] = []

    posted_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    source_url: Optional[str] = None
    source_platform: Optional[str] = None

    salary_range: Optional[SalaryRange] = None
    ml_features: Optional[MLFeatures] = None


class JobPostingUpdate(BaseModel):
    external_id: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None

    remote_type: Optional[str] = None
    skills_required: Optional[List[str]] = None

    posted_date: Optional[datetime] = None

    source_url: Optional[str] = None
    source_platform: Optional[str] = None

    salary_range: Optional[SalaryRangeUpdate] = None
    ml_features: Optional[MLFeaturesUpdate] = None


class JobInDB(JobPosting):
    id: PyObjectId = Field(..., alias="_id")
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


def job_helper(job) -> dict:
    return {
        "id": str(job["_id"]),
        "external_id": job["external_id"],
        "title": job["title"],
        "company": job["company"],
        "description": job["description"],
        "location": job["location"],
        "remote_type": job.get("remote_type"),
        "skills_required": job.get("skills_required", []),
        "posted_date": job["posted_date"],
        "source_url": job.get("source_url"),
        "source_platform": job.get("source_platform"),
        "salary_range": job.get("salary_range"),
        "ml_features": job.get("ml_features"),
    }
