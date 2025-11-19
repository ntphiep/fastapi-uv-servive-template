import abc
import enum
import typing as t

from pydantic import BaseModel

from python_service_template.domain.coffee.repository import CoffeeClient


class HealthIndicator(str, enum.Enum):
    HEALTHY = "HEALTHY"
    UNHEALTHY = "UNHEALTHY"


class SimpleHealthStatus(BaseModel):
    git_commit_sha: str
    heartbeat: HealthIndicator
    version: str


class DetailedHealthStatus(SimpleHealthStatus):
    checks: dict[str, HealthIndicator]


T = t.TypeVar("T", SimpleHealthStatus, DetailedHealthStatus)


class HealthChecker(abc.ABC, t.Generic[T]):
    def __init__(self, coffee_client: CoffeeClient, app_version: str, git_sha: str) -> None:
        self.coffee_client = coffee_client
        self.app_version = app_version
        self.git_sha = git_sha

    async def check(self) -> T:
        checks: dict[str, HealthIndicator] = {}

        if await self.coffee_client.healthy():
            checks["coffee"] = HealthIndicator.HEALTHY
        else:
            checks["coffee"] = HealthIndicator.UNHEALTHY

        # More sophisticated checks can be added here
        return self._create_status(checks)

    @abc.abstractmethod
    def _create_status(self, checks: dict[str, HealthIndicator]) -> T:
        pass


class DetailedHealthChecker(HealthChecker[DetailedHealthStatus]):
    def _create_status(self, checks: dict[str, HealthIndicator]) -> DetailedHealthStatus:
        all_healthy = all(v == HealthIndicator.HEALTHY for v in checks.values())
        status = HealthIndicator.HEALTHY if all_healthy else HealthIndicator.UNHEALTHY
        return DetailedHealthStatus(
            git_commit_sha=self.git_sha,
            heartbeat=status,
            version=self.app_version,
            checks=checks,
        )


class SimpleHealthChecker(HealthChecker[SimpleHealthStatus]):
    def _create_status(self, checks: dict[str, HealthIndicator]) -> SimpleHealthStatus:
        all_healthy = all(v == HealthIndicator.HEALTHY for v in checks.values())
        status = HealthIndicator.HEALTHY if all_healthy else HealthIndicator.UNHEALTHY
        return SimpleHealthStatus(
            git_commit_sha=self.git_sha,
            heartbeat=status,
            version=self.app_version,
        )
