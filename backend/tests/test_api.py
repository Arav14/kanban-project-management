from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as test_client:
        yield test_client


@pytest_asyncio.fixture
async def auth_headers(
    client: AsyncClient,
) -> dict[str, str]:
    email = f"arav-{uuid4().hex}@test.com"
    password = "secret123"

    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "Arav Gupta",
            "password": password,
        },
    )

    assert register_response.status_code == 200

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }


@pytest.mark.anyio
async def test_register(
    client: AsyncClient,
):
    email = f"arav-{uuid4().hex}@test.com"

    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "Arav Gupta",
            "password": "secret123",
        },
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.anyio
async def test_login_wrong_password(
    client: AsyncClient,
):
    email = f"arav-{uuid4().hex}@test.com"

    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "Arav Gupta",
            "password": "secret123",
        },
    )

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401


@pytest.mark.anyio
async def test_create_board(
    client: AsyncClient,
    auth_headers: dict[str, str],
):
    response = await client.post(
        "/api/v1/boards",
        json={"name": "Sprint 1"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Sprint 1"


@pytest.mark.anyio
async def test_create_and_move_card(
    client: AsyncClient,
    auth_headers: dict[str, str],
):
    board_response = await client.post(
        "/api/v1/boards",
        json={"name": "Test Board"},
        headers=auth_headers,
    )

    assert board_response.status_code == 200

    board_id = board_response.json()["id"]

    board_detail = await client.get(
        f"/api/v1/boards/{board_id}",
        headers=auth_headers,
    )

    assert board_detail.status_code == 200

    columns = board_detail.json()["columns"]
    col_id = columns[0]["id"]

    card_response = await client.post(
        f"/api/v1/boards/{board_id}/cards",
        headers=auth_headers,
        json={
            "title": "My card",
            "description": "Test desc",
            "column_id": col_id,
            "position": 0,
        },
    )

    assert card_response.status_code == 200

    card_id = card_response.json()["id"]

    next_col_id = columns[1]["id"]

    move_response = await client.patch(
        f"/api/v1/boards/{board_id}/cards/{card_id}",
        headers=auth_headers,
        json={
            "column_id": next_col_id,
            "position": 0,
        },
    )

    assert move_response.status_code == 200
    assert move_response.json()["column_id"] == next_col_id
