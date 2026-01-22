"""
Tests for Health Check Router
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient) -> None:
    """Testa o endpoint de health check."""
    response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "godrive-api"


@pytest.mark.asyncio
async def test_readiness_check(client: AsyncClient) -> None:
    """Testa o endpoint de readiness check."""
    response = await client.get("/health/ready")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
