import os

import pytest
from bson import ObjectId
from datetime import datetime
from backend.db.mongo import get_db


# ------------------------
# CRUD Tests for /users
# ------------------------
@pytest.mark.asyncio
async def test_create_user(client):

    payload = {
        "name": "John Doe",
        "email": "john@test.com"
    }

    response = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json=payload
    )

    assert response.status_code == 201

    body = response.json()

    assert body["name"] == payload["name"]
    assert body["email"] == payload["email"]
    assert "_id" in body


@pytest.mark.asyncio
async def test_get_users(client):

    await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "name": "Jane Hill",
            "email": "jane@test.com"
        }
    )

    response = await client.get(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")}
    )

    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_get_user_by_id(client):

    create = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "name": "Noelle Lee",
            "email": "noelle@test.com"
        }
    )

    user_id = create.json()["_id"]

    response = await client.get(
        f"/users/{user_id}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")}
    )

    assert response.status_code == 200
    assert response.json()["_id"] == user_id


@pytest.mark.asyncio
async def test_update_user(client):

    create = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "name": "Bob Sam",
            "email": "bob@test.com"
        }
    )

    user_id = create.json()["_id"]

    update = await client.put(
        f"/users/{user_id}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "New Name"}
    )

    assert update.status_code == 200
    assert update.json()["name"] == "New Name"


@pytest.mark.asyncio
async def test_delete_user(client):

    create = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "name": "Delete Me",
            "email": "delete@test.com"
        }
    )

    user_id = create.json()["_id"]

    delete = await client.delete(
        f"/users/{user_id}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")}
    )

    assert delete.status_code == 204

    check = await client.get(
        f"/users/{user_id}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")}
    )
    assert check.status_code == 404


@pytest.mark.asyncio
async def test_create_user_with_preferences(client):
    payload = {
        "name": "Pref User",
        "email": "pref@test.com",
        "preferences": {
            "desired_locations": ["NYC", "SF"],
            "target_roles": ["ML Engineer"],
            "skills": ["Python", "FastAPI"],
            "experience_level": "mid",
            "salary_min": 90000,
            "salary_max": 130000,
        },
    }

    res = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json=payload
    )

    assert res.status_code == 201

    body = res.json()

    assert body["preferences"]["experience_level"] == "mid"
    assert body["preferences"]["salary_min"] == 90000


@pytest.mark.asyncio
async def test_patch_user_preferences(client):
    create = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "name": "Patch Pref",
            "email": "patch@test.com",
            "preferences": {
                "experience_level": "junior"
            },
        }
    )

    user_id = create.json()["_id"]

    patch = await client.patch(
        f"/users/{user_id}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "preferences": {
                "salary_min": 80000,
                "salary_max": 120000,
            }
        },
    )

    assert patch.status_code == 200

    prefs = patch.json()["preferences"]

    assert prefs["salary_min"] == 80000
    assert prefs["salary_max"] == 120000
    assert prefs["experience_level"] == "junior"


@pytest.mark.asyncio
async def test_salary_validation(client):
    res = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "name": "Bad Salary",
            "email": "bad@test.com",
            "preferences": {
                "salary_min": 150000,
                "salary_max": 90000,
            },
        })

    assert res.status_code == 422


@pytest.mark.asyncio
async def test_patch_empty_payload(client):
    create = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "name": "Empty Patch",
            "email": "empty@test.com",
        }
    )

    user_id = create.json()["_id"]

    patch = await client.patch(
        f"/users/{user_id}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={}
    )

    assert patch.status_code == 400


@pytest.mark.asyncio
async def test_patch_invalid_id(client):
    res = await client.patch(
        "/users/notanid",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "X"}
    )

    assert res.status_code == 400


@pytest.mark.asyncio
async def test_updated_at_changes(client):
    create = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "name": "Time Test",
            "email": "time@test.com",
        }
    )

    body = create.json()
    user_id = body["_id"]

    assert body["updated_at"] is None

    patch = await client.patch(
        f"/users/{user_id}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "Later"},
    )

    assert patch.json()["updated_at"] is not None


# ------------------------
# CRUD Tests for /jobs
# ------------------------
@pytest.mark.asyncio
async def test_create_job(client):

    payload = {
        "external_id": "job-123",
        "title": "Research Scientist",
        "company": "OpenAI Labs",
        "description": "Work on cutting-edge research.",
        "location": "San Francisco",
        "remote_type": "hybrid",
        "skills_required": ["Statistics", "Python"],
        "source_url": "https://example.com/job/123",
        "source_platform": "LinkedIn",
        "salary_range": {
            "min": 140000,
            "max": 200000,
            "currency": "USD",
        },
        "ml_features": {
            "processed_text": "research scientist statistics python",
            "keyword_vector": [0.1, 0.5, 0.9],
        },
    }

    res = await client.post(
        "/jobs/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json=payload
    )

    assert res.status_code == 201

    body = res.json()

    assert body["external_id"] == payload["external_id"]
    assert body["title"] == payload["title"]
    assert body["salary_range"]["min"] == 140000


@pytest.mark.asyncio
async def test_create_job_duplicate_external_id(client):

    payload = {
        "external_id": "job-dup",
        "title": "Chef",
        "company": "Bistro Co",
        "description": "Cook amazing food.",
        "location": "NYC",
    }

    await client.post(
        "/jobs/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json=payload
    )

    dup = await client.post(
        "/jobs/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json=payload
    )

    assert dup.status_code == 409


@pytest.mark.asyncio
async def test_get_jobs(client):

    await client.post(
        "/jobs/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "external_id": "job-list",
            "title": "Doctor",
            "company": "City Hospital",
            "description": "Provide patient care.",
            "location": "Boston",
        })

    res = await client.get(
        "/jobs/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
    )

    assert res.status_code == 200
    assert len(res.json()) >= 1


@pytest.mark.asyncio
async def test_get_job_by_id(client):

    create = await client.post(
        "/jobs/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "external_id": "job-get",
            "title": "Teacher",
            "company": "Public School",
            "description": "Teach students.",
            "location": "Denver",
        })

    job_id = create.json()["_id"]

    res = await client.get(
        f"/jobs/{job_id}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
    )

    assert res.status_code == 200
    assert res.json()["_id"] == job_id


@pytest.mark.asyncio
async def test_patch_job_salary_range(client):

    create = await client.post(
        "/jobs/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "external_id": "job-patch",
            "title": "Urban Planner",
            "company": "City Office",
            "description": "Plan cities.",
            "location": "Seattle",
        })

    job_id = create.json()["_id"]

    patch = await client.patch(
        f"/jobs/{job_id}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "salary_range": {
                "min": 90000,
                "max": 130000,
            }
        },
    )

    assert patch.status_code == 200

    salary = patch.json()["salary_range"]

    assert salary["min"] == 90000
    assert salary["max"] == 130000


@pytest.mark.asyncio
async def test_job_salary_validation(client):

    res = await client.post(
        "/jobs/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "external_id": "job-bad-salary",
            "title": "Analyst",
            "company": "Finance Corp",
            "description": "Analyze data.",
            "location": "Chicago",
            "salary_range": {
                "min": 150000,
                "max": 80000,
            },
        })

    assert res.status_code == 422


@pytest.mark.asyncio
async def test_patch_empty_job_payload(client):

    create = await client.post(
        "/jobs/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "external_id": "job-empty",
            "title": "Consultant",
            "company": "Biz Co",
            "description": "Advise clients.",
            "location": "Remote",
        })

    job_id = create.json()["_id"]

    patch = await client.patch(
        f"/jobs/{job_id}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={})

    assert patch.status_code == 400


@pytest.mark.asyncio
async def test_patch_job_invalid_id(client):

    res = await client.patch(
        "/jobs/notanid",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"title": "X"}
    )
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_delete_job(client):

    create = await client.post(
        "/jobs/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "external_id": "job-del",
            "title": "Music Producer",
            "company": "Studio Inc",
            "description": "Produce music.",
            "location": "Nashville",
        })

    job_id = create.json()["_id"]

    delete = await client.delete(
        f"/jobs/{job_id}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
    )

    assert delete.status_code == 204

    check = await client.get(
        f"/jobs/{job_id}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
    )

    assert check.status_code == 404


# ------------------------
# CRUD Tests for /savedsearches
# ------------------------
@pytest.mark.asyncio
async def test_create_saved_search(client):

    # create user first
    user = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "Saved User", "email": "saved@test.com"},
    )

    user_id = user.json()["_id"]

    payload = {
        "user_id": user_id,
        "search_name": "Data Scientist Roles",
        "search_query": {
            "title": "data scientist",
            "location": "remote",
        },
    }

    res = await client.post(
        "/saved-searches/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json=payload
    )

    assert res.status_code == 201

    body = res.json()

    assert body["search_name"] == payload["search_name"]
    assert body["user_id"] == user_id
    assert body["total_matches"] == 0
    assert body["new_matches"] == 0
    assert "created_at" in body


@pytest.mark.asyncio
async def test_get_saved_searches_for_user(client):

    user = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "Search Owner", "email": "owner@test.com"},
    )

    user_id = user.json()["_id"]

    await client.post(
        "/saved-searches/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "user_id": user_id,
            "search_name": "ML Roles",
            "search_query": {"title": "ml"},
        },
    )

    res = await client.get(
        f"/saved-searches/user/{user_id}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
    )

    assert res.status_code == 200
    assert len(res.json()) == 1


@pytest.mark.asyncio
async def test_get_saved_search_by_id(client):

    user = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "Search Owner", "email": "owner@test.com"},
    )

    user_id = user.json()["_id"]

    create = await client.post(
        "/saved-searches/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "user_id": user_id,
            "search_name": "Backend Jobs",
            "search_query": {"title": "backend"},
        },
    )

    search_id = create.json()["id"]

    res = await client.get(
        f"/saved-searches/{search_id}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
    )

    assert res.status_code == 200
    assert res.json()["id"] == search_id


@pytest.mark.asyncio
async def test_patch_saved_search(client):

    user = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "Patch User", "email": "patch@test.com"},
    )

    user_id = user.json()["_id"]

    create = await client.post(
        "/saved-searches/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "user_id": user_id,
            "search_name": "Old Name",
            "search_query": {"title": "qa"},
        },
    )

    search_id = create.json()["id"]

    patch = await client.patch(
        f"/saved-searches/{search_id}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"search_name": "Updated Name"},
    )

    assert patch.status_code == 200
    assert patch.json()["search_name"] == "Updated Name"


@pytest.mark.asyncio
async def test_put_saved_search(client):

    user = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "Put User", "email": "put@test.com"},
    )

    user_id = user.json()["_id"]

    create = await client.post(
        "/saved-searches/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "user_id": user_id,
            "search_name": "Old",
            "search_query": {"role": "dev"},
        },
    )

    search_id = create.json()["id"]

    put = await client.put(
        f"/saved-searches/{search_id}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "search_name": "New",
            "search_query": {"role": "frontend"},
        },
    )

    assert put.status_code == 200
    assert put.json()["search_name"] == "New"


@pytest.mark.asyncio
async def test_delete_saved_search(client):

    user = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "Delete User", "email": "delete@test.com"},
    )

    user_id = user.json()["_id"]

    create = await client.post(
        "/saved-searches/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "user_id": user_id,
            "search_name": "Temp",
            "search_query": {"title": "temp"},
        },
    )

    search_id = create.json()["id"]

    delete = await client.delete(
        f"/saved-searches/{search_id}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")}
    )

    assert delete.status_code == 204

    check = await client.get(
        f"/saved-searches/{search_id}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")}
    )

    assert check.status_code == 404


@pytest.mark.asyncio
async def test_patch_empty_saved_search_payload(client):

    user = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "Empty Patch", "email": "empty@test.com"},
    )

    user_id = user.json()["_id"]

    create = await client.post(
        "/saved-searches/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "user_id": user_id,
            "search_name": "Name",
            "search_query": {"q": "x"},
        },
    )

    search_id = create.json()["id"]

    patch = await client.patch(
        f"/saved-searches/{search_id}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={},
    )

    assert patch.status_code == 400


@pytest.mark.asyncio
async def test_saved_search_invalid_id(client):

    res = await client.get(
        "/saved-searches/not-an-id",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")}
    )

    assert res.status_code == 400


@pytest.mark.asyncio
async def test_saved_search_invalid_user_fk(client):

    payload = {
        "user_id": "not-an-object-id",
        "search_name": "Bad",
        "search_query": {},
    }

    res = await client.post(
        "/saved-searches/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json=payload
    )

    assert res.status_code == 400


# ------------------------
# CRUD Tests for /users/{user_id}/stats
# ------------------------

@pytest.mark.asyncio
async def test_userstats_auto_created(client):
    """Test that user stats are automatically created when a user is created"""
    user = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "Stats User", "email": "stats@test.com"},
    )

    user_id = user.json()["_id"]

    res = await client.get(
        f"/users/{user_id}/stats",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")}
    )

    assert res.status_code == 200

    body = res.json()

    assert body["user_id"] == user_id
    assert body["jobs_viewed"] == 0
    assert body["jobs_saved"] == 0
    assert body["top_missing_skill"] is None
    assert body["created_at"] is not None
    assert body["last_calculated"] is None


@pytest.mark.asyncio
async def test_patch_userstats_fields(client):
    """Test updating user stats with valid data"""
    user = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "Stats Patch", "email": "patch@test.com"},
    )

    user_id = user.json()["_id"]

    patch = await client.patch(
        f"/users/{user_id}/stats",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "jobs_viewed": 5,
            "jobs_saved": 2,
            "top_missing_skill": "Docker",
        },
    )

    assert patch.status_code == 200

    body = patch.json()

    assert body["jobs_viewed"] == 5
    assert body["jobs_saved"] == 2
    assert body["top_missing_skill"] == "Docker"
    assert body["last_calculated"] is not None


@pytest.mark.asyncio
async def test_patch_userstats_partial_update(client):
    """Test partial update of user stats"""
    user = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "Partial Update", "email": "partial@test.com"},
    )

    user_id = user.json()["_id"]

    # Update only jobs_viewed
    patch = await client.patch(
        f"/users/{user_id}/stats",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"jobs_viewed": 10},
    )

    assert patch.status_code == 200

    body = patch.json()

    assert body["jobs_viewed"] == 10
    assert body["jobs_saved"] == 0
    assert body["top_missing_skill"] is None
    assert body["last_calculated"] is not None


@pytest.mark.asyncio
async def test_patch_empty_userstats_payload(client):
    """Test that empty payload returns error"""
    user = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "Empty Stats", "email": "empty@test.com"},
    )

    user_id = user.json()["_id"]

    patch = await client.patch(
        f"/users/{user_id}/stats",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={},
    )

    assert patch.status_code == 400
    assert "No fields provided for update" in patch.json()["detail"]


@pytest.mark.asyncio
async def test_get_userstats_invalid_user_id(client):
    """Test getting stats with invalid user ID format"""
    res = await client.get(
        "/users/not_an_id/stats",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")}
    )

    assert res.status_code == 400
    assert "Invalid user ID" in res.json()["detail"]


@pytest.mark.asyncio
async def test_get_userstats_nonexistent_user(client):
    """Test getting stats for a user that doesn't exist"""
    from bson import ObjectId
    fake_id = str(ObjectId())
    res = await client.get(
        f"/users/{fake_id}/stats",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")}
    )

    assert res.status_code == 404
    assert "UserStats not found" in res.json()["detail"]


@pytest.mark.asyncio
async def test_patch_userstats_nonexistent_user(client):
    """Test patching stats for a user that doesn't exist"""
    from bson import ObjectId
    fake_id = str(ObjectId())
    res = await client.patch(
        f"/users/{fake_id}/stats",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"jobs_viewed": 5},
    )

    assert res.status_code == 404
    assert "UserStats not found" in res.json()["detail"]


@pytest.mark.asyncio
async def test_userstats_deleted_with_user(client):
    """Test that user stats are automatically deleted when user is deleted"""
    user = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "Stats Delete", "email": "del@test.com"},
    )

    user_id = user.json()["_id"]

    # Verify stats exist
    stats = await client.get(
        f"/users/{user_id}/stats",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")}
    )
    assert stats.status_code == 200

    # Delete user
    delete_user = await client.delete(
        f"/users/{user_id}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")}
    )
    assert delete_user.status_code == 204

    # Verify stats are also gone
    check_stats = await client.get(
        f"/users/{user_id}/stats",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")}
    )
    assert check_stats.status_code == 404


@pytest.mark.asyncio
async def test_patch_userstats_invalid_data_types(client):
    """Test that invalid data types are rejected"""
    user = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "Invalid Data", "email": "invalid@test.com"},
    )

    user_id = user.json()["_id"]

    # Try to send string for integer field
    patch = await client.patch(
        f"/users/{user_id}/stats",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"jobs_viewed": "not_a_number"},
    )

    assert patch.status_code == 422


@pytest.mark.asyncio
async def test_userstats_incrementing_workflow(client):
    """Test a realistic workflow of incrementing stats over time"""
    user = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "Workflow User", "email": "workflow@test.com"},
    )

    user_id = user.json()["_id"]

    # First update
    await client.patch(
        f"/users/{user_id}/stats",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"jobs_viewed": 1},
    )

    # Second update
    await client.patch(
        f"/users/{user_id}/stats",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"jobs_viewed": 5, "jobs_saved": 1},
    )

    # Third update
    res = await client.patch(
        f"/users/{user_id}/stats",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "jobs_viewed": 10,
            "jobs_saved": 3,
            "top_missing_skill": "Python"
        },
    )

    assert res.status_code == 200
    body = res.json()
    assert body["jobs_viewed"] == 10
    assert body["jobs_saved"] == 3
    assert body["top_missing_skill"] == "Python"
    assert body["last_calculated"] is not None


# ------------------------
# CRUD Tests for /interactions
# ------------------------
@pytest.mark.asyncio
async def test_create_userjobinteraction(client):
    """Test creating a user-job interaction with valid data"""

    user = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "Interaction User", "email": "ij@test.com"},
    )

    job = await client.post(
        "/jobs/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "external_id": "job-int-1",
            "title": "Biologist",
            "company": "BioLab",
            "description": "Research life.",
            "location": "Boston",
        },
    )

    res = await client.post(
        "/interactions/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "user_id": user.json()["_id"],
            "job_id": job.json()["_id"],
            "interaction_type": "viewed",
        },
    )

    assert res.status_code == 201

    body = res.json()

    assert body["user_id"] == user.json()["_id"]
    assert body["job_id"] == job.json()["_id"]
    assert body["interaction_type"] == "viewed"
    assert "id" in body
    assert "timestamp" in body


@pytest.mark.asyncio
async def test_userjobinteraction_invalid_user_fk(client):
    """Test that creating an interaction with invalid user_id FK fails"""

    job = await client.post(
        "/jobs/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "external_id": "job-int-2",
            "title": "Chemist",
            "company": "Lab",
            "description": "Analyze samples.",
            "location": "NYC",
        },
    )

    res = await client.post(
        "/interactions/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "user_id": "notanid",
            "job_id": job.json()["_id"],
            "interaction_type": "viewed",
        },
    )

    assert res.status_code == 400


@pytest.mark.asyncio
async def test_userjobinteraction_duplicate_blocked(client):
    """Test that creating a duplicate interaction
    (same user_id, job_id, interaction_type) is blocked"""

    user = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "Dup IJ", "email": "dupij@test.com"},
    )

    job = await client.post(
        "/jobs/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "external_id": "job-int-3",
            "title": "Teacher",
            "company": "School",
            "description": "Teach.",
            "location": "Denver",
        },
    )

    payload = {
        "user_id": user.json()["_id"],
        "job_id": job.json()["_id"],
        "interaction_type": "saved",
    }

    first = await client.post(
        "/interactions/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json=payload,
    )

    assert first.status_code == 201

    second = await client.post(
        "/interactions/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json=payload,
    )

    assert second.status_code == 409


@pytest.mark.asyncio
async def test_get_interactions_by_user(client):
    """Test fetching interactions for a user returns all
    interactions associated with that user"""

    user = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "User Fetch", "email": "uf@test.com"},
    )

    job1 = await client.post(
        "/jobs/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "external_id": "job-int-4",
            "title": "Nurse",
            "company": "Hospital",
            "description": "Care.",
            "location": "Miami",
        },
    )

    job2 = await client.post(
        "/jobs/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "external_id": "job-int-5",
            "title": "Analyst",
            "company": "Corp",
            "description": "Analyze.",
            "location": "Chicago",
        },
    )

    await client.post(
        "/interactions/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "user_id": user.json()["_id"],
            "job_id": job1.json()["_id"],
            "interaction_type": "viewed",
        },
    )

    await client.post(
        "/interactions/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "user_id": user.json()["_id"],
            "job_id": job2.json()["_id"],
            "interaction_type": "applied",
        },
    )

    res = await client.get(
        f"/interactions/user/{user.json()['_id']}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
    )

    assert res.status_code == 200
    assert len(res.json()) == 2


@pytest.mark.asyncio
async def test_get_interactions_by_job(client):
    """Test fetching interactions for a job returns all interactions
    associated with that job"""

    user = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "User Fetch", "email": "uf@test.com"},
    )

    job = await client.post(
        "/jobs/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "external_id": "job-int-5",
            "title": "Analyst",
            "company": "Corp",
            "description": "Analyze.",
            "location": "Chicago",
        },
    )

    await client.post(
        "/interactions/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "user_id": user.json()["_id"],
            "job_id": job.json()["_id"],
            "interaction_type": "applied",
        },
    )

    res = await client.get(
        f"/interactions/job/{job.json()['_id']}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
    )

    assert res.status_code == 200
    assert res.json()[0]["interaction_type"] == "applied"
    assert len(res.json()) == 1


@pytest.mark.asyncio
async def test_patch_userjobinteraction(client):
    """Test updating the interaction_type of an
    existing user-job interaction"""

    user = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "Patch IJ", "email": "patchij@test.com"},
    )

    job = await client.post(
        "/jobs/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "external_id": "job-int-6",
            "title": "Designer",
            "company": "Studio",
            "description": "Design.",
            "location": "Remote",
        },
    )

    create = await client.post(
        "/interactions/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "user_id": user.json()["_id"],
            "job_id": job.json()["_id"],
            "interaction_type": "viewed",
        },
    )

    iid = create.json()["id"]

    patch = await client.patch(
        f"/interactions/{iid}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"interaction_type": "saved"},
    )

    assert patch.status_code == 200
    assert patch.json()["interaction_type"] == "saved"


@pytest.mark.asyncio
async def test_patch_userjobinteraction_empty_payload(client):
    """Test that patching a user-job interaction with
    an empty payload returns an error"""

    user = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "Empty IJ", "email": "emptyij@test.com"},
    )

    job = await client.post(
        "/jobs/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "external_id": "job-int-7",
            "title": "Writer",
            "company": "Media",
            "description": "Write.",
            "location": "LA",
        },
    )

    create = await client.post(
        "/interactions/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "user_id": user.json()["_id"],
            "job_id": job.json()["_id"],
            "interaction_type": "viewed",
        },
    )

    iid = create.json()["id"]

    patch = await client.patch(
        f"/interactions/{iid}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={},
    )

    assert patch.status_code == 400


@pytest.mark.asyncio
async def test_delete_userjobinteraction(client):
    """Test deleting a user-job interaction by ID"""

    user = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "Del IJ", "email": "delij@test.com"},
    )

    job = await client.post(
        "/jobs/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "external_id": "job-int-8",
            "title": "Clerk",
            "company": "Office",
            "description": "Admin.",
            "location": "Austin",
        },
    )

    create = await client.post(
        "/interactions/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "user_id": user.json()["_id"],
            "job_id": job.json()["_id"],
            "interaction_type": "viewed",
        },
    )

    iid = create.json()["id"]

    delete = await client.delete(
        f"/interactions/{iid}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
    )

    assert delete.status_code == 204


@pytest.mark.asyncio
async def test_interactions_deleted_with_user(client):
    """Test that interactions are automatically deleted
    when a user is deleted"""

    user = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "Cascade User", "email": "cascade@test.com"},
    )

    job = await client.post(
        "/jobs/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "external_id": "job-cascade-1",
            "title": "Scientist",
            "company": "Lab",
            "description": "Research.",
            "location": "NYC",
        },
    )

    # Create interaction
    await client.post(
        "/interactions/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "user_id": user.json()["_id"],
            "job_id": job.json()["_id"],
            "interaction_type": "viewed",
        },
    )

    # Delete user
    await client.delete(
        f"/users/{user.json()['_id']}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
    )

    # Verify interactions are gone
    res = await client.get(
        f"/interactions/user/{user.json()['_id']}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
    )

    assert res.status_code == 200
    assert res.json() == []


@pytest.mark.asyncio
async def test_interactions_deleted_with_job(client):
    """Test that interactions are automatically deleted
    when a job is deleted"""

    user = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "Cascade Job", "email": "cascadejob@test.com"},
    )

    job = await client.post(
        "/jobs/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "external_id": "job-cascade-2",
            "title": "Engineer",
            "company": "Tech",
            "description": "Build.",
            "location": "SF",
        },
    )

    # Create interaction
    await client.post(
        "/interactions/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "user_id": user.json()["_id"],
            "job_id": job.json()["_id"],
            "interaction_type": "saved",
        },
    )

    # Delete job
    await client.delete(
        f"/jobs/{job.json()['_id']}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
    )

    # Verify interactions are gone
    res = await client.get(
        f"/interactions/job/{job.json()['_id']}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
    )

    assert res.status_code == 200
    assert res.json() == []


# ------------------------
# CRUD Tests for /jobmatches
# ------------------------

@pytest.mark.asyncio
async def test_create_jobmatch(client):
    """Test creating a job match with valid data"""

    user = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "Match User", "email": "match@test.com"},
    )

    job = await client.post(
        "/jobs/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "external_id": "job-match-1",
            "title": "Data Scientist",
            "company": "AI Corp",
            "description": "ML work.",
            "location": "Remote",
        },
    )

    payload = {
        "user_id": user.json()["_id"],
        "job_id": job.json()["_id"],
        "score": 0.87,
        "missing_skills": ["Docker"],
    }

    res = await client.post(
        "/job-matches/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json=payload,
    )

    assert res.status_code == 201

    body = res.json()

    assert body["user_id"] == payload["user_id"]
    assert body["job_id"] == payload["job_id"]
    assert body["score"] == 0.87
    assert body["missing_skills"] == ["Docker"]
    assert "id" in body
    assert "match_date" in body


@pytest.mark.asyncio
async def test_jobmatch_duplicate_blocked(client):
    """Test that creating a duplicate job match
    (same user_id and job_id) is blocked"""

    user = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "Dup Match", "email": "dup-match@test.com"},
    )

    job = await client.post(
        "/jobs/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "external_id": "job-match-dup",
            "title": "Engineer",
            "company": "Tech",
            "description": "Build.",
            "location": "SF",
        },
    )

    payload = {
        "user_id": user.json()["_id"],
        "job_id": job.json()["_id"],
        "score": 0.75,
        "missing_skills": [],
    }

    first = await client.post(
        "/job-matches/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json=payload,
    )
    assert first.status_code == 201

    second = await client.post(
        "/job-matches/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json=payload,
    )
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_get_jobmatches_for_user(client):
    """Test fetching job matches for a user returns
    all matches associated with that user"""

    user = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "List Match", "email": "list@test.com"},
    )

    job = await client.post(
        "/jobs/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "external_id": "job-match-list",
            "title": "Analyst",
            "company": "Finance",
            "description": "Analyze.",
            "location": "NYC",
        },
    )

    await client.post(
        "/job-matches/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "user_id": user.json()["_id"],
            "job_id": job.json()["_id"],
            "score": 0.6,
            "missing_skills": [],
        },
    )

    res = await client.get(
        f"/job-matches/user/{user.json()['_id']}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
    )

    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["score"] == 0.6


@pytest.mark.asyncio
async def test_patch_jobmatch(client):
    """Test updating score and missing_skills"""

    user = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "Patch Match", "email": "patchmatch@test.com"},
    )

    job = await client.post(
        "/jobs/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "external_id": "job-match-patch",
            "title": "Architect",
            "company": "Design",
            "description": "Design systems.",
            "location": "Chicago",
        },
    )

    create = await client.post(
        "/job-matches/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "user_id": user.json()["_id"],
            "job_id": job.json()["_id"],
            "score": 0.5,
            "missing_skills": [],
        },
    )

    match_id = create.json()["id"]

    patch = await client.patch(
        f"/job-matches/{match_id}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"score": 0.9},
    )

    assert patch.status_code == 200
    assert patch.json()["score"] == 0.9


@pytest.mark.asyncio
async def test_delete_jobmatch(client):
    """Test deleting a job match by ID and verifying it no longer
    exists"""

    user = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "Delete Match", "email": "delmatch@test.com"},
    )

    job = await client.post(
        "/jobs/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "external_id": "job-match-del",
            "title": "Nurse",
            "company": "Hospital",
            "description": "Care.",
            "location": "Boston",
        },
    )

    create = await client.post(
        "/job-matches/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "user_id": user.json()["_id"],
            "job_id": job.json()["_id"],
            "score": 0.8,
            "missing_skills": [],
        },
    )

    match_id = create.json()["id"]

    delete = await client.delete(
        f"/job-matches/{match_id}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
    )
    assert delete.status_code == 204


@pytest.mark.asyncio
async def test_jobmatch_invalid_fk(client):
    """Test that creating a job match with invalid user_id
    and job_id foreign keys fails"""

    res = await client.post(
        "/job-matches/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "user_id": "invalid",
            "job_id": "invalid",
            "score": 0.5,
            "missing_skills": [],
        },
    )

    assert res.status_code == 400


@pytest.mark.asyncio
async def test_jobmatch_score_validation(client):
    """Test that creating a job match with an invalid relevancy score
    (e.g. greater than 1) fails"""

    user = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "Score Test", "email": "score@test.com"},
    )

    job = await client.post(
        "/jobs/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "external_id": "job-score",
            "title": "QA",
            "company": "TestCo",
            "description": "Test.",
            "location": "Remote",
        },
    )

    res = await client.post(
        "/job-matches/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "user_id": user.json()["_id"],
            "job_id": job.json()["_id"],
            "score": 1.5,  # invalid
            "missing_skills": [],
        },
    )

    assert res.status_code == 422


@pytest.mark.asyncio
async def test_user_delete_cascades_jobmatches(client):
    """Test that when a user is deleted,
    their associated job matches are also deleted"""

    user = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "Cascade User", "email": "cascade_user@test.com"},
    )
    user_id = user.json()["_id"]

    job = await client.post(
        "/jobs/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "external_id": "job-cascade-1",
            "title": "Engineer",
            "company": "Tech Co",
            "description": "Build stuff",
            "location": "Remote",
        },
    )
    job_id = job.json()["_id"]

    await client.post(
        "/job-matches/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "user_id": user_id,
            "job_id": job_id,
            "score": 0.85,
            "missing_skills": [],
        },
    )

    delete = await client.delete(
        f"/users/{user_id}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
    )
    assert delete.status_code == 204

    matches = await client.get(
        f"/job-matches/user/{user_id}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
    )
    assert matches.status_code == 200
    assert matches.json() == []


@pytest.mark.asyncio
async def test_job_delete_cascades_jobmatches(client):
    """Test that when a job is deleted,
    its associated job matches are also deleted"""

    user = await client.post(
        "/users/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={"name": "Cascade Job User", "email": "cascade_job@test.com"},
    )
    user_id = user.json()["_id"]

    job = await client.post(
        "/jobs/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "external_id": "job-cascade-2",
            "title": "Data Scientist",
            "company": "AI Corp",
            "description": "Analyze data",
            "location": "NYC",
        },
    )
    job_id = job.json()["_id"]

    await client.post(
        "/job-matches/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "user_id": user_id,
            "job_id": job_id,
            "score": 0.92,
            "missing_skills": ["AWS"],
        },
    )

    delete = await client.delete(
        f"/jobs/{job_id}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
    )
    assert delete.status_code == 204

    matches = await client.get(
        f"/job-matches/user/{user_id}",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
    )
    assert matches.status_code == 200
    assert matches.json() == []


@pytest.mark.asyncio
async def test_top_missing_skill_updates_on_create(client):

    db = get_db()

    # Create user
    user_id = ObjectId()
    await db.users.insert_one({"_id": user_id})

    # Create UserStats for that user
    await db.user_stats.insert_one({
        "user_id": user_id,
        "jobs_viewed": 0,
        "jobs_saved": 0,
        "top_missing_skill": None,
        "created_at": datetime.utcnow()
    })

    # Create job
    job_id = ObjectId()
    await db.jobs.insert_one({"_id": job_id})

    # Create job match with missing skills
    response = await client.post(
        "/job-matches/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "user_id": str(user_id),
            "job_id": str(job_id),
            "score": 0.7,
            "missing_skills": ["Python", "SQL"]
        }
    )

    assert response.status_code == 201

    # Verify automatic recalculation happened
    stats = await db.user_stats.find_one({"user_id": user_id})

    assert stats["top_missing_skill"] in ["Python", "SQL"]


@pytest.mark.asyncio
async def test_top_missing_skill_counts_correctly(client):

    db = get_db()

    user_id = ObjectId()
    await db.users.insert_one({"_id": user_id})
    await db.user_stats.insert_one({
        "user_id": user_id,
        "jobs_viewed": 0,
        "jobs_saved": 0,
        "top_missing_skill": None,
        "created_at": datetime.utcnow()
    })

    job1 = ObjectId()
    job2 = ObjectId()

    await db.jobs.insert_many([
        {"_id": job1, "external_id": "job1"},
        {"_id": job2, "external_id": "job2"}
    ])

    # First match
    await client.post(
        "/job-matches/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "user_id": str(user_id),
            "job_id": str(job1),
            "score": 0.8,
            "missing_skills": ["Python"]
        })

    # Second match
    await client.post(
        "/job-matches/",
        headers={"aijobhunt-api-secret": os.getenv("API_SECRET")},
        json={
            "user_id": str(user_id),
            "job_id": str(job2),
            "score": 0.9,
            "missing_skills": ["Python", "AWS"]
        })

    stats = await db.user_stats.find_one({"user_id": user_id})

    # Python appears twice
    assert stats["top_missing_skill"] == "Python"
