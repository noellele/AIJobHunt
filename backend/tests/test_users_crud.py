import pytest


# ------------------------
# CRUD Tests for /users
# ------------------------
@pytest.mark.asyncio
async def test_create_user(client):

    payload = {
        "name": "John Doe",
        "email": "john@test.com"
    }

    response = await client.post("/users/", json=payload)

    assert response.status_code == 201

    body = response.json()

    assert body["name"] == payload["name"]
    assert body["email"] == payload["email"]
    assert "id" in body


@pytest.mark.asyncio
async def test_get_users(client):

    await client.post("/users/", json={
        "name": "Jane Hill",
        "email": "jane@test.com"
    })

    response = await client.get("/users/")

    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_get_user_by_id(client):

    create = await client.post("/users/", json={
        "name": "Noelle Lee",
        "email": "noelle@test.com"
    })

    user_id = create.json()["id"]

    response = await client.get(f"/users/{user_id}")

    assert response.status_code == 200
    assert response.json()["id"] == user_id


@pytest.mark.asyncio
async def test_update_user(client):

    create = await client.post("/users/", json={
        "name": "Bob Sam",
        "email": "bob@test.com"
    })

    user_id = create.json()["id"]

    update = await client.put(
        f"/users/{user_id}",
        json={"name": "New Name"}
    )

    assert update.status_code == 200
    assert update.json()["name"] == "New Name"


@pytest.mark.asyncio
async def test_delete_user(client):

    create = await client.post("/users/", json={
        "name": "Delete Me",
        "email": "delete@test.com"
    })

    user_id = create.json()["id"]

    delete = await client.delete(f"/users/{user_id}")

    assert delete.status_code == 204

    check = await client.get(f"/users/{user_id}")
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

    res = await client.post("/users/", json=payload)

    assert res.status_code == 201

    body = res.json()

    assert body["preferences"]["experience_level"] == "mid"
    assert body["preferences"]["salary_min"] == 90000


@pytest.mark.asyncio
async def test_patch_user_preferences(client):
    create = await client.post("/users/", json={
        "name": "Patch Pref",
        "email": "patch@test.com",
        "preferences": {
            "experience_level": "junior"
        },
    })

    user_id = create.json()["id"]

    patch = await client.patch(
        f"/users/{user_id}",
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
    res = await client.post("/users/", json={
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
    create = await client.post("/users/", json={
        "name": "Empty Patch",
        "email": "empty@test.com",
    })

    user_id = create.json()["id"]

    patch = await client.patch(f"/users/{user_id}", json={})

    assert patch.status_code == 400


@pytest.mark.asyncio
async def test_patch_invalid_id(client):
    res = await client.patch("/users/notanid", json={"name": "X"})

    assert res.status_code == 400


@pytest.mark.asyncio
async def test_updated_at_changes(client):
    create = await client.post("/users/", json={
        "name": "Time Test",
        "email": "time@test.com",
    })

    body = create.json()
    user_id = body["id"]

    assert body["updated_at"] is None

    patch = await client.patch(
        f"/users/{user_id}",
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

    res = await client.post("/jobs/", json=payload)

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

    await client.post("/jobs/", json=payload)

    dup = await client.post("/jobs/", json=payload)

    assert dup.status_code == 409


@pytest.mark.asyncio
async def test_get_jobs(client):

    await client.post("/jobs/", json={
        "external_id": "job-list",
        "title": "Doctor",
        "company": "City Hospital",
        "description": "Provide patient care.",
        "location": "Boston",
    })

    res = await client.get("/jobs/")

    assert res.status_code == 200
    assert len(res.json()) >= 1


@pytest.mark.asyncio
async def test_get_job_by_id(client):

    create = await client.post("/jobs/", json={
        "external_id": "job-get",
        "title": "Teacher",
        "company": "Public School",
        "description": "Teach students.",
        "location": "Denver",
    })

    job_id = create.json()["id"]

    res = await client.get(f"/jobs/{job_id}")

    assert res.status_code == 200
    assert res.json()["id"] == job_id


@pytest.mark.asyncio
async def test_patch_job_salary_range(client):

    create = await client.post("/jobs/", json={
        "external_id": "job-patch",
        "title": "Urban Planner",
        "company": "City Office",
        "description": "Plan cities.",
        "location": "Seattle",
    })

    job_id = create.json()["id"]

    patch = await client.patch(
        f"/jobs/{job_id}",
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

    res = await client.post("/jobs/", json={
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

    create = await client.post("/jobs/", json={
        "external_id": "job-empty",
        "title": "Consultant",
        "company": "Biz Co",
        "description": "Advise clients.",
        "location": "Remote",
    })

    job_id = create.json()["id"]

    patch = await client.patch(f"/jobs/{job_id}", json={})

    assert patch.status_code == 400


@pytest.mark.asyncio
async def test_patch_job_invalid_id(client):

    res = await client.patch("/jobs/notanid", json={"title": "X"})

    assert res.status_code == 400


@pytest.mark.asyncio
async def test_delete_job(client):

    create = await client.post("/jobs/", json={
        "external_id": "job-del",
        "title": "Music Producer",
        "company": "Studio Inc",
        "description": "Produce music.",
        "location": "Nashville",
    })

    job_id = create.json()["id"]

    delete = await client.delete(f"/jobs/{job_id}")

    assert delete.status_code == 204

    check = await client.get(f"/jobs/{job_id}")

    assert check.status_code == 404


# ------------------------
# CRUD Tests for /savedsearches
# ------------------------
@pytest.mark.asyncio
async def test_create_saved_search(client):

    # create user first
    user = await client.post(
        "/users/",
        json={"name": "Saved User", "email": "saved@test.com"},
    )

    user_id = user.json()["id"]

    payload = {
        "user_id": user_id,
        "search_name": "Data Scientist Roles",
        "search_query": {
            "title": "data scientist",
            "location": "remote",
        },
    }

    res = await client.post("/saved-searches/", json=payload)

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
        json={"name": "Search Owner", "email": "owner@test.com"},
    )

    user_id = user.json()["id"]

    await client.post(
        "/saved-searches/",
        json={
            "user_id": user_id,
            "search_name": "ML Roles",
            "search_query": {"title": "ml"},
        },
    )

    res = await client.get(f"/saved-searches/user/{user_id}")

    assert res.status_code == 200
    assert len(res.json()) == 1


@pytest.mark.asyncio
async def test_get_saved_search_by_id(client):

    user = await client.post(
        "/users/",
        json={"name": "Lookup User", "email": "lookup@test.com"},
    )

    user_id = user.json()["id"]

    create = await client.post(
        "/saved-searches/",
        json={
            "user_id": user_id,
            "search_name": "Backend Jobs",
            "search_query": {"title": "backend"},
        },
    )

    search_id = create.json()["id"]

    res = await client.get(f"/saved-searches/{search_id}")

    assert res.status_code == 200
    assert res.json()["id"] == search_id


@pytest.mark.asyncio
async def test_patch_saved_search(client):

    user = await client.post(
        "/users/",
        json={"name": "Patch User", "email": "patch@test.com"},
    )

    user_id = user.json()["id"]

    create = await client.post(
        "/saved-searches/",
        json={
            "user_id": user_id,
            "search_name": "Old Name",
            "search_query": {"title": "qa"},
        },
    )

    search_id = create.json()["id"]

    patch = await client.patch(
        f"/saved-searches/{search_id}",
        json={"search_name": "Updated Name"},
    )

    assert patch.status_code == 200
    assert patch.json()["search_name"] == "Updated Name"


@pytest.mark.asyncio
async def test_put_saved_search(client):

    user = await client.post(
        "/users/",
        json={"name": "Put User", "email": "put@test.com"},
    )

    user_id = user.json()["id"]

    create = await client.post(
        "/saved-searches/",
        json={
            "user_id": user_id,
            "search_name": "Old",
            "search_query": {"role": "dev"},
        },
    )

    search_id = create.json()["id"]

    put = await client.put(
        f"/saved-searches/{search_id}",
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
        json={"name": "Delete User", "email": "delete@test.com"},
    )

    user_id = user.json()["id"]

    create = await client.post(
        "/saved-searches/",
        json={
            "user_id": user_id,
            "search_name": "Temp",
            "search_query": {"title": "temp"},
        },
    )

    search_id = create.json()["id"]

    delete = await client.delete(
        f"/saved-searches/{search_id}",
    )

    assert delete.status_code == 204

    check = await client.get(
        f"/saved-searches/{search_id}",
    )

    assert check.status_code == 404


@pytest.mark.asyncio
async def test_patch_empty_saved_search_payload(client):

    user = await client.post(
        "/users/",
        json={"name": "Empty Patch", "email": "empty@test.com"},
    )

    user_id = user.json()["id"]

    create = await client.post(
        "/saved-searches/",
        json={
            "user_id": user_id,
            "search_name": "Name",
            "search_query": {"q": "x"},
        },
    )

    search_id = create.json()["id"]

    patch = await client.patch(
        f"/saved-searches/{search_id}",
        json={},
    )

    assert patch.status_code == 400


@pytest.mark.asyncio
async def test_saved_search_invalid_id(client):

    res = await client.get("/saved-searches/not-an-id")

    assert res.status_code == 400


@pytest.mark.asyncio
async def test_saved_search_invalid_user_fk(client):

    payload = {
        "user_id": "not-an-object-id",
        "search_name": "Bad",
        "search_query": {},
    }

    res = await client.post("/saved-searches/", json=payload)

    assert res.status_code == 400
