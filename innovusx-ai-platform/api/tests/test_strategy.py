"""Tests for strategy generation endpoints."""

import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_demo_strategy_endpoint():
    """Test demo strategy generation endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/strategy/demo",
            params={
                "industry": "fintech",
                "challenge": "Expand into European markets"
            }
        )

    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert "strategies" in data
    assert "quality_metrics" in data
    assert "metadata" in data

    # Check strategies
    assert len(data["strategies"]) >= 1
    strategy = data["strategies"][0]
    assert "id" in strategy
    assert "title" in strategy
    assert "category" in strategy
    assert "description" in strategy
    assert "confidence_score" in strategy
    assert "action_steps" in strategy

    # Check quality metrics
    metrics = data["quality_metrics"]
    assert "relevance" in metrics
    assert "groundedness" in metrics
    assert "coherence" in metrics
    assert "actionability" in metrics

    # Check metadata
    metadata = data["metadata"]
    assert "correlation_id" in metadata
    assert "model_version" in metadata
    assert "latency_ms" in metadata


@pytest.mark.asyncio
async def test_demo_strategy_with_defaults():
    """Test demo endpoint with default parameters."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/strategy/demo")

    assert response.status_code == 200
    data = response.json()
    assert len(data["strategies"]) >= 1


@pytest.mark.asyncio
async def test_strategy_quality_scores_in_range():
    """Test that quality scores are within valid range."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/strategy/demo")

    data = response.json()
    metrics = data["quality_metrics"]

    for metric_name in ["relevance", "groundedness", "coherence", "actionability"]:
        score = metrics[metric_name]
        assert 0.0 <= score <= 1.0, f"{metric_name} score out of range: {score}"


@pytest.mark.asyncio
async def test_strategy_confidence_scores_in_range():
    """Test that strategy confidence scores are within valid range."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/strategy/demo")

    data = response.json()

    for strategy in data["strategies"]:
        score = strategy["confidence_score"]
        assert 0.0 <= score <= 1.0, f"Confidence score out of range: {score}"


@pytest.mark.asyncio
async def test_strategy_action_steps_present():
    """Test that strategies have action steps."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/strategy/demo")

    data = response.json()

    for strategy in data["strategies"]:
        assert len(strategy["action_steps"]) >= 1
        for step in strategy["action_steps"]:
            assert "step_number" in step
            assert "title" in step
            assert "description" in step
