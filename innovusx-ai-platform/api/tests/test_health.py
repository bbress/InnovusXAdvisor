"""Tests for health check endpoints."""

import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    """Test basic health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "uptime_seconds" in data


@pytest.mark.asyncio
async def test_liveness_check():
    """Test liveness probe endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/live")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"


@pytest.mark.asyncio
async def test_readiness_check():
    """Test readiness probe endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/ready")

    assert response.status_code == 200
    data = response.json()
    assert "ready" in data
    assert "checks" in data


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint returns API info."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert data["status"] == "operational"
