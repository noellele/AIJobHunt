from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

from backend.services.userstats_service import (
    recalculate_top_missing_skill_for_user
)
from .logic import JobMatcher, SemanticJobMatcher
from .train import build_semantic_model
from backend.services.jobmatches_service import upsert_job_match
from backend.db.mongo import get_db
from bson import ObjectId
from .mongo_ingestion_utils import get_async_matches_collection

router = APIRouter()

# LOAD CACHED MODELS
tfidf_matcher = None
semantic_matcher = None

try:
    print("🔄 Loading ML Models...")
    tfidf_matcher = JobMatcher()
    semantic_matcher = SemanticJobMatcher()
    print("✅ ML Models loaded successfully.")
except FileNotFoundError as e:
    print(f"⚠️ Warning: ML model files not found. Did you run train.py? Error: {e}")
except Exception as e:
    print(f"❌ Unexpected error loading models: {e}")


# --- Pydantic Models
class UserPreferences(BaseModel):
    desired_locations: List[str] = []
    target_roles: List[str] = []
    skills: List[str] = []
    experience_level: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None


class RecommendationRequest(BaseModel):
    id: str = Field(
        ...,
        alias="_id",
        description="The ID of the user requesting matches"
    )
    preferences: UserPreferences


# --- API Endpoints ---

@router.get("/matches/user/{user_id}/job/{job_id}")
async def get_specific_match(user_id: str, job_id: str):
    """
    Fetches a previously calculated match score from the database.
    """
    if user_id == "undefined" or job_id == "undefined":
        return {"score": 0, "missing_skills": [], "status": "pending_id"}
    try:
        u_oid = ObjectId(user_id)
        j_oid = ObjectId(job_id)
        collection = get_async_matches_collection()
        match = await collection.find_one({
            "user_id": u_oid,
            "job_id": j_oid
        })

        if not match:
            # If no match exists in the DB, return a neutral response 
            return {"score": 0, "missing_skills": []}

        return {
            "score": match.get("score", 0),
            "missing_skills": match.get("missing_skills", []),
            "match_date": match.get("match_date")
        }

    except Exception as e:
        print(f"Error fetching match score: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving match data.")


@router.post("/job-matches")
async def get_recommendations(request: RecommendationRequest):
    """
    Generates job recommendations based on user preferences.
    Args:
        request: dict

    Returns:
    """
    global semantic_matcher, tfidf_matcher
    
    # 1. Convert to ObjectId immediately to avoid format errors later
    try:
        user_oid = ObjectId(request.id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid User ID format")

    # On-the-fly recovery if models are None
    if semantic_matcher is None:
        try:
            print("🔄 Attempting on-the-fly model load...")
            semantic_matcher = SemanticJobMatcher()
            tfidf_matcher = JobMatcher()
        except Exception as e:
            print(f"❌ Failed to initialize models: {e}")
            raise HTTPException(status_code=503, detail="ML Models not ready. Run /train.")

    model_type = "semantic"
    try:
        if model_type == "tfidf":
            matches = tfidf_matcher.recommend(request.preferences.model_dump(), top_n=10)
        else:
            matches = semantic_matcher.recommend(request.preferences.model_dump(), top_n=10)

        db = get_db()

        for match in matches:
            await upsert_job_match(
                db=db,
                user_id=user_oid,
                job_id=ObjectId(match.get("job_id")),
                score=match["score"],
                missing_skills=match["missing_skills"],
                recalc=False,  # Defer top missing skill recalculation until all matches are upserted
            )

        await recalculate_top_missing_skill_for_user(db, user_oid)

        return {"status": "success", "model_used": model_type,
                "matches": matches}

    except Exception as e:
        print(f"ML Recommendation Error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate or save recommendations."
        )


@router.post("/train")
async def trigger_training():
    """
    Manually triggers the ML model training/refresh process.
    """

    try:
        build_semantic_model()
        tfidf_matcher = JobMatcher()
        semantic_matcher = SemanticJobMatcher()
        return {"status": "success",
                "message": "ML models rebuilt and cached."}
    except Exception as e:
        print(f"Training Error: {e}")
        raise HTTPException(status_code=500,
                            detail="Failed to rebuild ML models.")
