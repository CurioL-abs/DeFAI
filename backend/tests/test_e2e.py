"""
End-to-end tests for the DeFAI backend API.

Tests the full flow: wallet auth → agent CRUD → lifecycle → transactions → performance.
Runs against the live backend at http://localhost:8000.
"""

import pytest
import pytest_asyncio
import httpx
import jwt
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"
API = f"{BASE_URL}/api/v1"

JWT_SECRET = "your-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"


def create_test_token(user_id: int, wallet_address: str = "0xTestWallet123") -> str:
    """Create a valid JWT token for testing (bypasses wallet signature verification)."""
    payload = {
        "user_id": user_id,
        "wallet_address": wallet_address,
        "chain": "ethereum",
        "exp": datetime.utcnow() + timedelta(days=1),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


@pytest_asyncio.fixture
async def client():
    async with httpx.AsyncClient(base_url=API, timeout=10) as c:
        yield c


@pytest_asyncio.fixture
async def db_session():
    """Direct DB access for seeding test data."""
    import asyncpg

    conn = await asyncpg.connect(
        "postgresql://postgres:password@localhost:5432/defai_agents"
    )
    yield conn
    await conn.close()


@pytest_asyncio.fixture
async def test_user(db_session):
    """Create a test user directly in DB and return (user_id, token)."""
    wallet = f"0xTestE2E_{datetime.utcnow().timestamp()}"
    row = await db_session.fetchrow(
        "INSERT INTO users (wallet_address, created_at, is_active) VALUES ($1, NOW(), true) RETURNING id, wallet_address",
        wallet,
    )
    user_id = row["id"]
    token = create_test_token(user_id, wallet)
    return {"id": user_id, "wallet": wallet, "token": token}


@pytest.fixture
def auth_headers(test_user):
    return {"Authorization": f"Bearer {test_user['token']}"}


# ── Health checks ──


@pytest.mark.asyncio
async def test_health(client):
    r = await client.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_health_db(client):
    r = await client.get(f"{BASE_URL}/health/db")
    assert r.status_code == 200
    assert r.json()["database"] == "connected"


# ── Auth endpoints ──


@pytest.mark.asyncio
async def test_auth_missing_header(client):
    r = await client.get("/auth/me")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_auth_invalid_token(client):
    r = await client.get("/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_auth_expired_token(client):
    payload = {
        "user_id": 1,
        "wallet_address": "0x123",
        "chain": "ethereum",
        "exp": datetime.utcnow() - timedelta(days=1),
        "iat": datetime.utcnow() - timedelta(days=2),
    }
    expired_token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    r = await client.get("/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_auth_me(client, test_user, auth_headers):
    r = await client.get("/auth/me", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == test_user["id"]
    assert data["wallet_address"] == test_user["wallet"]
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_auth_verify(client, auth_headers):
    r = await client.get("/auth/verify", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["valid"] is True


# ── Agent CRUD ──


@pytest.mark.asyncio
async def test_create_agent(client, test_user, auth_headers):
    r = await client.post(
        "/agents",
        json={"name": "Test Agent", "description": "E2E test", "risk_tolerance": 0.7, "max_position_size": 500.0},
        headers=auth_headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "Test Agent"
    assert data["description"] == "E2E test"
    assert data["risk_tolerance"] == 0.7
    assert data["max_position_size"] == 500.0
    assert data["status"] == "paused"
    assert data["user_id"] == test_user["id"]


@pytest.mark.asyncio
async def test_list_agents(client, test_user, auth_headers):
    # Create two agents
    await client.post("/agents", json={"name": "Agent A"}, headers=auth_headers)
    await client.post("/agents", json={"name": "Agent B"}, headers=auth_headers)

    r = await client.get("/agents", headers=auth_headers)
    assert r.status_code == 200
    agents = r.json()
    assert len(agents) >= 2
    names = [a["name"] for a in agents]
    assert "Agent A" in names
    assert "Agent B" in names


@pytest.mark.asyncio
async def test_get_agent(client, test_user, auth_headers):
    r = await client.post("/agents", json={"name": "Get Me"}, headers=auth_headers)
    agent_id = r.json()["id"]

    r = await client.get(f"/agents/{agent_id}", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["name"] == "Get Me"


@pytest.mark.asyncio
async def test_get_agent_not_found(client, auth_headers):
    r = await client.get("/agents/999999", headers=auth_headers)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_update_agent(client, auth_headers):
    r = await client.post("/agents", json={"name": "Before Update"}, headers=auth_headers)
    agent_id = r.json()["id"]

    r = await client.put(
        f"/agents/{agent_id}",
        json={"name": "After Update", "risk_tolerance": 0.9},
        headers=auth_headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "After Update"
    assert data["risk_tolerance"] == 0.9


@pytest.mark.asyncio
async def test_update_agent_empty_body(client, auth_headers):
    r = await client.post("/agents", json={"name": "No Change"}, headers=auth_headers)
    agent_id = r.json()["id"]

    r = await client.put(f"/agents/{agent_id}", json={}, headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["name"] == "No Change"


@pytest.mark.asyncio
async def test_delete_agent(client, auth_headers):
    r = await client.post("/agents", json={"name": "Delete Me"}, headers=auth_headers)
    agent_id = r.json()["id"]

    r = await client.delete(f"/agents/{agent_id}", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["message"] == "Agent deleted"

    r = await client.get(f"/agents/{agent_id}", headers=auth_headers)
    assert r.status_code == 404


# ── Agent lifecycle ──


@pytest.mark.asyncio
async def test_agent_start(client, auth_headers):
    r = await client.post("/agents", json={"name": "Lifecycle Agent"}, headers=auth_headers)
    agent_id = r.json()["id"]

    r = await client.post(f"/agents/{agent_id}/start", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["status"] == "active"

    r = await client.get(f"/agents/{agent_id}", headers=auth_headers)
    assert r.json()["status"] == "active"


@pytest.mark.asyncio
async def test_agent_pause(client, auth_headers):
    r = await client.post("/agents", json={"name": "Pause Agent"}, headers=auth_headers)
    agent_id = r.json()["id"]

    await client.post(f"/agents/{agent_id}/start", headers=auth_headers)
    r = await client.post(f"/agents/{agent_id}/pause", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["status"] == "paused"


@pytest.mark.asyncio
async def test_agent_stop(client, auth_headers):
    r = await client.post("/agents", json={"name": "Stop Agent"}, headers=auth_headers)
    agent_id = r.json()["id"]

    await client.post(f"/agents/{agent_id}/start", headers=auth_headers)
    r = await client.post(f"/agents/{agent_id}/stop", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["status"] == "stopped"


# ── Agent isolation (user B cannot access user A's agents) ──


@pytest.mark.asyncio
async def test_agent_isolation(client, test_user, db_session):
    # Create a second user
    wallet_b = f"0xUserB_{datetime.utcnow().timestamp()}"
    row = await db_session.fetchrow(
        "INSERT INTO users (wallet_address, created_at, is_active) VALUES ($1, NOW(), true) RETURNING id",
        wallet_b,
    )
    token_b = create_test_token(row["id"], wallet_b)
    headers_b = {"Authorization": f"Bearer {token_b}"}

    headers_a = {"Authorization": f"Bearer {test_user['token']}"}

    # User A creates an agent
    r = await client.post("/agents", json={"name": "A's Agent"}, headers=headers_a)
    agent_id = r.json()["id"]

    # User B cannot access it
    r = await client.get(f"/agents/{agent_id}", headers=headers_b)
    assert r.status_code == 404

    r = await client.put(f"/agents/{agent_id}", json={"name": "Hacked"}, headers=headers_b)
    assert r.status_code == 404

    r = await client.delete(f"/agents/{agent_id}", headers=headers_b)
    assert r.status_code == 404


# ── Transactions ──


@pytest.mark.asyncio
async def test_list_transactions_empty(client, auth_headers):
    r = await client.post("/agents", json={"name": "TX Agent"}, headers=auth_headers)
    agent_id = r.json()["id"]

    r = await client.get(f"/agents/{agent_id}/transactions", headers=auth_headers)
    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.asyncio
async def test_list_transactions_with_data(client, auth_headers, db_session):
    r = await client.post("/agents", json={"name": "TX Agent 2"}, headers=auth_headers)
    agent_id = r.json()["id"]

    # Seed transactions directly
    for i in range(3):
        await db_session.execute(
            "INSERT INTO transactions (agent_id, transaction_type, amount, blockchain, status, created_at) VALUES ($1, $2, $3, $4, $5, NOW())",
            agent_id, "swap", 100.0 + i, "solana", "completed",
        )

    r = await client.get(f"/agents/{agent_id}/transactions", headers=auth_headers)
    assert r.status_code == 200
    txs = r.json()
    assert len(txs) == 3


@pytest.mark.asyncio
async def test_list_transactions_pagination(client, auth_headers, db_session):
    r = await client.post("/agents", json={"name": "TX Paginate"}, headers=auth_headers)
    agent_id = r.json()["id"]

    for i in range(5):
        await db_session.execute(
            "INSERT INTO transactions (agent_id, transaction_type, amount, blockchain, status, created_at) VALUES ($1, $2, $3, $4, $5, NOW())",
            agent_id, "swap", float(i), "solana", "completed",
        )

    r = await client.get(f"/agents/{agent_id}/transactions?limit=2&offset=0", headers=auth_headers)
    assert len(r.json()) == 2

    r = await client.get(f"/agents/{agent_id}/transactions?limit=2&offset=3", headers=auth_headers)
    assert len(r.json()) == 2


# ── Performance ──


@pytest.mark.asyncio
async def test_performance_empty(client, auth_headers):
    r = await client.post("/agents", json={"name": "Perf Agent"}, headers=auth_headers)
    agent_id = r.json()["id"]

    r = await client.get(f"/agents/{agent_id}/performance", headers=auth_headers)
    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.asyncio
async def test_performance_with_data(client, auth_headers, db_session):
    r = await client.post("/agents", json={"name": "Perf Agent 2"}, headers=auth_headers)
    agent_id = r.json()["id"]

    for i in range(3):
        await db_session.execute(
            "INSERT INTO performance (agent_id, date, total_value, daily_pnl, total_pnl, total_trades, successful_trades) VALUES ($1, NOW(), $2, $3, $4, $5, $6)",
            agent_id, 1000.0 + i * 100, 50.0 + i, 150.0 + i, 10 + i, 7 + i,
        )

    r = await client.get(f"/agents/{agent_id}/performance", headers=auth_headers)
    assert r.status_code == 200
    assert len(r.json()) == 3


@pytest.mark.asyncio
async def test_performance_summary(client, auth_headers, db_session):
    r = await client.post("/agents", json={"name": "Summary Agent"}, headers=auth_headers)
    agent_id = r.json()["id"]

    await db_session.execute(
        "INSERT INTO performance (agent_id, date, total_value, daily_pnl, total_pnl, win_rate, total_trades, successful_trades) VALUES ($1, NOW(), $2, $3, $4, $5, $6, $7)",
        agent_id, 1000.0, 50.0, 50.0, 0.7, 10, 7,
    )
    await db_session.execute(
        "INSERT INTO performance (agent_id, date, total_value, daily_pnl, total_pnl, win_rate, total_trades, successful_trades) VALUES ($1, NOW(), $2, $3, $4, $5, $6, $7)",
        agent_id, 1200.0, 100.0, 150.0, 0.8, 20, 16,
    )

    r = await client.get(f"/agents/{agent_id}/performance/summary", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["total_pnl"] == 150.0  # 50 + 100
    assert data["total_trades"] == 30  # 10 + 20
    assert data["peak_value"] == 1200.0
    assert data["avg_win_rate"] == pytest.approx(0.75, abs=0.01)


@pytest.mark.asyncio
async def test_performance_summary_empty(client, auth_headers):
    r = await client.post("/agents", json={"name": "Empty Summary"}, headers=auth_headers)
    agent_id = r.json()["id"]

    r = await client.get(f"/agents/{agent_id}/performance/summary", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["total_pnl"] == 0
    assert data["total_trades"] == 0


# ── Validation ──


@pytest.mark.asyncio
async def test_create_agent_validation(client, auth_headers):
    # risk_tolerance out of range
    r = await client.post("/agents", json={"name": "Bad", "risk_tolerance": 1.5}, headers=auth_headers)
    assert r.status_code == 422

    # max_position_size must be > 0
    r = await client.post("/agents", json={"name": "Bad", "max_position_size": -1}, headers=auth_headers)
    assert r.status_code == 422

    # name too long
    r = await client.post("/agents", json={"name": "x" * 200}, headers=auth_headers)
    assert r.status_code == 422
