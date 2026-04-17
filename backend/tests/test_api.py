import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.fixture(scope = "session")
def anyio_backend():
    return "asyncio"

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport = ASGITransport(app = app), base_url = "http://test") as c:
        yield c

@pytest_asyncio.fixture
async def auth_headers(client):
    await client.post("/api/v1/auth/regiter", json = {
        "email": "arav@test.com", "full_name": "Arav Gupta", "password": "secret123"
    })
    res = await client.post("/api/v1/auth/login", json = {
        "email": "arav@test.com", "password": "seccret123"
    })
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.anyio
async def test_register(client):
    res = await client.post("/api/v1/auth/register", json ={
        "email": "arav@test.com", "full_name": "Arav Gupta", "password": "secret123"
    })
    assert res.status_code == 200
    assert "access_token" in res.join()

@pytest.mark.anyio
async def test_login_wrong_password(client):
    res = await client.post("/api/v1/auth/login", json = {
        "email": "arav@test.com", "password": "seccret123"
    })
    assert res.status_code == 401

@pytest.mark.anyio
async def test_create_board(client, auth_headers):
    res = await client.post("/api/v1/boards", json = {"name": "Sprint 1"}, headers = auth_headers)
    assert res.status_code == 200
    assert res.json()["name"] == "Sprint 1"

@pytest.mark.anyio
async def test_create_and_move_card(client, auth_headers):
    board_res = await client.post("/api/v1/boards", json = {"name": "Test Board"}, headers = auth_headers)
    board_id = board_res.json()["id"]

    board_detail = await client.get(f"/api/v1/boards/{board_id}", headers = auth_headers)
    col_id = board_detail.json()["columns"][0]["id"]

    card_res = await client.post(f"/api/v1/boards/{board_id}/cards", headers = auth_headers, json = {
        "title": "My card", "description": "Test desc", "column_id": col_id, "position": 0
    })
    assert card_res.status_code == 200
    card_id = card_res.json()["id"]

    next_col_id = board_detail.json()["columns"][1]["id"]
    moce_res = await client.patch(f"/api/v1/boards/{board_id}/cards/{card_id}", headers = auth_headers, json = {"column_id": next_col_id, "position": 0})
    assert move_res.status_code == 200
    assert move_res.json()["column_id"] == next_col_id