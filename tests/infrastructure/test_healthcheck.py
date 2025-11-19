import pytest

from python_service_template.infrastructure.health import (
    DetailedHealthChecker,
    HealthIndicator,
    SimpleHealthChecker,
)


class MockCoffeeClient:
    def __init__(self, healthy: bool) -> None:
        self._healthy: bool = healthy

    async def healthy(self) -> bool:
        return self._healthy


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "client_healthy,expected_status",
    [
        (True, HealthIndicator.HEALTHY),
        (False, HealthIndicator.UNHEALTHY),
    ],
)
async def test_detailed_health_checker_status(client_healthy: bool, expected_status: HealthIndicator) -> None:
    client = MockCoffeeClient(client_healthy)
    healthcheck = DetailedHealthChecker(client, "1.0.0", "test-sha")  # type: ignore
    response = await healthcheck.check()
    assert response.heartbeat == expected_status
    assert response.checks["coffee"] == expected_status
    assert response.version == "1.0.0"
    assert response.git_commit_sha == "test-sha"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "client_healthy,expected_status",
    [
        (True, HealthIndicator.HEALTHY),
        (False, HealthIndicator.UNHEALTHY),
    ],
)
async def test_simple_health_checker_status(client_healthy: bool, expected_status: HealthIndicator) -> None:
    client = MockCoffeeClient(client_healthy)
    healthcheck = SimpleHealthChecker(client, "1.0.0", "test-sha")  # type: ignore
    response = await healthcheck.check()
    assert response.heartbeat == expected_status
    assert response.version == "1.0.0"
    assert response.git_commit_sha == "test-sha"


@pytest.mark.asyncio
async def test_detailed_health_checker_git_commit_sha():
    client = MockCoffeeClient(True)
    healthcheck = DetailedHealthChecker(client, "1.0.0", "testsha123")  # type: ignore
    response = await healthcheck.check()
    assert response.git_commit_sha == "testsha123"


@pytest.mark.asyncio
async def test_simple_health_checker_git_commit_sha():
    client = MockCoffeeClient(True)
    healthcheck = SimpleHealthChecker(client, "1.0.0", "testsha456")  # type: ignore
    response = await healthcheck.check()
    assert response.git_commit_sha == "testsha456"
