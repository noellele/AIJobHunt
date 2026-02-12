from fastapi import HTTPException
from bson import ObjectId


def validate_object_id(id_value: str, field_name: str = "ID") -> ObjectId:
    """Validates and convert a string to ObjectId.
    Raises HTTPException if invalid."""
    if not ObjectId.is_valid(id_value):
        raise HTTPException(400, f"Invalid {field_name}")
    return ObjectId(id_value)
