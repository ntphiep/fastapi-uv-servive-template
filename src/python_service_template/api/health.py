import typing as t

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field

from python_service_template.dependencies import (
    detailed_health_checker,
    simple_health_checker,
)
from python_service_template.infrastructure.health import (
    DetailedHealthChecker,
    DetailedHealthStatus,
    HealthIndicator,
    SimpleHealthChecker,
    SimpleHealthStatus,
)


class SimpleHealthResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    git_commit_sha: str = Field(alias="gitCommitSha")
    heartbeat: HealthIndicator
    version: str

    def to_domain(self) -> SimpleHealthStatus:
        return SimpleHealthStatus(
            git_commit_sha=self.git_commit_sha,
            heartbeat=self.heartbeat,
            version=self.version,
        )

    @classmethod
    def from_domain(cls, domain: SimpleHealthStatus) -> "SimpleHealthResponse":
        return cls(
            git_commit_sha=domain.git_commit_sha,
            heartbeat=domain.heartbeat,
            version=domain.version,
        )


class DetailedHealthResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    git_commit_sha: str = Field(alias="gitCommitSha")
    heartbeat: HealthIndicator
    version: str
    checks: dict[str, HealthIndicator]

    def to_domain(self) -> DetailedHealthStatus:
        return DetailedHealthStatus(
            git_commit_sha=self.git_commit_sha,
            heartbeat=self.heartbeat,
            version=self.version,
            checks=self.checks,
        )

    @classmethod
    def from_domain(cls, domain: DetailedHealthStatus) -> "DetailedHealthResponse":
        return cls(
            git_commit_sha=domain.git_commit_sha,
            heartbeat=domain.heartbeat,
            version=domain.version,
            checks=domain.checks,
        )


router = APIRouter(tags=["system"])


@router.get("/")
async def simple_health(
    simple_health_checker: t.Annotated[SimpleHealthChecker, Depends(simple_health_checker)],
) -> SimpleHealthResponse:
    """Simple health check endpoint."""
    status = await simple_health_checker.check()
    return SimpleHealthResponse.from_domain(status)


@router.get("/health")
async def detailed_health(
    detailed_health_checker: t.Annotated[DetailedHealthChecker, Depends(detailed_health_checker)],
) -> DetailedHealthResponse:
    """Detailed health check endpoint with system checks."""
    status = await detailed_health_checker.check()
    return DetailedHealthResponse.from_domain(status)
