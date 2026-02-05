import pytest


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
