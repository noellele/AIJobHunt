from fastapi import APIRouter, HTTPException, status, Depends
from backend.db.mongo import get_db
from backend.models.user import (
    UserCreate,
    UserLogin,
    UserPreferencesUpdate,
    UserInDB,
    user_helper
)
from datetime import datetime, timezone
from backend.utils.security import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter()

@router.put("/preferences")
async def update_preferences(
    preferences: UserPreferencesUpdate,
    current_user: dict = Depends(get_current_user)
):
    update_data = {
        f"preferences.{k}": v 
        for k, v in preferences.model_dump(exclude_unset=True).items()
    }
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid preference data provided")
    update_data["updated_at"] = datetime.now(timezone.utc)
    db = get_db()
    await db.users.update_one(
        {"email": current_user["email"]},
        {"$set": update_data}
    )
    updated_user = await db.users.find_one({"email": current_user["email"]})
    updated_user["id"] = str(updated_user["_id"])
    del updated_user["_id"]
    if "password" in updated_user: 
        del updated_user["password"]
    return updated_user


@router.post("/register", status_code=201)
async def register_user(user_in: UserCreate):
    db = get_db()
    # check if user already exists
    existing_user = await db.users.find_one({"email": user_in.email})
    if existing_user:
        raise HTTPException(
            status_code=400, 
            detail="A user with this email already exists."
        )
    user_dict = user_in.model_dump()
    # hash password
    user_dict["password"] = hash_password(user_dict.pop("password"))
    user_dict["created_at"] = datetime.now(timezone.utc)
    # insert into DB
    result = await db.users.insert_one(user_dict)
    #generate token
    access_token = create_access_token(data={"sub": user_dict["email"]})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "id": str(result.inserted_id),
            "name": user_dict.get("name"),
            "email": user_dict["email"]
        }
    }

@router.post("/login")
async def login(credentials: UserLogin):
    db = get_db()
    user = await db.users.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # generate token
    access_token = create_access_token(data={"sub": user["email"]})
    user_dict = user_helper(user)
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": user_dict
    }

@router.get("/me", response_model=UserInDB)
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Fetches the current authenticated user's profile, 
    including preferences for pre-filling forms.
    """
    return current_user
